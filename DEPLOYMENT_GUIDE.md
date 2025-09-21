# 🚀 Ultimate Scraper V2 - Web Interface Deployment Guide

**A comprehensive guide for deploying the Ultimate Scraper V2 Web Interface to production environments.**

---

## Table of Contents

1. [Environment Variables and Configuration](#1-environment-variables-and-configuration)
2. [Setup Instructions](#2-setup-instructions)
3. [Deployment Steps](#3-deployment-steps)
4. [Validation and Testing](#4-validation-and-testing)
5. [Common Pitfalls](#5-common-pitfalls)
6. [Changing EC2 Instance](#6-changing-ec2-instance)

---

## Project Overview

The **Ultimate Scraper V2 Web Interface** is a **completely self-contained** Flask-based web application that provides a beautiful, modern interface for managing EC2-based article scraping jobs. This project includes everything needed for deployment with no external dependencies.

**✅ SELF-CONTAINED PROJECT STRUCTURE:**
- **Web Server** (`web_server.py`) - Flask backend with real-time progress tracking and full S3 integration
- **Main Scraper** (`ultimate_scraper_v2.py`) - The core scraping engine that runs on EC2 (now with relative paths)
- **Web Interface** (`index.html`) - Modern responsive frontend
- **Launcher** (`launch_scraper_interface.bat`) - One-click Windows launcher with enhanced error handling
- **Configuration** (`.env`, `s3_config.example.env`) - All S3 and AWS configuration files included
- **Dependencies** (`requirements_web.txt`) - All Python packages including boto3 for S3
- **Documentation** (`README.md`) - Updated project documentation

**🎯 DEPLOYMENT READY:** This folder can be copied anywhere and deployed independently!

---

## 🚀 **SELF-CONTAINED PROJECT NOTICE**

**✅ IMPORTANT**: This is now a **completely self-contained project**. All changes have been made to ensure:

### ✅ **What's Included (All Dependencies)**
- ✅ **All configuration files** (`.env`, `s3_config.example.env`)
- ✅ **All Python dependencies** (`requirements_web.txt` with boto3)
- ✅ **Enhanced launcher** with improved error handling
- ✅ **Relative paths** in scraper (no hardcoded absolute paths)
- ✅ **Full S3 integration** in web server
- ✅ **Updated documentation** (this guide + README.md)

### ✅ **What This Means**
- 📁 **Portable**: Copy the `final/` folder anywhere - it will work
- 🚀 **Independent**: No external dependencies outside this folder
- 🔧 **Complete**: Everything needed for deployment is included
- 🎯 **Production Ready**: Can be deployed immediately

### ✅ **Deployment Options**
1. **Copy to new server**: Just copy the entire `final/` folder
2. **Local development**: Run directly from this folder
3. **Team deployment**: Share this folder - everything is included
4. **Clean deployment**: Can delete everything else except `final/` folder

---

## 1. Environment Variables and Configuration

### 1.1 Core Configuration Files That Need Updates

| **File Path** | **Line Numbers** | **Configuration Type** | **Current Value** | **Action Required** |
|---------------|------------------|------------------------|-------------------|---------------------|
| `web_server.py` | Lines 30-32 | EC2 Instance Details | `EC2_HOST = "54.82.140.246"` | **CHANGE** to your EC2 IP |
| `web_server.py` | Line 32 | SSH Key Path | `r"C:\Users\heman\Downloads\key-scraper.pem"` | **CHANGE** to your key path |
| `web_server.py` | Line 37 | S3 Bucket Name | `S3_BUCKET_NAME = 'bockscraper'` | **CHANGE** to your bucket |
| `.env` | Lines 7-8 | S3 Configuration | `S3_BUCKET_NAME=bockscraper` | **CHANGE** to your bucket |
| `.env` | Line 13-14 | AWS Credentials | `# AWS_ACCESS_KEY_ID=...` | **UNCOMMENT** and add credentials |
| `launch_scraper_interface.bat` | Line 66 | EC2 IP for Testing | `54.82.140.246` | **CHANGE** to your EC2 IP |

### 1.2 Required Configuration Changes

#### **A. Update Web Server Configuration (`web_server.py`)**

**Lines 28-32: EC2 Connection Settings**
```python
# BEFORE (current values):
EC2_HOST = "54.82.140.246"                                    # CHANGE THIS
EC2_USER = "ec2-user"                                         # Keep as-is
EC2_KEY_PATH = r"C:\Users\heman\Downloads\key-scraper.pem"   # CHANGE THIS
EC2_SCRAPER_PATH = "/home/ec2-user/ultimate_scraper_v2.py"    # Keep as-is
EC2_ENV_PATH = "/home/ec2-user/ultimate_scraper_env/bin/activate"  # Keep as-is

# AFTER (your production values):
EC2_HOST = "YOUR_PRODUCTION_EC2_IP"                           # Your EC2 public IP
EC2_USER = "ec2-user"                                         # Keep as-is
EC2_KEY_PATH = r"C:\path\to\your\production-key.pem"        # Your SSH key path
EC2_SCRAPER_PATH = "/home/ec2-user/ultimate_scraper_v2.py"    # Keep as-is
EC2_ENV_PATH = "/home/ec2-user/ultimate_scraper_env/bin/activate"  # Keep as-is
```

#### **B. Update Launcher Script (`launch_scraper_interface.bat`)**

**Line 66: EC2 Connection Test**
```batch
REM BEFORE:
echo Checking connection to 54.82.140.246...

REM AFTER:
echo Checking connection to YOUR_PRODUCTION_EC2_IP...
```

### 1.3 S3 Configuration Required

This **self-contained** web interface project **DOES require S3 setup** for the complete workflow:
- ✅ S3 bucket configuration
- ✅ AWS credentials setup  
- ✅ Environment variables for S3 access
- ✅ S3 bucket name configuration

**✅ SELF-CONTAINED S3 SETUP**: All S3 configuration files are now included in this project folder (`.env`, `s3_config.example.env`).

**Workflow**: Articles are scraped on EC2 → Uploaded to S3 → Downloaded to local machine via web interface

#### **A. S3 Configuration File (`.env`)**
```bash
# S3 Configuration - CHANGE THESE VALUES
S3_UPLOAD_ENABLED=true
S3_BUCKET_NAME=your-production-bucket-name
AWS_REGION=us-east-1

# AWS Credentials - UNCOMMENT AND UPDATE
AWS_ACCESS_KEY_ID=your-access-key-id
AWS_SECRET_ACCESS_KEY=your-secret-access-key
```

#### **B. Web Server S3 Configuration (`web_server.py`)**
```python
# Line 37: Update S3 bucket name
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME', 'your-production-bucket-name')
```

---

## 2. Setup Instructions

### 2.1 EC2 Instance Setup

#### **A. Launch EC2 Instance**
1. **AMI**: Amazon Linux 2 or Amazon Linux 2023
2. **Instance Type**: `t3.medium` or larger (minimum 2 vCPU, 4GB RAM)
3. **Security Group**: 
   - SSH (port 22) from your deployment machine IP
   - **No need for port 5000** - web server runs locally
4. **Key Pair**: Download and save the `.pem` file securely
5. **Storage**: 20GB+ EBS volume

#### **B. Install Dependencies on EC2**
```bash
# Connect to EC2
ssh -i /path/to/your-key.pem ec2-user@YOUR_EC2_IP

# Update system
sudo yum update -y

# Install Python 3 and development tools
sudo yum install -y python3 python3-pip python3-devel gcc

# Install required system packages for image processing
sudo yum install -y libjpeg-devel zlib-devel freetype-devel

# Create project directory
mkdir -p ~/
cd ~/
```

#### **C. Upload Scraper Script to EC2**
```bash
# From your local machine (Windows PowerShell or Command Prompt)
scp -i "C:\path\to\your-key.pem" "C:\path\to\final\ultimate_scraper_v2.py" ec2-user@YOUR_EC2_IP:~/

# Verify upload
ssh -i "C:\path\to\your-key.pem" ec2-user@YOUR_EC2_IP "ls -la ~/ultimate_scraper_v2.py"
```

#### **D. Setup Python Environment on EC2**
```bash
# On EC2 instance
cd ~/

# Create virtual environment
python3 -m venv ultimate_scraper_env
source ultimate_scraper_env/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install required packages for ultimate_scraper_v2.py
pip install scrapy>=2.11.0
pip install trafilatura>=1.6.0
pip install beautifulsoup4>=4.12.0
pip install lxml>=4.9.0
pip install newspaper3k>=0.2.8
pip install Pillow>=9.0.0
pip install aiohttp>=3.8.0
pip install requests>=2.28.0

# Test the scraper installation
python ultimate_scraper_v2.py --help
```

### 2.2 Local Machine Setup (Windows)

#### **A. Prerequisites**
- Windows 10/11 with PowerShell
- Python 3.8+ installed and in PATH
- SSH client available (built into Windows 10/11)

#### **B. Verify Python Installation**
```cmd
# Open Command Prompt or PowerShell
python --version
# Should show Python 3.8.0 or higher
```

#### **C. Download Project Files**
Ensure you have all files from the `final` folder:
- `web_server.py`
- `ultimate_scraper_v2.py` 
- `index.html`
- `requirements_web.txt`
- `launch_scraper_interface.bat`
- `README.md`

---

## 3. Deployment Steps

### 3.1 Pre-Deployment Checklist

- [ ] EC2 instance is running and accessible via SSH
- [ ] SSH key file (.pem) has correct permissions and path is noted
- [ ] `ultimate_scraper_v2.py` is uploaded to EC2 home directory
- [ ] Python virtual environment is created on EC2 with required packages
- [ ] Local machine has Python 3.8+ installed
- [ ] All configuration files are updated with production values

### 3.2 Update Configuration Files

#### **Step 1: Update Web Server Configuration**
```bash
# Edit web_server.py with your production values
# Lines 28-32: Update EC2 connection details

# Example using notepad:
notepad web_server.py

# Or using VS Code:
code web_server.py
```

**Required Changes:**
```python
# Line 28: Change EC2 IP address
EC2_HOST = "YOUR_PRODUCTION_EC2_IP"

# Line 30: Change SSH key path  
EC2_KEY_PATH = r"C:\path\to\your\production-key.pem"
```

#### **Step 2: Update Launcher Script**
```bash
# Edit launch_scraper_interface.bat
notepad launch_scraper_interface.bat

# Line 66: Update the connection test IP
echo Checking connection to YOUR_PRODUCTION_EC2_IP...
```

#### **Step 3: Verify SSH Key Permissions**
```cmd
# On Windows, ensure the SSH key file is secure
# Right-click the .pem file → Properties → Security
# Remove all users except your account and SYSTEM
# Give your account Full Control
```

### 3.3 Test EC2 Connection

#### **Step 1: Manual SSH Test**
```cmd
# Test SSH connection manually
ssh -i "C:\path\to\your-key.pem" ec2-user@YOUR_EC2_IP

# If successful, you should see the EC2 command prompt
# Test the scraper:
ls -la ~/ultimate_scraper_v2.py
source ~/ultimate_scraper_env/bin/activate
python ~/ultimate_scraper_v2.py --help

# Exit EC2
exit
```

#### **Step 2: Test Scraper Execution**
```cmd
# Test a quick scrape to verify everything works
ssh -i "C:\path\to\your-key.pem" ec2-user@YOUR_EC2_IP "source ~/ultimate_scraper_env/bin/activate && python ~/ultimate_scraper_v2.py 'https://www.bbc.com/news' --max-articles 2 --output test_output"
```

### 3.4 Deploy Web Interface

#### **Step 1: Launch Web Interface**
```cmd
# Navigate to the final folder
cd C:\path\to\your\final\folder

# Run the launcher (this will set up everything automatically)
launch_scraper_interface.bat
```

The launcher script will:
1. ✅ Check Python installation
2. ✅ Create virtual environment (`web_venv`)
3. ✅ Install Flask dependencies
4. ✅ Test EC2 connection
5. ✅ Launch the web server
6. ✅ Open browser to `http://localhost:5000`

#### **Step 2: Alternative Manual Launch**
```cmd
# If you prefer manual setup:
cd C:\path\to\your\final\folder

# Create virtual environment
python -m venv web_venv
web_venv\Scripts\activate

# Install dependencies
pip install -r requirements_web.txt

# Start web server
python web_server.py
```

### 3.5 Production Deployment Options

#### **Option A: Windows Service (Advanced)**
```cmd
# Install NSSM (Non-Sucking Service Manager)
# Download from: https://nssm.cc/download

# Create Windows service
nssm install "UltimateScraperWeb" "C:\path\to\final\web_venv\Scripts\python.exe" "C:\path\to\final\web_server.py"
nssm set "UltimateScraperWeb" AppDirectory "C:\path\to\final"
nssm start "UltimateScraperWeb"
```

#### **Option B: Task Scheduler (Simple)**
```cmd
# Create a scheduled task that runs at startup
# Task Scheduler → Create Basic Task
# Name: Ultimate Scraper Web Interface
# Trigger: When the computer starts
# Action: Start a program
# Program: C:\path\to\final\launch_scraper_interface.bat
```

---

## 4. Validation and Testing

### 4.1 Test Self-Contained Setup

#### **A. Verify Project Completeness**
```cmd
# Navigate to the final folder
cd C:\path\to\final

# Check all required files are present
dir
```

**Expected self-contained files:**
- ✅ `.env` - S3 configuration
- ✅ `DEPLOYMENT_GUIDE.md` - This guide
- ✅ `index.html` - Web interface
- ✅ `launch_scraper_interface.bat` - Enhanced launcher
- ✅ `README.md` - Updated project documentation
- ✅ `requirements_web.txt` - Python dependencies (includes boto3)
- ✅ `s3_config.example.env` - Configuration template
- ✅ `ultimate_scraper_v2.py` - Core scraper (now with relative paths)
- ✅ `web_server.py` - Flask backend with full S3 integration

#### **B. Launch Test**
```cmd
# Run the enhanced launcher
launch_scraper_interface.bat
```

**Expected Output:**
```
===============================================
   🚀 ULTIMATE SCRAPER V2 WEB INTERFACE 🚀
===============================================

  Modern • Beautiful • Real-time • Cloud-powered

===============================================
✅ Python detected
📦 Creating virtual environment for web interface...
✅ Virtual environment created
🔄 Activating virtual environment...
📥 Installing/updating web interface dependencies...
✅ Dependencies ready
🔍 Testing EC2 connection...
Checking connection to YOUR_EC2_IP...
🚀 Starting Flask web server...
```

#### **B. Browser Test**
1. **Browser should open automatically** to `http://localhost:5000`
2. **Verify interface loads** with modern design
3. **Check "Test EC2 Connection"** button works
4. **Expected response**: `"EC2 connection successful"`

### 4.2 Test Complete Scraping Pipeline

#### **A. Quick Test Scrape**
1. **Open web interface**: `http://localhost:5000`
2. **Enter test URL**: `https://www.bbc.com/news`
3. **Set max articles**: `5` (for quick testing)
4. **Set output path**: `test_results`
5. **Click "Start Scraping"**

#### **B. Monitor Progress**
Watch for these status updates:
```
Connecting to EC2...           (Progress: 5%)
Connected to EC2 successfully! (Progress: 10%)
Preparing scraper...           (Progress: 15%)
Scraping in progress...        (Progress: 15-85%)
Downloading results...         (Progress: 85-100%)
Completed! Files saved to...   (Progress: 100%)
```

#### **C. Verify Results**
```cmd
# Check that files were downloaded locally
dir test_results
# Should show article folders with images and JSON files
```

### 4.3 Test EC2 Connection Endpoint

#### **A. Direct API Test**
```cmd
# Test the connection endpoint directly
curl http://localhost:5000/test_connection

# Expected response:
{"status": "connected", "message": "EC2 connection successful"}
```

#### **B. Web Interface Connection Test**
1. **Click "Test EC2 Connection"** in the web interface
2. **Green success message** should appear
3. **Check browser console** for any errors (F12 → Console)

### 4.4 Verify Log Files

#### **A. Check Web Server Logs**
```cmd
# Web server logs are displayed in the console
# Look for these key messages:
Web server starting...
Ultimate Scraper V2 Web Interface Ready
EC2 Instance: YOUR_EC2_IP
🌐 Open your browser and go to: http://localhost:5000
```

#### **B. Check Scraper Logs on EC2**
```cmd
# SSH to EC2 and check for any log files
ssh -i "C:\path\to\your-key.pem" ec2-user@YOUR_EC2_IP
ls -la ~/*.log
ls -la ~/scraping_output_*/
```

---

## 5. Common Pitfalls

### 5.1 Connection Issues

#### **Problem: "SSH connection failed"**
**Causes & Solutions:**

**A. Security Group Issues**
```cmd
# Check EC2 security group allows SSH from your IP
# AWS Console → EC2 → Security Groups → Inbound Rules
# Required: SSH (port 22) from YOUR_PUBLIC_IP/32
```

**B. SSH Key Permissions (Windows)**
```cmd
# Fix Windows SSH key permissions:
# 1. Right-click .pem file → Properties → Security
# 2. Click "Advanced" → "Disable inheritance"
# 3. Remove all users except your account
# 4. Give your account "Full control"
```

**C. Wrong IP Address**
```cmd
# Verify you're using the correct public IP
# AWS Console → EC2 → Instances → Select instance → Public IPv4 address
# Or use AWS CLI:
aws ec2 describe-instances --instance-ids i-1234567890abcdef0 --query 'Reservations[0].Instances[0].PublicIpAddress'
```

#### **Problem: "Connection timeout"**
**Causes & Solutions:**

**A. Instance Not Running**
```cmd
# Check instance state in AWS Console
# Start the instance if it's stopped
aws ec2 start-instances --instance-ids i-1234567890abcdef0
```

**B. Network ACLs or VPC Issues**
```cmd
# Ensure instance is in a public subnet
# Verify internet gateway and route table configuration
# Check Network ACLs allow SSH traffic
```

### 5.2 Web Interface Issues

#### **Problem: "Web interface not loading"**
**Causes & Solutions:**

**A. Python Not Installed**
```cmd
# Install Python 3.8+ from python.org
# Verify installation:
python --version
```

**B. Port 5000 Already in Use**
```cmd
# Check what's using port 5000:
netstat -ano | findstr :5000

# Kill the process if needed:
taskkill /PID [PID_NUMBER] /F

# Or change port in web_server.py (line 373):
app.run(host='0.0.0.0', port=5001, debug=False, threaded=True)
```

**C. Firewall Blocking Local Access**
```cmd
# Add Windows Firewall exception:
# Control Panel → System and Security → Windows Defender Firewall
# → Allow an app through firewall → Allow Python
```

#### **Problem: "Module not found errors"**
**Causes & Solutions:**

**A. Virtual Environment Issues**
```cmd
# Delete and recreate virtual environment:
rmdir /s web_venv
python -m venv web_venv
web_venv\Scripts\activate
pip install -r requirements_web.txt
```

**B. Missing Dependencies**
```cmd
# Install dependencies manually:
pip install Flask>=2.3.0
pip install flask-cors>=4.0.0
pip install paramiko>=3.3.0
pip install pathlib2>=2.3.0
```

### 5.3 EC2 Scraper Issues

#### **Problem: "Scraper script not found on EC2"**
**Causes & Solutions:**

**A. File Not Uploaded**
```cmd
# Re-upload the scraper script:
scp -i "C:\path\to\key.pem" ultimate_scraper_v2.py ec2-user@YOUR_EC2_IP:~/

# Verify upload:
ssh -i "C:\path\to\key.pem" ec2-user@YOUR_EC2_IP "ls -la ~/ultimate_scraper_v2.py"
```

**B. Wrong File Permissions**
```cmd
# Make script executable:
ssh -i "C:\path\to\key.pem" ec2-user@YOUR_EC2_IP "chmod +x ~/ultimate_scraper_v2.py"
```

#### **Problem: "Virtual environment not found"**
**Causes & Solutions:**

**A. Environment Not Created**
```cmd
# Create virtual environment on EC2:
ssh -i "C:\path\to\key.pem" ec2-user@YOUR_EC2_IP
python3 -m venv ~/ultimate_scraper_env
source ~/ultimate_scraper_env/bin/activate
pip install --upgrade pip
pip install scrapy trafilatura beautifulsoup4 lxml newspaper3k Pillow aiohttp requests
```

**B. Wrong Path in Configuration**
```cmd
# Verify the virtual environment path in web_server.py line 32:
EC2_ENV_PATH = "/home/ec2-user/ultimate_scraper_env/bin/activate"

# Check actual path on EC2:
ssh -i "C:\path\to\key.pem" ec2-user@YOUR_EC2_IP "ls -la ~/ultimate_scraper_env/bin/activate"
```

### 5.4 Scraping Performance Issues

#### **Problem: "Slow scraping or timeouts"**
**Causes & Solutions:**

**A. Insufficient EC2 Resources**
```cmd
# Upgrade to larger instance type:
# t3.medium → t3.large or t3.xlarge
# More CPU and memory = faster processing
```

**B. Network Bandwidth Limits**
```cmd
# Consider instances with better network performance:
# t3.medium: Up to 5 Gbps
# t3.large: Up to 5 Gbps  
# t3.xlarge: Up to 5 Gbps
# m5.large: Up to 10 Gbps
```

**C. Concurrent Processing Limits**
```cmd
# Reduce concurrency in web interface if causing issues
# Default: 50 concurrent requests
# Try: 20-30 for better stability
```

### 5.5 Local File Download Issues

#### **Problem: "Files not downloading to local machine"**
**Causes & Solutions:**

**A. SSH Connection Lost During Transfer**
```cmd
# Check SSH connection stability
# Increase SSH timeout in web_server.py line 93:
self.ssh_client.connect(
    hostname=EC2_HOST,
    username=EC2_USER,
    key_filename=EC2_KEY_PATH,
    timeout=60  # Increase from 30 to 60 seconds
)
```

**B. Local Disk Space Issues**
```cmd
# Check available disk space:
dir C:\ 
# Ensure sufficient space for downloaded results
# Each article with image: ~1-5MB
```

**C. File Permissions on Windows**
```cmd
# Ensure output directory is writable:
# Right-click output folder → Properties → Security
# Verify your user has "Full control"
```

---

## 🎯 **Quick Deployment Summary**

### **Essential Changes Required:**
1. **Update IP Address**: Change `54.82.140.246` to your EC2 IP (2 files)
2. **Update SSH Key Path**: Change key path to your production key (1 file)
3. **Upload Scraper**: Copy `ultimate_scraper_v2.py` to EC2 home directory
4. **Setup EC2 Environment**: Create virtual env and install packages on EC2

### **Critical Files to Update:**
- `web_server.py` (lines 28, 30)
- `launch_scraper_interface.bat` (line 66)

### **Deployment Commands:**
```cmd
# 1. Update configuration files locally (EC2 IP and SSH key path)

# 2. Upload scraper to EC2
scp -i "C:\path\to\key.pem" ultimate_scraper_v2.py ec2-user@YOUR_EC2_IP:~/

# 3. Setup EC2 environment
ssh -i "C:\path\to\key.pem" ec2-user@YOUR_EC2_IP
python3 -m venv ~/ultimate_scraper_env
source ~/ultimate_scraper_env/bin/activate
pip install scrapy trafilatura beautifulsoup4 lxml newspaper3k Pillow aiohttp requests

# 4. Launch web interface locally
cd C:\path\to\final
launch_scraper_interface.bat
```

### **Testing Checklist:**
- [ ] SSH connection to EC2 works
- [ ] Scraper script exists on EC2: `~/ultimate_scraper_v2.py`
- [ ] Virtual environment works on EC2
- [ ] Web interface loads at `http://localhost:5000`
- [ ] "Test EC2 Connection" button shows success
- [ ] Test scrape with 2-3 articles completes successfully
- [ ] Files download to local output directory

**🚀 Your Ultimate Scraper V2 Web Interface is now ready for production use!**

---

## 📋 **File Structure After Deployment**

```
C:\path\to\final\
├── web_server.py              (Updated with your EC2 IP)
├── ultimate_scraper_v2.py     (Also copied to EC2)
├── index.html                 (Web interface - no changes needed)
├── requirements_web.txt       (Dependencies - no changes needed)
├── launch_scraper_interface.bat (Updated with your EC2 IP)
├── README.md                  (Documentation)
├── DEPLOYMENT_GUIDE.md        (This file)
└── web_venv\                  (Created by launcher script)
    ├── Scripts\
    └── Lib\

EC2 Instance (~/):
├── ultimate_scraper_v2.py     (Uploaded from local)
└── ultimate_scraper_env\      (Created during setup)
    ├── bin\
    └── lib\
```

The system is designed to be **simple and reliable** - update the configuration files, set up S3 access, upload one file to EC2, and launch!

## 6. Changing EC2 Instance or S3 Bucket

### 6.1 Changing EC2 Instance

If you need to switch to a different EC2 instance:

#### **Step 1: Update Configuration Files**
```bash
# 1. Update web_server.py (lines 30-32)
EC2_HOST = "NEW_EC2_IP_ADDRESS"
EC2_KEY_PATH = r"C:\path\to\new-key.pem"

# 2. Update launch_scraper_interface.bat (line 66)
echo Checking connection to NEW_EC2_IP_ADDRESS...
```

#### **Step 2: Setup New EC2 Instance**
```bash
# Connect to new EC2 instance
ssh -i "C:\path\to\new-key.pem" ec2-user@NEW_EC2_IP

# Install dependencies (follow Section 2.1.B)
sudo yum update -y
sudo yum install -y python3 python3-pip python3-devel gcc awscli
sudo yum install -y libjpeg-devel zlib-devel freetype-devel

# Upload scraper script
scp -i "C:\path\to\new-key.pem" ultimate_scraper_v2.py ec2-user@NEW_EC2_IP:~/

# Create virtual environment
python3 -m venv ~/ultimate_scraper_env
source ~/ultimate_scraper_env/bin/activate
pip install scrapy trafilatura beautifulsoup4 lxml newspaper3k Pillow aiohttp requests

# Configure AWS CLI (if using access keys)
aws configure
```

#### **Step 3: Test New EC2 Connection**
```bash
# Test from final folder
cd final
python web_server.py
# Click "Test EC2 Connection" in web interface
```

### 6.2 Changing S3 Bucket

If you need to switch to a different S3 bucket:

#### **Step 1: Create New S3 Bucket**
```bash
# Create new bucket
aws s3 mb s3://your-new-bucket-name --region us-east-1

# Enable versioning (optional)
aws s3api put-bucket-versioning \
  --bucket your-new-bucket-name \
  --versioning-configuration Status=Enabled
```

#### **Step 2: Update Configuration Files**
```bash
# 1. Update .env file
S3_BUCKET_NAME=your-new-bucket-name

# 2. Update web_server.py (line 37)
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME', 'your-new-bucket-name')
```

#### **Step 3: Update IAM Permissions**
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:PutObjectAcl",
                "s3:GetObject",
                "s3:ListBucket",
                "s3:DeleteObject"
            ],
            "Resource": [
                "arn:aws:s3:::your-new-bucket-name",
                "arn:aws:s3:::your-new-bucket-name/*"
            ]
        }
    ]
}
```

#### **Step 4: Test S3 Access**
```bash
# Test bucket access
aws s3 ls s3://your-new-bucket-name
aws s3 cp test-file.txt s3://your-new-bucket-name/test/

# Test via web interface
# Run a small scraping job and verify S3 upload works
```

### 6.3 Quick Configuration Summary

**For EC2 Change:**
1. Update `web_server.py` (2 lines)
2. Update `launch_scraper_interface.bat` (1 line)  
3. Setup new EC2 instance
4. Test connection

**For S3 Change:**
1. Create new S3 bucket
2. Update `.env` file (1 line)
3. Update `web_server.py` (1 line)
4. Update IAM permissions
5. Test S3 access

**Both are completely independent** - you can change EC2 without touching S3, or change S3 without touching EC2.
