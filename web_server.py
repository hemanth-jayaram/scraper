#!/usr/bin/env python3
"""
Ultimate Scraper V2 - Web Interface Backend
Beautiful Flask server for managing EC2 scraping jobs with improved real-time updates
"""

import os
import json
import time
import subprocess
import threading
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import paramiko
import queue
import logging
import boto3
from botocore.exceptions import ClientError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configuration
EC2_HOST = "54.82.140.246"
EC2_USER = "ec2-user" 
EC2_KEY_PATH = r"C:\Users\heman\Downloads\key-scraper.pem"
EC2_SCRAPER_PATH = "/home/ec2-user/ultimate_scraper_v2.py"
EC2_ENV_PATH = "/home/ec2-user/ultimate_scraper_env/bin/activate"

# S3 Configuration (using the same bucket as SCRAPER folder)
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME', 'bockscraper')  # Same bucket used by the SCRAPER folder

# Global state
scraping_active = False
current_job = None
all_logs = []  # Store all logs for proper tracking
progress_percentage = 0
current_status = "Ready"
job_completed = False
s3_upload_completed = False
s3_session_folder = None

class ScrapingJob:
    def __init__(self, url, max_articles, output_path, concurrent):
        self.url = url
        self.max_articles = max_articles
        self.output_path = output_path
        self.concurrent = concurrent
        self.start_time = time.time()
        self.ssh_client = None
        self.process_thread = None
        self.is_running = False
        self.articles_found = 0
        self.articles_saved = 0
        
    def start(self):
        """Start the scraping job on EC2"""
        self.is_running = True
        self.process_thread = threading.Thread(target=self._run_scraping)
        self.process_thread.start()
        
    def stop(self):
        """Stop the scraping job"""
        self.is_running = False
        if self.ssh_client:
            try:
                # Kill any running scraper processes on EC2
                self.ssh_client.exec_command("pkill -f ultimate_scraper_v2.py")
                self.ssh_client.close()
            except Exception as e:
                logger.error(f"Error stopping scraping: {e}")
        
    def _run_scraping(self):
        """Run the scraping process on EC2 and stream logs"""
        global progress_percentage, current_status, job_completed
        
        try:
            # Connect to EC2
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            add_log("Connecting to EC2 instance...", "info")
            progress_percentage = 5
            current_status = "Connecting to EC2..."
            
            self.ssh_client.connect(
                hostname=EC2_HOST,
                username=EC2_USER,
                key_filename=EC2_KEY_PATH,
                timeout=30
            )
            
            add_log("Connected to EC2 successfully!", "success")
            progress_percentage = 10
            current_status = "Preparing scraper..."
            
            # Prepare the command with S3 upload
            session_id = f"session_{int(time.time())}"
            global s3_session_folder
            s3_session_folder = session_id
            
            remote_output_path = f"/home/ec2-user/scraping_output_{session_id}"
            
            # First, just run the scraper without S3 upload to test
            command = f"source {EC2_ENV_PATH} && mkdir -p {remote_output_path} && python {EC2_SCRAPER_PATH} \"{self.url}\" --max-articles {self.max_articles} --output {remote_output_path} --concurrent {self.concurrent}"
            
            add_log(f"Starting scraper with {self.max_articles} articles", "info")
            add_log(f"Output path: {remote_output_path}", "info")
            progress_percentage = 15
            current_status = "Scraping articles..."
            
            # Execute command
            stdin, stdout, stderr = self.ssh_client.exec_command(command)
            
            # Stream output in real-time
            while self.is_running:
                line = stdout.readline()
                if not line:
                    break
                    
                line = line.strip()
                if line:
                    add_log(line, self._classify_log_line(line))
                    
                    # Parse statistics from logs for progress tracking
                    if "VERIFIED ARTICLE" in line:
                        self.articles_found += 1
                        progress_percentage = min(15 + (self.articles_found / self.max_articles) * 60, 75)
                        current_status = f"Found {self.articles_found} articles, processing images..."
                        
                    elif "SUCCESS: Saved" in line and "image.jpg" in line:
                        self.articles_saved += 1
                        progress_percentage = min(75 + (self.articles_saved / max(self.articles_found, 1)) * 15, 90)
                        current_status = f"Saved {self.articles_saved}/{self.articles_found} articles with images"
                        
                    elif "COMPLETE:" in line or "completed successfully" in line:
                        progress_percentage = 90
                        current_status = "Scraping completed, starting S3 upload..."
                        add_log("Scraping completed, starting S3 upload...", "success")
            
            # Wait for completion
            exit_status = stdout.channel.recv_exit_status()
            
            if exit_status == 0 and self.is_running:
                add_log("Scraping completed successfully! Starting S3 upload...", "success")
                progress_percentage = 92
                current_status = "Uploading to S3..."
                
                # Now run S3 upload as separate command
                s3_command = f"aws s3 sync {remote_output_path}/ s3://{S3_BUCKET_NAME}/{session_id}/ --exclude \"*.log\""
                add_log(f"S3 upload command: aws s3 sync to {S3_BUCKET_NAME}/{session_id}/", "info")
                
                try:
                    stdin, stdout, stderr = self.ssh_client.exec_command(s3_command)
                    s3_exit_status = stdout.channel.recv_exit_status()
                    
                    if s3_exit_status == 0:
                        global s3_upload_completed, scraping_active
                        s3_upload_completed = True
                        job_completed = True
                        scraping_active = False  # Reset scraping_active when job completes
                        progress_percentage = 100
                        current_status = f"All {self.articles_saved} articles uploaded to S3! Ready to download."
                        add_log(f"S3 upload completed! Articles saved to bucket: {S3_BUCKET_NAME}/{session_id}", "success")
                        
                        # Clean up remote directory after successful S3 upload
                        self.ssh_client.exec_command(f"rm -rf {remote_output_path}")
                        add_log("Cleaned up temporary files on EC2", "info")
                    else:
                        add_log("S3 upload failed", "error")
                        current_status = "Scraping completed but S3 upload failed"
                        scraping_active = False  # Reset on S3 upload failure
                        
                except Exception as e:
                    add_log(f"S3 upload error: {str(e)}", "error")
                    current_status = "S3 upload failed"
                    scraping_active = False  # Reset on S3 upload error
                
            else:
                add_log("Scraping encountered an error or was stopped", "error")
                current_status = "Error or stopped"
                scraping_active = False  # Reset on scraping error
                
        except Exception as e:
            error_msg = f"Error during scraping: {str(e)}"
            add_log(error_msg, "error")
            current_status = "Error occurred"
            scraping_active = False  # Reset on any error
            logger.error(error_msg)
            
        finally:
            if self.ssh_client:
                self.ssh_client.close()
            self.is_running = False
            
    def _classify_log_line(self, line):
        """Classify log lines by type for styling"""
        line_lower = line.lower()
        if any(word in line_lower for word in ['error', 'failed', 'exception']):
            return 'error'
        elif any(word in line_lower for word in ['success', 'saved', 'complete', 'downloaded']):
            return 'success'
        elif any(word in line_lower for word in ['warning', 'filtered']):
            return 'warning'
        else:
            return 'info'
            

def add_log(message, log_type="info"):
    """Add a log message to the global log list"""
    global all_logs
    
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_entry = {
        'timestamp': timestamp,
        'message': message,
        'type': log_type
    }
    all_logs.append(log_entry)
    
    # Keep only last 200 log entries to prevent memory issues
    if len(all_logs) > 200:
        all_logs = all_logs[-200:]

@app.route('/')
def index():
    """Serve the main interface"""
    return send_from_directory('.', 'index.html')

@app.route('/start_scraping', methods=['POST'])
def start_scraping():
    """Start a new scraping job"""
    global scraping_active, current_job, all_logs, progress_percentage, current_status, job_completed
    
    if scraping_active:
        return jsonify({'error': 'Scraping already in progress'}), 400
    
    try:
        data = request.json
        url = data.get('url')
        max_articles = data.get('maxArticles', 40)
        output_path = data.get('outputPath', 'scraped_results')
        concurrent = data.get('concurrent', 50)
        
        # Validate inputs
        if not url:
            return jsonify({'error': 'URL is required'}), 400
            
        # Reset global state
        all_logs = []
        progress_percentage = 0
        current_status = 'Starting...'
        job_completed = False
        s3_upload_completed = False
        s3_session_folder = None
        
        # Create and start job
        current_job = ScrapingJob(url, max_articles, output_path, concurrent)
        current_job.start()
        scraping_active = True
        
        add_log(f"Scraping job started for {url}", "success")
        
        return jsonify({'message': 'Scraping started successfully'})
        
    except Exception as e:
        error_msg = f"Error starting scraping: {str(e)}"
        add_log(error_msg, "error")
        return jsonify({'error': error_msg}), 500

@app.route('/stop_scraping', methods=['POST'])
def stop_scraping():
    """Stop the current scraping job"""
    global scraping_active, current_job, current_status
    
    if not scraping_active or not current_job:
        return jsonify({'error': 'No active scraping job'}), 400
    
    try:
        current_job.stop()
        scraping_active = False
        current_status = 'Stopped by user'
        add_log("Scraping stopped by user", "warning")
        
        return jsonify({'message': 'Scraping stopped successfully'})
        
    except Exception as e:
        error_msg = f"Error stopping scraping: {str(e)}"
        add_log(error_msg, "error")
        return jsonify({'error': error_msg}), 500

@app.route('/get_status', methods=['GET'])
def get_status():
    """Get current scraping status and logs"""
    global all_logs, progress_percentage, current_status, job_completed, s3_upload_completed, s3_session_folder
    
    response_data = {
        'progress': progress_percentage,
        'status': current_status,
        'completed': job_completed,
        'logs': all_logs,  # Send all logs so frontend can track properly
        'isActive': scraping_active,
        's3_upload_completed': s3_upload_completed,
        's3_session_folder': s3_session_folder
    }
    
    return jsonify(response_data)

@app.route('/test_connection', methods=['GET'])
def test_connection():
    """Test EC2 connection"""
    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(
            hostname=EC2_HOST,
            username=EC2_USER,
            key_filename=EC2_KEY_PATH,
            timeout=10
        )
        
        # Test if scraper exists
        stdin, stdout, stderr = ssh_client.exec_command(f"ls -la {EC2_SCRAPER_PATH}")
        result = stdout.read().decode()
        
        ssh_client.close()
        
        if "ultimate_scraper_v2.py" in result:
            return jsonify({'status': 'connected', 'message': 'EC2 connection successful'})
        else:
            return jsonify({'status': 'error', 'message': 'Scraper not found on EC2'}), 500
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Connection failed: {str(e)}'}), 500

@app.route('/download_from_s3', methods=['POST'])
def download_from_s3():
    """Download articles from S3 to local output path"""
    global s3_session_folder, s3_upload_completed
    
    if not s3_upload_completed or not s3_session_folder:
        return jsonify({'error': 'No S3 session available for download'}), 400
    
    try:
        data = request.json
        output_path = data.get('outputPath', 'scraped_results')
        
        add_log("Starting download from S3...", "info")
        
        # Create local output directory
        local_output = Path(output_path)
        local_output.mkdir(parents=True, exist_ok=True)
        
        # Connect to EC2 and download from S3
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(
            hostname=EC2_HOST,
            username=EC2_USER,
            key_filename=EC2_KEY_PATH,
            timeout=30
        )
        
        # Create temporary download directory on EC2
        temp_download_path = f"/home/ec2-user/temp_download_{int(time.time())}"
        download_command = f"""
        mkdir -p {temp_download_path} &&
        aws s3 sync s3://{S3_BUCKET_NAME}/{s3_session_folder}/ {temp_download_path}/ &&
        echo "S3_DOWNLOAD_COMPLETED"
        """
        
        add_log("Downloading from S3 to EC2...", "info")
        stdin, stdout, stderr = ssh_client.exec_command(download_command)
        
        # Monitor download progress
        while True:
            line = stdout.readline()
            if not line:
                break
            line = line.strip()
            if line:
                add_log(line, "info")
                if "S3_DOWNLOAD_COMPLETED" in line:
                    break
        
        # Now transfer from EC2 to local
        add_log("Transferring files from EC2 to local machine...", "info")
        sftp = ssh_client.open_sftp()
        
        def download_recursive(remote_dir, local_dir):
            try:
                remote_items = sftp.listdir_attr(remote_dir)
                for item in remote_items:
                    remote_item_path = f"{remote_dir}/{item.filename}"
                    local_item_path = local_dir / item.filename
                    
                    if item.st_mode & 0o40000:  # Directory
                        local_item_path.mkdir(exist_ok=True)
                        download_recursive(remote_item_path, local_item_path)
                    else:  # File
                        sftp.get(remote_item_path, str(local_item_path))
                        add_log(f"Downloaded: {item.filename}", "success")
                        
            except Exception as e:
                add_log(f"Download error: {str(e)}", "error")
        
        download_recursive(temp_download_path, local_output)
        
        # Clean up temporary directory on EC2
        ssh_client.exec_command(f"rm -rf {temp_download_path}")
        ssh_client.close()
        
        add_log(f"All files downloaded successfully to: {output_path}", "success")
        
        return jsonify({'message': f'Files downloaded successfully to {output_path}'})
        
    except Exception as e:
        error_msg = f"Error downloading from S3: {str(e)}"
        add_log(error_msg, "error")
        return jsonify({'error': error_msg}), 500

if __name__ == '__main__':
    # Initialize logs
    add_log("Web server starting...", "info")
    add_log("Ultimate Scraper V2 Web Interface Ready", "success")
    add_log(f"EC2 Instance: {EC2_HOST}", "info")
    
    print("=" * 80)
    print("🚀 ULTIMATE SCRAPER V2 - WEB INTERFACE")
    print("=" * 80)
    print(f"🌐 Open your browser and go to: http://localhost:5000")
    print(f"☁️  EC2 Instance: {EC2_HOST}")
    print(f"📁 Default Output: scraped_results/")
    print("=" * 80)
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
        if current_job and scraping_active:
            current_job.stop()
    except Exception as e:
        print(f"\n❌ Server error: {e}")
