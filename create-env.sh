#!/bin/bash
# Creates frontend/.env for local development, prompting for an optional Cesium ion token.

set -e

ENV_PATH="frontend/.env"
if [ -f "$ENV_PATH" ]; then
    read -p "$ENV_PATH already exists. Overwrite? (y/n): " -n 1 -r
    echo
    [[ $REPLY =~ ^[Yy]$ ]] || { echo "Cancelled."; exit 0; }
fi

echo "A Cesium ion token is optional. With one the globe shows world terrain and Bing imagery;"
echo "without one it uses OpenStreetMap tiles. Free tokens: https://ion.cesium.com"
read -p "Cesium ion token (leave empty to skip): " token

cat > "$ENV_PATH" <<EOF
VITE_API_URL=http://localhost:8000/api
VITE_WS_URL=ws://localhost:8000/api
VITE_CESIUM_ION_TOKEN=$token
VITE_LANDING_URL=
EOF

echo "Created $ENV_PATH"
echo "Next: docker compose up -d   (frontend at http://localhost:3001)"
echo "  or: cd frontend && npm ci && npm run dev   (frontend at http://localhost:3000)"
