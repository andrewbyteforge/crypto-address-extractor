@echo off
setlocal enabledelayedexpansion

:: Set window title
title Cryptocurrency Address Extractor

:: Get the directory where this batch file is located
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

echo ========================================
echo  Cryptocurrency Address Extractor
echo ========================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7 or higher from https://www.python.org/
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

:: Display Python version
echo Found Python installation:
python --version
echo.

:: Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo Virtual environment found.
    call venv\Scripts\activate.bat
) else (
    echo No virtual environment found. Creating one...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    call venv\Scripts\activate.bat
    
    :: Install requirements
    echo.
    echo Installing required packages...
    if exist "requirements.txt" (
        pip install -r requirements.txt
        if errorlevel 1 (
            echo ERROR: Failed to install requirements
            pause
            exit /b 1
        )
    ) else (
        echo WARNING: requirements.txt not found
        echo Installing basic requirements...
        pip install pandas openpyxl requests python-dotenv
    )
)

:: Check if main.py exists
if not exist "main.py" (
    echo ERROR: main.py not found in %SCRIPT_DIR%
    echo Please ensure all project files are in the correct location
    pause
    exit /b 1
)

:: Clear screen for clean start
cls
echo ========================================
echo  Cryptocurrency Address Extractor
echo ========================================
echo.
echo Starting application...
echo.

:: Run the main script
python main.py

:: Check if the script exited with an error
if errorlevel 1 (
    echo.
    echo Application exited with an error.
    pause
) else (
    echo.
    echo Application closed successfully.
    timeout /t 3 >nul
)

:: Deactivate virtual environment
deactivate

endlocal