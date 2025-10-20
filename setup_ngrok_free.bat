@echo off
echo Setting Up ngrok for Free Remote Access
echo =======================================

echo.
echo Since localtunnel is having issues, let's set up ngrok properly.
echo.
echo This is a 2-minute process:
echo.
echo STEP 1: Get Free ngrok Account
echo -----------------------------
echo 1. Open your browser
echo 2. Go to: https://dashboard.ngrok.com/signup
echo 3. Sign up for FREE (no credit card required)
echo 4. Verify your email
echo.
echo STEP 2: Get Your Auth Token
echo ---------------------------
echo 1. After signing up, go to: https://dashboard.ngrok.com/get-started/your-authtoken
echo 2. Copy your authtoken (it looks like: 2abc123def456_...)
echo.
echo STEP 3: Configure ngrok
echo ----------------------
echo 1. Press any key below when you have your authtoken
echo 2. I'll configure ngrok automatically
echo.
pause

echo.
echo Please paste your ngrok authtoken here:
set /p authtoken="Enter authtoken: "

echo.
echo Configuring ngrok with your token...
.\ngrok.exe config add-authtoken %authtoken%

echo.
echo Starting ngrok tunnels...
start "Frontend Tunnel" cmd /k "ngrok http 3000"
timeout /t 3 /nobreak > nul
start "Backend Tunnel" cmd /k "ngrok http 5000"

echo.
echo ==========================================
echo ngrok is now configured and starting!
echo.
echo In 30 seconds, check:
echo 1. The ngrok terminal windows for URLs
echo 2. OR go to: http://localhost:4040
echo.
echo Your system will be accessible worldwide!
echo ==========================================
pause
