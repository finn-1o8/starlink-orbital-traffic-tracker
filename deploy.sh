#!/bin/bash
# Deployment script for karmanlab.org
# Server: Hetzner CX23 VPS (Helsinki)
# Domain: karmanlab.org

set -e  # Exit on error

echo "🚀 Starting deployment to karmanlab.org..."
echo ""

# Navigate to project directory
cd /opt/karmanlabs || {
    echo "❌ Error: Directory /opt/karmanlabs not found!"
    echo "   Please ensure you're on the server and the project is cloned."
    exit 1
}

# Pull latest changes from GitHub
echo "📥 Pulling latest changes from GitHub..."
git pull origin main

if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to pull from GitHub"
    exit 1
fi

echo "✅ Successfully pulled latest changes"
echo ""

# Stop existing containers gracefully
echo "🛑 Stopping existing containers..."
docker-compose -f docker-compose.prod.yml down

# Rebuild and start containers
echo "🔨 Building and starting containers..."
docker-compose -f docker-compose.prod.yml up -d --build

if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to build/start containers"
    exit 1
fi

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📊 Checking container status..."
docker-compose -f docker-compose.prod.yml ps

echo ""
echo "🌐 Site should be live at: https://karmanlab.org"
echo ""
echo "📝 To view logs, run:"
echo "   docker-compose -f docker-compose.prod.yml logs -f"


