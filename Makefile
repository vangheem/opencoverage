POETRY ?= poetry

install:
	$(POETRY) install --no-dev 

install-dev:
	$(POETRY) install

format:
	$(POETRY) run isort opencoverage tests
	$(POETRY) run black opencoverage tests

lint:
	$(POETRY) run isort --check-only opencoverage tests
	$(POETRY) run black --check opencoverage tests
	$(POETRY) run flake8 --config setup.cfg opencoverage tests

mypy:
	$(POETRY) run mypy -p opencoverage

test-dev:
	$(POETRY) run pytest tests --env=.env.dev

test:
	$(POETRY) run pytest tests

coverage:
	$(POETRY) run pytest -v tests -s --tb=native -v --cov=opencoverage --cov-report xml

coverage-dev:
	$(POETRY) run pytest -v tests -s --tb=native -v --cov=opencoverage --cov-report xml --env=.env.dev

send-codecov:
	$(POETRY) run codecov --url="https://open-coverage.org/api" --token=- --slug=vangheem/opencoverage --file=coverage.xml -F project:api

run:
	$(POETRY) run opencoverage

run-dev:
	$(POETRY) run opencoverage -e .env.dev


.PHONY: clean install test coverage run run-dev
