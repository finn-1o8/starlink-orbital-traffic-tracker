# 🚀 Deployment Directory

This directory contains all files needed to deploy the Tracker application to production.

## 📁 Files

### Essential Files
- `DEPLOYMENT.md` - **Complete deployment guide** (read this first)
- `docker-compose.yml` - Service orchestration for production server
- `Caddyfile` - Reverse proxy and SSL configuration
- `env.template` - Environment variables template
- `setup-server.sh` - Automated server setup script

### Example Files (for Portfolio Landing repo)
- `portfolio-landing-Dockerfile.example` - Dockerfile template
- `portfolio-landing-github-actions.example.yml` - GitHub Actions workflow

## 📖 Documentation

**👉 Start here:** [DEPLOYMENT.md](./DEPLOYMENT.md)

This guide covers:
- Architecture overview
- How path-based routing works
- Configuration details
- Deployment process
- Troubleshooting

## 🚀 Quick Reference

**Server:** 135.181.254.130  
**Directory:** `/srv/karmanlabs`  
**Domain:** https://karmanlab.org/tracker

**Services:**
- Tracker Frontend (React + Cesium)
- Tracker Backend (FastAPI)
- PostgreSQL (TimescaleDB)
- Redis
- Caddy (Reverse Proxy + SSL)

---

For detailed deployment instructions, see [DEPLOYMENT.md](./DEPLOYMENT.md).
