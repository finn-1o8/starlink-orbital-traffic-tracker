# ✅ Deployment Checklist

Use this checklist to ensure everything is properly configured and deployed.

---

## 📝 Pre-Deployment Checklist

### GitHub Configuration

#### Tracker Repository
- [ ] Repository exists at `finn-1o8/Tracker`
- [ ] GitHub Actions workflows exist:
  - [ ] `.github/workflows/deploy-backend.yml`
  - [ ] `.github/workflows/deploy-frontend.yml`
- [ ] GitHub Secrets configured:
  - [ ] `SSH_HOST` = `135.181.254.130`
  - [ ] `SSH_USER` = `root`
  - [ ] `SSH_PRIVATE_KEY` = (your SSH private key)
- [ ] Dockerfiles exist:
  - [ ] `backend/Dockerfile`
  - [ ] `frontend/Dockerfile.prod`

#### Portfolio Landing Repository  
- [ ] Repository exists at `finn-1o8/portfolio-landing`
- [ ] Dockerfile added at repo root
- [ ] GitHub Actions workflow added: `.github/workflows/deploy.yml`
- [ ] GitHub Secrets configured:
  - [ ] `SSH_HOST` = `135.181.254.130`
  - [ ] `SSH_USER` = `root`
  - [ ] `SSH_PRIVATE_KEY` = (same as Tracker)

### SSH Access
- [ ] SSH key generated (if needed)
- [ ] Public key added to Hetzner server
- [ ] Private key copied for GitHub Secrets
- [ ] Can SSH to server: `ssh root@135.181.254.130`

### DNS Configuration
- [ ] `karmanlab.org` A record → `135.181.254.130`
- [ ] `www.karmanlab.org` A record → `135.181.254.130`
- [ ] `tracker.karmanlab.org` A record → `135.181.254.130`
- [ ] DNS propagated (checked with `dig` or `nslookup`)

---

## 🚀 Server Deployment Checklist

### Server Setup
- [ ] Server is running (Ubuntu 22.04+)
- [ ] Docker installed
- [ ] Docker Compose plugin installed
- [ ] Firewall configured (ports 22, 80, 443 open)
- [ ] DNS pointing to server

### Deployment Files
- [ ] Logged into server: `ssh root@135.181.254.130`
- [ ] Created directory: `/srv/karmanlabs`
- [ ] Downloaded docker-compose.yml
- [ ] Downloaded Caddyfile
- [ ] Downloaded env.template
- [ ] Created `.env` from template
- [ ] Set secure passwords in `.env`

### Environment Configuration
- [ ] `POSTGRES_DB` set
- [ ] `POSTGRES_USER` set
- [ ] `POSTGRES_PASSWORD` set (strong password)
- [ ] `.env` file not in git (on server only)

### Initial Deployment
- [ ] `docker compose pull` successful
- [ ] `docker compose up -d` successful
- [ ] All services started: `docker compose ps`
- [ ] No crashes in logs: `docker compose logs`

### SSL Certificates
- [ ] Caddy obtained SSL certs (check logs)
- [ ] HTTPS working for main domain
- [ ] HTTPS working for tracker subdomain
- [ ] No certificate errors in browser

---

## ✅ Verification Checklist

### Connectivity
- [ ] `curl https://karmanlab.org` returns 200
- [ ] `curl https://www.karmanlab.org` returns 200
- [ ] `curl https://tracker.karmanlab.org` returns 200
- [ ] `curl https://karmanlab.org/api/health` returns 200
- [ ] HTTP redirects to HTTPS

### Landing Page
- [ ] Main site loads in browser
- [ ] No console errors
- [ ] Images/assets load correctly
- [ ] Responsive design works

### Tracker Application
- [ ] Tracker loads at /tracker or subdomain
- [ ] 3D globe renders
- [ ] Satellites visible
- [ ] API calls working
- [ ] WebSocket connects

### API
- [ ] `/api/docs` accessible
- [ ] `/api/health` returns 200
- [ ] `/api/satellites` returns data
- [ ] WebSocket endpoint works

### Service Health
- [ ] All containers "Up" and "healthy"
- [ ] No restarts in `docker compose ps`
- [ ] Postgres database accessible
- [ ] Redis cache working
- [ ] Backend logs show no errors
- [ ] Frontend logs show no errors
- [ ] Caddy logs show no errors

---

## 🔄 Testing Auto-Deployment Checklist

### Backend Deployment Test
- [ ] Made small change to `backend/README.md`
- [ ] Committed and pushed to main
- [ ] GitHub Actions workflow triggered
- [ ] Image built successfully
- [ ] Image pushed to GHCR
- [ ] Deployment to server succeeded
- [ ] Changes visible on site

### Frontend Deployment Test
- [ ] Made small change to `frontend/README.md`
- [ ] Committed and pushed to main
- [ ] GitHub Actions workflow triggered
- [ ] Image built successfully
- [ ] Image pushed to GHCR
- [ ] Deployment to server succeeded
- [ ] Changes visible on site

### Landing Deployment Test
- [ ] Made small change to landing repo
- [ ] Committed and pushed to main
- [ ] GitHub Actions workflow triggered
- [ ] Image built successfully
- [ ] Image pushed to GHCR
- [ ] Deployment to server succeeded
- [ ] Changes visible on site

---

## 🔒 Security Checklist

- [ ] SSH password authentication disabled
- [ ] Firewall enabled and configured
- [ ] Only necessary ports open (22, 80, 443)
- [ ] Strong database password set
- [ ] `.env` file not committed to git
- [ ] GitHub Secrets configured (not plain text)
- [ ] SSL certificates valid (not expired)
- [ ] No source code on server (verify)
- [ ] Docker images from trusted registry
- [ ] Regular backups configured

---

## 📊 Monitoring Checklist

### Logs
- [ ] No errors in Caddy logs
- [ ] No errors in backend logs
- [ ] No errors in frontend logs
- [ ] No connection refused errors
- [ ] SSL renewal working in Caddy logs

### Performance
- [ ] Site loads in <3 seconds
- [ ] API responds in <500ms
- [ ] Database queries optimized
- [ ] Redis cache working
- [ ] No memory leaks

### Backups
- [ ] Database backup script created
- [ ] Backup runs automatically (cron)
- [ ] Backups tested (can restore)
- [ ] Backups stored off-server
- [ ] Retention policy set

---

## 🎓 Documentation Checklist

- [ ] DEPLOYMENT_HISTORY.md updated
- [ ] README.md reflects new setup
- [ ] Team knows deployment process
- [ ] Rollback procedure documented
- [ ] Emergency contacts listed
- [ ] Monitoring tools configured (optional)

---

## 🆘 Rollback Preparation

- [ ] Know how to rollback each service
- [ ] Have previous image tags noted
- [ ] Backup database before major changes
- [ ] Test rollback in staging (if exists)
- [ ] Document rollback commands

---

## 📞 Emergency Contacts

- [ ] Hetzner support: (account URL)
- [ ] Domain registrar: (where karmanlab.org registered)
- [ ] GitHub account: finn-1o8
- [ ] SSH access: root@135.181.254.130
- [ ] Backup location: (where backups stored)

---

## ✅ Post-Deployment

### Testing Complete
- [ ] All manual tests passed
- [ ] Auto-deployment tests passed
- [ ] No critical issues found
- [ ] Site stable for 24+ hours
- [ ] Performance acceptable

### Handoff Complete
- [ ] Documentation up to date
- [ ] Team trained on new process
- [ ] Old deployment archived
- [ ] `/opt/karmanlabs` cleaned up (old setup)
- [ ] Monitoring alerts configured

---

## 🎉 Success Criteria

✅ **Zero manual intervention** for deployments  
✅ **All services healthy** for 7 days  
✅ **No SSL issues** for 30 days  
✅ **Fast deployments** (< 2 minutes)  
✅ **Zero downtime** during updates  
✅ **Clean server** (no source code)  
✅ **Automatic backups** working  
✅ **Team happy** with new process  

---

**Checklist Status:**  
Completed: ___ / ___ items  
Last Updated: _______________  
Next Review: _______________

