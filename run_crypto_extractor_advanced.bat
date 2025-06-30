@echo off
setlocal enabledelayedexpansion

:: Set window title and colors
title Cryptocurrency Address Extractor
color 0A

:: Get the directory where this batch file is located
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

:MENU
cls
echo ==========================================
echo   Cryptocurrency Address Extractor
echo ==========================================
echo.
echo   1. Run GUI Application
echo   2. Run Command Line (with file)
echo   3. Update Dependencies
echo   4. Create Desktop Shortcut
echo   5. View Logs
echo   6. Exit
echo.
set /p choice="Select an option (1-6): "

if "%choice%"=="1" goto RUN_GUI
if "%choice%"=="2" goto RUN_CLI
if "%choice%"=="3" goto UPDATE_DEPS
if "%choice%"=="4" goto CREATE_SHORTCUT
if "%choice%"=="5" goto VIEW_LOGS
if "%choice%"=="6" goto EXIT

echo Invalid choice. Please try again.
pause
goto MENU

:RUN_GUI
cls
echo Starting GUI application...
call :CHECK_PYTHON
if errorlevel 1 goto END
call :ACTIVATE_VENV
if errorlevel 1 goto END
python main.py
if errorlevel 1 (
    echo.
    echo Application exited with an error.
    pause
)
goto END

:RUN_CLI
cls
echo Command Line Mode
echo.
set /p input_file="Enter CSV/Excel file path (or drag and drop file here): "
:: Remove quotes if present
set input_file=%input_file:"=%

if not exist "%input_file%" (
    echo ERROR: File not found
    pause
    goto MENU
)

call :CHECK_PYTHON
if errorlevel 1 goto END
call :ACTIVATE_VENV
if errorlevel 1 goto END

echo.
echo Processing file...
python main.py -i "%input_file%"
echo.
pause
goto END

:UPDATE_DEPS
cls
echo Updating dependencies...
call :CHECK_PYTHON
if errorlevel 1 goto END
call :ACTIVATE_VENV
if errorlevel 1 goto END

echo.
echo Upgrading pip...
python -m pip install --upgrade pip

echo.
echo Updating requirements...
if exist "requirements.txt" (
    pip install --upgrade -r requirements.txt
) else (
    echo ERROR: requirements.txt not found
)
echo.
echo Update complete!
pause
goto MENU

:CREATE_SHORTCUT
cls
echo Creating desktop shortcut...

:: Create VBS script to create shortcut
set "VBS_FILE=%TEMP%\CreateShortcut.vbs"
(
echo Set oWS = WScript.CreateObject("WScript.Shell"^)
echo sLinkFile = oWS.SpecialFolders("Desktop"^) ^& "\Crypto Address Extractor.lnk"
echo Set oLink = oWS.CreateShortcut(sLinkFile^)
echo oLink.TargetPath = "%SCRIPT_DIR%run_crypto_extractor.bat"
echo oLink.WorkingDirectory = "%SCRIPT_DIR%"
echo oLink.IconLocation = "%SystemRoot%\System32\SHELL32.dll,13"
echo oLink.Description = "Cryptocurrency Address Extractor"
echo oLink.Save
) > "%VBS_FILE%"

cscript //nologo "%VBS_FILE%"
del "%VBS_FILE%"

echo Desktop shortcut created successfully!
pause
goto MENU

:VIEW_LOGS
cls
echo Opening logs directory...
if exist "logs" (
    start "" "logs"
) else (
    echo No logs directory found.
    pause
)
goto MENU

:CHECK_PYTHON
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
exit /b 0

:ACTIVATE_VENV
:: Check and activate virtual environment
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    call venv\Scripts\activate.bat
    
    :: Install requirements
    echo Installing required packages...
    if exist "requirements.txt" (
        pip install -r requirements.txt
    ) else (
        echo WARNING: requirements.txt not found
        pip install pandas openpyxl requests python-dotenv reportlab python-docx
    )
)
exit /b 0

:EXIT
exit

:END
deactivate
endlocal