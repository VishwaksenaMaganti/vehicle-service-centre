@echo off
title AutoCare Precision - Launching with Real-Time SQL Monitor
color 0B
cd /d "%~dp0"

echo ========================================================================
echo   AUTOCARE PRECISION - MULTI-BRAND VEHICLE SERVICE CENTRE
echo   Starting Web Application + Background Real-Time SQL Monitor Window
echo ========================================================================
echo.

:: 1. Launch the Live SQL Query Monitor in a separate popup Command Prompt window
echo [*] Spawning Live SQL Monitor in a separate popup window...
start "MySQL 8.0 Live Query Stream" cmd /k "color 0A && cd /d "%~dp0" && python sql_monitor.py"

:: 2. Wait 2 seconds for monitor to initialize
timeout /t 2 /nobreak >nul

:: 3. Open browser to application dashboard
echo [*] Opening Web Browser to http://127.0.0.1:5000...
start http://127.0.0.1:5000

:: 4. Start the Flask application in this window
echo [*] Starting Flask Web Server...
echo ========================================================================
echo   SERVER RUNNING AT: http://127.0.0.1:5000
echo   Watch queries execute in BOTH this window and the popup SQL window!
echo   Press CTRL + C to stop the server.
echo ========================================================================
python app.py

pause
