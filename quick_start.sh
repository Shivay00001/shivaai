@echo off
REM ShivAI Quick Start Script for Windows
REM This script sets up ShivAI on a fresh Windows system

echo.
echo ================================================================
echo          ShivAI - Quick Start Installation
echo          India's First Offline AGI Assistant
echo ================================================================
echo.

REM Check Python installation
echo [1/7] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found!
    echo Please install Python 3.10 or higher from python.org
    pause
    exit /b 1
)
echo [OK] Python found

REM Check pip
echo.
echo [2/7] Checking pip...
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] pip not found!
    echo Installing pip...
    python -m ensurepip
)
echo [OK] pip ready

REM Create virtual environment
echo.
echo [3/7] Creating virtual environment...
if exist venv (
    echo [SKIP] Virtual environment already exists
) else (
    python -m venv venv
    echo [OK] Virtual environment created
)

REM Activate virtual environment
echo.
echo [4/7] Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)
echo [OK] Virtual environment activated

REM Install dependencies
echo.
echo [5/7] Installing ShivAI dependencies...
echo This may take a few minutes...
python -m pip install --upgrade pip
pip install -e .
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)
echo [OK] Dependencies installed

REM Create config file
echo.
echo [6/7] Setting up configuration...
if exist config.yaml (
    echo [SKIP] config.yaml already exists
) else (
    copy config.example.yaml config.yaml
    echo [OK] config.yaml created
)

REM Create data directories
echo.
echo [7/7] Creating data directories...
if not exist data mkdir data
if not exist data\db mkdir data\db
if not exist data\logs mkdir data\logs
if not exist models mkdir models
echo [OK] Directories created

REM Success message
echo.
echo ================================================================
echo              Installation Complete!
echo ================================================================
echo.
echo Next steps:
echo.
echo 1. Download speech models (optional, for offline voice):
echo    scripts\setup-vosk-models.bat
echo.
echo 2. Run ShivAI in text mode (no voice needed):
echo    python -m shivai --text
echo.
echo 3. Run ShivAI with voice (requires microphone):
echo    python -m shivai
echo.
echo 4. Run tests:
echo    pytest
echo.
echo 5. View help:
echo    python -m shivai --help
echo.
echo ================================================================
echo.

REM Keep window open
echo Press any key to start ShivAI in text mode...
pause >nul

REM Run ShivAI
python -m shivai --text
