@echo off
echo Alternative Remote Access Methods
echo =================================

echo.
echo Here are several ways to give remote access to your system:
echo.

echo METHOD 1: Serveo (Free SSH Tunnel)
echo ==================================
echo Starting Serveo tunnel...
echo This creates a public URL automatically.
start "Serveo Tunnel" cmd /k "ssh -R 80:localhost:3000 serveo.net"

echo.
echo METHOD 2: Cloudflare Tunnel (Free)
echo ==================================
echo Install cloudflared for free tunneling:
echo 1. Go to: https://github.com/cloudflare/cloudflared/releases
echo 2. Download cloudflared-windows-amd64.exe
echo 3. Run: cloudflared tunnel --url http://localhost:3000

echo.
echo METHOD 3: Railway (Free Deployment)
echo ===================================
echo Deploy directly to cloud:
echo 1. Go to: https://railway.app
echo 2. Connect your GitHub repository
echo 3. Deploy for free with custom domain

echo.
echo METHOD 4: Netlify (Free Static Hosting)
echo ======================================
echo For frontend only:
echo 1. Build your React app: npm run build
echo 2. Go to: https://netlify.com
echo 3. Drag and drop your 'build' folder
echo 4. Get instant public URL

echo.
echo METHOD 5: Vercel (Free)
echo =====================
echo Deploy with one command:
echo 1. Install: npm i -g vercel
echo 2. Run: vercel
echo 3. Get public URL instantly

echo.
echo ==========================================
echo Serveo tunnel is starting above...
echo Look for a URL like: https://abc123.serveo.net
echo ==========================================
echo.
pause
