.PHONY: help install run dev clean test format lint

# Variables
PYTHON := python3
VENV := env
PIP := $(VENV)/bin/pip
UVICORN := $(VENV)/bin/uvicorn
MAIN := main:app
HOST := 0.0.0.0
PORT := 8000

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install dependencies
	@if [ ! -d "$(VENV)" ]; then \
		$(PYTHON) -m venv $(VENV); \
	fi
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

run: ## Run the FastAPI server
	$(UVICORN) $(MAIN) --host $(HOST) --port $(PORT)

dev: ## Run the FastAPI server in development mode with auto-reload
	$(UVICORN) $(MAIN) --host $(HOST) --port $(PORT) --reload

clean: ## Clean up cache files and __pycache__ directories
	find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} + 2>/dev/null || true
	@echo "Cleaned up cache files"
