@echo off
setlocal
title Push Project to GitHub - AutoCare Precision
color 0B

echo =========================================================
echo    AUTOCARE PRECISION - PUSH TO GITHUB REPOSITORY
echo    Target: https://github.com/VishwaksenaMaganti/vehicle-service-centre
echo =========================================================
echo.

set "GIT_EXE=C:\Users\vishw\AppData\Local\Programs\Git\cmd\git.exe"

if not exist "%GIT_EXE%" (
    set "GIT_EXE=git"
)

echo [1/3] Verifying Git status...
"%GIT_EXE%" status >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Git repository not detected or Git is not found.
    pause
    exit /b 1
)

set "REPO_URL=https://github.com/VishwaksenaMaganti/vehicle-service-centre.git"

echo [2/3] Configuring remote origin...
"%GIT_EXE%" remote remove origin >nul 2>&1
"%GIT_EXE%" remote add origin %REPO_URL%
"%GIT_EXE%" branch -M main

echo [3/3] Uploading all commits and files to GitHub...
echo (If a browser window opens, please sign in to GitHub and click "Authorize")
echo.

"%GIT_EXE%" push -u origin main

if %ERRORLEVEL% equ 0 (
    echo.
    echo =========================================================
    echo  [SUCCESS] All project files pushed to GitHub successfully!
    echo  Repository: https://github.com/VishwaksenaMaganti/vehicle-service-centre
    echo =========================================================
) else (
    echo.
    echo [NOTE] If authentication was required, please ensure you
    echo approved the sign-in prompt in your web browser.
)

echo.
pause
