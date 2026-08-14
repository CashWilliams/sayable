.PHONY: test lint

# Run test suite using uv in the repo.
test:
	uv run --extra dev pytest

lint:
	uv run --extra dev ruff check src tests scripts
