.PHONY: help build dev prod logs stop clean test lint up

# ============================================================================
# Campus Runner - Makefile for Docker Commands
# ============================================================================

help:
	@echo "Campus Runner - Docker Commands"
	@echo "=================================="
	@echo ""
	@echo "Development:"
	@echo "  make dev              Start development environment (with hot reload)"
	@echo "  make logs             Show real-time logs from all services"
	@echo "  make stop             Stop running services"
	@echo "  make clean            Remove containers, networks (keep volumes)"
	@echo ""
	@echo "Production:"
	@echo "  make prod             Start production environment"
	@echo ""
	@echo "Building & Testing:"
	@echo "  make build            Build Docker images"
	@echo "  make build-no-cache   Build Docker images without cache"
	@echo "  make test-backend     Run backend tests in container"
	@echo "  make test-frontend    Run frontend tests in container"
	@echo "  make lint             Run linters (backend + frontend)"
	@echo ""
	@echo "Database:"
	@echo "  make db-init          Initialize database"
	@echo "  make db-seed          Seed database with sample data"
	@echo "  make db-backup        Backup database"
	@echo ""
	@echo "Utilities:"
	@echo "  make shell-backend    Open shell in backend container"
	@echo "  make shell-frontend   Open shell in frontend container"
	@echo "  make ps               Show running containers"
	@echo "  make health           Check service health"
	@echo "  make prune            Remove unused Docker resources"

# ========================================================================
# Development
# ========================================================================

dev:
	@echo "Starting development environment..."
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
	@echo "✅ Development environment started!"
	@echo "Frontend: http://localhost:5173 (with hot reload)"
	@echo "Backend: http://localhost:5000"
	@echo "API Docs: http://localhost:5000/api/docs"

dev-logs:
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml logs -f

up:
	docker-compose up -d

logs:
	docker-compose logs -f

stop:
	@echo "Stopping services..."
	docker-compose stop
	@echo "✅ Services stopped"

clean:
	@echo "Removing containers and networks..."
	docker-compose down
	@echo "✅ Cleaned! (volumes preserved)"

clean-all:
	@echo "Removing containers, networks, and volumes..."
	docker-compose down -v
	@echo "✅ Full cleanup complete"

# ========================================================================
# Production
# ========================================================================

prod:
	@echo "Starting production environment..."
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml pull
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
	@echo "✅ Production environment started!"
	@echo "Frontend: http://localhost:8080"
	@echo "Backend: http://localhost:5000"

prod-logs:
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml logs -f

prod-stop:
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml down

# ========================================================================
# Building & Testing
# ========================================================================

build:
	@echo "Building Docker images..."
	docker-compose build
	@echo "✅ Build complete"

build-no-cache:
	@echo "Building Docker images (no cache)..."
	docker-compose build --no-cache
	@echo "✅ Build complete"

test-backend:
	@echo "Running backend tests..."
	docker-compose exec backend pytest backend/tests/ -v --cov=backend --cov-report=html
	@echo "✅ Backend tests complete (coverage: htmlcov/index.html)"

test-frontend:
	@echo "Running frontend tests..."
	docker-compose exec frontend npm run test
	@echo "✅ Frontend tests complete"

test: test-backend test-frontend
	@echo "✅ All tests passed"

lint:
	@echo "Running linters..."
	docker-compose exec backend flake8 backend/ --max-complexity=10 --max-line-length=127
	docker-compose exec frontend npm run lint
	docker-compose exec frontend npm run typecheck
	@echo "✅ Linting complete"

# ========================================================================
# Database
# ========================================================================

db-init:
	@echo "Initializing database..."
	docker-compose exec backend python backend/init_db.py
	@echo "✅ Database initialized"

db-seed:
	@echo "Seeding database..."
	docker-compose exec backend python backend/seed.py
	@echo "✅ Database seeded"

db-migrate:
	@echo "Running database migrations..."
	docker-compose exec backend python backend/init_db.py
	@echo "✅ Migrations complete"

db-backup:
	@echo "Backing up database..."
	docker-compose exec -T backend tar -czf - instance/ > backup-$$(date +%Y%m%d_%H%M%S).tar.gz
	@echo "✅ Backup created: backup-$$(date +%Y%m%d_%H%M%S).tar.gz"

# ========================================================================
# Utilities
# ========================================================================

shell-backend:
	docker-compose exec backend bash

shell-frontend:
	docker-compose exec frontend sh

ps:
	docker-compose ps

status:
	@echo "Service Status:"
	@docker-compose ps
	@echo ""
	@echo "Resource Usage:"
	@docker stats --no-stream

health:
	@echo "Checking health endpoints..."
	@echo "Backend: "
	@curl -s http://localhost:5000/api/health || echo "❌ Unreachable"
	@echo ""
	@echo "Frontend: "
	@curl -s http://localhost:8080/health || echo "❌ Unreachable"

prune:
	@echo "Cleaning up Docker resources..."
	docker system prune -a --volumes -f
	@echo "✅ Cleanup complete"

# ========================================================================
# Admin Commands
# ========================================================================

admin-create:
	@echo "Creating admin user..."
	docker-compose exec backend python backend/create_admin.py

install-deps:
	@echo "Installing dependencies..."
	docker-compose exec backend pip install -r backend/requirements.txt
	docker-compose exec frontend npm ci

update-deps:
	@echo "Updating dependencies..."
	docker-compose exec backend pip install --upgrade -r backend/requirements.txt
	docker-compose exec frontend npm update

# ========================================================================
# Git Hooks (Optional)
# ========================================================================

install-hooks:
	@echo "Installing git hooks..."
	@chmod +x .githooks/pre-commit
	git config core.hooksPath .githooks
	@echo "✅ Git hooks installed"

# ========================================================================
# Stats & Info
# ========================================================================

images:
	@echo "Docker Images:"
	docker images --format "table {{.Repository}}\t{{.Size}}"

version:
	@echo "Component Versions:"
	@docker-compose exec backend python --version
	@docker-compose exec frontend node --version
	@docker-compose exec frontend npm --version
