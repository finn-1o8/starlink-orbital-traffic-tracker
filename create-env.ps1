# Quick Environment Setup Script for Windows
# Creates the necessary .env file for the frontend

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "   Orbital Traffic Analyzer - Setup" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Check if .env already exists
$envPath = "frontend\.env"
if (Test-Path $envPath) {
    Write-Host "⚠️  Warning: frontend\.env already exists!" -ForegroundColor Yellow
    $response = Read-Host "Do you want to overwrite it? (y/n)"
    if ($response -ne "y") {
        Write-Host "❌ Setup cancelled." -ForegroundColor Red
        exit
    }
}

Write-Host "📝 Creating frontend environment file..." -ForegroundColor Green
Write-Host ""
Write-Host "You need a FREE Cesium Ion token (takes 1 minute):" -ForegroundColor Yellow
Write-Host "  1. Visit: https://ion.cesium.com/" -ForegroundColor White
Write-Host "  2. Create a free account" -ForegroundColor White
Write-Host "  3. Go to 'Access Tokens'" -ForegroundColor White
Write-Host "  4. Copy your default token" -ForegroundColor White
Write-Host ""

# Prompt for Cesium token
$token = Read-Host "Enter your Cesium Ion token"

if ([string]::IsNullOrWhiteSpace($token)) {
    Write-Host "❌ Error: Token cannot be empty!" -ForegroundColor Red
    exit 1
}

# Create .env file
$envContent = @"
# Backend API URLs
VITE_API_URL=http://localhost:8000/api
VITE_WS_URL=ws://localhost:8000/api

# Cesium Ion Access Token
VITE_CESIUM_ION_TOKEN=$token

# Feature Flags (optional)
VITE_ENABLE_ANALYTICS=true
VITE_ENABLE_HISTORICAL=true
"@

try {
    $envContent | Out-File -FilePath $envPath -Encoding ASCII -NoNewline
    Write-Host ""
    Write-Host "✅ Success! Created: $envPath" -ForegroundColor Green
    Write-Host ""
    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host "   Next Steps:" -ForegroundColor Cyan
    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "1. Start the application:" -ForegroundColor Yellow
    Write-Host "   docker-compose up -d" -ForegroundColor White
    Write-Host ""
    Write-Host "2. Wait 2-3 minutes for TLE data to load" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "3. Open your browser:" -ForegroundColor Yellow
    Write-Host "   http://localhost:3000" -ForegroundColor White
    Write-Host ""
    Write-Host "For more details, see TESTING.md" -ForegroundColor Green
    Write-Host ""
}
catch {
    Write-Host "❌ Error creating .env file: $_" -ForegroundColor Red
    exit 1
}

