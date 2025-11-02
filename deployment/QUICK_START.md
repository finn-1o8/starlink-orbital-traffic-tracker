# ⚡ Quick Start Deployment

Get your site deployed in 15 minutes following these steps.

---

## Prerequisites Checklist

- [ ] GitHub repositories exist and you have access
- [ ] Hetzner server running at 135.181.254.130
- [ ] SSH access to server works: `ssh root@135.181.254.130`
- [ ] Domain karmanlab.org DNS pointing to 135.181.254.130

---

## Step 1: Clone and Push Tracking Repo (Already Done!)

Your Tracker repo already has:
- ✅ Dockerfiles for backend and frontend
- ✅ GitHub Actions workflows
- Just needs GitHub Secrets configured

---

## Step 2: Setup Portfolio Landing Repo

### 2.1 Add Dockerfile

In your portfolio-landing repo, add this Dockerfile at root:

```bash
cd /path/to/portfolio-landing
# Copy from deployment/portfolio-landing-Dockerfile.example or create:
```

Create `.github/workflows/deploy.yml`:
- Copy from `deployment/portfolio-landing-github-actions.example.yml`

### 2.2 Configure GitHub Secrets

In **portfolio-landing** repo on GitHub:
1. Settings → Secrets → Actions
2. Add: SSH_HOST, SSH_USER, SSH_PRIVATE_KEY

---

## Step 3: Configure GitHub Secrets for Tracker

In **Tracker** repo on GitHub:
1. Settings → Secrets → Actions  
2. Add: SSH_HOST, SSH_USER, SSH_PRIVATE_KEY

---

## Step 4: Deploy to Server

### Option A: Automated Script

```bash
# SSH into server
ssh root@135.181.254.130

# Run automated setup
curl -fsSL https://raw.githubusercontent.com/finn-1o8/Tracker/main/deployment/setup-server.sh | bash
```

### Option B: Manual Setup

```bash
# SSH into server
ssh root@135.181.254.130

# Create directory
mkdir -p /srv/karmanlabs
cd /srv/karmanlabs

# Download files
curl -L -o docker-compose.yml https://raw.githubusercontent.com/finn-1o8/Tracker/main/deployment/docker-compose.yml
curl -L -o Caddyfile https://raw.githubusercontent.com/finn-1o8/Tracker/main/deployment/Caddyfile
curl -L -o env.template https://raw.githubusercontent.com/finn-1o8/Tracker/main/deployment/env.template

# Create .env
cp env.template .env
nano .env  # Set secure passwords

# Pull and start
docker compose pull
docker compose up -d
```

---

## Step 5: Verify Deployment

Wait 2-3 minutes, then check:

```bash
# On server
docker compose ps
docker compose logs caddy

# Should see:
# - All services "Up" and "healthy"
# - SSL certificates obtained
```

Visit in browser:
- https://karmanlab.org (landing page)
- https://karmanlab.org/tracker (tracker app)
- https://tracker.karmanlab.org (tracker subdomain)
- https://karmanlab.org/api/docs (API docs)

---

## Step 6: Test Auto-Deployment

Make a small change to any repo, push to main:

```bash
# Example: Update Tracker README
echo "Updated" >> README.md
git add README.md
git commit -m "Test deployment"
git push origin main
```

Watch GitHub Actions, should auto-deploy!

---

## Troubleshooting

**"Port already in use":**
```bash
cd /opt/karmanlabs
docker compose down
```

**"Can't pull images":**
```bash
docker login ghcr.io
# Use GitHub Personal Access Token
```

**"SSL not working":**
- Wait 5 minutes
- Check DNS is propagated
- Check port 80 is open: `ufw allow 80/tcp`

**"502 Bad Gateway":**
```bash
docker compose logs tracker-backend
docker compose logs caddy
```

---

## Next Steps

- [ ] Read full DEPLOYMENT_GUIDE.md for details
- [ ] Setup monitoring (optional)
- [ ] Configure backups (optional)
- [ ] Customize Caddyfile if needed

---

**Done! Your site is live at karmanlab.org** 🎉

Need help? Check DEPLOYMENT_GUIDE.md or logs.

