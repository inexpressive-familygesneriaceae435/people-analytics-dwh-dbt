.PHONY: help install dev generate-data dbt-deps dbt-seed dbt-run dbt-test dbt-docs dbt-all lint format type-check test test-cov clean docker-build docker-up docker-down

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install production dependencies
	pip install -r requirements.txt

dev: ## Install dev dependencies
	pip install -r requirements-dev.txt

generate-data: ## Generate synthetic HR data (CSVs → data/raw/ + dbt seeds)
	python -m src.generate_data

dbt-deps: ## Install dbt packages
	cd dbt_project && dbt deps

dbt-seed: ## Load CSV seeds into DuckDB
	cd dbt_project && dbt seed --target dev

dbt-run: ## Run all dbt models
	cd dbt_project && dbt run --target dev

dbt-test: ## Run all dbt tests
	cd dbt_project && dbt test --target dev

dbt-docs: ## Generate dbt documentation site
	cd dbt_project && dbt docs generate --target dev

dbt-docs-serve: ## Serve dbt docs locally (port 8080)
	cd dbt_project && dbt docs serve --port 8080

dbt-all: dbt-deps dbt-seed dbt-run dbt-test ## Full dbt pipeline: deps → seed → run → test

pipeline: generate-data dbt-all ## Full pipeline: generate data → dbt build

lint: ## Run ruff linter
	ruff check src/ tests/

format: ## Auto-format with ruff
	ruff format src/ tests/
	ruff check --fix src/ tests/

type-check: ## Run mypy type checker
	mypy src/ --ignore-missing-imports

test: ## Run Python tests
	pytest tests/ -v

test-cov: ## Run Python tests with coverage
	pytest tests/ -v --cov=src --cov-report=term-missing --cov-report=html

clean: ## Remove generated artifacts
	rm -rf data/raw/*.csv data/seeds/*.csv dbt_project/seeds/*.csv
	rm -rf dbt_project/target/ dbt_project/dbt_packages/ dbt_project/logs/
	rm -rf data/*.duckdb data/*.duckdb.wal
	rm -rf htmlcov/ .coverage __pycache__ .pytest_cache .mypy_cache .ruff_cache

docker-build: ## Build Docker image
	docker compose build

docker-up: ## Start services
	docker compose up -d

docker-down: ## Stop services
	docker compose down -v
