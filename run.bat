@echo off
chcp 65001 >nul
title NYC Taxi Dashboard

echo ============================================
echo   NYC Taxi Trip Data Visualization Dashboard
echo ============================================
echo.

:: Set Python path - use Python 3.11 if available
set PYTHON_EXE=D:\python\python3.11.4\python.exe
if exist "%PYTHON_EXE%" (
    echo Using Python 3.11: %PYTHON_EXE%
) else (
    echo Python 3.11 not found at %PYTHON_EXE%
    echo Falling back to default Python...
    set PYTHON_EXE=python
)

echo.
echo [1/3] Checking data preparation...
if not exist "dashboard_data\chart_1_kpi.json" (
    echo   Data not yet prepared. Running data preparation...
    echo   This will take 5-10 minutes on first run...
    "%PYTHON_EXE%" data_prep.py
    if %errorlevel% neq 0 (
        echo   [ERROR] Data preparation failed!
        pause
        exit /b 1
    )
) else (
    echo   Data already prepared. Skipping data prep.
    echo   To re-run data prep, delete the dashboard_data folder.
)

echo.
echo [2/3] Starting web server...
echo [3/3] Opening browser...
start "" http://localhost:5000

echo.
echo ============================================
echo   Server running at: http://localhost:5000
echo   Press Ctrl+C to stop
echo ============================================
echo.

"%PYTHON_EXE%" server.py

pause
