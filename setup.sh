#!/bin/bash

# Orbital Traffic Impact Analyzer - Setup Script
# This script sets up the development environment

set -e

echo "🛰️  Orbital Traffic Impact Analyzer - Setup"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check for required tools
echo "📋 Checking prerequisites..."

command -v docker >/dev/null 2>&1 || { 
    echo -e "${RED}❌ Docker is required but not installed. Please install Docker first.${NC}" 
    exit 1
}

command -v docker-compose >/dev/null 2>&1 || { 
    echo -e "${RED}❌ Docker Compose is required but not installed. Please install Docker Compose first.${NC}" 
    exit 1
}

echo -e "${GREEN}✅ Prerequisites check passed!${NC}"
echo ""

# Create environment files if they don't exist
echo "📝 Setting up environment files..."

if [ ! -f backend/.env ]; then
    echo "Creating backend/.env from example..."
    cp backend/.env.example backend/.env
    echo -e "${YELLOW}⚠️  Please edit backend/.env and configure your database credentials${NC}"
fi

if [ ! -f frontend/.env ]; then
    echo "Creating frontend/.env from example..."
    cp frontend/.env.example frontend/.env
    echo -e "${YELLOW}⚠️  Please edit frontend/.env and add your Cesium Ion token${NC}"
    echo -e "${YELLOW}   Get your token from: https://ion.cesium.com/${NC}"
fi

echo -e "${GREEN}✅ Environment files created!${NC}"
echo ""

# Ask if user wants to start with Docker
read -p "Do you want to start the application with Docker now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    echo ""
    echo "🐳 Starting Docker containers..."
    echo ""
    
    docker-compose up -d
    
    echo ""
    echo -e "${GREEN}✅ Containers started!${NC}"
    echo ""
    echo "Waiting for services to be ready..."
    sleep 10
    
    echo ""
    echo "📊 Container status:"
    docker-compose ps
    
    echo ""
    echo -e "${GREEN}🎉 Setup complete!${NC}"
    echo ""
    echo "📍 Access points:"
    echo "   Frontend: http://localhost:3000"
    echo "   Backend API: http://localhost:8000"
    echo "   API Docs: http://localhost:8000/docs"
    echo ""
    echo "📝 Note: The first TLE data fetch may take 2-3 minutes."
    echo "   Monitor progress with: docker-compose logs -f backend"
    echo ""
    echo "🛑 To stop: docker-compose down"
else
    echo ""
    echo -e "${GREEN}✅ Setup files created!${NC}"
    echo ""
    echo "To start manually:"
    echo "  1. Configure backend/.env and frontend/.env"
    echo "  2. Run: docker-compose up -d"
    echo ""
fi

