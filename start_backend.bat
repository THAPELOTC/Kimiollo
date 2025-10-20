@echo off
echo Starting Python Backend for Business Proposal Generator
echo =====================================================

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://python.org/
    pause
    exit /b 1
)

echo Installing Python dependencies...
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo WARNING: Some dependencies might have failed to install
    echo Continuing anyway...
)

echo.
echo Starting Flask server...
echo Backend will be available at: http://localhost:5000
echo API Health Check: http://localhost:5000/api/health
echo.
echo Press Ctrl+C to stop the server
echo.

python app.py

pause
