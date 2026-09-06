# Creates frontend\.env for local development, prompting for an optional Cesium ion token.

$envPath = "frontend\.env"
if (Test-Path $envPath) {
    $response = Read-Host "$envPath already exists. Overwrite? (y/n)"
    if ($response -ne "y") { Write-Host "Cancelled."; exit 0 }
}

Write-Host "A Cesium ion token is optional. With one the globe shows world terrain and Bing imagery;"
Write-Host "without one it uses OpenStreetMap tiles. Free tokens: https://ion.cesium.com"
$token = Read-Host "Cesium ion token (leave empty to skip)"

$content = @"
VITE_API_URL=http://localhost:8000/api
VITE_WS_URL=ws://localhost:8000/api
VITE_CESIUM_ION_TOKEN=$token
VITE_LANDING_URL=
"@

$content | Out-File -FilePath $envPath -Encoding ASCII
Write-Host "Created $envPath" -ForegroundColor Green
Write-Host "Next: docker compose up -d   (frontend at http://localhost:3001)"
Write-Host "  or: cd frontend; npm ci; npm run dev   (frontend at http://localhost:3000)"
