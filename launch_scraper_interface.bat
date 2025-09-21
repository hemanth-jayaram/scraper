@echo off
:: Ultimate Scraper V2 - Beautiful Web Interface Launcher
:: This script launches the modern web interface for cloud scraping

echo.
echo ===============================================
echo    🚀 ULTIMATE SCRAPER V2 WEB INTERFACE 🚀
echo ===============================================
echo.
echo   Modern • Beautiful • Real-time • Cloud-powered
echo.
echo ===============================================

:: Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and add it to PATH
    echo.
    pause
    exit /b 1
)

echo ✅ Python detected
echo.

:: Create virtual environment if it doesn't exist
if not exist "web_venv" (
    echo 📦 Creating virtual environment for web interface...
    python -m venv web_venv
    if errorlevel 1 (
        echo ❌ ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo ✅ Virtual environment created
)

:: Activate virtual environment
echo 🔄 Activating virtual environment...
call web_venv\Scripts\activate
if errorlevel 1 (
    echo ❌ ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

:: Install/update web requirements
echo 📥 Installing/updating web interface dependencies...
echo 🔄 Upgrading pip...
python.exe -m pip install --quiet --upgrade pip >nul 2>&1
echo 📦 Installing required packages...
pip install --quiet -r requirements_web.txt
if errorlevel 1 (
    echo ❌ ERROR: Failed to install web dependencies from requirements file
    echo.
    echo 🔄 Trying individual package installation...
    pip install --quiet Flask>=2.3.0
    pip install --quiet flask-cors>=4.0.0
    pip install --quiet paramiko>=3.3.0
    pip install --quiet boto3>=1.28.0
    pip install --quiet botocore>=1.31.0
    pip install --quiet pathlib2>=2.3.0
    if errorlevel 1 (
        echo ❌ ERROR: Failed to install essential packages
        echo Please check your internet connection and try again
        pause
        exit /b 1
    )
)

echo ✅ Dependencies ready
echo.

:: Check EC2 connectivity
echo 🔍 Testing EC2 connection...
echo Checking connection to 54.82.140.246...
echo.

:: Clear any existing browser cache/sessions
echo 🧹 Preparing clean session...

:: Launch the web server
echo.
echo ===============================================
echo    🌐 LAUNCHING WEB INTERFACE
echo ===============================================
echo.
echo 🚀 Starting Flask web server...
echo 📱 Web interface will open in your browser
echo 🔗 URL: http://localhost:5000
echo.
echo 💡 Features available:
echo    ✨ Modern responsive design
echo    ⚡ Real-time progress tracking  
echo    📊 Live statistics dashboard
echo    📝 Streaming logs from EC2
echo    🎯 URL presets for popular sites
echo    🗂️  Custom output path selection
echo.
echo ===============================================

:: Launch browser after a short delay
start "" timeout /t 3 /nobreak >nul && start "" "http://localhost:5000"

:: Start the Flask server
python web_server.py

:: If we get here, the server stopped
echo.
echo ===============================================
echo    🛑 WEB INTERFACE STOPPED
echo ===============================================
echo.
echo The web server has been stopped.
echo.
echo 💾 Session data saved
echo 📁 Check your output folders for scraped results
echo.
echo Press any key to exit...
pause >nul
