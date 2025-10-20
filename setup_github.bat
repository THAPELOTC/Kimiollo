@echo off
echo Setting up GitHub deployment for Business Proposal Generator
echo ===========================================================

echo.
echo STEP 1: Configure Git (if needed)
echo Your current git config:
git config --list | findstr user

echo.
echo If no username/email shown above, run this first:
echo git config --global user.name "Your Name"
echo git config --global user.email "your.email@example.com"
echo.

echo STEP 2: Setting up GitHub repository
echo ====================================
echo 1. Go to https://github.com and sign in
echo 2. Click the "+" icon in top right corner
echo 3. Select "New repository"
echo 4. Repository name: kimiollo (or your preferred name)
echo 5. Description: "AI-Powered Business Proposal Generator & Funding Finder"
echo 6. Make it PUBLIC (so others can access it)
echo 7. DO NOT initialize with README (we already have files)
echo 8. Click "Create repository"

echo.
echo STEP 3: Connect your local repository to GitHub
echo ==============================================
echo After creating the repository, GitHub will show you commands like:
echo git remote add origin https://github.com/YOUR_USERNAME/kimiollo.git
echo git branch -M main
echo git push -u origin main

echo.
echo STEP 4: Enable GitHub Pages
echo ===========================
echo 1. Go to your repository on GitHub
echo 2. Click Settings tab
echo 3. Scroll to "Pages" in left sidebar
echo 4. Source: "GitHub Actions"
echo 5. Your site will be available at: https://YOUR_USERNAME.github.io/kimiollo

echo.
echo STEP 5: Set up backend API (Important!)
echo ======================================
echo For the deployed frontend to work, you need:
echo 1. A backend API hosted somewhere (Heroku, Railway, etc.)
echo 2. Set the API URL in GitHub repository secrets:
echo    - Go to repository Settings ^> Secrets ^> Actions
echo    - Add secret named "API_URL"
echo    - Value: Your backend API URL (e.g., https://your-backend.herokuapp.com/api)

echo.
echo Ready to proceed? Press any key when you've created the GitHub repository...
pause

echo.
echo Enter your GitHub username (without @):
set /p USERNAME=

echo Adding remote origin...
git remote add origin https://github.com/%USERNAME%/kimiollo.git

echo Switching to main branch...
git branch -M main

echo Pushing to GitHub...
git push -u origin main

echo.
echo ====================================
echo DEPLOYMENT COMPLETE!
echo ====================================
echo Your frontend will be available at:
echo https://%USERNAME%.github.io/kimiollo
echo.
echo NOTE: Backend still needs to be deployed separately!
echo See README.md for backend deployment options.

pause
