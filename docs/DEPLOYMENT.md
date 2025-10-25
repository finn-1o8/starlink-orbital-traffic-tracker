# 🚀 Deployment Guide

This guide covers deploying the Orbital Traffic Impact Analyzer to production.

## 📋 Pre-Deployment Checklist

- [ ] Domain name configured
- [ ] SSL certificate obtained
- [ ] Database backups configured
- [ ] Environment variables secured
- [ ] Cesium Ion token for production
- [ ] Monitoring tools setup
- [ ] Error tracking configured (e.g., Sentry)

---

## 🏗️ Production Architecture

```
┌─────────────────┐
│   Users/Clients │
└────────┬────────┘
         │
    ┌────▼────┐
    │  CDN    │ (Static Assets)
    └────┬────┘
         │
    ┌────▼────────┐
    │   Nginx     │ (Reverse Proxy, SSL)
    └──┬──────┬───┘
       │      │
   ┌───▼───┐ │
   │Frontend│ │
   │ (React)│ │
   └────────┘ │
              │
         ┌────▼────────┐
         │   Backend   │ (FastAPI)
         │  (Python)   │
         └──┬──────┬───┘
            │      │
    ┌───────▼──┐ ┌─▼──────┐
    │PostgreSQL│ │ Redis  │
    └──────────┘ └────────┘
```

---

## 🎯 Deployment Options

### Option 1: Railway (Recommended for Beginners)

**Backend:**
```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login to Railway
railway login

# 3. Deploy backend
cd backend
railway init
railway up

# 4. Add environment variables in Railway dashboard
# DATABASE_URL (Postgres plugin)
# REDIS_URL (Redis plugin)
# CORS_ORIGINS=https://yourdomain.com
```

**Frontend:**
```bash
# 1. Build frontend
cd frontend
npm run build

# 2. Deploy to Vercel
npm install -g vercel
vercel --prod

# 3. Set environment variables in Vercel dashboard
# VITE_API_URL=https://your-backend.railway.app/api
# VITE_CESIUM_ION_TOKEN=your_token
```

### Option 2: DigitalOcean App Platform

**Full Stack:**
```yaml
# app.yaml
name: orbital-traffic-analyzer

services:
  - name: backend
    github:
      repo: your-username/orbital-traffic-analyzer
      branch: main
      deploy_on_push: true
    source_dir: backend
    build_command: pip install -r requirements.txt
    run_command: uvicorn app.main:app --host 0.0.0.0 --port 8000
    envs:
      - key: DATABASE_URL
        value: ${db.DATABASE_URL}
      - key: REDIS_URL
        value: ${redis.REDIS_URL}
    health_check:
      http_path: /api/health

  - name: frontend
    github:
      repo: your-username/orbital-traffic-analyzer
      branch: main
    source_dir: frontend
    build_command: npm install && npm run build
    output_dir: dist
    envs:
      - key: VITE_API_URL
        value: ${backend.PUBLIC_URL}/api

databases:
  - name: db
    engine: PG
    version: "15"

services:
  - name: redis
    engine: REDIS
    version: "7"
```

Deploy:
```bash
doctl apps create --spec app.yaml
```

### Option 3: AWS (Production Grade)

**Backend on ECS:**
```bash
# 1. Build and push Docker image
docker build -t orbital-backend backend/
docker tag orbital-backend:latest YOUR_ECR_REPO:latest
docker push YOUR_ECR_REPO:latest

# 2. Create ECS task definition
# 3. Create ECS service with ALB
# 4. Configure RDS PostgreSQL
# 5. Configure ElastiCache Redis
```

**Frontend on S3 + CloudFront:**
```bash
# 1. Build frontend
cd frontend
npm run build

# 2. Upload to S3
aws s3 sync dist/ s3://your-bucket-name/

# 3. Create CloudFront distribution
# 4. Configure SSL certificate (ACM)
```

### Option 4: Self-Hosted (VPS)

**Requirements:**
- Ubuntu 22.04 LTS
- 4GB RAM minimum
- 20GB storage
- Docker installed

**Setup:**
```bash
# 1. Clone repository
git clone https://github.com/yourusername/orbital-traffic-analyzer.git
cd orbital-traffic-analyzer

# 2. Configure environment
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
# Edit .env files with production values

# 3. Create production docker-compose
cat > docker-compose.prod.yml <<EOF
version: '3.8'

services:
  postgres:
    image: timescale/timescaledb:latest-pg15
    restart: always
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: orbital_tracker
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    networks:
      - internal

  redis:
    image: redis:7-alpine
    restart: always
    volumes:
      - redis_data:/data
    networks:
      - internal

  backend:
    build: ./backend
    restart: always
    depends_on:
      - postgres
      - redis
    environment:
      DATABASE_URL: postgresql://${DB_USER}:${DB_PASSWORD}@postgres:5432/orbital_tracker
      REDIS_URL: redis://redis:6379/0
      CORS_ORIGINS: https://yourdomain.com
    networks:
      - internal
      - web

  frontend:
    image: nginx:alpine
    restart: always
    volumes:
      - ./frontend/dist:/usr/share/nginx/html
      - ./nginx.conf:/etc/nginx/nginx.conf
    ports:
      - "80:80"
      - "443:443"
    networks:
      - web

networks:
  web:
  internal:

volumes:
  postgres_data:
  redis_data:
EOF

# 4. Start services
docker-compose -f docker-compose.prod.yml up -d

# 5. Setup SSL with Let's Encrypt
sudo certbot --nginx -d yourdomain.com
```

---

## 🔐 Security Configuration

### Environment Variables

**NEVER commit these to git:**
```env
# Backend Production
DATABASE_URL=postgresql://user:STRONG_PASSWORD@host:5432/db
REDIS_URL=redis://STRONG_PASSWORD@host:6379/0
SECRET_KEY=random_64_character_string
ALLOWED_HOSTS=yourdomain.com
CORS_ORIGINS=https://yourdomain.com

# Frontend Production
VITE_API_URL=https://api.yourdomain.com/api
VITE_CESIUM_ION_TOKEN=production_token
```

### Nginx Configuration

```nginx
# /etc/nginx/sites-available/orbital-tracker

upstream backend {
    server backend:8000;
}

server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # Frontend
    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket
    location /api/ws {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
}
```

---

## 📊 Monitoring

### Health Checks

```bash
# Backend health
curl https://api.yourdomain.com/api/health

# Database connection
docker exec orbital-postgres pg_isready

# Redis connection
docker exec orbital-redis redis-cli ping
```

### Logging

**Backend logs:**
```bash
docker logs -f orbital-backend --tail 100
```

**PostgreSQL logs:**
```bash
docker logs -f orbital-postgres --tail 100
```

### Monitoring Tools

**Recommended:**
- **Uptime**: UptimeRobot or Better Uptime
- **Error Tracking**: Sentry
- **Metrics**: Prometheus + Grafana
- **Logs**: Papertrail or CloudWatch

**Setup Sentry (Backend):**
```python
# backend/app/main.py
import sentry_sdk

sentry_sdk.init(
    dsn="your-sentry-dsn",
    environment="production",
)
```

---

## 🔄 CI/CD

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build and push Docker image
        run: |
          docker build -t orbital-backend backend/
          docker tag orbital-backend ${{ secrets.DOCKER_REGISTRY }}/orbital-backend:latest
          docker push ${{ secrets.DOCKER_REGISTRY }}/orbital-backend:latest
      
      - name: Deploy to server
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.HOST }}
          username: ${{ secrets.USERNAME }}
          key: ${{ secrets.SSH_KEY }}
          script: |
            cd /opt/orbital-tracker
            docker-compose pull
            docker-compose up -d

  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build frontend
        run: |
          cd frontend
          npm install
          npm run build
      
      - name: Deploy to S3
        run: |
          aws s3 sync frontend/dist/ s3://${{ secrets.S3_BUCKET }}/ --delete
```

---

## 📦 Database Backups

### Automated Backups

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# PostgreSQL backup
docker exec orbital-postgres pg_dump -U orbital_user orbital_tracker > \
  "$BACKUP_DIR/backup_$DATE.sql"

# Compress
gzip "$BACKUP_DIR/backup_$DATE.sql"

# Delete old backups (keep 30 days)
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +30 -delete
```

**Schedule with cron:**
```bash
# Run daily at 2 AM
0 2 * * * /opt/orbital-tracker/backup.sh
```

---

## 🎯 Performance Optimization

### Backend
- Use Gunicorn with multiple workers
- Enable Redis caching
- Configure database connection pooling
- Use CDN for static assets

### Frontend
- Enable Vite build optimizations
- Use code splitting
- Lazy load components
- Compress assets (gzip/brotli)

---

## 🐛 Troubleshooting Production

### High CPU Usage
```bash
# Check processes
docker stats

# Scale backend workers
docker-compose up -d --scale backend=3
```

### Database Performance
```sql
-- Check slow queries
SELECT * FROM pg_stat_statements 
ORDER BY total_time DESC LIMIT 10;

-- Add indexes
CREATE INDEX idx_positions_time ON satellite_positions(timestamp);
```

### WebSocket Issues
```bash
# Check nginx WebSocket proxy settings
# Ensure proxy_set_header Upgrade is set
```

---

## 📞 Support

For deployment issues:
1. Check logs: `docker-compose logs`
2. Review documentation
3. Open GitHub issue

---

**Good luck with your deployment! 🚀**

