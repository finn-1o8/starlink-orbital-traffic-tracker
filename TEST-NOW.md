# 🚀 START TESTING IN 3 MINUTES

## TL;DR - Super Quick Start

### 1. Get FREE Cesium Token (1 minute)
👉 **https://ion.cesium.com/** → Sign up → Copy your token

### 2. Run Setup Script

**Windows PowerShell:**
```powershell
.\create-env.ps1
```

**Mac/Linux Terminal:**
```bash
chmod +x create-env.sh
./create-env.sh
```

**Or manually create `frontend/.env`:**
```env
VITE_API_URL=http://localhost:8000/api
VITE_WS_URL=ws://localhost:8000/api
VITE_CESIUM_ION_TOKEN=your_cesium_token_here
```

### 3. Start Everything
```bash
docker-compose up -d
```

### 4. Wait & Watch (optional)
```bash
docker-compose logs -f backend
# Wait for: "TLE update completed successfully"
```

### 5. Open Browser
**🌐 http://localhost:3000**

---

## ✅ You're Done!

You should now see:
- 🌍 3D globe
- 🛰️ 1000+ Starlink satellites
- 📊 Live tracking

---

## 🐛 Problems?

**Satellites not showing?**
```bash
docker-compose restart backend
# Wait 2-3 minutes
```

**Globe black/blank?**
- Check your Cesium token in `frontend/.env`
- Make sure there are no extra spaces
- Restart: `docker-compose restart frontend`

**Port conflicts?**
```bash
docker-compose down
# Edit docker-compose.yml to change ports
docker-compose up -d
```

---

## 📖 More Details

See **[TESTING.md](TESTING.md)** for comprehensive testing guide.

---

## 🔑 About API Keys

**✅ Required:**
- Cesium Ion Token (FREE) - for 3D globe visualization

**❌ NOT Required:**
- No CelesTrak API key (public data)
- No Space-Track.org account
- No database passwords (handled by Docker)
- No other API keys

---

**That's it! Happy testing! 🎉**

