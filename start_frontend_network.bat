@echo off
echo Starting React Frontend for Network Access
echo =========================================

REM Set environment variables for network access
set REACT_APP_API_URL=http://192.168.8.49:5000/api
set HOST=0.0.0.0

echo API URL: %REACT_APP_API_URL%
echo Host: %HOST%
echo.

echo Starting development server...
echo Frontend will be available at: http://192.168.8.49:3000
echo.

npm start
