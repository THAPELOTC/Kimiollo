@echo off
echo Getting your public URLs...
echo ==========================

echo.
echo Checking ngrok tunnels...
timeout /t 3 /nobreak > nul

powershell -Command "try { $response = Invoke-RestMethod -Uri 'http://localhost:4040/api/tunnels' -TimeoutSec 5; Write-Host 'Your public URLs:'; Write-Host '==============='; $response.tunnels | ForEach-Object { if($_.config.addr -eq 'localhost:3000') { Write-Host 'Frontend URL: ' $_.public_url -ForegroundColor Green; $frontend = $_.public_url } elseif($_.config.addr -eq 'localhost:5000') { Write-Host 'Backend URL: ' $_.public_url -ForegroundColor Blue; $backend = $_.public_url } }; Write-Host ''; Write-Host 'Share this URL with your friends: ' $frontend -ForegroundColor Yellow; Write-Host 'They can access your Business Proposal Generator from anywhere!' } catch { Write-Host 'ngrok is still starting up. Please wait a moment and run this script again.' }"

echo.
echo Alternative: Check the ngrok web interface at http://localhost:4040
echo.
pause
