@echo off
REM EEG Emotion Recognition System - Setup Script for Windows
REM This script sets up the project environment

echo ==========================================
echo EEG Emotion Recognition System Setup
echo ==========================================

REM Check Python version
echo Checking Python version...
python --version

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Create .env file from template
if not exist ".env" (
    echo Creating .env file...
    copy .env.example .env
    echo Please update .env file with your settings
)

REM Create necessary directories
echo Creating project directories...
mkdir backend\config 2>nul
mkdir backend\users 2>nul
mkdir backend\eeg_processing 2>nul
mkdir backend\ml_models 2>nul
mkdir backend\api 2>nul
mkdir backend\recommendations 2>nul
mkdir backend\media\eeg_uploads 2>nul
mkdir backend\media\reports 2>nul
mkdir backend\media\models 2>nul
mkdir backend\static\css 2>nul
mkdir backend\static\js 2>nul
mkdir backend\static\images 2>nul
mkdir backend\templates\users 2>nul
mkdir backend\templates\eeg 2>nul
mkdir backend\templates\admin 2>nul
mkdir dataset\DEAP\raw 2>nul
mkdir dataset\DEAP\processed 2>nul
mkdir notebooks 2>nul
mkdir tests 2>nul
mkdir docs 2>nul

REM Create .gitkeep files
type nul > backend\media\eeg_uploads\.gitkeep
type nul > backend\media\reports\.gitkeep
type nul > backend\media\models\.gitkeep
type nul > dataset\DEAP\raw\.gitkeep
type nul > dataset\DEAP\processed\.gitkeep

echo ==========================================
echo Setup complete!
echo ==========================================
echo.
echo Next steps:
echo 1. Update .env file with your settings
echo 2. Run: cd backend ^&^& python manage.py migrate
echo 3. Run: python manage.py createsuperuser
echo 4. Run: python manage.py runserver
echo.
pause

@REM Made with Bob
