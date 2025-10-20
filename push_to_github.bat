@echo off
echo ========================================
echo PUSHING CODE TO GITHUB - STEP 2
echo ========================================

echo.
echo First, make sure you've created your GitHub repository:
echo 1. Go to https://github.com
echo 2. Click "+" then "New repository"
echo 3. Name: kimiollo
echo 4. Make it PUBLIC
echo 5. DO NOT add README or .gitignore
echo.

echo Enter your GitHub username (just the username, no @ symbol):
set /p USERNAME=

echo.
echo Setting up remote origin for GitHub...
git remote add origin https://github.com/%USERNAME%/kimiollo.git

echo.
echo Pushing your code to GitHub...
git push -u origin main

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo SUCCESS! Your code is now on GitHub!
    echo ========================================
    echo.
    echo Next steps:
    echo 1. Go to https://github.com/%USERNAME%/kimiollo
    echo 2. Go to Settings ^> Pages
    echo 3. Source: GitHub Actions
    echo 4. Your site will be at: https://%USERNAME%.github.io/kimiollo
    echo.
) else (
    echo.
    echo ========================================
    echo There was an error pushing to GitHub.
    echo ========================================
    echo.
    echo Make sure:
    echo 1. You created the repository on GitHub first
    echo 2. Your username is correct: %USERNAME%
    echo 3. You're signed in to GitHub
    echo.
)

pause
