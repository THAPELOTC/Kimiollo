@echo off
echo Setting up Internet Access for Business Proposal Generator
echo ========================================================

echo.
echo Step 1: Downloading ngrok...
powershell -Command "if (!(Test-Path 'ngrok.exe')) { Invoke-WebRequest -Uri 'https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip' -OutFile 'ngrok.zip'; Expand-Archive ngrok.zip -DestinationPath .; Remove-Item ngrok.zip }"

echo.
echo Step 2: Starting ngrok tunnel for frontend (port 3000)...
start "Frontend Tunnel" ngrok http 3000

echo.
echo Step 3: Starting ngrok tunnel for backend (port 5000)...  
start "Backend Tunnel" ngrok http 5000

echo.
echo ============================================================
echo Your system is now accessible from the internet!
echo.
echo Please check the ngrok windows that opened to get your public URLs.
echo Frontend URL will be displayed in the "Frontend Tunnel" window
echo Backend URL will be displayed in the "Backend Tunnel" window
echo.
echo Share the Frontend URL with your friends to access your system.
echo ============================================================
echo.
pause
