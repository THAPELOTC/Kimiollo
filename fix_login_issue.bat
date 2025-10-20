@echo off
echo Fixing Login Issue - Getting ngrok URLs
echo =======================================

echo.
echo Step 1: Getting your ngrok URLs...
timeout /t 3 /nobreak > nul

echo Checking ngrok tunnels at http://localhost:4040/api/tunnels

powershell -Command "try { Write-Host 'Getting ngrok tunnel information...'; $response = Invoke-RestMethod -Uri 'http://localhost:4040/api/tunnels' -TimeoutSec 10; $frontendUrl = ''; $backendUrl = ''; $response.tunnels | ForEach-Object { if($_.config.addr -eq 'localhost:3000') { $frontendUrl = $_.public_url; Write-Host 'Frontend URL:' $frontendUrl -ForegroundColor Green } elseif($_.config.addr -eq 'localhost:5000') { $backendUrl = $_.public_url; Write-Host 'Backend URL:' $backendUrl -ForegroundColor Blue } }; if($backendUrl) { $envUpdate = 'REACT_APP_API_URL=' + $backendUrl + '/api'; (Get-Content .env) -replace 'REACT_APP_API_URL=.*', $envUpdate | Set-Content .env; Write-Host 'Updated .env with backend ngrok URL' -ForegroundColor Yellow; Write-Host ''; Write-Host 'SOLUTION: Restart your React app to use the new backend URL'; Write-Host 'Or manually access your app using:' $frontendUrl -ForegroundColor Cyan } else { Write-Host 'Backend tunnel not found. Please check if ngrok is running for port 5000.' } } catch { Write-Host 'Could not connect to ngrok API. Please ensure:' -ForegroundColor Red; Write-Host '1. ngrok is running (check the ngrok windows)' -ForegroundColor Yellow; Write-Host '2. Visit http://localhost:4040 to see your URLs manually' -ForegroundColor Yellow }"

echo.
echo Step 2: If login still fails, try these solutions:
echo.
echo 1. Make sure you've registered an account first at the /register page
echo 2. Check that both Flask backend and React frontend are running
echo 3. Ensure ngrok tunnels are active for both ports 3000 and 5000
echo.
echo Alternative: Try accessing http://localhost:3000 directly if ngrok isn't working
echo.

pause
