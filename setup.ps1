# Development setup (Windows): creates the env files and optionally starts the Docker stack.

Write-Host "Orbital Traffic Impact Analyzer - setup" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "Docker is required. Install Docker Desktop first." -ForegroundColor Red
    exit 1
}
docker compose version *> $null
if ($LASTEXITCODE -ne 0) {
    Write-Host "The Docker Compose plugin is required (docker compose version)." -ForegroundColor Red
    exit 1
}

$pairs = @(
    @(".env.example", ".env"),
    @("backend\.env.example", "backend\.env"),
    @("frontend\.env.example", "frontend\.env")
)
foreach ($pair in $pairs) {
    if (-not (Test-Path $pair[1])) {
        Copy-Item $pair[0] $pair[1]
        Write-Host "Created $($pair[1]) from $($pair[0])"
    }
}

Write-Host "Edit .env and set POSTGRES_PASSWORD. CESIUM_ION_TOKEN is optional." -ForegroundColor Yellow
Write-Host ""

$response = Read-Host "Start the application with Docker now? (y/n)"
if ($response -eq "y" -or $response -eq "Y") {
    docker compose up -d
    Write-Host ""
    docker compose ps
    Write-Host ""
    Write-Host "Frontend:  http://localhost:3001" -ForegroundColor Green
    Write-Host "API:       http://localhost:8000  (docs at /docs)" -ForegroundColor Green
    Write-Host "The first catalogue download takes about a minute: docker compose logs -f backend"
    Write-Host "Stop with: docker compose down"
} else {
    Write-Host "Start later with: docker compose up -d"
}
