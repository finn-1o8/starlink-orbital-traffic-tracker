# Orbital Traffic Impact Analyzer

Real-time 3D view of the Starlink constellation, orbital-density statistics, and a geometric estimate of when Starlink satellites cross an Earth-observation satellite's field of view.

FastAPI and SGP4 on the backend, React and Cesium on the frontend, PostgreSQL and Redis behind them, wired together with Docker Compose.

![CI](https://github.com/finn-1o8/starlink-orbital-traffic-tracker/actions/workflows/ci.yml/badge.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## What it does

- Tracks every object in CelesTrak's Starlink group (elements refreshed every 6 hours) and propagates all of them with SGP4 in one vectorised call.
- Pushes positions to the browser over WebSocket every 5 seconds (configurable). Positions are computed once per interval and fanned out to every client.
- Congestion statistics for any region and altitude band: count, density, mean spacing and closest approach, plus a global density grid and the per-shell distribution.
- EO interference analysis: propagates an EO satellite (Sentinel-2A, Landsat 8 or Sentinel-1A from live CelesTrak elements, or any TLE you paste) together with the whole Starlink catalogue and flags each imaging pass during which a Starlink satellite sits inside the sensor's nadir-pointed field-of-view cone.
- Daily snapshots of satellite counts per shell, kept in PostgreSQL and served from `/api/history/snapshots`.

## How the EO analysis works

1. Imaging passes. Without a target region, every orbit is one pass. With a region, a pass is the time during which the sensor swath reaches the region, meaning the sub-satellite point is within the region radius plus half the swath width of the region centre.
2. Inside each pass the EO satellite and every Starlink satellite are propagated at a fixed step (20 s by default).
3. A Starlink satellite counts as interfering at a sample when it is below the EO satellite and the angle between the nadir vector and the line of sight to it is within half the field of view.

Limits worth knowing before quoting the numbers: the cone is always nadir-pointed, so side-looking instruments such as SAR are approximated; crossings shorter than the sampling step can be missed; the metric is purely geometric and ignores sun geometry, glint and whether the sensor would resolve the object.

## Quick start with Docker

```bash
git clone https://github.com/finn-1o8/starlink-orbital-traffic-tracker.git
cd starlink-orbital-traffic-tracker
cp .env.example .env        # set POSTGRES_PASSWORD; CESIUM_ION_TOKEN is optional
docker compose up -d
```

Frontend at http://localhost:3001, API at http://localhost:8000, interactive API docs at http://localhost:8000/docs. The first catalogue download takes about a minute.

Without a Cesium ion token the globe uses OpenStreetMap tiles on a plain ellipsoid. With one it uses Cesium World Terrain and Bing imagery. Tokens are free at https://ion.cesium.com; restrict yours to your own domain in the ion dashboard, since it ships to the browser.

## Local development

Backend:

```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
cp .env.example .env    # optional; without DATABASE_URL a local SQLite file is used
uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
npm ci
cp .env.example .env
npm run dev
```

Checks:

```bash
cd backend && ruff check . && python -m pytest
cd frontend && npm run lint && npm run build
```

The backend tests run against SQLite with frozen element sets and never touch the network.

## Configuration

| Variable | Default | Purpose |
|---|---|---|
| `DATABASE_URL` | local SQLite | PostgreSQL connection string in production |
| `REDIS_URL` | `redis://localhost:6379/0` | Position cache; unreachable Redis just disables caching |
| `CORS_ORIGINS` | localhost dev origins | Browser origins allowed to call the API and open the WebSocket |
| `TLE_UPDATE_INTERVAL_HOURS` | `6` | CelesTrak refresh interval |
| `WS_UPDATE_SECONDS` | `5` | WebSocket broadcast interval |
| `POSITION_CACHE_SECONDS` | `30` | Lifetime of cached positions |
| `SCHEDULER_ENABLED` | `true` | Background TLE refresh and daily snapshot |
| `WS_BROADCAST_ENABLED` | `true` | WebSocket position broadcaster |
| `VITE_CESIUM_ION_TOKEN` | empty | Frontend: Cesium ion token |
| `VITE_LANDING_URL` | empty | Frontend: optional "Back" link in the header |

## API

| Method | Path | Description |
|---|---|---|
| GET | `/api/satellites` | Catalogue with metadata |
| GET | `/api/satellites/positions?time=` | Geodetic position of every satellite |
| GET | `/api/satellites/{norad_id}` | One satellite with its current position |
| GET | `/api/satellites/{norad_id}/orbit?duration=` | Ground-track points for the next `duration` minutes |
| GET | `/api/congestion?lat=&lon=&radius_km=&alt_min=&alt_max=` | Regional congestion metrics |
| GET | `/api/congestion/heatmap?alt_min=&alt_max=&grid_size=` | Global density grid |
| GET | `/api/congestion/altitude-distribution` | Counts per Starlink shell |
| POST | `/api/eo-analysis` | Field-of-view interference analysis |
| GET | `/api/eo-analysis/presets` | Available EO satellites |
| GET | `/api/history/snapshots?days=` | Daily statistics |
| WS | `/api/ws/positions` | Live position feed |
| GET | `/api/health` | Health and background-task status |

## Project layout

```
backend/app/services/propagation.py     vectorised SGP4, frame conversion, field-of-view geometry
backend/app/services/eo_analyzer.py     pass detection and interference model
backend/app/services/congestion_analyzer.py
backend/app/services/tle_fetcher.py     CelesTrak client and catalogue upsert
backend/app/routers/                    FastAPI endpoints
backend/tests/                          pytest suite (SQLite, frozen elements)
frontend/src/components/Globe.tsx       Cesium viewer
frontend/src/components/EOAnalyzer.tsx  EO analysis UI
deployment/                             Compose file, Caddyfile and notes for a single-VPS deployment
```

## Deployment

`deployment/` contains the Compose file, the Caddy reverse-proxy configuration and a setup script for running the whole stack on one Linux host behind automatic TLS. See `deployment/DEPLOYMENT.md`.

## Data sources and acknowledgements

- Orbital elements: [CelesTrak](https://celestrak.org)
- Propagation: [sgp4](https://pypi.org/project/sgp4/) and [Skyfield](https://rhodesmill.org/skyfield/)
- Globe: [CesiumJS](https://cesium.com/platform/cesiumjs/)

## License

MIT, see [LICENSE](LICENSE).
