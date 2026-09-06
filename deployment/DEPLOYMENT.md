# Deployment

The stack runs on a single Linux host with Docker Compose behind Caddy, which terminates TLS automatically. The frontend is served under the `/tracker` path of a site that also hosts a separate landing page; the API is proxied under `/api`.

```
Browser -> Caddy (TLS, reverse proxy) -> tracker-frontend (nginx, static build)
                                      -> tracker-backend  (FastAPI)  -> postgres, redis
                                      -> landing          (static site, separate repo)
```

## Files

- `docker-compose.yml`: production services. Database and cache sit on an internal network and publish no ports.
- `Caddyfile`: routing. `/tracker*` has its prefix stripped and goes to the frontend, `/api*` goes to the backend with HTTP/1.1 forced so WebSockets work.
- `env.template`: variables the Compose file needs.
- `setup-server.sh`: installs Docker, downloads the three files above, opens the firewall and starts the stack.

## First deployment

1. Create a non-root user on the host and add it to the `docker` group. Deploy and log in as that user; do not run services or CI deploys as root.
2. Point DNS A/AAAA records for your domain at the host.
3. Run `setup-server.sh` as root once, or reproduce its steps by hand: install Docker, create `/srv/karmanlabs`, copy `docker-compose.yml`, `Caddyfile` and `env.template` there, rename the template to `.env` and set a strong `POSTGRES_PASSWORD`.
4. Edit the domain names in `Caddyfile` and `CORS_ORIGINS` in `docker-compose.yml`.
5. Build or pull the images (see below), then `docker compose up -d`.

## Images

Images are built from `backend/Dockerfile` and `frontend/Dockerfile.prod`. The frontend build takes an optional Cesium ion token and landing URL as build arguments:

```bash
docker build -t karmanlabs_tracker-backend:latest backend
docker build -t karmanlabs_tracker-frontend:latest \
  --build-arg CESIUM_ION_TOKEN="$CESIUM_ION_TOKEN" \
  --build-arg LANDING_URL="https://example.org" \
  -f frontend/Dockerfile.prod frontend
```

For automated deploys, build and push to GitHub Container Registry from GitHub Actions and let the deploy step SSH in as the deploy user to `docker compose pull && docker compose up -d`. Keep the workflow in a private repository or protect it with environments; keep the SSH key, host and user in repository secrets. Never commit hostnames, IPs or keys.

## Path-based routing notes

- The frontend is built with `base: '/tracker/'` in `vite.config.ts`, so its assets reference `/tracker/assets/...` and `/tracker/cesium/...`.
- Caddy strips `/tracker` before proxying, so nginx receives `/assets/...` and `/cesium/...`.
- `vite-plugin-cesium` places the Cesium static files under the base path inside `dist`, which is why `frontend/nginx.conf` aliases `/cesium/*` to `/usr/share/nginx/html/tracker/cesium/*`.

## Operations

```bash
cd /srv/karmanlabs
docker compose ps
docker compose logs -f tracker-backend
docker compose pull && docker compose up -d     # update
docker compose exec postgres pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" > backup.sql
```

Health: `curl https://your-domain/api/health` returns the scheduler and WebSocket status.
