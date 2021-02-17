# We like colors
# From: https://coderwall.com/p/izxssa/colored-makefile-for-golang-projects
RED=`tput setaf 1`
GREEN=`tput setaf 2`
RESET=`tput sgr0`
YELLOW=`tput setaf 3`

# Vars
POETRY ?= poetry

help: ## This help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	$(POETRY) install --no-dev

install-dev: ## Install DEV dependencies
	$(POETRY) install

format: ## Format with isort and black
	$(POETRY) run isort opencoverage tests
	$(POETRY) run black opencoverage tests

lint: ## Run isort, black and flake8
	$(POETRY) run isort --check-only opencoverage tests
	$(POETRY) run black --check opencoverage tests
	$(POETRY) run flake8 --config setup.cfg opencoverage tests

mypy:
	$(POETRY) run mypy -p opencoverage

test-dev: ## Run pytest against DEV environment
	$(POETRY) run pytest tests --env=.env.dev

test: ## Run pytest
	$(POETRY) run pytest tests

coverage: ## Create coverage report
	$(POETRY) run pytest -v tests -s --tb=native -v --cov=opencoverage --cov-report xml

coverage-dev: ## Create coverage report for DEV environment
	$(POETRY) run pytest -v tests -s --tb=native -v --cov=opencoverage --cov-report xml --env=.env.dev

send-codecov:
	$(POETRY) run codecov --url="https://open-coverage.org/api" --token=- --slug=vangheem/opencoverage --file=coverage.xml -F project:api

run: ## Run Open Coverage
	$(POETRY) run opencoverage

run-dev: ## Run Open Coverage DEV environment
	$(POETRY) run opencoverage -e .env.dev


.PHONY: clean install test coverage run run-dev help
