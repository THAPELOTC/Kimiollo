@echo off
echo Starting ngrok for Remote Access
echo ===============================

echo.
echo Make sure your servers are running first:
echo - Flask backend on port 5000
echo - React frontend on port 3000
echo.
pause

echo Starting ngrok tunnel for Frontend (port 3000)...
start "Frontend ngrok" cmd /k "ngrok http 3000"

echo Waiting 3 seconds...
timeout /t 3 /nobreak > nul

echo Starting ngrok tunnel for Backend (port 5000)...
start "Backend ngrok" cmd /k "ngrok http 5000"

echo.
echo ==========================================
echo ngrok tunnels are starting up!
echo.
echo To get your public URLs:
echo 1. Wait 10-15 seconds for ngrok to start
echo 2. Check the ngrok windows that opened
echo 3. Look for URLs like: https://abc123.ngrok-free.app
echo 4. OR go to: http://localhost:4040 in your browser
echo.
echo Share the HTTPS URL with anyone for remote access!
echo ==========================================
echo.
pause
