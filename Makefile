.PHONY: test

# Run test suite using uv in the repo.
test:
	uv run --extra dev pytest
