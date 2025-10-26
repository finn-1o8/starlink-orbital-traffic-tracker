# 🧪 Testing Guide

## Quick Test Setup (5 minutes)

### Prerequisites
- Docker Desktop installed and running
- A web browser
- Internet connection (for TLE data)

---

## Step-by-Step Testing Instructions

### 1️⃣ Get Your FREE Cesium Ion Token

This is the **ONLY** API key you need!

1. Visit **https://ion.cesium.com/**
2. Create a free account (takes 1 minute)
3. Navigate to **"Access Tokens"** in the dashboard
4. Copy your **default access token** (starts with "eyJhb...")

---

### 2️⃣ Create Frontend Environment File

Create a file named `.env` in the `frontend` folder:

**Windows (PowerShell):**
```powershell
cd frontend
@"
VITE_API_URL=http://localhost:8000/api
VITE_WS_URL=ws://localhost:8000/api
VITE_CESIUM_ION_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiI3ZTNlMTc0OC1iYjkzLTRkZWYtOTJmZS1iMGE3NTJhMjMwMzciLCJpZCI6MzU0MDEyLCJpYXQiOjE3NjE0MzgxMTR9.FHPtMVfJrwVPrU8BfSsVaxGbfIWorLrmbSS6z683-as
"@ | Out-File -FilePath .env -Encoding ASCII
```

**Mac/Linux (Terminal):**
```bash
cd frontend
cat > .env << EOF
VITE_API_URL=http://localhost:8000/api
VITE_WS_URL=ws://localhost:8000/api
VITE_CESIUM_ION_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiI3ZTNlMTc0OC1iYjkzLTRkZWYtOTJmZS1iMGE3NTJhMjMwMzciLCJpZCI6MzU0MDEyLCJpYXQiOjE3NjE0MzgxMTR9.FHPtMVfJrwVPrU8BfSsVaxGbfIWorLrmbSS6z683-as
EOF
```

**Or manually create `frontend/.env`:**
```env
VITE_API_URL=http://localhost:8000/api
VITE_WS_URL=ws://localhost:8000/api
VITE_CESIUM_ION_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiI3ZTNlMTc0OC1iYjkzLTRkZWYtOTJmZS1iMGE3NTJhMjMwMzciLCJpZCI6MzU0MDEyLCJpYXQiOjE3NjE0MzgxMTR9.FHPtMVfJrwVPrU8BfSsVaxGbfIWorLrmbSS6z683-as
```

⚠️ **IMPORTANT:** Replace `YOUR_TOKEN_HERE` with your actual Cesium token!

---

### 3️⃣ Start All Services with Docker

From the project root directory:

```bash
docker-compose up -d
```

This will start:
- ✅ PostgreSQL database
- ✅ Redis cache
- ✅ Backend API
- ✅ Frontend app

**First-time startup takes 2-3 minutes** as it downloads TLE data for 1000+ satellites.

---

### 4️⃣ Monitor Startup (Optional but Recommended)

Watch the backend logs to see when TLE data is ready:

```bash
docker-compose logs -f backend
```

Look for this message:
```
✅ TLE update completed successfully
✅ Updated XXXX satellites in database
```

Press `Ctrl+C` to exit logs (services keep running).

---

### 5️⃣ Verify Backend is Running

**Test the health endpoint:**

```bash
curl http://localhost:8000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "scheduler_running": true
}
```

**Check satellite count:**

```bash
curl http://localhost:8000/api/satellites | jq '. | length'
```

Should return a number like `1000` or more.

---

### 6️⃣ Open the Application

Open your browser and go to:

**🌐 http://localhost:3000**

You should see:
- 🌍 A beautiful 3D globe
- 🛰️ Thousands of Starlink satellites orbiting in real-time
- 📊 Sidebar with satellite list
- ⚡ Live position updates every 30 seconds

---

## 🎮 Testing Features

### Basic Interactions

1. **Rotate the Globe**
   - Left-click + drag to rotate
   - Right-click + drag to pan
   - Scroll to zoom in/out

2. **Select a Satellite**
   - Click on any satellite point
   - See its orbit path appear in cyan
   - View details in the sidebar

3. **Filter by Altitude**
   - Use the sidebar dropdown
   - Filter by altitude bands:
     - 🔴 Low (340-360km)
     - 🔵 Medium (500-570km)
     - 🟡 High (1100-1325km)

4. **Search Satellites**
   - Use the search box in sidebar
   - Search by name or NORAD ID

5. **View Analytics**
   - Click "Analytics" in the header
   - See constellation statistics
   - View altitude distribution charts

6. **EO Analysis**
   - Click "EO Analysis" button (top-right)
   - Select an Earth Observation satellite preset
   - Choose a target region
   - Analyze interference from Starlink

---

## 🧪 API Testing

### Test via Browser

Open these URLs in your browser:

- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/api/health
- **All Satellites:** http://localhost:8000/api/satellites
- **Current Positions:** http://localhost:8000/api/satellites/positions

### Test via curl

**Get satellite positions:**
```bash
curl http://localhost:8000/api/satellites/positions
```

**Analyze congestion over New York:**
```bash
curl "http://localhost:8000/api/congestion?lat=40.7128&lon=-74.0060&radius_km=500&alt_min=500&alt_max=600"
```

**Get orbit path for a specific satellite:**
```bash
curl http://localhost:8000/api/satellites/44713/orbit?duration=90
```

---

## 🐛 Troubleshooting

### Issue: "Satellites not appearing"

**Solution:**
```bash
# Check if TLE data was fetched
docker-compose logs backend | grep "TLE"

# Wait 2-3 minutes on first startup
# Or manually trigger TLE fetch by restarting backend
docker-compose restart backend
```

### Issue: "Cesium/Globe not loading"

**Solution:**
1. Open browser Developer Console (F12)
2. Look for errors about "Ion token"
3. Verify your token in `frontend/.env`
4. Make sure there are no extra spaces or quotes
5. Restart frontend:
   ```bash
   docker-compose restart frontend
   ```

### Issue: "Cannot connect to backend"

**Solution:**
```bash
# Check if all services are running
docker-compose ps

# Restart all services
docker-compose restart

# Or full reset
docker-compose down
docker-compose up -d
```

### Issue: "Database connection error"

**Solution:**
```bash
# Reset database and start fresh
docker-compose down -v
docker-compose up -d
```

### Issue: "Port already in use"

If ports 3000, 8000, 5432, or 6379 are taken:

1. Edit `docker-compose.yml`
2. Change port mappings (e.g., `3001:3000` instead of `3000:3000`)
3. Update `frontend/.env` with new backend port

---

## 📊 Expected Performance

- **Backend Response Time:** < 500ms
- **Satellite Position Calculation:** 1000+ satellites in < 5 seconds
- **Frontend FPS:** 30+ with 1000+ satellites rendered
- **WebSocket Updates:** Every 30 seconds
- **TLE Auto-Update:** Every 6 hours

---

## 🔄 Development Mode

If you want to develop and see live changes:

### Backend (Python)
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend (React)
```bash
cd frontend
npm install
npm run dev
```

---

## 🧹 Cleanup

When you're done testing:

```bash
# Stop services (keep data)
docker-compose down

# Stop services and remove all data
docker-compose down -v
```

---

## ✅ What to Test

### Checklist for Complete Testing

- [ ] 3D globe loads successfully
- [ ] Satellites appear on the globe
- [ ] Can click and select satellites
- [ ] Orbit paths display correctly
- [ ] Sidebar filters work (altitude, search)
- [ ] Analytics dashboard opens
- [ ] WebSocket connection shows "Connected" (green dot)
- [ ] API endpoints respond correctly
- [ ] EO Analysis tool works
- [ ] Congestion analysis returns data

---

## 📚 Additional Resources

- **API Documentation:** http://localhost:8000/docs
- **Full README:** [README.md](README.md)
- **Quick Start:** [QUICKSTART.md](QUICKSTART.md)

---

## 🆘 Need Help?

If you encounter issues not covered here:

1. Check logs: `docker-compose logs`
2. Verify all services are healthy: `docker-compose ps`
3. Try a fresh start: `docker-compose down -v && docker-compose up -d`
4. Review error messages in browser console (F12)

---

**Happy Testing! 🚀🛰️**

