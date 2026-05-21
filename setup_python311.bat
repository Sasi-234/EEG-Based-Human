@echo off
echo ========================================
echo EEG Emotion Recognition System Setup
echo Python 3.11 + TensorFlow Installation
echo ========================================
echo.

echo Step 1: Checking Python 3.11 installation...
py -3.11 --version
if %errorlevel% neq 0 (
    echo Python 3.11 not found. Installing...
    py install 3.11
    echo Waiting for installation to complete...
    timeout /t 10
)

echo.
echo Step 2: Creating virtual environment with Python 3.11...
py -3.11 -m venv venv311
if %errorlevel% neq 0 (
    echo ERROR: Failed to create virtual environment
    echo Please ensure Python 3.11 is fully installed
    pause
    exit /b 1
)

echo.
echo Step 3: Activating virtual environment...
call venv311\Scripts\activate.bat

echo.
echo Step 4: Upgrading pip...
python -m pip install --upgrade pip

echo.
echo Step 5: Installing all dependencies (this may take 5-10 minutes)...
pip install -r requirements.txt

echo.
echo Step 6: Navigating to backend directory...
cd backend

echo.
echo Step 7: Running database migrations...
python manage.py migrate

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo To start the server with TensorFlow support:
echo 1. Make sure virtual environment is activated: venv311\Scripts\activate
echo 2. Navigate to backend: cd backend
echo 3. Run server: python manage.py runserver
echo.
echo Your server will be available at: http://127.0.0.1:8000/
echo.
echo Now you can upload CSV files and get emotion predictions!
echo Processing time: 30-60 seconds per file
echo.
pause

@REM Made with Bob
