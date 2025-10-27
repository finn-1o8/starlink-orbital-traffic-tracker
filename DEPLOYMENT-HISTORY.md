# 🚀 Deployment History - karmanlab.org

**Deployment Date:** October 27, 2025  
**Domain:** https://karmanlab.org  
**Server:** Hetzner CX23 VPS (Helsinki)  
**Server IP:** 135.181.254.130  
**Status:** ✅ Live & Production Ready

---

## 📋 Overview

Successfully deployed Orbital Traffic Impact Analyzer to production on Hetzner infrastructure with Docker Compose, featuring 8,570+ Starlink satellites with real-time 3D visualization.

---

## 🏗️ Infrastructure Setup

### Server Specifications
- **Provider:** Hetzner Cloud
- **Type:** CX23 VPS
- **Location:** Helsinki, Finland
- **OS:** Ubuntu 24.04.1 LTS
- **Pre-installed:** Docker CE
- **SSH:** Configured with local SSH key

### Domain Configuration
- **Domain:** karmanlab.org (registered separately)
- **DNS Records:**
  ```
  Type: A
  Name: @
  Value: 135.181.254.130
  TTL: 3600

  Type: A
  Name: www
  Value: 135.181.254.130
  TTL: 3600
  ```

---

## 🔧 Deployment Process

### 1. Initial Server Setup
```bash
apt update && apt upgrade -y
apt install -y git docker-compose nano curl ufw
```

### 2. Firewall Configuration
```bash
ufw allow 22/tcp   # SSH
ufw allow 80/tcp   # HTTP
ufw allow 443/tcp  # HTTPS
ufw --force enable
```

### 3. Project Deployment
- Cloned GitHub repository to `/opt/karmanlabs`
- Created production environment files (not in git)
- Built Docker containers with production configurations

### 4. SSL Certificate
- Obtained Let's Encrypt SSL certificate using Certbot
- Certificate valid for: karmanlab.org & www.karmanlab.org
- Expires: January 25, 2026
- Auto-renewal: Configured via Certbot container

---

## 🐳 Docker Architecture

### Services Running

**Production Stack (`docker-compose.prod.yml`):**

1. **PostgreSQL (TimescaleDB)**
   - Image: `timescale/timescaledb:latest-pg15`
   - Port: 5432 (internal only)
   - Volume: `postgres_data`
   - Health checks enabled

2. **Redis**
   - Image: `redis:7-alpine`
   - Port: 6379 (internal only)
   - Volume: `redis_data`
   - Used for position caching

3. **Backend (FastAPI)**
   - Build: `./backend`
   - Port: 8000 (internal only)
   - Networks: internal, web
   - Environment: Production settings from `backend/.env`

4. **Frontend (React + Nginx)**
   - Build: `./frontend` (Dockerfile.prod)
   - Multi-stage build (Node.js → Nginx)
   - Port: 80 (internal only)
   - Network: web

5. **Nginx (Reverse Proxy)**
   - Image: `nginx:alpine`
   - Ports: 80, 443 (public)
   - SSL termination
   - Routes traffic to backend & frontend

### Network Architecture
- **Internal network:** Backend ↔ Database & Redis
- **Web network:** Nginx ↔ Frontend & Backend
- **Public access:** Only through Nginx (ports 80/443)

---

## 🔒 Security Configuration

### Environment Variables

**Backend (`/opt/karmanlabs/backend/.env`):**
```env
DATABASE_URL=postgresql://orbital_user:PASSWORD@postgres:5432/orbital_tracker
REDIS_URL=redis://redis:6379/0
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=https://karmanlab.org,http://karmanlab.org
TLE_UPDATE_INTERVAL_HOURS=6
POSITION_CACHE_SECONDS=30
ENVIRONMENT=production
DEBUG=false
```

**Frontend (`/opt/karmanlabs/frontend/.env`):**
```env
VITE_API_URL=/api
VITE_WS_URL=wss://karmanlab.org/api
VITE_CESIUM_ION_TOKEN=<token>
```

### SSL/TLS Configuration
- **Protocols:** TLSv1.2, TLSv1.3
- **Certificate:** Let's Encrypt
- **Auto-renewal:** Certbot container checks every 12 hours
- **Certificate location:** `/var/lib/docker/volumes/karmanlabs_certbot_conf/_data/`

### Firewall Rules
- SSH (22): Open
- HTTP (80): Open (redirects to HTTPS)
- HTTPS (443): Open
- All other ports: Blocked by default

---

## ⚠️ Key Issues Encountered & Solutions

### Issue 1: Environment Variables Not Building into Frontend
**Problem:** Frontend built with wrong API URLs (hardcoded HTTPS before SSL was ready)

**Root Cause:** Vite requires environment variables at build time, not runtime

**Solution:** 
- Use relative URLs (`/api`) instead of absolute URLs for API
- Use `wss://karmanlab.org/api` for WebSocket (requires domain-specific)
- Rebuild frontend container after any .env changes

**Command:**
```bash
docker-compose -f docker-compose.prod.yml build --no-cache frontend
docker-compose -f docker-compose.prod.yml up -d frontend
```

### Issue 2: Docker Compose 'ContainerConfig' Error
**Problem:** `KeyError: 'ContainerConfig'` when trying to recreate containers

**Root Cause:** Docker Compose 1.29.2 bug with corrupted container metadata

**Solution:**
- Remove containers manually before recreating:
```bash
docker ps -a --filter "name=SERVICE_NAME" -q | xargs docker rm -f
docker-compose -f docker-compose.prod.yml up -d SERVICE_NAME
```

### Issue 3: SSL Certificates Not Visible to Nginx
**Problem:** Nginx couldn't find SSL certificates despite successful Certbot run

**Root Cause:** Certificates were in `/opt/karmanlabs/certbot_conf/` but Docker volume was separate

**Solution:**
```bash
cp -r /opt/karmanlabs/certbot_conf/* /var/lib/docker/volumes/karmanlabs_certbot_conf/_data/
docker restart karmanlabs_nginx_1
```

### Issue 4: PostgreSQL Container Stopped
**Problem:** Database exited unexpectedly, causing 500 errors

**Root Cause:** Container stopped during rebuild process

**Solution:**
```bash
docker ps -a --filter "name=postgres" -q | xargs docker rm -f
docker-compose -f docker-compose.prod.yml up -d postgres
docker-compose -f docker-compose.prod.yml restart backend
```

### Issue 5: WebSocket Connection Failures After SSL
**Problem:** WebSocket used `ws://` (insecure) on HTTPS site

**Root Cause:** Frontend .env still had HTTP WebSocket URL

**Solution:**
- Changed `ws://` to `wss://` in frontend/.env
- Rebuilt frontend to use secure WebSocket

---

## 📝 Important Notes for Future

### 1. Environment Files Are NOT in Git
- `.env` files are in `.gitignore` for security
- Must manually create on server:
  - `/opt/karmanlabs/backend/.env`
  - `/opt/karmanlabs/frontend/.env`

### 2. Frontend Requires Rebuild for Config Changes
- Vite bundles environment variables at **build time**
- Any change to `frontend/.env` requires:
  ```bash
  docker-compose -f docker-compose.prod.yml build --no-cache frontend
  docker-compose -f docker-compose.prod.yml up -d frontend
  ```

### 3. SSL Certificate Renewal
- Auto-renewal is configured via Certbot container
- Manual renewal if needed:
  ```bash
  docker-compose -f docker-compose.prod.yml stop nginx
  docker run -it --rm -v /opt/karmanlabs/certbot_conf:/etc/letsencrypt \
    -v /opt/karmanlabs/certbot_www:/var/www/certbot -p 80:80 \
    certbot/certbot certonly --standalone -d karmanlab.org -d www.karmanlab.org \
    --email finanwmkl@gmail.com --agree-tos --no-eff-email
  cp -r /opt/karmanlabs/certbot_conf/* /var/lib/docker/volumes/karmanlabs_certbot_conf/_data/
  docker-compose -f docker-compose.prod.yml start nginx
  ```

### 4. Database Persistence
- Database stored in Docker volume: `karmanlabs_postgres_data`
- Volume persists even if containers are removed
- **Backup command:**
  ```bash
  docker exec karmanlabs_postgres_1 pg_dump -U orbital_user orbital_tracker > backup.sql
  ```

### 5. IP Address vs Domain
- **Always use domain:** https://karmanlab.org
- **IP address (135.181.254.130):** Shows SSL warning (expected - certificate is for domain only)
- This is normal behavior; users should use domain name

### 6. Container Networking
- Backend connects to database using hostname `postgres` (Docker DNS)
- Frontend uses relative path `/api` (proxied by Nginx)
- WebSocket requires explicit domain: `wss://karmanlab.org/api`

### 7. Common Commands

**View logs:**
```bash
docker-compose -f docker-compose.prod.yml logs -f
docker-compose -f docker-compose.prod.yml logs -f backend  # Specific service
```

**Restart services:**
```bash
docker-compose -f docker-compose.prod.yml restart
docker-compose -f docker-compose.prod.yml restart backend  # Specific service
```

**Check status:**
```bash
docker-compose -f docker-compose.prod.yml ps
docker ps  # All running containers
```

**Update application:**
```bash
cd /opt/karmanlabs
git pull
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d --build
```

**Clean up Docker:**
```bash
docker system prune -a  # Remove unused images/containers
```

---

## 🎯 Production Checklist

- [x] Server provisioned and secured
- [x] Domain DNS configured
- [x] SSL certificate installed
- [x] Firewall configured
- [x] Docker containers running
- [x] Database initialized with 8,570+ satellites
- [x] HTTPS redirect working
- [x] WebSocket connections secured
- [x] API responding correctly
- [x] Frontend loading with satellites
- [x] Auto-renewal configured for SSL

---

## 📊 Current Performance

- **Satellites tracked:** 8,570+ Starlink
- **TLE update frequency:** Every 6 hours
- **Position cache:** 30 seconds
- **API response time:** <500ms
- **Frontend load time:** ~3 seconds
- **SSL certificate expiry:** January 25, 2026

---

## 🔗 Useful Links

- **Live Site:** https://karmanlab.org
- **GitHub Repository:** https://github.com/finn-1o8/Tracker
- **Server Location:** Hetzner Helsinki
- **SSL Certificate Provider:** Let's Encrypt
- **Cesium Ion:** https://ion.cesium.com/

---

## 📞 Maintenance Contacts

- **Domain Registrar:** [Where karmanlab.org was purchased]
- **Server Provider:** Hetzner Cloud
- **Email for SSL notifications:** finanwmkl@gmail.com

---

**Last Updated:** October 27, 2025  
**Deployed By:** Esrom  
**Deployment Status:** ✅ Production Ready

