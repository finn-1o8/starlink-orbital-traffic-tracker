#!/bin/bash
# Quick Environment Setup Script for Linux/Mac
# Creates the necessary .env file for the frontend

set -e

# Colors
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

echo -e "${CYAN}================================================${NC}"
echo -e "${CYAN}   Orbital Traffic Analyzer - Setup${NC}"
echo -e "${CYAN}================================================${NC}"
echo ""

# Check if .env already exists
ENV_PATH="frontend/.env"
if [ -f "$ENV_PATH" ]; then
    echo -e "${YELLOW}⚠️  Warning: frontend/.env already exists!${NC}"
    read -p "Do you want to overwrite it? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${RED}❌ Setup cancelled.${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}📝 Creating frontend environment file...${NC}"
echo ""
echo -e "${YELLOW}You need a FREE Cesium Ion token (takes 1 minute):${NC}"
echo -e "${WHITE}  1. Visit: https://ion.cesium.com/${NC}"
echo -e "${WHITE}  2. Create a free account${NC}"
echo -e "${WHITE}  3. Go to 'Access Tokens'${NC}"
echo -e "${WHITE}  4. Copy your default token${NC}"
echo ""

# Prompt for Cesium token
read -p "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiI3ZTNlMTc0OC1iYjkzLTRkZWYtOTJmZS1iMGE3NTJhMjMwMzciLCJpZCI6MzU0MDEyLCJpYXQiOjE3NjE0MzgxMTR9.FHPtMVfJrwVPrU8BfSsVaxGbfIWorLrmbSS6z683-as" token

if [ -z "$token" ]; then
    echo -e "${RED}❌ Error: Token cannot be empty!${NC}"
    exit 1
fi

# Create .env file
cat > "$ENV_PATH" << EOF
# Backend API URLs
VITE_API_URL=http://localhost:8000/api
VITE_WS_URL=ws://localhost:8000/api

# Cesium Ion Access Token
VITE_CESIUM_ION_TOKEN=$token

# Feature Flags (optional)
VITE_ENABLE_ANALYTICS=true
VITE_ENABLE_HISTORICAL=true
EOF

echo ""
echo -e "${GREEN}✅ Success! Created: $ENV_PATH${NC}"
echo ""
echo -e "${CYAN}================================================${NC}"
echo -e "${CYAN}   Next Steps:${NC}"
echo -e "${CYAN}================================================${NC}"
echo ""
echo -e "${YELLOW}1. Start the application:${NC}"
echo -e "${WHITE}   docker-compose up -d${NC}"
echo ""
echo -e "${YELLOW}2. Wait 2-3 minutes for TLE data to load${NC}"
echo ""
echo -e "${YELLOW}3. Open your browser:${NC}"
echo -e "${WHITE}   http://localhost:3000${NC}"
echo ""
echo -e "${GREEN}For more details, see TESTING.md${NC}"
echo ""

