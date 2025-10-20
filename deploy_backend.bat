@echo off
echo ========================================
echo FLASK BACKEND DEPLOYMENT OPTIONS
echo ========================================
echo.
echo Choose your deployment platform:
echo.
echo 1. Railway (Recommended - Free, Easy)
echo 2. Heroku (Classic platform)
echo 3. Render (Good alternative)
echo 4. Manual setup instructions
echo.

set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" goto railway
if "%choice%"=="2" goto heroku
if "%choice%"=="3" goto render
if "%choice%"=="4" goto manual
goto invalid

:railway
echo.
echo ========================================
echo DEPLOYING TO RAILWAY
echo ========================================
echo.
echo 1. Go to https://railway.app
echo 2. Sign up with GitHub
echo 3. Click "New Project"
echo 4. Select "Deploy from GitHub repo"
echo 5. Choose your kimiollo repository
echo 6. Railway will auto-detect it's a Python app
echo 7. Set these environment variables in Railway:
echo    - FLASK_ENV=production
echo    - SECRET_KEY=your-secret-key-here
echo    - JWT_SECRET_KEY=your-jwt-secret-key
echo    - OPENAI_API_KEY=your-openai-key (if you have one)
echo 8. Your backend will be automatically deployed!
echo.
echo Your Railway URL will be something like:
echo https://your-app-name.up.railway.app
echo.
goto end

:heroku
echo.
echo ========================================
echo DEPLOYING TO HEROKU
echo ========================================
echo.
echo 1. Install Heroku CLI from https://devcenter.heroku.com/articles/heroku-cli
echo 2. Run these commands:
echo    heroku login
echo    heroku create your-app-name
echo    heroku config:set FLASK_ENV=production
echo    heroku config:set SECRET_KEY=your-secret-key
echo    heroku config:set JWT_SECRET_KEY=your-jwt-secret-key
echo    git subtree push --prefix=. heroku main
echo.
echo Your Heroku URL will be: https://your-app-name.herokuapp.com
echo.
goto end

:render
echo.
echo ========================================
echo DEPLOYING TO RENDER
echo ========================================
echo.
echo 1. Go to https://render.com
echo 2. Sign up with GitHub
echo 3. Click "New" -> "Web Service"
echo 4. Connect your GitHub repository
echo 5. Configure:
echo    - Build Command: pip install -r requirements.txt
echo    - Start Command: gunicorn app:app
echo    - Environment: Python 3
echo 6. Add environment variables in Render dashboard
echo.
goto end

:manual
echo.
echo ========================================
echo MANUAL DEPLOYMENT CHECKLIST
echo ========================================
echo.
echo Files created for deployment:
echo - Procfile (for Heroku/Railway)
echo - runtime.txt (Python version)
echo - railway.json (Railway config)
echo - Updated app.py (production ready)
echo.
echo Environment variables needed:
echo - FLASK_ENV=production
echo - SECRET_KEY=your-secret-key
echo - JWT_SECRET_KEY=your-jwt-secret-key
echo - DATABASE_URL (auto-provided by most platforms)
echo - PORT (auto-provided by platform)
echo.
goto end

:invalid
echo Invalid choice. Please run the script again.
goto end

:end
echo.
echo After deployment, update your frontend:
echo Go to GitHub repository Settings -> Secrets -> Actions
echo Update API_URL secret with your backend URL
echo.
pause
