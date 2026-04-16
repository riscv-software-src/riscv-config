# Makefile for riscv-config project

.PHONY: help test test-coverage clean install-test

help: ## Show this help message
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install-test: ## Install test dependencies
	pip install pytest pytest-cov

test: ## Run all tests
	pytest tests/test_constants.py -v

test-coverage: ## Run tests with coverage report
	python -W ignore::SyntaxWarning -m pytest tests/test_constants.py --cov=riscv_config --cov-report=html
	@echo "Coverage report generated in htmlcov/index.html"

test-coverage-constants: ## Run tests with coverage for constants module only
	pytest tests/test_constants.py --cov=riscv_config.constants --cov-report=html --cov-report=term-missing
	@echo "Focused coverage report for constants module"

clean: ## Clean up generated files
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf __pycache__/
	rm -rf tests/__pycache__/
	rm -rf riscv_config/__pycache__/
	find . -name "*.pyc" -delete
	find . -name ".coverage" -delete
