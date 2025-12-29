.PHONY: help install dev test lint format clean docker-up docker-down migrate

help:  ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install dependencies
	python3.11 -m venv venv
	. venv/bin/activate && pip install --upgrade pip
	. venv/bin/activate && pip install -r requirements.txt
	. venv/bin/activate && pre-commit install

dev:  ## Run development server
	. venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:  ## Run tests with coverage
	. venv/bin/activate && pytest

lint:  ## Run linting checks
	. venv/bin/activate && flake8 app/
	. venv/bin/activate && mypy app/

format:  ## Format code with black and isort
	. venv/bin/activate && black app/
	. venv/bin/activate && isort app/

clean:  ## Clean up generated files
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.coverage" -delete
	rm -rf .pytest_cache htmlcov .mypy_cache

docker-up:  ## Start Docker containers
	docker-compose up -d

docker-down:  ## Stop Docker containers
	docker-compose down

docker-logs:  ## View Docker logs
	docker-compose logs -f

migrate:  ## Run database migrations
	. venv/bin/activate && alembic upgrade head

migrate-create:  ## Create new migration
	. venv/bin/activate && alembic revision --autogenerate -m "$(name)"

migrate-rollback:  ## Rollback last migration
	. venv/bin/activate && alembic downgrade -1

db-shell:  ## Open PostgreSQL shell
	docker-compose exec postgres psql -U autoflow -d autoflow

pre-commit:  ## Run pre-commit hooks on all files
	. venv/bin/activate && pre-commit run --all-files
