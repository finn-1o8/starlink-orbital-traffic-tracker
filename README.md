# 🛰️ Orbital Traffic Impact Analyzer

A cutting-edge web application that visualizes the Starlink satellite constellation in real-time 3D and analyzes its impact on Earth Observation (EO) satellite operations.

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![React](https://img.shields.io/badge/react-18.3+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Docker](https://img.shields.io/badge/docker-ready-blue.svg)
![TypeScript](https://img.shields.io/badge/typescript-5.7+-blue.svg)
![FastAPI](https://img.shields.io/badge/fastapi-0.104+-009688.svg)
![Cesium](https://img.shields.io/badge/cesium-1.121+-4285F4.svg)

## 🌟 Features

### Core Features
- **Real-Time 3D Visualization**: View 1000+ Starlink satellites orbiting Earth in stunning 3D
- **Interactive Globe**: Rotate, zoom, and click satellites for detailed information
- **Orbital Congestion Analysis**: Calculate satellite density for any region and altitude band
- **EO Interference Analysis**: Predict when Starlink satellites interfere with Earth Observation imaging
- **Clean Imaging Windows**: Identify optimal times for satellite imaging operations
- **WebSocket Live Updates**: Satellite positions update automatically every 30 seconds
- **Historical Tracking**: Daily snapshots of constellation growth and metrics

### Advanced Features
- **Orbit Path Visualization**: Display complete orbital trajectories
- **Altitude Band Filtering**: View satellites by altitude shells (340-360km, 500-570km, 1100-1325km)
- **Congestion Heatmaps**: Global density visualization
- **Analytics Dashboard**: Real-time charts and statistics
- **REST API**: Full programmatic access to all features

## 🏗️ Architecture

### Tech Stack

**Backend:**
- Python 3.11+ with FastAPI
- Skyfield for SGP4 orbital propagation
- PostgreSQL with TimescaleDB for time-series data
- Redis for position caching
- APScheduler for automated TLE updates
- WebSocket for real-time updates

**Frontend:**
- React 18+ with TypeScript
- Cesium.js for 3D globe visualization
- Tailwind CSS for styling
- Recharts for analytics
- Axios & TanStack Query for API communication

**Infrastructure:**
- Docker & Docker Compose
- Caddy reverse proxy with automatic SSL
- GitHub Actions for CI/CD
- Hetzner cloud hosting

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 20+ (for local development)
- Python 3.11+ (for local development)

### Local Development

```bash
# Clone repository
git clone https://github.com/yourusername/Tracker.git
cd Tracker

# Start services
docker compose up -d

# Frontend: http://localhost:3001
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Environment Variables

Copy `env.example` files and configure:
- `backend/env.example` → `backend/.env`
- `frontend/env.example` → `frontend/.env`

See individual README files in `backend/` and `frontend/` for details.

## 📚 Documentation

- **[Deployment Guide](deployment/DEPLOYMENT.md)** - Production deployment on Hetzner
- **[Contributing](CONTRIBUTING.md)** - Contribution guidelines

## 🌐 Production

**Live App:** https://karmanlab.org/tracker

**Deployment:**
- Automated via GitHub Actions
- Server: Hetzner Cloud
- Reverse Proxy: Caddy (automatic SSL)
- Database: PostgreSQL with TimescaleDB
- Cache: Redis

## 🛠️ Development

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## 📊 API Endpoints

- `GET /api/satellites` - List all satellites
- `GET /api/satellites/positions` - Real-time positions
- `GET /api/satellites/{norad_id}/orbit` - Orbit path
- `GET /api/congestion` - Congestion analysis
- `GET /api/eo-analysis` - EO interference analysis
- `WebSocket /api/ws/positions` - Live position updates

Full API documentation at `/docs` when running locally.

## 📝 License

MIT License - see [LICENSE](LICENSE) file

## 🙏 Acknowledgments

- Cesium.js for 3D globe visualization
- Space-Track.org for TLE data
- Starlink for the inspiration

---

**Status:** ✅ Production-ready  
**Last Updated:** November 2025
