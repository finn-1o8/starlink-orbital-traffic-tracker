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
- Nginx (production)
- Environment-based configuration

## 📦 Installation

### Prerequisites

- Docker & Docker Compose (recommended)
- OR:
  - Python 3.11+
  - Node.js 20+
  - PostgreSQL 15+
  - Redis 7+

### Quick Start with Docker (Recommended)

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/orbital-traffic-analyzer.git
cd orbital-traffic-analyzer
```

2. **Create environment files:**

Backend `.env`:
```bash
cp backend/.env.example backend/.env
# Edit backend/.env with your settings
```

Frontend `.env`:
```bash
cp frontend/.env.example frontend/.env
# Add your Cesium Ion token: https://ion.cesium.com/
```

3. **Start all services:**
```bash
docker-compose up -d
```

4. **Wait for initialization (first run takes ~2 minutes):**
```bash
docker-compose logs -f backend
# Wait for "TLE update completed successfully"
```

5. **Open your browser:**
- Frontend: http://localhost:3000
- API Documentation: http://localhost:8000/docs

### Manual Installation

#### Backend Setup

1. **Install Python dependencies:**
```bash
cd backend
pip install -r requirements.txt
```

2. **Setup PostgreSQL database:**
```bash
createdb orbital_tracker
```

3. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your database credentials
```

4. **Start the backend:**
```bash
uvicorn app.main:app --reload
```

#### Frontend Setup

1. **Install dependencies:**
```bash
cd frontend
npm install
```

2. **Configure environment:**
```bash
cp .env.example .env
# Add your Cesium Ion token
```

3. **Start development server:**
```bash
npm run dev
```

## 🚀 Usage

### Basic Usage

1. **View Satellites**: The 3D globe automatically displays all tracked Starlink satellites
2. **Select Satellite**: Click any satellite point to view details and orbit path
3. **Filter by Altitude**: Use the sidebar to filter satellites by altitude band
4. **Search**: Find specific satellites by name or NORAD ID
5. **Analytics**: Click "Analytics" button to view constellation statistics

### API Usage

#### Get All Satellite Positions

```bash
curl http://localhost:8000/api/satellites/positions
```

Response:
```json
[
  {
    "satellite_id": 1,
    "norad_id": 44713,
    "name": "STARLINK-1007",
    "lat": 45.123,
    "lon": -93.456,
    "alt_km": 550.2,
    "velocity_km_s": 7.56,
    "timestamp": "2025-10-25T10:30:00+00:00"
  }
]
```

#### Analyze Orbital Congestion

```bash
curl "http://localhost:8000/api/congestion?lat=40.7128&lon=-74.0060&radius_km=500&alt_min=500&alt_max=600"
```

Response:
```json
{
  "total_satellites": 45,
  "density_per_1000km3": 0.023,
  "mean_spacing_km": 150.5,
  "closest_approach_km": 12.3,
  "timestamp": "2025-10-25T10:30:00+00:00"
}
```

#### Get Satellite Orbit Path

```bash
curl http://localhost:8000/api/satellites/44713/orbit?duration=90
```

#### EO Interference Analysis

```bash
curl -X POST http://localhost:8000/api/eo-analysis \
  -H "Content-Type: application/json" \
  -d '{
    "eo_preset": "sentinel-2a",
    "target_region": {"lat": 40.7128, "lon": -74.0060, "radius_km": 100},
    "duration_hours": 24
  }'
```

### WebSocket Connection

```javascript
const ws = new WebSocket('ws://localhost:8000/api/ws/positions');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Positions:', data.data);
};
```

## 📊 API Endpoints

### Satellites

- `GET /api/satellites` - List all satellites
- `GET /api/satellites/positions` - Get current positions
- `GET /api/satellites/{norad_id}` - Get satellite info
- `GET /api/satellites/{norad_id}/orbit` - Get orbit path

### Congestion Analysis

- `GET /api/congestion` - Analyze regional congestion
- `GET /api/congestion/heatmap` - Get global density heatmap
- `GET /api/congestion/altitude-distribution` - Get altitude distribution

### EO Analysis

- `POST /api/eo-analysis` - Analyze EO interference
- `GET /api/eo-analysis/presets` - Get available EO satellite presets

### WebSocket

- `WS /api/ws/positions` - Real-time position updates

Full API documentation: http://localhost:8000/docs

## 🎨 Screenshots

### Main Interface
![Main Interface](docs/screenshots/main-interface.png)
*3D globe showing Starlink constellation with real-time tracking*

### Analytics Dashboard
![Analytics Dashboard](docs/screenshots/dashboard.png)
*Constellation statistics and altitude distribution charts*

### Satellite Details
![Satellite Details](docs/screenshots/satellite-info.png)
*Detailed satellite information with orbit visualization*

## 🔧 Configuration

### Backend Configuration (`backend/.env`)

```env
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/orbital_tracker

# Redis
REDIS_URL=redis://localhost:6379/0

# API Settings
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:3000

# TLE Updates
TLE_UPDATE_INTERVAL_HOURS=6
POSITION_CACHE_SECONDS=30
```

### Frontend Configuration (`frontend/.env`)

```env
# API Endpoints
VITE_API_URL=http://localhost:8000/api
VITE_WS_URL=ws://localhost:8000/api

# Cesium Ion Token (Required)
VITE_CESIUM_ION_TOKEN=your_token_here

# Feature Flags
VITE_ENABLE_ANALYTICS=true
VITE_ENABLE_HISTORICAL=true
```

### Getting Cesium Ion Token

1. Create free account at https://ion.cesium.com/
2. Navigate to "Access Tokens"
3. Create new token or use default token
4. Copy token to `VITE_CESIUM_ION_TOKEN`

## 📈 Performance

- **Backend**: Calculates 1000+ satellite positions in <5 seconds
- **API Response Time**: <500ms (95th percentile)
- **Frontend**: Maintains 30+ FPS with 1000+ rendered satellites
- **WebSocket Updates**: Every 30 seconds
- **TLE Updates**: Automatic every 6 hours

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest tests/ -v
```

### Frontend Tests

```bash
cd frontend
npm run test
```

### End-to-End Tests

```bash
npm run test:e2e
```

## 🐛 Troubleshooting

### Satellites Not Appearing

1. Check backend logs: `docker-compose logs backend`
2. Verify TLE data was fetched: Look for "TLE update completed successfully"
3. Wait 2-3 minutes on first startup for initial data fetch

### Cesium Not Loading

1. Verify Cesium Ion token is set in `frontend/.env`
2. Check browser console for errors
3. Ensure token has access to required assets

### WebSocket Connection Failed

1. Verify backend is running: `curl http://localhost:8000/api/health`
2. Check CORS settings in `backend/.env`
3. Try fallback polling mode (positions refresh every 30s via HTTP)

### Database Connection Error

1. Ensure PostgreSQL is running: `docker-compose ps`
2. Check credentials in `.env` file
3. Reset database: `docker-compose down -v && docker-compose up -d`

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 for Python code
- Use TypeScript strict mode
- Add tests for new features
- Update documentation
- Keep commits atomic and well-described

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **CelesTrak** for providing TLE data
- **Cesium** for the amazing 3D globe engine
- **Skyfield** for orbital mechanics calculations
- **FastAPI** for the excellent Python web framework
- **Starlink** constellation data from SpaceX/CelesTrak

## 📚 Resources

### Documentation
- [Cesium.js Documentation](https://cesium.com/learn/)
- [Skyfield Documentation](https://rhodesmill.org/skyfield/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

### Data Sources
- [CelesTrak - Starlink TLEs](https://celestrak.org/NORAD/elements/gp.php?GROUP=starlink&FORMAT=tle)
- [Space-Track.org](https://www.space-track.org/)

### Similar Projects
- [Stuff in Space](http://stuffin.space/)
- [SatFlare](https://www.satflare.com/)
- [N2YO](https://www.n2yo.com/)

## 📞 Contact

- **Project Link**: https://github.com/yourusername/orbital-traffic-analyzer
- **Issues**: https://github.com/yourusername/orbital-traffic-analyzer/issues
- **Discussions**: https://github.com/yourusername/orbital-traffic-analyzer/discussions

## 🗺️ Roadmap

### Phase 1 (Current)
- ✅ Real-time 3D visualization
- ✅ Satellite tracking and orbit paths
- ✅ Basic congestion analysis
- ✅ WebSocket live updates
- ✅ Analytics dashboard

### Phase 2 (Q1 2026)
- [ ] Historical playback (time machine)
- [ ] Advanced EO interference analysis with FOV cone visualization
- [ ] Ground station coverage calculator
- [ ] Collision risk assessment
- [ ] Mobile responsive design

### Phase 3 (Q2 2026)
- [ ] User accounts and saved analyses
- [ ] PDF report generation
- [ ] Social sharing features
- [ ] Multi-constellation support (OneWeb, Amazon Kuiper)
- [ ] Predictive analytics and forecasting

### Phase 4 (Future)
- [ ] Machine learning for interference prediction
- [ ] Real-time conjunction alerts
- [ ] Integration with telescope scheduling systems
- [ ] Public API with rate limiting and authentication

---

**Built with ❤️ for the space community**

Last Updated: October 25, 2025

