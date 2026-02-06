##
# Linting
lint: lint-logger lint-config lint-auth

lint-logger:
	cd packages/logger && uv run ruff check --fix

lint-config:
	cd packages/config && uv run ruff check --fix

lint-auth:
	cd packages/auth && uv run ruff check --fix

##
# Format
format: format-logger format-config format-auth

format-logger:
	cd packages/logger && uv run ruff format .

format-config:
	cd packages/config && uv run ruff format .

format-auth:
	cd packages/auth && uv run ruff format .


##
# Testing
test: test-logger test-config test-auth

test-logger:
	cd packages/logger && uv run pytest -xvs

test-config:
	cd packages/config && uv run pytest -xvs

test-auth:
	cd packages/auth && uv run pytest -xvs
