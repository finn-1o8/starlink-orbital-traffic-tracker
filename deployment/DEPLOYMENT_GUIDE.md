# 🚀 Professional Deployment Guide - KarmanLabs

This guide walks you through deploying both the Tracker and Portfolio Landing repositories to your Hetzner server using a professional CI/CD setup.

---

## 📋 Overview

**Architecture:**
```
GitHub (Source of Truth)
    ├── finn-1o8/Tracker (backend + frontend)
    └── finn-1o8/portfolio-landing
    
         ↓ GitHub Actions CI/CD
         
GitHub Container Registry (ghcr.io)
    ├── tracker-backend:latest
    ├── tracker-frontend:latest
    └── portfolio-landing:latest
    
         ↓ Docker pull
    
Hetzner Server (/srv/karmanlabs/)
    └── Docker Compose orchestrates:
        ├── PostgreSQL + Redis
        ├── tracker-backend
        ├── tracker-frontend
        ├── landing
        └── Caddy (reverse proxy + SSL)
```

**Key Benefits:**
- ✅ No source code on server (only runs Docker images)
- ✅ Automatic deployments via GitHub Actions
- ✅ Zero downtime updates
- ✅ SSL certificates managed by Caddy
- ✅ Easy rollbacks
- ✅ Clean, professional setup

---

## 🎯 Prerequisites

1. **GitHub Account** with access to both repositories
2. **Hetzner Server** (already running at <SERVER_IP>)
3. **SSH Access** to the server
4. **Domain**: karmanlab.org configured in DNS

---

## 📝 Part 1: Setup Portfolio Landing Repo

### Step 1.1: Add Dockerfile to Portfolio Landing

In your `portfolio-landing` repository, create a `Dockerfile` at the root:

```bash
# If not already cloned, clone it
git clone https://github.com/finn-1o8/portfolio-landing.git
cd portfolio-landing

# Create Dockerfile (copy from deployment/portfolio-landing-Dockerfile.example)
# Or download from example
```

**The Dockerfile should use a multi-stage build** (Node.js build → Nginx serve) - see the example file provided.

### Step 1.2: Create GitHub Actions Workflow

Create `.github/workflows/deploy.yml` in portfolio-landing repo:

```bash
# Copy from deployment/portfolio-landing-github-actions.example.yml
# Or download from example
```

### Step 1.3: Configure GitHub Secrets

In your **portfolio-landing** repository on GitHub:

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Add these secrets:
   - `SSH_HOST`: `<SERVER_IP>`
   - `SSH_USER`: `root`
   - `SSH_PRIVATE_KEY`: Your private SSH key content

---

## 📝 Part 2: Setup Tracker Repo

The Tracker repo already has GitHub Actions workflows configured:
- `.github/workflows/deploy-backend.yml`
- `.github/workflows/deploy-frontend.yml`

### Step 2.1: Configure GitHub Secrets

In your **Tracker** repository on GitHub:

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Add the same secrets as above:
   - `SSH_HOST`: `<SERVER_IP>`
   - `SSH_USER`: `root`
   - `SSH_PRIVATE_KEY`: Your private SSH key content

### Step 2.2: Generate SSH Key (If Needed)

If you don't have an SSH key for GitHub Actions:

```bash
# On your local machine
ssh-keygen -t ed25519 -C "github-actions-karmanlabs"

# Save it (e.g., as ~/.ssh/github_actions)
# Copy the private key content
cat ~/.ssh/github_actions

# Copy the entire output including BEGIN/END lines to GitHub Secrets

# Add public key to Hetzner server
ssh-copy-id -i ~/.ssh/github_actions.pub root@<SERVER_IP>
```

---

## 📝 Part 3: Initial Server Setup

### Step 3.1: Backup Current Setup

```bash
ssh root@<SERVER_IP>

# Backup current setup
cd /opt/karmanlabs
docker compose down
tar -czf backup-$(date +%Y%m%d-%H%M%S).tar.gz .

# Save backup somewhere safe
mv backup-*.tar.gz /root/backups/
```

### Step 3.2: Run Server Setup Script

Download and run the automated setup script:

```bash
curl -fsSL https://raw.githubusercontent.com/finn-1o8/Tracker/main/deployment/setup-server.sh | bash
```

**Or manually:**

```bash
# Create project directory
mkdir -p /srv/karmanlabs
cd /srv/karmanlabs

# Download deployment files from GitHub
curl -L -o docker-compose.yml https://raw.githubusercontent.com/finn-1o8/Tracker/main/deployment/docker-compose.yml
curl -L -o Caddyfile https://raw.githubusercontent.com/finn-1o8/Tracker/main/deployment/Caddyfile
curl -L -o env.template https://raw.githubusercontent.com/finn-1o8/Tracker/main/deployment/env.template

# Create .env file
cp env.template .env
nano .env  # Edit with secure passwords

# Install Docker if needed
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
apt install -y docker-compose-plugin

# Setup firewall
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 443/udp
ufw --force enable
```

### Step 3.3: Configure .env File

Edit `/srv/karmanlabs/.env`:

```env
POSTGRES_DB=tracker_db
POSTGRES_USER=tracker_user
POSTGRES_PASSWORD=your_very_secure_password_here
```

**Generate a secure password:**
```bash
openssl rand -base64 32
```

### Step 3.4: Initial Deployment

```bash
cd /srv/karmanlabs

# Pull all images
docker compose pull

# Start everything
docker compose up -d

# Watch logs
docker compose logs -f
```

**First run will:**
1. Pull images from GHCR (you may need to login first)
2. Create volumes for database and Caddy
3. Initialize PostgreSQL database
4. Request SSL certificates from Let's Encrypt
5. Start all services

### Step 3.5: GHCR Login (If Images are Private)

If your GHCR images are private:

```bash
# On Hetzner server
docker login ghcr.io

# Username: finn-1o8
# Password: Personal Access Token with packages:read permission
```

Get token from: https://github.com/settings/tokens

---

## 📝 Part 4: Configure DNS

Make sure your DNS is configured:

```
Type: A
Name: @
Value: <SERVER_IP>
TTL: 3600

Type: A
Name: www
Value: <SERVER_IP>
TTL: 3600

Type: A
Name: tracker
Value: <SERVER_IP>
TTL: 3600
```

---

## 🎉 Part 5: How It Works Going Forward

### Automatic Deployments

**When you push to any repo main branch:**

1. GitHub Actions automatically triggers
2. Docker image is built
3. Image pushed to GHCR
4. Server is SSH'd into
5. `docker compose pull` runs
6. `docker compose up -d` runs
7. Zero downtime update (Caddy handles gracefully)

**Complete workflow:**
```
Developer pushes code
    ↓
GitHub Actions builds Docker image
    ↓
Image pushed to ghcr.io
    ↓
GitHub Actions SSHs to server
    ↓
docker compose pull <service>
    ↓
docker compose up -d <service>
    ↓
Site updates (~30 seconds)
```

### Manual Server Management

**Check status:**
```bash
cd /srv/karmanlabs
docker compose ps
```

**View logs:**
```bash
docker compose logs -f
docker compose logs -f caddy
docker compose logs -f tracker-backend
```

**Restart services:**
```bash
docker compose restart
docker compose restart tracker-backend
```

**Update all images:**
```bash
docker compose pull
docker compose up -d
```

**Full reset (careful!):**
```bash
docker compose down -v  # Removes volumes too
docker compose up -d --force-recreate
```

**Backup database:**
```bash
docker exec karmanlabs-postgres-1 pg_dump -U tracker_user tracker_db > backup.sql
```

---

## 🔍 Troubleshooting

### Images Won't Pull (Private GHCR)

**Problem:** `Error pulling image: unauthorized`

**Solution:**
```bash
docker login ghcr.io
# Or configure in docker-compose.yml to use personal access token
```

### SSL Certificate Issues

**Problem:** Caddy can't get certificates

**Solutions:**
1. Check DNS is pointing to server
2. Port 80 must be open
3. Wait 2-3 minutes for first cert request
4. Check logs: `docker compose logs caddy`

### Database Connection Issues

**Problem:** Backend can't connect to database

**Solutions:**
1. Check postgres is healthy: `docker compose ps postgres`
2. Check .env file has correct credentials
3. Check backend logs: `docker compose logs tracker-backend`

### Frontend Can't Reach API

**Problem:** 404 on /api endpoints

**Solutions:**
1. Check Caddyfile has /api* route
2. Check tracker-backend is running
3. Check Caddy logs: `docker compose logs caddy`

### Port Already in Use

**Problem:** Port 80 or 443 already in use

**Solutions:**
1. Stop old services: `cd /opt/karmanlabs && docker compose down`
2. Or kill process: `lsof -ti:80 | xargs kill -9`

---

## 📊 Monitoring & Maintenance

### Regular Maintenance

**Weekly:**
- Check logs for errors
- Verify backups are running

**Monthly:**
- Update Docker images: `docker compose pull && docker compose up -d`
- Check SSL certificates: `docker compose logs caddy | grep certificate`

**Quarterly:**
- Review and update dependencies
- Security audit
- Database cleanup if needed

### Monitoring Tools (Optional)

Add to docker-compose.yml:
```yaml
uptime-kuma:
  image: louislam/uptime-kuma:1
  volumes:
    - uptime_data:/app/data
  ports:
    - "3001:3001"
  networks:
    - web
  restart: unless-stopped
```

Access at: http://<SERVER_IP>:3001

---

## 🔒 Security Best Practices

1. **Strong passwords** in .env file
2. **Firewall enabled** (ufw)
3. **SSH key only** (disable password auth)
4. **Regular updates** for Docker images
5. **GitHub Secrets** for sensitive data
6. **Private GHCR** if needed
7. **Database backups** automated
8. **Rate limiting** on API (can add to Caddy)

---

## 🎓 Reference

### File Locations

**On Server:**
- `/srv/karmanlabs/` - Main deployment directory
- `/srv/karmanlabs/docker-compose.yml` - Service definitions
- `/srv/karmanlabs/Caddyfile` - Reverse proxy config
- `/srv/karmanlabs/.env` - Environment variables

**In Git Repos:**
- Tracker: `.github/workflows/deploy-backend.yml`
- Tracker: `.github/workflows/deploy-frontend.yml`
- Landing: `.github/workflows/deploy.yml`
- Landing: `Dockerfile`

### Important URLs

- Main site: https://karmanlab.org
- Tracker (path): https://karmanlab.org/tracker
- Tracker (subdomain): https://tracker.karmanlab.org
- API: https://karmanlab.org/api
- API docs: https://karmanlab.org/api/docs

### GitHub Secrets Required

For **both** repositories:
- `SSH_HOST`: Server IP
- `SSH_USER`: Username (usually root)
- `SSH_PRIVATE_KEY`: Private SSH key content

---

## ✅ Deployment Checklist

- [ ] Portfolio Landing has Dockerfile
- [ ] Portfolio Landing has GitHub Actions workflow
- [ ] Tracker has both GitHub Actions workflows
- [ ] All repos have GitHub Secrets configured
- [ ] Server has /srv/karmanlabs set up
- [ ] docker-compose.yml downloaded
- [ ] Caddyfile downloaded
- [ ] .env file created with secure passwords
- [ ] DNS configured correctly
- [ ] Ports 80, 443 open in firewall
- [ ] GHCR login configured (if private)
- [ ] Initial `docker compose up -d` run
- [ ] SSL certificates obtained
- [ ] All services healthy
- [ ] Main site loads
- [ ] Tracker loads
- [ ] API responds
- [ ] Test auto-deployment by pushing a commit

---

## 🆘 Need Help?

1. Check logs: `docker compose logs -f`
2. Check service status: `docker compose ps`
3. Check Caddy logs: `docker compose logs caddy`
4. Review DEPLOYMENT-HISTORY.md for known issues
5. Check GitHub Actions logs for deployment issues

---

**Last Updated:** January 2025  
**Maintained By:** KarmanLabs Team

