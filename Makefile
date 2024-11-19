.PHONY: pre-commit-install install clean clean-build clean-pyc clean-test clean-misc check-lint lint unit-tests integration-tests prepare-integration-tests tests

# install pre-commit
pre-commit-install:
	uvx pre-commit install

# install dependencies
install: clean pre-commit-install
	uv sync


# remove all build, test, coverage and Python artifacts
clean: clean-build clean-pyc clean-test clean-misc

# remove build artifacts
clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr wheelhouse/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

# remove Python file artifacts
clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

# remove test and coverage artifacts
clean-test:
	rm -f .coverage
	rm -f coverage.xml
	rm -rf htmlcov/
	rm -rf .tox/
	rm -rf .pytest_cache/

# remove other artifacts
clean-misc:
	rm -rf .ruff_cache/
	rm -rf .mypy_cache/

# check the linting of the project
check-lint:
	uv run ruff check .
	uv run ruff format --check .

# perform the linting on the project
lint:
	uv run ruff check --fix .
	uv run ruff format .

# run unit tests
unit-tests: install
	uv run pytest --collect-only --no-cov -m "not integration"; EXITCODE=$$?; \
	if [ $$EXITCODE = 0 ]; then uv run pytest -vv -s -m "not integration"; \
	elif [ $$EXITCODE = 5 ]; then true; \
	else exit $$EXITCODE; \
	fi

# prepare integration test
prepare-integration-tests: install

# run integration tests
integration-tests: prepare-integration-tests
	uv run pytest --collect-only --no-cov -m "integration"; EXITCODE=$$?; \
	if [ $$EXITCODE = 0 ]; then uv run pytest -vv --no-cov -s -m "integration"; \
	elif [ $$EXITCODE = 5 ]; then true; \
	else exit $$EXITCODE; \
	fi

# run all tests
tests: unit-tests integration-tests
