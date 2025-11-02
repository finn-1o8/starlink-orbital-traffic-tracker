# 🚀 Deployment Files

This directory contains all files needed to deploy your Tracker and Portfolio Landing applications to your Hetzner server using a professional CI/CD setup.

---

## 📁 Files Overview

### Core Deployment Files

| File | Description | Usage |
|------|-------------|-------|
| `docker-compose.yml` | Main orchestration file for all services | Place in `/srv/karmanlabs/` on server |
| `Caddyfile` | Reverse proxy and SSL configuration | Place in `/srv/karmanlabs/` on server |
| `env.template` | Environment variables template | Copy to `.env` and customize |
| `setup-server.sh` | Automated server setup script | Run on Hetzner server |
| `DEPLOYMENT_GUIDE.md` | Complete deployment instructions | Read this first |
| `QUICK_START.md` | Fast track deployment guide | For quick setup |

### Example Files (Portfolio Landing)

| File | Description | Usage |
|------|-------------|-------|
| `portfolio-landing-Dockerfile.example` | Dockerfile template for landing page | Copy to portfolio-landing repo root |
| `portfolio-landing-github-actions.example.yml` | GitHub Actions workflow | Copy to `.github/workflows/` in portfolio-landing repo |

### GitHub Actions (Tracker)

Already configured in this repo:
- `.github/workflows/deploy-backend.yml` - Backend deployment
- `.github/workflows/deploy-frontend.yml` - Frontend deployment

---

## 🏗️ Architecture

```
GitHub Repos
    ├── Tracker (this repo)
    │   ├── Backend Dockerfile
    │   ├── Frontend Dockerfile
    │   └── GitHub Actions → deploys to ghcr.io
    │
    └── Portfolio Landing
        ├── Dockerfile
        └── GitHub Actions → deploys to ghcr.io

              ↓ Docker images

GitHub Container Registry (ghcr.io)
    ├── tracker-backend:latest
    ├── tracker-frontend:latest
    └── portfolio-landing:latest

              ↓ docker compose pull

Hetzner Server (/srv/karmanlabs/)
    ├── docker-compose.yml
    ├── Caddyfile
    ├── .env
    │
    └── Docker Compose Services:
        ├── postgres (database)
        ├── redis (cache)
        ├── tracker-backend
        ├── tracker-frontend
        ├── landing
        └── caddy (reverse proxy + SSL)
```

---

## 🚀 Quick Deployment

### 1. Setup Portfolio Landing

```bash
cd /path/to/portfolio-landing

# Add Dockerfile
cp ../Tracker/deployment/portfolio-landing-Dockerfile.example ./Dockerfile

# Add GitHub Actions
mkdir -p .github/workflows
cp ../Tracker/deployment/portfolio-landing-github-actions.example.yml .github/workflows/deploy.yml

git add .
git commit -m "Add Docker and deployment config"
git push
```

### 2. Configure GitHub Secrets

In both repositories (Tracker and portfolio-landing):

1. Go to Settings → Secrets → Actions
2. Add:
   - `SSH_HOST`: `135.181.254.130`
   - `SSH_USER`: `root`
   - `SSH_PRIVATE_KEY`: Your SSH private key

### 3. Deploy to Server

```bash
# SSH to server
ssh root@135.181.254.130

# Run setup
bash <(curl -fsSL https://raw.githubusercontent.com/finn-1o8/Tracker/main/deployment/setup-server.sh)
```

### 4. Done!

Visit:
- https://karmanlab.org
- https://tracker.karmanlab.org

---

## 📖 Documentation

- **[QUICK_START.md](./QUICK_START.md)** - Get deployed in 15 minutes
- **[DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)** - Complete guide with troubleshooting

---

## 🔧 Customization

### Change Service Names

Edit `docker-compose.yml` and update service names as needed.

### Add New Services

Add to `docker-compose.yml` and update Caddyfile routing rules.

### Modify Caddy Configuration

Edit `Caddyfile`:
- Add routes
- Change security headers
- Modify SSL settings

### Environment Variables

Edit `.env` file on server:
```bash
cd /srv/karmanlabs
nano .env
docker compose restart
```

---

## 🔍 Verification

Check deployment:

```bash
# On server
cd /srv/karmanlabs
docker compose ps          # All services running?
docker compose logs -f     # Any errors?
```

Test endpoints:
```bash
curl https://karmanlab.org
curl https://tracker.karmanlab.org
curl https://karmanlab.org/api/health
```

---

## 🆘 Troubleshooting

See [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md#-troubleshooting) for common issues.

---

## 📝 Maintenance

### Update Images

```bash
cd /srv/karmanlabs
docker compose pull
docker compose up -d
```

### Backup Database

```bash
docker exec karmanlabs-postgres-1 pg_dump -U tracker_user tracker_db > backup.sql
```

### View Logs

```bash
docker compose logs -f caddy
docker compose logs -f tracker-backend
```

---

## 🎯 Goals Achieved

✅ **No source code on server** - only runs Docker images  
✅ **Automatic deployments** via GitHub Actions  
✅ **Zero downtime** updates  
✅ **Automatic SSL** with Caddy  
✅ **Clean architecture** - easy to maintain  
✅ **Professional CI/CD** - industry best practices  

---

**Questions?** Check the full [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) or review server logs.

