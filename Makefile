.PHONY: help install install-backend install-frontend \
        dev dev-backend dev-frontend \
        test lint build clean

# ── Colours ──────────────────────────────────────────────────────────────────
CYAN  := \033[0;36m
RESET := \033[0m

help: ## Show this help message
	@echo ""
	@echo "  Sports League Scoreboard"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  $(CYAN)%-20s$(RESET) %s\n", $$1, $$2}'
	@echo ""

# ── Install ───────────────────────────────────────────────────────────────────
install: install-backend install-frontend ## Install all dependencies

install-backend: ## Install backend dependencies (uv sync)
	cd backend && uv sync --all-groups

install-frontend: ## Install frontend dependencies (npm install)
	cd frontend && npm install

# ── Dev servers ───────────────────────────────────────────────────────────────
dev: ## Run both backend and frontend dev servers in parallel
	@$(MAKE) -j2 dev-backend dev-frontend

dev-backend: ## Run the FastAPI backend (uvicorn, port 8000)
	cd backend && uv run uvicorn app.main:app --reload --port 8000

dev-frontend: ## Run the Vite frontend dev server (port 5173)
	cd frontend && npm run dev

# ── Test ──────────────────────────────────────────────────────────────────────
test: ## Run backend tests with pytest
	cd backend && uv run pytest -v

# ── Lint ──────────────────────────────────────────────────────────────────────
lint: ## Lint the frontend with oxlint
	cd frontend && npm run lint

# ── Build ─────────────────────────────────────────────────────────────────────
build: ## Build the frontend for production
	cd frontend && npm run build

# ── Clean ─────────────────────────────────────────────────────────────────────
clean: ## Remove build artefacts
	rm -rf frontend/dist
	find backend -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find backend -name "*.pyc" -delete 2>/dev/null || true
