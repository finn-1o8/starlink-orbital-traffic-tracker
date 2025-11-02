#!/bin/bash
# Server Setup Script for Professional Deployment
# Run this script on your Hetzner server

set -e

echo "🚀 Setting up KarmanLabs deployment on Hetzner server..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Please run as root (use sudo)"
    exit 1
fi

# Update system
echo "📦 Updating system packages..."
apt update && apt upgrade -y

# Install Docker if not already installed
if ! command -v docker &> /dev/null; then
    echo "🐳 Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
else
    echo "✅ Docker already installed"
fi

# Install Docker Compose plugin
if ! docker compose version &> /dev/null; then
    echo "🐳 Installing Docker Compose..."
    apt install -y docker-compose-plugin
else
    echo "✅ Docker Compose already installed"
fi

# Create project directory
PROJECT_DIR="/srv/karmanlabs"
echo "📁 Creating project directory at $PROJECT_DIR..."
mkdir -p $PROJECT_DIR
cd $PROJECT_DIR

# Download deployment files
echo "📥 Downloading deployment files..."
curl -L -o docker-compose.yml https://raw.githubusercontent.com/finn-1o8/Tracker/main/deployment/docker-compose.yml
curl -L -o Caddyfile https://raw.githubusercontent.com/finn-1o8/Tracker/main/deployment/Caddyfile
curl -L -o env.template https://raw.githubusercontent.com/finn-1o8/Tracker/main/deployment/env.template

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp env.template .env
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file with secure passwords!"
    echo "   Run: nano $PROJECT_DIR/.env"
    echo ""
    read -p "Press Enter after editing .env to continue..."
fi

# Setup firewall
echo "🔥 Configuring firewall..."
ufw allow 22/tcp   # SSH
ufw allow 80/tcp   # HTTP
ufw allow 443/tcp  # HTTPS
ufw allow 443/udp  # HTTP/3
ufw --force enable

# Install GitHub CLI for image pulling (optional)
if ! command -v gh &> /dev/null; then
    echo "📦 Installing GitHub CLI..."
    curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | gpg --dearmor -o /usr/share/keyrings/githubcli-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | tee /etc/apt/sources.list.d/github-cli.list > /dev/null
    apt update
    apt install gh -y
    echo "✅ GitHub CLI installed"
fi

# Login to GHCR (optional, for manual pulls)
echo "🔐 Login to GitHub Container Registry..."
echo "   You may need to login manually with: echo \$GITHUB_TOKEN | docker login ghcr.io -u finn-1o8 --password-stdin"
echo "   Get token from: https://github.com/settings/tokens"

# Pull initial images
echo "📥 Pulling Docker images..."
docker compose pull

# Start services
echo "🚀 Starting all services..."
docker compose up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to start..."
sleep 10

# Show status
echo ""
echo "📊 Service Status:"
docker compose ps

echo ""
echo "✅ Setup complete!"
echo ""
echo "🌐 Your site should be available at:"
echo "   Main: https://karmanlab.org"
echo "   Tracker: https://tracker.karmanlab.org or https://karmanlab.org/tracker"
echo ""
echo "📝 Useful commands:"
echo "   cd $PROJECT_DIR"
echo "   docker compose ps           # Check status"
echo "   docker compose logs -f      # View logs"
echo "   docker compose pull         # Update images"
echo "   docker compose up -d        # Restart services"
echo ""
echo "🔍 First time setup may take a few minutes for SSL certificates."
echo "   Monitor logs with: docker compose logs -f caddy"

