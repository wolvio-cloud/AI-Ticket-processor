@echo off
REM ============================================================================
REM Dashboard Quick Start Script - Windows
REM ============================================================================
REM
REM This script helps you test the dashboard integration quickly.
REM It will start the API server in one window and provide instructions
REM for starting the dashboard in another.
REM
REM Usage: Double-click this file or run: start_dashboard_test.bat
REM ============================================================================

echo.
echo ================================================================================
echo   AI TICKET PROCESSOR - DASHBOARD TESTING
echo ================================================================================
echo.
echo This script will help you test the dashboard integration.
echo.
echo STEP 1: Starting API Server...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

echo Python found:
python --version
echo.

REM Check if required packages are installed
echo Checking dependencies...
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo.
    echo WARNING: FastAPI not found. Installing dependencies...
    echo.
    pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

echo.
echo Dependencies OK
echo.
echo ================================================================================
echo   STARTING API SERVER
echo ================================================================================
echo.
echo API Server will start on: http://localhost:8000
echo API Documentation: http://localhost:8000/api/docs
echo.
echo Leave this window open. The API server must keep running.
echo.
echo To test the dashboard:
echo   1. Open a NEW command prompt
echo   2. cd ai-ticket-dashboard
echo   3. npm install (first time only)
echo   4. npm run dev
echo   5. Open browser: http://localhost:3000
echo.
echo ================================================================================
echo.

REM Start API server
python api_server.py

REM If the server exits
echo.
echo API Server stopped.
pause
