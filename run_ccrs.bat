@echo off
color 0B
echo ========================================================
echo        Campus Complaint Registry System (CCRS)
echo            Setup and Startup Script
echo ========================================================
echo.

:: 1. Check Python installation
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not added to PATH.
    echo Please install Python 3 from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b
)
echo [OK] Python is installed.

:: 2. Create and Activate Virtual Environment
IF NOT EXIST "venv\Scripts\activate" (
    echo [INFO] Creating Python virtual environment...
    python -m venv venv
)
echo [INFO] Activating virtual environment...
call venv\Scripts\activate

:: 3. Install requirements
echo [INFO] Installing required dependencies...
pip install -r requirements.txt --quiet
echo [OK] Dependencies installed successfully.

:: 4. Database Setup
echo [INFO] Setting up database...
python init_db.py

echo.
echo ========================================================
echo Starting the Flask Application...
echo Access the site at: http://127.0.0.1:5000/
echo Press Ctrl+C in this window to stop the server.
echo ========================================================
echo.

:: 5. Run the app
python app.py

pause
