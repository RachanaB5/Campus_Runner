# Campus Runner - Docker Quick Reference

## 🚀 Quick Start

```bash
# Copy environment file
cp .env.example .env

# Start development environment (with hot reload)
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Start production environment
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# View logs
docker-compose logs -f
```

## 📦 Common Docker Commands

### Build & Run

```bash
# Build images
docker-compose build

# Rebuild without cache
docker-compose build --no-cache

# Start services in background
docker-compose up -d

# Start services in foreground (see logs)
docker-compose up

# Stop services
docker-compose stop

# Stop and remove containers, networks (keeps volumes)
docker-compose down

# Stop and remove containers, networks, volumes
docker-compose down -v
```

### Logs & Inspection

```bash
# View logs for all services
docker-compose logs

# View logs for specific service
docker-compose logs backend
docker-compose logs frontend

# Follow logs in real-time
docker-compose logs -f

# View logs from last 50 lines
docker-compose logs --tail=50

# View logs with timestamps
docker-compose logs -t

# Stream logs from specific time
docker-compose logs --since 2024-04-14T10:00:00
```

### Running Commands in Containers

```bash
# Execute command in running container
docker-compose exec backend python backend/init_db.py
docker-compose exec backend pytest backend/tests/

# Run one-off container
docker-compose run --rm backend python backend/init_db.py
```

### Database Management

```bash
# Initialize database
docker-compose exec backend python backend/init_db.py

# Create admin user
docker-compose exec backend python backend/create_admin.py

# Seed database
docker-compose exec backend python backend/seed.py

# Backup database
docker-compose exec -T backend tar -czf - instance/ > backup-$(date +%s).tar.gz

# Restore database
tar -xzf backup-timestamp.tar.gz
docker cp instance/. campus_runner_backend:/app/instance/
```

### Development Workflows

```bash
# Run backend tests
docker-compose exec backend pytest backend/tests/ -v --cov=backend

# Run frontend tests
docker-compose exec frontend npm test

# Type check frontend
docker-compose exec frontend npm run typecheck

# Lint frontend
docker-compose exec frontend npm run lint

# Lint backend with flake8
docker-compose exec backend flake8 backend/

# Build frontend
docker-compose exec frontend npm run build
```

## 🔍 Monitoring & Debugging

### Health Checks

```bash
# Check if services are running
docker-compose ps

# Test backend health
curl http://localhost:5000/api/health

# Test frontend health
curl http://localhost:8080/health

# Check container logs for errors
docker-compose logs | grep -i error
```

### Resource Usage

```bash
# Monitor resource usage
docker stats

# Get CPU and memory usage
docker ps --format "table {{.Names}}\t{{.CPUPerc}}\t{{.MemUsage}}"

# Inspect container details
docker inspect campus_runner_backend

# View container processes
docker top campus_runner_backend
```

### Network Debugging

```bash
# Check network
docker network ls
docker network inspect campus_runner_network

# Test inter-container connectivity
docker exec campus_runner_frontend ping backend

# Check open ports
docker port campus_runner_backend
docker port campus_runner_frontend
```

## 🐛 Troubleshooting

### Container won't start

```bash
# Check logs
docker-compose logs backend
docker logs campus_runner_backend

# Run container interactively
docker-compose run --rm backend bash

# Rebuild and start with verbose output
docker-compose up backend --no-detach
```

### Port conflicts

```bash
# Find process using port
lsof -i :5000
lsof -i :8080
netstat -tuln | grep LISTEN

# Change port mapping in docker-compose.yml
# From: "5000:5000" to "5001:5000"
```

### Database issues

```bash
# Re-initialize database
docker-compose exec backend python backend/init_db.py

# Check database file
docker exec campus_runner_backend ls -la instance/

# Backup and remove database
docker exec campus_runner_backend tar -czf /tmp/backup.tar.gz instance/
docker exec campus_runner_backend rm instance/campusrunner.db

# Restart to recreate
docker-compose restart backend
```

### Cleanup & Maintenance

```bash
# Remove unused images
docker image prune

# Remove unused networks
docker network prune

# Remove unused volumes
docker volume prune

# Remove unused images, containers, networks, volumes
docker system prune -a --volumes

# Check disk usage
docker system df
```

## 📊 Image & Container Management

### Image Operations

```bash
# List images
docker images

# List images with size
docker images --format "table {{.Repository}}\t{{.Size}}"

# Remove unused images
docker image prune

# Remove specific image
docker rmi ghcr.io/username/campus-runner/backend:latest

# Save image as tar
docker save campus_runner_backend -o backend.tar

# Load image from tar
docker load -i backend.tar

# Tag image
docker tag campus_runner_backend:latest ghcr.io/username/campus-runner/backend:1.0.0

# Push to registry
docker push ghcr.io/username/campus-runner/backend:1.0.0
```

### Container Operations

```bash
# List containers (running)
docker ps

# List all containers
docker ps -a

# List containers with size
docker ps -as

# Stop all containers
docker stop $(docker ps -q)

# Remove all stopped containers
docker container prune

# Rename container
docker rename old_name new_name

# Copy files from container
docker cp campus_runner_backend:/app/instance/data.db ./backup/

# Copy files to container
docker cp ./config.env campus_runner_backend:/app/.env
```

## 🔒 Security

### Run as Non-Root

```bash
# Both images run as non-root users by default
# Backend: appuser (UID 1000)
# Frontend: nginx (UID 1001)
```

### Network Security

```bash
# Internal network only (no outside access)
docker network inspect campus_runner_network

# Only exposed ports: 5000 (backend), 8080 (frontend)
```

### Environment Security

```bash
# Never commit .env file
git status | grep "\.env"

# Use GitHub Secrets for CI/CD
# Add to .github/workflows/ci.yml:
env:
  JWT_SECRET_KEY: ${{ secrets.JWT_SECRET_KEY }}
```

## 📈 Performance

### Layer Caching

```bash
# Multi-stage builds optimize layer caching
# Rebuilds only affected stages

# Check image layers
docker inspect campus_runner_backend | jq '.[0].RootFS.Layers'

# Check build cache
docker system df -v
```

### Image Size

```bash
# Backend: ~200MB (Python + dependencies)
# Frontend: ~30MB (Nginx + built app)

# Compare with original sizes
docker history campus_runner_backend
docker history campus_runner_frontend
```

## 🚢 Deployment

### Production Deployment

```bash
# Pull latest images
docker-compose -f docker-compose.yml -f docker-compose.prod.yml pull

# Start containers
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Verify services
docker-compose -f docker-compose.yml -f docker-compose.prod.yml ps

# Check health
curl https://yourdomain.com/health
curl https://yourdomain.com/api/health
```

### Rollback

```bash
# Stop current version
docker-compose down

# Pull specific version
docker pull ghcr.io/username/campus-runner/backend:v1.0.0

# Update docker-compose.yml with version tag

# Start previous version
docker-compose up -d
```

## 📚 Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Campus Runner DEVOPS.md](./DEVOPS.md) - Comprehensive guide
