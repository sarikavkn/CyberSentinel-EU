@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title CyberSentinel EU v1.5.2

echo ============================================================
echo   CyberSentinel EU v1.5.2 - Python 3.12 Windows Launcher
echo ============================================================
echo.

echo [1/6] Looking specifically for Python 3.12...
py -3.12 --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python 3.12 was not found by the Windows Python Launcher.
    echo.
    echo Please verify it with:
    echo   py -3.12 --version
    echo.
    pause
    exit /b 1
)

for /f "delims=" %%V in ('py -3.12 --version 2^>^&1') do set "PYVER=%%V"
echo Found: %PYVER%

if exist ".venv\Scripts\python.exe" (
    echo.
    echo [2/6] Removing the old virtual environment so it cannot keep Python 3.14...
    rmdir /s /q ".venv"
)

echo.
echo [2/6] Creating a fresh virtual environment with Python 3.12...
py -3.12 -m venv .venv
if errorlevel 1 goto :fail

set "VENV_PY=.venv\Scripts\python.exe"

echo.
echo [3/6] Confirming virtual environment Python...
"%VENV_PY%" --version
if errorlevel 1 goto :fail

echo.
echo [4/6] Updating pip and installing dependencies...
"%VENV_PY%" -m pip install --upgrade pip
if errorlevel 1 goto :fail
"%VENV_PY%" -m pip install -r requirements.txt
if errorlevel 1 goto :fail

echo.
echo [5/6] Verifying application dependencies...
"%VENV_PY%" -c "import fastapi, uvicorn, sqlalchemy, jinja2, psycopg; print('Dependency verification: OK')"
if errorlevel 1 goto :fail

if "%CYBERSENTINEL_SESSION_SECRET%"=="" (
    set "CYBERSENTINEL_SESSION_SECRET=local-development-only-change-this-before-production"
)

echo.
echo [6/6] Starting CyberSentinel EU...
echo.
echo ------------------------------------------------------------
echo Open your browser at:
echo   http://127.0.0.1:8000
echo.
echo Development login:
echo   Username: admin
echo   Password: ChangeMe!2026
echo.
echo Keep this window open while CyberSentinel is running.
echo Press CTRL+C to stop the server.
echo ------------------------------------------------------------
echo.

"%VENV_PY%" -m uvicorn app.main:app --host 127.0.0.1 --port 8000

if errorlevel 1 (
    echo.
    echo [ERROR] CyberSentinel stopped unexpectedly.
    echo Screenshot the error above and send it to ChatGPT.
    echo.
    pause
)
exit /b 0

:fail
echo.
echo ============================================================
echo [ERROR] Setup could not be completed.
echo ============================================================
echo The terminal will stay open so you can screenshot the error.
echo.
pause
exit /b 1
