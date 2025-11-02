# 🚀 Deployment Guide

Complete deployment guide for the Orbital Traffic Impact Analyzer on Hetzner server.

## 📋 Overview

**Server:** Hetzner 135.181.254.130  
**Deployment Directory:** `/srv/karmanlabs`  
**Domain:** https://karmanlab.org/tracker

## 🏗️ Architecture

```
Browser → Caddy (Reverse Proxy + SSL) → Docker Services
                                       ├── tracker-frontend (nginx)
                                       ├── tracker-backend (FastAPI)
                                       ├── landing (static)
                                       ├── postgres (TimescaleDB)
                                       └── redis (cache)
```

## ✅ Current Setup (Working)

### Key Configuration Decisions

1. **Path-Based Routing:** Tracker deployed at `/tracker` path (not subdomain)
2. **Vite Base Path:** `base: '/tracker/'` in `vite.config.ts`
3. **Caddy Stripping:** `uri strip_prefix /tracker` to forward clean paths to container
4. **Nginx Alias:** Maps `/cesium/*` requests to `/tracker/cesium/*` in container

### Why This Works

**The Problem:**
- Cesium assets are injected as static files by `vite-plugin-cesium`
- When built with `base: '/tracker/'`, assets reference `/tracker/cesium/*`
- Browser requests `/tracker/cesium/widgets.css`
- Caddy strips `/tracker` → forwards `/cesium/widgets.css` to nginx
- But Cesium files are at `/usr/share/nginx/html/tracker/cesium/` in container

**The Solution:**
```nginx
# Nginx location block maps /cesium/* → /tracker/cesium/*
location ~ ^/cesium(/.*)?$ {
    alias /usr/share/nginx/html/tracker/cesium$1;
}
```

### Complete Request Flow

```
1. Browser: https://karmanlab.org/tracker/cesium/Cesium.js
2. Caddy: Strips /tracker → forwards /cesium/Cesium.js
3. Nginx: Alias maps to /usr/share/nginx/html/tracker/cesium/Cesium.js
4. Response: Correct file with proper MIME type ✅
```

## 📁 Essential Files

### Server Files (in `/srv/karmanlabs/`)

- `docker-compose.yml` - Service orchestration
- `Caddyfile` - Reverse proxy configuration
- `.env` - Environment variables (not in repo)

### Repository Files

- `frontend/vite.config.ts` - Has `base: '/tracker/'`
- `frontend/Dockerfile.prod` - Nginx config with `/cesium` alias
- `deployment/docker-compose.yml` - Server docker-compose
- `deployment/Caddyfile` - Server Caddyfile
- `.github/workflows/deploy-*.yml` - CI/CD pipelines

## 🔧 Configuration Details

### Vite Config
```typescript
export default defineConfig({
  base: '/tracker/',  // All asset paths prefixed
  plugins: [react(), cesium()],
})
```

### Caddyfile
```caddy
handle /tracker* {
    uri strip_prefix /tracker  # Remove /tracker before forwarding
    reverse_proxy tracker-frontend:80
}
```

### Nginx (in Dockerfile.prod)
```nginx
# Map /cesium/* to /tracker/cesium/* in container
location ~ ^/cesium(/.*)?$ {
    alias /usr/share/nginx/html/tracker/cesium$1;
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

## 🚀 Deployment Process

### Initial Setup

```bash
# On server
cd /srv/karmanlabs
# Copy docker-compose.yml and Caddyfile from deployment/
# Create .env file from env.template
docker compose up -d
```

### Update Frontend

```bash
# SSH to server
ssh root@135.181.254.130

# Update code and rebuild
cd /opt/karmanlabs/frontend
git pull origin main
docker build -f Dockerfile.prod -t karmanlabs_tracker-frontend:latest .

# Restart service
cd /srv/karmanlabs
docker compose restart tracker-frontend
```

### Update Backend

```bash
# SSH to server
cd /opt/karmanlabs/backend  # or wherever backend code is
git pull origin main
docker build -t karmanlabs_tracker-backend:latest .
cd /srv/karmanlabs
docker compose restart tracker-backend
```

## 🔍 Troubleshooting

### Assets Return 404

**Check nginx config:**
```bash
docker exec karmanlabs-tracker-frontend-1 cat /etc/nginx/conf.d/default.conf | grep cesium
```

**Verify Cesium files exist:**
```bash
docker exec karmanlabs-tracker-frontend-1 ls -la /usr/share/nginx/html/tracker/cesium/
```

### 403 Forbidden Errors

**Check nginx root:**
```bash
docker exec karmanlabs-tracker-frontend-1 cat /etc/nginx/conf.d/default.conf | grep root
```
Should be: `root /usr/share/nginx/html;` (NOT `/tracker`)

### MIME Type Errors

**Verify assets are served correctly:**
```bash
curl -I https://karmanlab.org/tracker/cesium/Cesium.js
```
Should return `Content-Type: application/javascript`

## 📝 Lessons Learned

1. **Path-Based Routing is Complex:** Subdomains are cleaner, but path-based works with proper nginx aliasing
2. **Cesium Assets are Special:** They're static files, not bundled, requiring special handling
3. **Nginx Alias is Key:** Without the alias, `/cesium/*` requests fail after prefix stripping
4. **Order Matters:** Location blocks in nginx must be ordered correctly (more specific first)

## 🔗 Related Files

- `frontend/vite.config.ts` - Base path configuration
- `frontend/Dockerfile.prod` - Nginx configuration
- `deployment/Caddyfile` - Reverse proxy setup
- `deployment/docker-compose.yml` - Service definitions

---

**Last Updated:** November 2, 2025  
**Status:** ✅ Production-ready and working

