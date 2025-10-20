# PowerShell script to start frontend with memory optimization
Write-Host "Starting React Frontend with Memory Optimization" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green

# Set Node.js memory options and other optimizations
$env:NODE_OPTIONS = "--max_old_space_size=8192 --max_semi_space_size=512"
$env:GENERATE_SOURCEMAP = "false"
$env:FAST_REFRESH = "false"

# Navigate to project directory
Set-Location "C:\Users\THAPELO_01\OneDrive\Desktop\kimiollo"

# Check if Node.js is available
try {
    $nodeVersion = node --version
    Write-Host "Node.js version: $nodeVersion" -ForegroundColor Yellow
} catch {
    Write-Host "ERROR: Node.js is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Node.js from https://nodejs.org/" -ForegroundColor Red
    exit 1
}

# Install dependencies if needed
if (!(Test-Path "node_modules")) {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to install dependencies" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "Starting development server with memory optimization..." -ForegroundColor Yellow
Write-Host "Frontend will be available at: http://localhost:3000" -ForegroundColor Cyan
Write-Host ""

# Start the development server
npm start

