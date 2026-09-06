# Deployment files

| File | Purpose |
|---|---|
| `DEPLOYMENT.md` | How the single-host deployment is put together and operated |
| `docker-compose.yml` | Production services (Caddy, frontend, backend, landing page, PostgreSQL, Redis) |
| `Caddyfile` | Reverse proxy and automatic TLS |
| `env.template` | Variables required by the Compose file |
| `setup-server.sh` | One-shot host setup |
| `portfolio-landing-*.example` | Templates for the separate landing-page repository that shares this host |

Start with `DEPLOYMENT.md`.
