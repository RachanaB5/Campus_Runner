# Campus Runner — DevOps & Docker Guide

## Quick Start

```bash
cp .env.example .env
# edit .env with your secrets

# Development (hot reload)
docker-compose up -d

# Production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

Access:
- Frontend: http://localhost:8080
- Backend API: http://localhost:5000
- Health: http://localhost:8080/health, http://localhost:5000/api/health

Default admin: `admin@rvu.edu.in` / `admin@123`

---

## Docker Architecture

### Images

| Image | Base | Size | User |
|-------|------|------|------|
| Backend | python:3.11-slim (multi-stage) | ~200MB | appuser (UID 1000) |
| Frontend | node:20-alpine → nginx:1.27-alpine (multi-stage) | ~30MB | nginx |

Both use multi-stage builds — build tools are not present in the final image.

### Networking

- Bridge network: `campus_runner_network`
- Frontend → Backend: nginx proxies `/api/` and `/socket.io` to `http://backend:5000`
- Exposed ports: `5000` (backend), `8080` (frontend)

### Volumes

- `./instance` → `/app/instance` — SQLite database persistence
- `./backend` → `/app/backend` — live source mount in dev

---

## Common Commands

### Build & Run

```bash
docker-compose build
docker-compose build --no-cache        # force full rebuild
docker-compose up -d                   # start in background
docker-compose up                      # start with logs
docker-compose stop                    # stop containers
docker-compose down                    # stop + remove containers/networks
docker-compose down -v                 # also remove volumes
```

### Logs

```bash
docker-compose logs -f                 # all services, follow
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs --tail=50 backend
docker-compose logs --since 2024-04-14T10:00:00 backend
```

### Exec into containers

```bash
docker-compose exec backend bash
docker-compose exec backend pytest backend/tests/ -v
docker-compose exec backend python backend/seed.py
docker-compose run --rm backend bash   # one-off container
```

### Database

```bash
# Seed data
docker-compose exec backend python backend/seed.py

# Backup
docker-compose exec -T backend tar -czf - instance/ > backup-$(date +%s).tar.gz

# Restore
tar -xzf backup-<timestamp>.tar.gz
docker cp instance/. campus_runner_backend:/app/instance/

# Reset DB (will recreate on next start)
docker exec campus_runner_backend rm instance/campusrunner.db
docker-compose restart backend
```

### Tests & Linting

```bash
docker-compose exec backend pytest backend/tests/ -v --cov=backend
docker-compose exec frontend npm test
docker-compose exec frontend npm run typecheck
docker-compose exec frontend npm run lint
docker-compose exec backend flake8 backend/
```

---

## Health Checks

```bash
docker-compose ps
curl http://localhost:5000/api/health
curl http://localhost:8080/health
```

---

## Resource Monitoring

```bash
docker stats
docker stats --no-stream
docker ps --format "table {{.Names}}\t{{.CPUPerc}}\t{{.MemUsage}}"
docker top campus_runner_backend
```

---

## Network Debugging

```bash
docker network ls
docker network inspect campus_runner_network
docker exec campus_runner_frontend ping backend
docker port campus_runner_backend
docker port campus_runner_frontend
```

---

## Troubleshooting

### Container won't start
```bash
docker-compose logs backend
docker logs campus_runner_backend
docker-compose run --rm backend bash
docker-compose up backend             # foreground, see output directly
```

### Port conflicts
```bash
netstat -tuln | grep 5000
# Change mapping in docker-compose.yml: "5001:5000"
```

### CORS errors (browser NetworkError on login)
Add your frontend origin to `CORS_ORIGINS` in `.env`:
```
CORS_ORIGINS=http://localhost:5173,http://localhost:3000,http://localhost:8080,http://127.0.0.1:8080
```
Then recreate the backend container (`docker-compose up -d backend`) — a plain restart does not re-read `.env`.

### Env var changes not taking effect
`docker-compose restart` does **not** re-read `.env`. Use:
```bash
docker-compose up -d <service>   # recreates the container
```

### Cleanup

```bash
docker image prune
docker system prune -a --volumes   # removes everything unused
docker system df                   # check disk usage
```

---

## Image Management

```bash
docker images
docker history campus_runner-backend
docker rmi campus_runner-backend

# Save / load
docker save campus_runner-backend -o backend.tar
docker load -i backend.tar

# Tag & push
docker tag campus_runner-backend:latest ghcr.io/<user>/campus-runner/backend:1.0.0
docker push ghcr.io/<user>/campus-runner/backend:1.0.0
```

---

## Production Deployment

```bash
# Pull & start
docker-compose -f docker-compose.yml -f docker-compose.prod.yml pull
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Verify
docker-compose -f docker-compose.yml -f docker-compose.prod.yml ps
curl https://yourdomain.com/api/health
```

### Rollback
```bash
docker-compose down
docker pull ghcr.io/<user>/campus-runner/backend:v1.0.0
# update image tag in docker-compose.yml
docker-compose up -d
```

---

## CI/CD (GitHub Actions)

Workflow: `.github/workflows/ci.yml`

Triggers: push/PR to `main`, `develop`, feature branches.

Jobs:
1. **Backend** — flake8 lint, pytest (Py 3.11 & 3.12), coverage upload
2. **Frontend** — ESLint, TypeScript check, Vitest, build verification, coverage upload
3. **Docker build & push** — builds both images, pushes to ghcr.io with branch/sha/semver tags
4. **Security scan** — Trivy SARIF scan → GitHub Security tab
5. **Deployment ready** — runs on `main` only after all jobs pass

---

## Security

- Non-root users in both containers (`appuser`, `nginx`)
- Alpine/slim base images — minimal attack surface
- No build tools in runtime images (multi-stage)
- Security headers on all nginx responses (X-Frame-Options, X-Content-Type-Options, XSS-Protection, Referrer-Policy, Permissions-Policy)
- `.env` is gitignored — use GitHub Secrets for CI/CD
- CORS restricted to explicit origin list
- HTTPS-ready nginx config (add SSL cert + redirect block to `nginx-default.conf`)
