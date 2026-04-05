# ─────────────────────────────────────────────────────────
# Video Script Writer – Makefile
# ─────────────────────────────────────────────────────────

.PHONY: install test test-cov lint run web clean help

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	pip install -r requirements.txt

install-dev: ## Install with dev dependencies
	pip install -e ".[dev]"

test: ## Run tests
	pytest tests/ -v

test-cov: ## Run tests with coverage
	pytest tests/ -v --cov=video_script --cov-report=term-missing

lint: ## Run basic linting checks
	python -m py_compile src/video_script/core.py
	python -m py_compile src/video_script/cli.py
	python -m py_compile src/video_script/web_ui.py

run: ## Run CLI (use ARGS, e.g. make run ARGS="--topic 'Python Tips'")
	python src/video_script/cli.py $(ARGS)

web: ## Launch Streamlit web UI
	streamlit run src/video_script/web_ui.py

clean: ## Clean caches and build artifacts
	rm -rf __pycache__ .pytest_cache build dist *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
