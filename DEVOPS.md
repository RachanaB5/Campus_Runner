# DevOps & Docker Documentation

## Overview

Campus Runner uses a modern DevOps setup with Docker, CI/CD pipelines, and production-ready configurations.

## Table of Contents

- [Local Development](#local-development)
- [Docker Architecture](#docker-architecture)
- [CI/CD Pipeline](#cicd-pipeline)
- [Deployment](#deployment)
- [Monitoring & Logging](#monitoring--logging)
- [Security](#security)

---

## Local Development

### Quick Start

1. **Clone and setup environment:**
   ```bash
   git clone <repo>
   cd Campus_Runner
   cp .env.example .env
   ```

2. **Start development environment:**
   ```bash
   # Using docker-compose with development overrides
   docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
   
   # Or using the provided setup script
   ./setup.sh
   ```

3. **Access the application:**
   - Frontend: http://localhost:5173 (with hot reload)
   - Backend API: http://localhost:5000
   - API Docs: http://localhost:5000/api/docs

### Development Commands

```bash
# View logs
docker-compose logs -f backend    # Backend logs
docker-compose logs -f frontend   # Frontend logs

# Run tests
docker-compose exec backend pytest backend/tests/ -v
docker-compose exec frontend npm test

# Stop and clean up
docker-compose down -v            # Remove volumes too

# Rebuild images
docker-compose build --no-cache backend
docker-compose build --no-cache frontend
```

---

## Docker Architecture

### Multi-Stage Builds

Both Dockerfiles use multi-stage builds for optimization:

#### Backend (`Dockerfile.backend`)
- **Stage 1 (Builder):** Installs dependencies in Python 3.11-slim
- **Stage 2 (Runtime):** Copies only installed packages, resulting in ~50% smaller image
- **Security:** Non-root user (appuser)
- **Health Check:** HTTP endpoint validation every 30s

#### Frontend (`Dockerfile.frontend`)
- **Stage 1 (Builder):** Node 20-alpine builds production bundle
- **Stage 2 (Runtime):** Nginx alpine serves static files
- **Security:** Non-root nginx user
- **Optimization:** Gzip compression, proper cache headers
- **Health Check:** HTTP health check every 30s

### Image Sizes

- Backend: ~200MB (Python + dependencies)
- Frontend: ~30MB (Nginx + built app)
- Total: ~230MB (optimized compared to ~1GB individual images)

### Networking

- Docker network: `campus_runner_network` (bridge)
- Backend exposed: `5000:5000`
- Frontend exposed: `8080:8080`
- Inter-container: Backend → Frontend via `http://frontend:8080`
- Frontend → Backend via `http://backend:5000`

### Volumes

- **Development:** Source code mounted for hot reload
- **Production:** Named volumes for data persistence
- **Instance folder:** Database and uploads stored in `/app/instance`

---

## CI/CD Pipeline

### GitHub Actions Workflow

Located in `.github/workflows/ci.yml`

#### Triggers
- Push to `main` or `develop` branches
- All pull requests

#### Jobs

**1. Backend Tests & Quality**
- Python 3.11 environment
- Dependency installation with caching
- Lint: flake8 (syntax errors + complexity)
- Tests: pytest with coverage
- Coverage uploaded to Codecov

**2. Frontend Tests & Quality**
- Node.js 20 environment
- Dependency caching with npm
- Lint: ESLint
- Type check: TypeScript
- Unit tests: Vitest
- Build verification
- Coverage uploaded to Codecov

**3. Docker Build & Push**
- Builds backend and frontend images
- Pushes to GitHub Container Registry (ghcr.io)
- Auto-tagging (branch, version, sha, latest)
- BuildKit cache for faster builds

**4. Security Scanning**
- Trivy vulnerability scanning
- SARIF format results
- Integration with GitHub Security tab

**5. Deployment Ready**
- Runs only on main branch after all tests pass
- Creates deployment checklist in GitHub workflow

### Running Tests Locally

```bash
# Backend tests
cd backend
pip install -r requirements.txt
pytest tests/ -v --cov=backend --cov-report=html

# Frontend tests
npm install
npm test
npm run typecheck
npm run lint
```

---

## Deployment

### Production Setup

1. **Prepare environment:**
   ```bash
   # Copy and edit production environment
   cp .env.example .env.production
   # Update with real secrets, database URL, etc.
   ```

2. **Deploy with production compose:**
   ```bash
   # Pull latest images
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml pull
   
   # Start containers
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
   
   # Verify health
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml ps
   ```

3. **Backup considerations:**
   ```bash
   # Backup instance folder (databases, uploads)
   tar -czf backup-$(date +%s).tar.gz ./instance
   
   # Backup volumes during runtime (optional)
   docker-compose exec backend tar -C /app/instance -czf - . > backup.tar.gz
   ```

### Post-Deployment

```bash
# Check service health
docker-compose ps

# View logs for errors
docker-compose logs backend
docker-compose logs frontend

# Monitor resources
docker stats
```

### Rollback

```bash
# Stop and remove containers
docker-compose down

# Restart with previous image version
docker pull $REGISTRY/campus-runner/backend:previous-tag
docker-compose up -d
```

---

## Monitoring & Logging

### Log Access

```bash
# Real-time logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Last 100 lines
docker-compose logs --tail=100 backend

# From specific time
docker-compose logs --since 2024-01-14 backend
```

### Log Configuration

- **Format:** JSON logs for structured parsing
- **Rotation:** Max 10MB per file, 3 files kept
- **Location:** Docker daemon manages (JSON file driver)

### Health Checks

Backend:
```bash
# Manual health check
curl http://localhost:5000/api/health
```

Frontend:
```bash
# Manual health check
curl http://localhost:8080/health
```

### Metrics & Monitoring

Resources:
```bash
# CPU and memory usage
docker stats campus_runner_backend campus_runner_frontend

# Per-container breakdown
docker ps --format "table {{.Names}}\t{{.CPUPerc}}\t{{.MemUsage}}"
```

---

## Security

### Best Practices Implemented

1. **Non-Root Users**
   - Backend: `appuser` (UID 1000)
   - Frontend: `nginx` (UID 1001)

2. **Security Headers (Nginx)**
   ```
   - X-Frame-Options: SAMEORIGIN
   - X-Content-Type-Options: nosniff
   - X-XSS-Protection: enabled
   - Referrer-Policy: strict-origin-when-cross-origin
   - Permissions-Policy: geolocation/microphone/camera disabled
   ```

3. **HTTPS Ready**
   - Add to `nginx-default.conf`:
     ```nginx
     listen 443 ssl http2;
     ssl_certificate /path/to/cert.pem;
     ssl_certificate_key /path/to/key.pem;
     # Redirect HTTP to HTTPS
     server {
         listen 80;
         return 301 https://$server_name$request_uri;
     }
     ```

4. **Secret Management**
   - `.env` NOT in git (+ `.gitignore`)
   - Use GitHub Secrets for CI/CD
   - Rotate `JWT_SECRET_KEY` regularly
   - Never log sensitive data

5. **Image Security**
   - Alpine-based images (minimal attack surface)
   - Multi-stage builds (no build tools in final image)
   - `--no-cache-dir` for pip (cleaner layers)

6. **Network Security**
   - Internal Docker network for service communication
   - CORS configured for allowed origins
   - Socket.io configured for secure connections

### Environment Secrets

**GitHub Secrets needed for CI/CD:**
- Deployment credentials (if using container registry)
- Database credentials (in .env.production)
- API keys for external services

---

## Troubleshooting

### Container won't start

```bash
# Check logs
docker logs campus_runner_backend

# Inspect configuration
docker inspect campus_runner_backend

# Try with verbose output
docker-compose up backend --no-detach
```

### Database connection issues

```bash
# Verify database service
docker-compose ps

# Check network connectivity
docker exec campus_runner_backend ping backend

# Re-initialize database
docker-compose exec backend python backend/init_db.py
```

### Port conflicts

```bash
# Find process using port
netstat -tuln | grep 5000
lsof -i :5000

# Use different port in docker-compose
# Change: "5000:5000" to "5001:5000"
```

### Performance issues

```bash
# Monitor resource usage
docker stats --no-stream

# Check image size
docker images campus_runner

# Prune unused images/containers/volumes
docker system prune -a --volumes
```

---

## Additional Resources

- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Flask Deployment](https://flask.palletsprojects.com/en/latest/deploying/)
