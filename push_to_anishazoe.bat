@echo off
title Push Project to AnishaZoe/DBMS_PBL - AutoCare Precision
color 0B
cd /d "%~dp0"

echo =========================================================
echo    PUSH TO GITHUB REPOSITORY: AnishaZoe/DBMS_PBL
echo    Target: https://github.com/AnishaZoe/DBMS_PBL
echo =========================================================
echo.

set "GIT_EXE=git"

echo [1/3] Verifying Git status...
%GIT_EXE% status

echo.
echo [2/3] Configuring target remote for AnishaZoe...
%GIT_EXE% remote remove anisha >nul 2>&1
%GIT_EXE% remote add anisha https://AnishaZoe@github.com/AnishaZoe/DBMS_PBL.git
%GIT_EXE% remote set-url anisha https://AnishaZoe@github.com/AnishaZoe/DBMS_PBL.git

echo.
echo [3/3] Uploading all commits and files to GitHub (AnishaZoe/DBMS_PBL)...
echo If a browser window opens, please sign in with the AnishaZoe account
echo in Brave / default browser and click "Authorize GitCredentialManager".
echo.

%GIT_EXE% push -u anisha main

if %ERRORLEVEL% equ 0 (
    echo.
    echo =========================================================
    echo  [SUCCESS] All project files pushed to AnishaZoe/DBMS_PBL!
    echo  Repository: https://github.com/AnishaZoe/DBMS_PBL
    echo =========================================================
) else (
    echo.
    echo [NOTE] If authorization was not completed, please ensure you
    echo approved the sign-in prompt in your web browser.
)

echo.
pause
