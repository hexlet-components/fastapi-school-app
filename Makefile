PORT ?= 8000

setup: install build-css

install:
	uv sync
	pnpm install

build-css:
	pnpm run build:css

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
