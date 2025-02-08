# https://github.com/casey/just

dev-sync:
    uv sync --all-extras

prod-sync:
	uv sync --all-extras --no-dev

format:
	uv run ruff format

lint:
	uv run ruff check --fix
	uv run mypy --ignore-missing-imports --install-types --non-interactive --package python_repo_template

test:
	uv run pytest --verbose --color=yes tests

# Use it like:
# just run 10
run number:
	uv run main.py --number {{number}}