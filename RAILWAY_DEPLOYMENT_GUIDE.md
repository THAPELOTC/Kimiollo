# Railway Deployment Guide - Flask Backend

## Quick Setup (5 minutes)

### Step 1: Deploy to Railway
1. Go to https://railway.app
2. Click "Start a New Project"
3. Choose "Deploy from GitHub repo"
4. Select your `THAPELOTC/Kimiollo` repository
5. Railway will automatically detect it's a Python app

### Step 2: Configure Environment Variables
In Railway dashboard, go to your project → Variables tab:

Add these environment variables:
- `FLASK_ENV` = `production`
- `SECRET_KEY` = `your-secret-key-change-me-123`
- `JWT_SECRET_KEY` = `jwt-secret-key-change-me-456`
- `OPENAI_API_KEY` = `your-openai-key` (optional, if you have one)

### Step 3: Get Your Backend URL
After deployment (2-3 minutes), Railway will give you a URL like:
`https://kimiollo-production-abc123.up.railway.app`

### Step 4: Update Frontend Configuration
1. Go to your GitHub repository: https://github.com/THAPELOTC/Kimiollo
2. Go to Settings → Secrets and variables → Actions
3. Update the `API_URL` secret with your Railway URL + `/api`
   Example: `https://kimiollo-production-abc123.up.railway.app/api`

### Step 5: Test Your Full System
- Frontend: https://thapelotc.github.io/Kimiollo
- Backend API: Your Railway URL

## Troubleshooting
- If deployment fails, check the Railway logs
- Make sure all environment variables are set
- The build might take 3-5 minutes on first deploy

## Cost
Railway offers a free tier with:
- 500 hours of execution time per month
- Perfect for development and small projects
