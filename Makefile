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

test:
	$(POETRY) run pytest tests

coverage:
	$(POETRY) run coverage run -m pytest -v tests/ --junitxml=build/test.xml
	$(POETRY) run coverage xml -i -o build/coverage.xml
	$(POETRY) run coverage report

run:
	$(POETRY) run opencoverage

run-dev:
	$(POETRY) run opencoverage -e .env.dev


.PHONY: clean install test coverage run run-dev
