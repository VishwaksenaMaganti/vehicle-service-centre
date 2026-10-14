@echo off
title MySQL 8.0 Real-Time SQL Query Stream - AutoCare Precision
color 0A
cd /d "%~dp0"

echo ========================================================================
echo   AUTOCARE PRECISION - LIVE SQL MONITOR WINDOW
echo ========================================================================
echo Starting Real-Time SQL Query Stream...
echo.

python sql_monitor.py

if errorlevel 1 (
    echo.
    echo [NOTE] Python exited. Press any key to close this monitor window.
    pause >nul
)
