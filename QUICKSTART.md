# 🚀 Quick Start Guide

Get the Orbital Traffic Impact Analyzer up and running in minutes!

## Prerequisites

- **Docker** and **Docker Compose** (recommended)
- OR: Python 3.11+, Node.js 20+, PostgreSQL, Redis

## 🎯 Option 1: Docker (Easiest)

### Linux/Mac

```bash
# Clone the repository
git clone https://github.com/yourusername/orbital-traffic-analyzer.git
cd orbital-traffic-analyzer

# Run setup script
chmod +x setup.sh
./setup.sh
```

### Windows (PowerShell)

```powershell
# Clone the repository
git clone https://github.com/yourusername/orbital-traffic-analyzer.git
cd orbital-traffic-analyzer

# Run setup script
.\setup.ps1
```

### Manual Docker Setup

```bash
# 1. Create environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# 2. Get Cesium Ion token from https://ion.cesium.com/
# Edit frontend/.env and add your token

# 3. Start all services
docker-compose up -d

# 4. Monitor startup (wait for TLE data fetch)
docker-compose logs -f backend
```

**That's it!** Open http://localhost:3000 in your browser.

## 🎯 Option 2: Manual Setup

### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup database (PostgreSQL must be running)
# Edit .env with your database credentials
cp .env.example .env

# Start backend
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Add your Cesium Ion token to .env

# Start frontend
npm run dev
```

**Access the app** at http://localhost:3000

## ⚙️ Configuration

### Required Configuration

1. **Cesium Ion Token** (Frontend)
   - Sign up at https://ion.cesium.com/
   - Copy your access token
   - Add to `frontend/.env`:
     ```
     VITE_CESIUM_ION_TOKEN=your_token_here
     ```

2. **Database** (Backend)
   - Default Docker setup uses PostgreSQL in container
   - For manual setup, configure `backend/.env`:
     ```
     DATABASE_URL=postgresql://user:pass@localhost:5432/orbital_tracker
     ```

### Optional Configuration

- **TLE Update Frequency**: Edit `TLE_UPDATE_INTERVAL_HOURS` in `backend/.env` (default: 6 hours)
- **API CORS**: Edit `CORS_ORIGINS` in `backend/.env` for production
- **Redis Cache**: Edit `REDIS_URL` in `backend/.env`

## 🔍 Verify Installation

1. **Check backend health**:
   ```bash
   curl http://localhost:8000/api/health
   ```
   Should return: `{"status":"healthy",...}`

2. **Check satellite count**:
   ```bash
   curl http://localhost:8000/api/satellites
   ```
   Should return list of satellites

3. **Check frontend**:
   - Open http://localhost:3000
   - You should see the 3D globe with satellites

## 🐛 Troubleshooting

### Satellites not appearing

```bash
# Check backend logs
docker-compose logs backend

# Wait for TLE data fetch (first run)
# Look for: "TLE update completed successfully"
```

### Cesium not loading

1. Check browser console for errors
2. Verify Cesium Ion token in `frontend/.env`
3. Ensure token has access to required assets

### Port conflicts

```bash
# Change ports in docker-compose.yml
# Frontend: change "3000:3000" to "YOUR_PORT:3000"
# Backend: change "8000:8000" to "YOUR_PORT:8000"
```

### Database connection error

```bash
# Reset database
docker-compose down -v
docker-compose up -d
```

## 📚 Next Steps

- Read the [full README](README.md) for detailed documentation
- Check out the [API Documentation](http://localhost:8000/docs)
- Explore the [Contributing Guide](CONTRIBUTING.md)

## 🆘 Get Help

- **Issues**: https://github.com/yourusername/orbital-traffic-analyzer/issues
- **Discussions**: https://github.com/yourusername/orbital-traffic-analyzer/discussions

---

**Happy tracking! 🛰️**

