# 🎯 Next Steps - Deploy Your Site

You now have everything you need for a professional deployment! Follow these steps to get your site live.

---

## ⚡ Quick Start (15 minutes)

### Step 1: Configure GitHub Secrets

**In BOTH repositories** (Tracker and portfolio-landing):

1. Open GitHub → Your Repo → **Settings**
2. Go to **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add these three secrets:

```
Name: SSH_HOST
Value: 135.181.254.130

Name: SSH_USER  
Value: root

Name: SSH_PRIVATE_KEY
Value: <your SSH private key content>
```

**To get SSH private key:**
```bash
# If you don't have one, create it
ssh-keygen -t ed25519 -C "karmanlabs-deployment"

# Copy the private key content
cat ~/.ssh/id_ed25519

# Copy everything including "BEGIN" and "END" lines
```

**Add public key to server:**
```bash
ssh-copy-id -i ~/.ssh/id_ed25519.pub root@135.181.254.130
```

---

### Step 2: Setup Portfolio Landing Repo

**If you haven't already:**

```bash
# Clone your portfolio-landing repo (if not already)
git clone https://github.com/finn-1o8/portfolio-landing.git
cd portfolio-landing

# Copy Dockerfile
cp ../Tracker/deployment/portfolio-landing-Dockerfile.example ./Dockerfile

# Create GitHub Actions directory
mkdir -p .github/workflows

# Copy GitHub Actions workflow
cp ../Tracker/deployment/portfolio-landing-github-actions.example.yml .github/workflows/deploy.yml

# Commit and push
git add .
git commit -m "Add Docker and CI/CD configuration"
git push origin main

# Also add GitHub Secrets (same as Tracker)
```

---

### Step 3: Deploy to Hetzner Server

**SSH into your server:**

```bash
ssh root@135.181.254.130
```

**Run the setup script:**

```bash
# Download and run automated setup
bash <(curl -fsSL https://raw.githubusercontent.com/finn-1o8/Tracker/main/deployment/setup-server.sh)
```

**OR manually:**

```bash
# Create directory
mkdir -p /srv/karmanlabs
cd /srv/karmanlabs

# Download files
curl -L -o docker-compose.yml https://raw.githubusercontent.com/finn-1o8/Tracker/main/deployment/docker-compose.yml
curl -L -o Caddyfile https://raw.githubusercontent.com/finn-1o8/Tracker/main/deployment/Caddyfile
curl -L -o env.template https://raw.githubusercontent.com/finn-1o8/Tracker/main/deployment/env.template

# Create .env with secure passwords
cp env.template .env
nano .env
# Set: POSTGRES_PASSWORD to a strong random password

# Generate secure password
openssl rand -base64 32

# Install Docker if needed
curl -fsSL https://get.docker.com | sh
apt install -y docker-compose-plugin

# Setup firewall
ufw allow 22/tcp
ufw allow 80/tcp  
ufw allow 443/tcp
ufw allow 443/udp
ufw --force enable

# Login to GHCR (if images are private)
docker login ghcr.io
# Username: finn-1o8
# Password: GitHub Personal Access Token with packages:read

# Pull and start
docker compose pull
docker compose up -d

# Watch logs
docker compose logs -f
```

---

### Step 4: Wait & Verify

**Wait 2-3 minutes for SSL certificates:**

```bash
# Check all services are up
docker compose ps

# Should all show "Up" and "(healthy)"
```

**Test your site:**

1. Open browser: https://karmanlab.org
2. Should see your landing page
3. Open: https://tracker.karmanlab.org  
4. Should see tracker app
5. Open: https://karmanlab.org/api/docs
6. Should see API documentation

**If any don't work:**

```bash
# Check logs
docker compose logs caddy
docker compose logs tracker-backend

# Look for errors
# Most common: SSL cert still provisioning (wait 5 min)
```

---

### Step 5: Test Auto-Deployment

**Make a small change to test:**

```bash
# In your Tracker repo
echo "# Test deployment" >> README.md
git add README.md
git commit -m "Test auto-deployment"
git push origin main
```

**Watch GitHub Actions:**

1. Go to Tracker repo on GitHub
2. Click **Actions** tab
3. Watch workflow run
4. Should see: Build → Push → Deploy
5. Site should update in ~30 seconds!

---

## 📋 What You've Built

### Infrastructure
✅ **Professional CI/CD** - GitHub Actions → GHCR → Hetzner  
✅ **Zero downtime** deployments  
✅ **Automatic SSL** - Caddy handles certificates  
✅ **Clean architecture** - No source code on server  
✅ **Easy rollback** - Change image tag  
✅ **Monitoring ready** - Health checks everywhere  

### Services
✅ **Landing Page** - Your portfolio at karmanlab.org  
✅ **Tracker App** - Satellite tracker at tracker.karmanlab.org  
✅ **API** - Full FastAPI backend with docs  
✅ **Database** - PostgreSQL with TimescaleDB  
✅ **Cache** - Redis for performance  
✅ **Proxy** - Caddy reverse proxy  

---

## 🎉 You're Done!

Your site is now live with:
- ✅ Professional deployment setup
- ✅ Automatic CI/CD pipelines  
- ✅ SSL certificates auto-managed
- ✅ Zero downtime updates
- ✅ Clean, maintainable architecture

---

## 🔍 Common Issues

### "Port already in use"
```bash
# Stop old deployment
cd /opt/karmanlabs
docker compose down

# Or kill process
lsof -ti:80 | xargs kill -9
```

### "Can't pull images"
```bash
# Login to GHCR
docker login ghcr.io
# Get token: https://github.com/settings/tokens
```

### "SSL not working"
- Wait 5 minutes
- Check DNS: `nslookup karmanlab.org`
- Check port 80 open: `ufw status`

### "502 Bad Gateway"
```bash
# Check backend is running
docker compose ps tracker-backend

# Check logs
docker compose logs tracker-backend
```

---

## 📚 Documentation

- **[QUICK_START.md](./QUICK_START.md)** - 15 minute setup
- **[DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)** - Complete guide
- **[CHECKLIST.md](./CHECKLIST.md)** - Deployment checklist
- **[DEPLOYMENT_SUMMARY.md](./DEPLOYMENT_SUMMARY.md)** - What was created

---

## 🆘 Need Help?

1. Check logs: `docker compose logs -f`
2. Check status: `docker compose ps`
3. Read troubleshooting in DEPLOYMENT_GUIDE.md
4. Verify DNS: `dig karmanlab.org`
5. Check GitHub Actions logs

---

**Congratulations! Your professional deployment is ready.** 🚀

**Questions?** Everything is documented in the deployment/ folder.

