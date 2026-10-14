@echo off
title AutoCare Precision - Vehicle Service Centre Management System
color 0A
cd /d "%~dp0"

echo ========================================================================
echo   AUTOCARE PRECISION - MULTI-BRAND VEHICLE SERVICE CENTRE
echo   College DBMS Project (MySQL 8.0 + Python Flask)
echo ========================================================================
echo.

:: 1. Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    goto :TRY_PY_LAUNCHER
)
set PYTHON_CMD=python
goto :PYTHON_OK

:TRY_PY_LAUNCHER
py --version >nul 2>&1
if errorlevel 1 (
    color 0C
    echo [ERROR] Python was not found in your system PATH!
    echo Please install Python 3.10 or newer from python.org and check
    echo the box to Add Python to PATH during installation.
    echo.
    pause
    exit /b 1
)
set PYTHON_CMD=py

:PYTHON_OK
echo [OK] Python found:
%PYTHON_CMD% --version

:: 2. Check and install Python dependencies if missing
echo [*] Checking Python dependencies...
%PYTHON_CMD% -c "import flask, mysql.connector, dotenv" >nul 2>&1
if errorlevel 1 (
    echo [*] Installing required Python libraries from requirements.txt...
    %PYTHON_CMD% -m pip install -r requirements.txt
    if errorlevel 1 (
        color 0C
        echo [ERROR] Failed to install dependencies via pip.
        pause
        exit /b 1
    )
)
echo [OK] Python dependencies verified.

:: 3. Test MySQL database connectivity
echo [*] Testing MySQL database connection...
%PYTHON_CMD% -c "from database import get_db_connection; conn=get_db_connection(); conn.close()" >nul 2>&1
if errorlevel 1 (
    color 0E
    echo [!] Database connection failed or database vehicle_service_centre not ready.
    echo [*] Running database setup script setup_db.py...
    %PYTHON_CMD% setup_db.py
    if errorlevel 1 (
        color 0C
        echo.
        echo [ERROR] Could not connect to MySQL Server.
        echo Please ensure MySQL Server 8.0 is running on port 3306 with password 1234.
        echo.
        pause
        exit /b 1
    )
)
echo [OK] MySQL Database connected successfully.

:: 4. Pop up the Live SQL Query Monitor in a separate background window
echo [*] Launching real-time SQL Query Monitor window...
start "MySQL 8.0 Live Query Stream" cmd /k "color 0A && cd /d ""%~dp0"" && %PYTHON_CMD% sql_monitor.py"

:: 5. Open default web browser to the dashboard
echo [*] Opening web browser at http://127.0.0.1:5000...
start http://127.0.0.1:5000

:: 6. Start the Flask server
echo.
echo ========================================================================
echo   SERVER RUNNING AT: http://127.0.0.1:5000
echo   SQL queries will stream in REAL TIME in the popup shell window!
echo   To stop the server at any time, press CTRL + C in this window.
echo ========================================================================
echo.

%PYTHON_CMD% app.py

if errorlevel 1 (
    echo.
    echo [!] Application exited with code %errorlevel%.
    pause
)
