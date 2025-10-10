.PHONY: lock-check lock-update test install lint format help

# Help target
help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Install dependencies
install: ## Install all dependencies
	poetry install

# Check if poetry.lock is up to date
lock-check: ## Check if poetry.lock is up to date with pyproject.toml
	@echo "🔒 Checking poetry lock file..."
	poetry lock --check

# Update poetry.lock file
lock-update: ## Update poetry.lock file
	@echo "🔄 Updating poetry.lock..."
	poetry lock
	@echo "✅ poetry.lock updated!"

# Run tests
test: ## Run all tests
	poetry run pytest

# Run linting
lint: ## Run linting and type checking
	poetry run black --check .
	poetry run ruff check .
	poetry run mypy .

# Format code
format: ## Format code with black and ruff
	poetry run black .
	poetry run ruff check . --fix

# Full check: lock, lint, test
check: lock-check lint test ## Run complete check (lock, lint, test)
	@echo "✅ All checks passed!"

# Update lock and run tests
update: lock-update test ## Update lock file and run tests
	@echo "✅ Lock file updated and tests pass!"
