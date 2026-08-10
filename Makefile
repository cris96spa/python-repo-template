.PHONY: all $(MAKECMDGOALS)
DOC_PORT ?= 8031
PROJECT_NAME ?= python_repo_template
PYTHON_TARGETS ?= main.py $(PROJECT_NAME) tests utils $(wildcard diagrams)
help: # print all the available targets
	@echo "\nAvailable targets:\n"
	@grep -E '^[a-zA-Z_-]+:.*?# .*$$' $(MAKEFILE_LIST) | sed 's/:.*#/\t/' | column -t -s '	' ; echo

install: # install requirements without development dependencies
	uv sync

dev: install-dev  # install requirements with all dependencies that are needed for development
	uv run pre-commit install --install-hooks

install-uv: # install uv tool
	curl -LsSf https://astral.sh/uv/install.sh | sh

install-dev: # install dev dependencies
	uv sync --all-groups

install-test: # install test dependencies
	uv sync --group test

format: # format the code with the ruff tool
	uv run ruff format $(PYTHON_TARGETS)

format-check: # check the formatting code with ruff
	uv run ruff format --check $(PYTHON_TARGETS)

lint: # check the code style
	uv run ruff check $(PYTHON_TARGETS)

lint-fix: # check and fix the code style
	uv run ruff check --fix $(PYTHON_TARGETS)

lint-doc: # check the docstring style
	uv run flake8 $(PYTHON_TARGETS)

doc: # create the project documentation; Build and visualize documentation through a local server
	uv run properdocs serve -f properdocs.yml --dev-addr 0.0.0.0:$(DOC_PORT)

test: # launch the tests
	uv run pytest -v -n auto --junitxml=tests_report.xml --doctest-modules --cov=$(PROJECT_NAME) --cov-report xml:coverage.xml --durations=0 tests

pre-commit: # run pre-commit hooks
	uv run pre-commit run --all-files

install-diagrams: # install the optional diagram toolchain
	uv sync --extra diagrams

diagrams: # build every diagram
	$(MAKE) -C diagrams all

diagrams-clean: # remove generated diagram output
	$(MAKE) -C diagrams clean