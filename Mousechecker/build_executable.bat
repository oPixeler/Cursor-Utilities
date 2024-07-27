@echo off

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in the system PATH.
    echo Please install Python and add it to your system PATH.
    pause
    exit /b 1
)

:: Change to the directory of the script
cd /d "%~dp0"

:: Run PyInstaller to create the executable
python -m PyInstaller --onefile --windowed mouse_checker.py

:: Check if PyInstaller ran successfully
if %errorlevel% neq 0 (
    echo.
    echo PyInstaller encountered an error.
    pause
) else (
    echo.
    echo Executable created successfully in the dist folder.
    pause
)