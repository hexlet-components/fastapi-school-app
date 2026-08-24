PORT ?= 8000

install:
	uv sync

dev:
	uv run fastapi dev app/main.py --port $(PORT)

start:
	uv run fastapi run app/main.py --port $(PORT)

lint:
	uv run ruff check .
	uv run ruff format --check .

lint-fix:
	uv run ruff check --fix .
	uv run ruff format .

.PHONY: test
test:
	uv run pytest
