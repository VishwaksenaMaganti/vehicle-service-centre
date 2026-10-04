@echo off
setlocal
title Push Project to GitHub
color 0B

echo =========================================================
echo    AUTOCARE PRECISION - PUSH TO GITHUB REPOSITORY
echo =========================================================
echo.

set "GIT_EXE=C:\Users\vishw\AppData\Local\Programs\Git\cmd\git.exe"

if not exist "%GIT_EXE%" (
    set "GIT_EXE=git"
)

echo Checking Git status...
"%GIT_EXE%" status >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Git repository not detected or Git is not found.
    pause
    exit /b 1
)

echo.
echo Please enter your GitHub Repository URL.
echo Example: https://github.com/your-username/vehicle-service-centre.git
echo.
set /p REPO_URL="Enter GitHub Repository URL: "

if "%REPO_URL%"=="" (
    echo [ERROR] No URL provided. Aborting.
    pause
    exit /b 1
)

echo.
echo Setting remote origin to: %REPO_URL%
"%GIT_EXE%" remote remove origin >nul 2>&1
"%GIT_EXE%" remote add origin %REPO_URL%

echo.
echo Renaming current branch to main...
"%GIT_EXE%" branch -M main

echo.
echo Pushing project to GitHub...
"%GIT_EXE%" push -u origin main

if %ERRORLEVEL% equ 0 (
    echo.
    echo =========================================================
    echo [SUCCESS] Entire project pushed to GitHub successfully!
    echo =========================================================
) else (
    echo.
    echo [NOTE] If GitHub asked you to sign in, please complete
    echo authentication in the browser window or Git Credential Manager prompt.
)

echo.
pause
