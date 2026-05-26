@echo off
echo ========================================
echo  EEG + Face Emotion Recognition System
echo  Server Startup Script
echo ========================================
echo.

REM Check if we're in the right directory
if not exist "backend\manage.py" (
    echo ERROR: Please run this script from the project root directory
    echo Current directory: %CD%
    echo Expected: c:\Users\SadineniSasi\OneDrive - IBM\Desktop\EEG Based Human
    pause
    exit /b 1
)

echo [1/4] Checking Python installation...
venv311\Scripts\python.exe --version
if errorlevel 1 (
    echo ERROR: Python not found in venv311
    pause
    exit /b 1
)
echo OK!
echo.

echo [2/4] Running migrations...
cd backend
..\venv311\Scripts\python.exe manage.py makemigrations face_emotion
..\venv311\Scripts\python.exe manage.py migrate
if errorlevel 1 (
    echo ERROR: Migrations failed
    pause
    exit /b 1
)
echo OK!
echo.

echo [3/4] Starting Django development server...
echo.
echo ========================================
echo  Server will start at:
echo  http://127.0.0.1:8000/
echo.
echo  Press CTRL+C to stop the server
echo ========================================
echo.

..\venv311\Scripts\python.exe manage.py runserver

pause

@REM Made with Bob
