.PHONY: help up down build rebuild logs test clean

help: ## Show this help message
	@echo "StudyMate Development Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

up: ## Start all services
	cd deploy && docker compose up -d

down: ## Stop all services
	cd deploy && docker compose down

build: ## Build all services
	cd deploy && docker compose build

rebuild: ## Rebuild and start all services
	cd deploy && docker compose up -d --build

logs: ## Show logs for all services
	cd deploy && docker compose logs -f

logs-api: ## Show API logs
	cd deploy && docker compose logs -f api

logs-ui: ## Show frontend logs
	cd deploy && docker compose logs -f ui

logs-db: ## Show database logs
	cd deploy && docker compose logs -f db

test: ## Run backend tests
	cd deploy && docker compose exec api pytest

test-backend: ## Run backend tests with coverage
	cd deploy && docker compose exec api pytest --cov=app --cov-report=html

migrate: ## Run database migrations
	cd deploy && docker compose exec api alembic upgrade head

migrate-create: ## Create new migration (usage: make migrate-create name=migration_name)
	cd deploy && docker compose exec api alembic revision --autogenerate -m "$(name)"

shell: ## Open shell in API container
	cd deploy && docker compose exec api bash

shell-ui: ## Open shell in frontend container
	cd deploy && docker compose exec ui sh

clean: ## Clean up containers, images, and volumes
	cd deploy && docker compose down -v --rmi all
	docker system prune -f

install-deps: ## Install frontend dependencies
	cd frontend && npm install

dev-frontend: ## Start frontend in development mode
	cd frontend && npm run dev

dev-backend: ## Start backend in development mode
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

status: ## Show service status
	cd deploy && docker compose ps

restart: ## Restart all services
	cd deploy && docker compose restart

restart-api: ## Restart API service
	cd deploy && docker compose restart api

restart-ui: ## Restart frontend service
	cd deploy && docker compose restart ui
