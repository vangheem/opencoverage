POETRY ?= poetry

install:
	$(POETRY) install 

format:
	$(POETRY) run isort .
	$(POETRY) run black .

lint:
	$(POETRY) run isort --check-only .
	$(POETRY) run black --check .
	$(POETRY) run flake8 --config setup.cfg

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
	$(POETRY) run codecov --url="http://localhost:8000" --token=foobar --slug=vangheem/opencoverage

run:
	$(POETRY) run opencoverage

run-dev:
	$(POETRY) run opencoverage -e .env.dev


.PHONY: clean install test coverage run run-dev
