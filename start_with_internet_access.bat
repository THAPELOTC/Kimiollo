@echo off
echo Starting Business Proposal Generator with Internet Access
echo =======================================================

REM Check if ngrok exists
if not exist "ngrok.exe" (
    echo Downloading ngrok...
    powershell -Command "Invoke-WebRequest -Uri 'https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip' -OutFile 'ngrok.zip'"
    powershell -Command "Expand-Archive ngrok.zip -DestinationPath ."
    del ngrok.zip
    echo ngrok downloaded successfully!
)

REM Start backend tunnel in background
echo Starting backend tunnel...
start /B ngrok http 5000 --log=stdout > backend_tunnel.log 2>&1

REM Wait a moment for ngrok to start
timeout /t 3 /nobreak > nul

REM Get the ngrok frontend URL (we'll start frontend tunnel after)
echo Starting frontend tunnel...
start /B ngrok http 3000 --log=stdout > frontend_tunnel.log 2>&1

REM Wait for tunnels to be established
timeout /t 5 /nobreak > nul

echo.
echo ============================================================
echo Your Business Proposal Generator is now accessible!
echo.
echo To get your public URLs:
echo 1. Check the ngrok web interface at http://localhost:4040
echo 2. Look for the "Forwarding" section to see your public URLs
echo 3. Share the HTTPS URL for port 3000 with your friends
echo.
echo The system will automatically update to work with the ngrok URLs.
echo ============================================================
echo.

REM Start the React app with the updated environment
set REACT_APP_API_URL=http://localhost:5000/api
start "React App" cmd /k "npm start"

echo React app is starting. Please check http://localhost:4040 for ngrok URLs.
pause


