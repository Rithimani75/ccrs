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

:: 4. Database Setup (Optional/Auto if MySQL is in PATH)
mysql -V >nul 2>&1
IF %ERRORLEVEL% EQU 0 (
    echo [INFO] MySQL detected. Ensuring database and tables exist...
    mysql -u root -e "CREATE DATABASE IF NOT EXISTS ccrs;" >nul 2>&1
    mysql -u root ccrs < database.sql >nul 2>&1
    echo [OK] Database verified.
) ELSE (
    echo.
    echo [WARNING] MySQL command not found in PATH.
    echo If you use XAMPP or WAMP, please ensure MySQL is running on port 3306.
    echo Note: You must manually import 'database.sql' into your 'ccrs' database via phpMyAdmin.
    echo.
)

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
