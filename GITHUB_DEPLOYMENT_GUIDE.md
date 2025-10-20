# GitHub Deployment Guide

## Quick Setup (5 minutes)

### Step 1: Create GitHub Repository
1. Go to https://github.com
2. Sign in or create account
3. Click the **"+"** button in top-right corner
4. Select **"New repository"**
5. Fill in:
   - Repository name: `kimiollo`
   - Description: `AI-Powered Business Proposal Generator & Funding Finder`
   - **Make it PUBLIC** (so others can access it)
   - **DO NOT** check "Add a README file" (we already have files)
6. Click **"Create repository"**

### Step 2: Push Your Code
After creating the repository, run these commands in this folder:

```bash
# Set your name (replace with your actual name)
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Add the remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/kimiollo.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### Step 3: Enable GitHub Pages
1. Go to your repository on GitHub
2. Click the **"Settings"** tab
3. Scroll down to **"Pages"** in the left sidebar
4. Under **"Source"**, select **"GitHub Actions"**
5. Save the settings

### Step 4: Set API URL (Important!)
Your frontend needs to know where the backend is hosted:

1. Go to repository **Settings** → **Secrets and variables** → **Actions**
2. Click **"New repository secret"**
3. Name: `API_URL`
4. Value: Your backend API URL (for now, use your ngrok URL or local IP)

## Your Live URLs
After deployment, your system will be available at:
- **Frontend**: `https://YOUR_USERNAME.github.io/kimiollo`
- **Backend**: (You'll need to deploy this separately - see backend deployment options below)

## Backend Deployment Options

### Option 1: Heroku (Recommended - Free)
```bash
# Install Heroku CLI, then:
heroku create your-app-name
git add .
git commit -m "Deploy backend"
git push heroku main
```

### Option 2: Railway
1. Go to https://railway.app
2. Connect GitHub repository
3. Deploy backend folder only

### Option 3: Render
1. Go to https://render.com
2. Connect GitHub repository
3. Deploy as web service

## Testing Your Deployment
1. Go to your GitHub Pages URL
2. The frontend should load
3. If you see connection errors, update the `API_URL` secret with your backend URL

## Troubleshooting
- **"Repository not found"**: Make sure you created the GitHub repository first
- **"Permission denied"**: Make sure you're signed in to GitHub
- **Frontend loads but backend errors**: Check your API_URL secret matches your backend URL

## Need Help?
Your project is now configured with:
✅ GitHub Actions workflow for deployment
✅ Proper package.json with homepage
✅ Gitignore for clean repository
✅ README with deployment instructions

Just follow the steps above and you'll have a live website!
