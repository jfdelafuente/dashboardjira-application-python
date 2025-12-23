# Support Team Dashboard - Makefile
# Simplifies common Docker and development commands

.PHONY: help build up down restart logs shell test clean migrate seed

# Default target
.DEFAULT_GOAL := help

help: ## Show this help message
	@echo "Support Team Dashboard - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Docker Commands
build: ## Build Docker images
	docker-compose build

up: ## Start all services in detached mode
	docker-compose up -d

up-dev: ## Start services in development mode with hot-reload
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

down: ## Stop all services
	docker-compose down

restart: ## Restart all services
	docker-compose restart

logs: ## View logs from all services
	docker-compose logs -f

logs-app: ## View logs from app service only
	docker-compose logs -f app

ps: ## Show running containers
	docker-compose ps

# Application Commands
shell: ## Open Python shell in app container
	docker-compose exec app flask shell

bash: ## Open bash shell in app container
	docker-compose exec app bash

db-shell: ## Open PostgreSQL shell
	docker-compose exec db psql -U dashboard_user -d support_dashboard

redis-cli: ## Open Redis CLI
	docker-compose exec redis redis-cli -a changeme_in_production

# Database Commands
migrate: ## Run database migrations
	docker-compose exec app flask db upgrade

migrate-create: ## Create new migration (usage: make migrate-create MSG="description")
	docker-compose exec app flask db migrate -m "$(MSG)"

migrate-downgrade: ## Rollback last migration
	docker-compose exec app flask db downgrade

seed: ## Seed database with sample data
	docker-compose exec app python scripts/seed_data.py --issues 50 --clear

# Testing Commands
test: ## Run all tests inside container
	docker-compose exec app pytest tests/ -v

test-unit: ## Run unit tests only
	docker-compose exec app pytest tests/unit/ -v

test-integration: ## Run integration tests only
	docker-compose exec app pytest tests/integration/ -v

test-coverage: ## Run tests with coverage report
	docker-compose exec app pytest tests/ --cov=app --cov-report=html --cov-report=term

lint: ## Run linting (flake8)
	docker-compose exec app flake8 app/ --max-line-length=100

format: ## Format code with black
	docker-compose exec app black app/ tests/ scripts/

# Cleanup Commands
clean: ## Remove all containers, volumes, and images
	docker-compose down -v --remove-orphans
	docker system prune -f

clean-volumes: ## Remove only volumes (WARNING: deletes database data)
	docker-compose down -v

# Production Commands
prod-up: ## Start services in production mode
	docker-compose --profile production up -d

prod-logs: ## View production logs
	docker-compose --profile production logs -f

prod-down: ## Stop production services
	docker-compose --profile production down

# Development Commands
dev-setup: build up migrate seed ## Complete development setup
	@echo "Development environment ready!"
	@echo "Access dashboard at: http://localhost:5000"

dev-reset: clean dev-setup ## Reset development environment

# Monitoring Commands
stats: ## Show container resource usage
	docker stats

inspect-app: ## Inspect app container
	docker-compose exec app env

health: ## Check health of all services
	@echo "Checking service health..."
	@docker-compose ps
	@echo ""
	@echo "App health:"
	@curl -f http://localhost:5000/api/kpis || echo "App not responding"

# Backup Commands
backup-db: ## Backup PostgreSQL database
	docker-compose exec -T db pg_dump -U dashboard_user support_dashboard > backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "Database backup created: backup_$$(date +%Y%m%d_%H%M%S).sql"

restore-db: ## Restore PostgreSQL database (usage: make restore-db FILE=backup.sql)
	docker-compose exec -T db psql -U dashboard_user -d support_dashboard < $(FILE)

# Quick Commands
quick-start: ## Quick start for first-time setup
	@echo "Starting Support Team Dashboard..."
	@cp .env.docker .env 2>/dev/null || true
	@$(MAKE) build
	@$(MAKE) up
	@echo "Waiting for services to start..."
	@sleep 10
	@$(MAKE) migrate
	@$(MAKE) seed
	@echo ""
	@echo "Dashboard is ready!"
	@echo "Access at: http://localhost:5000"
	@echo ""
	@echo "Default credentials:"
	@echo "  Database: dashboard_user / changeme_in_production"
	@echo "  Redis: changeme_in_production"

stop-all: ## Stop all Docker containers (not just this project)
	docker stop $$(docker ps -q)
