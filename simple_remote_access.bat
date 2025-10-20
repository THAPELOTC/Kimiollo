@echo off
echo Multiple Remote Access Options
echo ==============================

echo.
echo Here are alternative ways to give remote access:
echo.

echo OPTION 1: Use Python's HTTP Server (Simplest)
echo =============================================
echo This will make your system accessible on your network:
echo.
echo 1. Make sure your React app is running on port 3000
echo 2. Share your local IP address: 
for /f "tokens=2 delims=:" %%i in ('ipconfig ^| findstr "IPv4"') do (
    set local_ip=%%i
    echo    http://!local_ip!:3000
)
echo.

echo OPTION 2: Deploy to Free Cloud Services
echo =======================================
echo.
echo A) Netlify (Free, 5 minutes):
echo    1. Build: npm run build
echo    2. Go to netlify.com
echo    3. Drag 'build' folder → Get instant URL
echo.
echo B) Vercel (Free, 2 minutes):
echo    1. Install: npm i -g vercel
echo    2. Run: vercel
echo    3. Get public URL
echo.
echo C) Railway.app (Free):
echo    1. Connect GitHub repo
echo    2. Deploy with one click
echo.

echo OPTION 3: Quick Tunnel with PowerShell
echo ======================================
echo I'll start a simple tunnel for you...

powershell -Command "try { $listener = New-Object System.Net.HttpListener; $listener.Prefixes.Add('http://+:8080/'); $listener.Start(); Write-Host 'Tunnel started on port 8080' -ForegroundColor Green; Write-Host 'Access via: http://YOUR_IP:8080' } catch { Write-Host 'Tunnel method not available' }"

echo.
echo OPTION 4: Using GitHub Codespaces (If available)
echo ===============================================
echo.
echo 1. Push code to GitHub
echo 2. Open in Codespaces
echo 3. Ports automatically exposed publicly
echo.

echo ==========================================
echo Which option would you like to try?
echo.
echo For immediate access, I recommend OPTION 2A (Netlify)
echo It's free and takes just 5 minutes!
echo ==========================================
pause
