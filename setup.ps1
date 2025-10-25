# Orbital Traffic Impact Analyzer - Setup Script (PowerShell)
# This script sets up the development environment on Windows

Write-Host "🛰️  Orbital Traffic Impact Analyzer - Setup" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check for required tools
Write-Host "📋 Checking prerequisites..." -ForegroundColor Yellow

$dockerInstalled = $null -ne (Get-Command docker -ErrorAction SilentlyContinue)
$dockerComposeInstalled = $null -ne (Get-Command docker-compose -ErrorAction SilentlyContinue)

if (-not $dockerInstalled) {
    Write-Host "❌ Docker is required but not installed. Please install Docker Desktop first." -ForegroundColor Red
    exit 1
}

if (-not $dockerComposeInstalled) {
    Write-Host "❌ Docker Compose is required but not installed. Please install Docker Compose first." -ForegroundColor Red
    exit 1
}

Write-Host "✅ Prerequisites check passed!" -ForegroundColor Green
Write-Host ""

# Create environment files if they don't exist
Write-Host "📝 Setting up environment files..." -ForegroundColor Yellow

if (-not (Test-Path "backend\.env")) {
    Write-Host "Creating backend\.env from example..."
    Copy-Item "backend\.env.example" "backend\.env"
    Write-Host "⚠️  Please edit backend\.env and configure your database credentials" -ForegroundColor Yellow
}

if (-not (Test-Path "frontend\.env")) {
    Write-Host "Creating frontend\.env from example..."
    Copy-Item "frontend\.env.example" "frontend\.env"
    Write-Host "⚠️  Please edit frontend\.env and add your Cesium Ion token" -ForegroundColor Yellow
    Write-Host "   Get your token from: https://ion.cesium.com/" -ForegroundColor Yellow
}

Write-Host "✅ Environment files created!" -ForegroundColor Green
Write-Host ""

# Ask if user wants to start with Docker
$response = Read-Host "Do you want to start the application with Docker now? (y/n)"
if ($response -eq "y" -or $response -eq "Y") {
    Write-Host ""
    Write-Host "🐳 Starting Docker containers..." -ForegroundColor Cyan
    Write-Host ""
    
    docker-compose up -d
    
    Write-Host ""
    Write-Host "✅ Containers started!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Waiting for services to be ready..."
    Start-Sleep -Seconds 10
    
    Write-Host ""
    Write-Host "📊 Container status:" -ForegroundColor Cyan
    docker-compose ps
    
    Write-Host ""
    Write-Host "🎉 Setup complete!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📍 Access points:" -ForegroundColor Cyan
    Write-Host "   Frontend: http://localhost:3000"
    Write-Host "   Backend API: http://localhost:8000"
    Write-Host "   API Docs: http://localhost:8000/docs"
    Write-Host ""
    Write-Host "📝 Note: The first TLE data fetch may take 2-3 minutes." -ForegroundColor Yellow
    Write-Host "   Monitor progress with: docker-compose logs -f backend"
    Write-Host ""
    Write-Host "🛑 To stop: docker-compose down" -ForegroundColor Yellow
} else {
    Write-Host ""
    Write-Host "✅ Setup files created!" -ForegroundColor Green
    Write-Host ""
    Write-Host "To start manually:" -ForegroundColor Cyan
    Write-Host "  1. Configure backend\.env and frontend\.env"
    Write-Host "  2. Run: docker-compose up -d"
    Write-Host ""
}

