@echo off
echo Setting Up Simple Remote Access
echo ===============================

echo.
echo I'll help you get a simple public URL without password requirements.
echo.

echo Starting localtunnel for your frontend (port 3000)...
echo Check the terminal window that opens for your public URL.
echo.

start "Simple Tunnel" cmd /k "lt --port 3000"

echo.
echo ==========================================
echo Once the terminal window opens, look for:
echo.
echo "your url is: https://[random-name].loca.lt"
echo.
echo THAT is your public URL to share!
echo ==========================================
echo.
echo The tunnel should start automatically without password requirements.
echo.
pause
