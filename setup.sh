#!/bin/bash
# Development setup: creates the env files and optionally starts the Docker stack.

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "Orbital Traffic Impact Analyzer - setup"
echo "======================================="

command -v docker >/dev/null 2>&1 || { echo -e "${RED}Docker is required. Install Docker Desktop or Docker Engine first.${NC}"; exit 1; }
docker compose version >/dev/null 2>&1 || { echo -e "${RED}The Docker Compose plugin is required (docker compose version).${NC}"; exit 1; }

for pair in ".env.example:.env" "backend/.env.example:backend/.env" "frontend/.env.example:frontend/.env"; do
    src="${pair%%:*}"; dst="${pair##*:}"
    if [ ! -f "$dst" ]; then
        cp "$src" "$dst"
        echo "Created $dst from $src"
    fi
done

echo -e "${YELLOW}Edit .env and set POSTGRES_PASSWORD. CESIUM_ION_TOKEN is optional.${NC}"
echo

read -p "Start the application with Docker now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker compose up -d
    echo
    docker compose ps
    echo
    echo -e "${GREEN}Frontend:  http://localhost:3001${NC}"
    echo -e "${GREEN}API:       http://localhost:8000  (docs at /docs)${NC}"
    echo "The first catalogue download takes about a minute: docker compose logs -f backend"
    echo "Stop with: docker compose down"
else
    echo "Start later with: docker compose up -d"
fi
