# IGERIM — hackathon monorepo make targets (docs/05 §1: `make up seed reset demo`)

.PHONY: up down logs seed reset demo eval-copilot fmt lint

## Bring up the whole stack (db + api + web), rebuilding images
up:
	docker compose up -d --build

## Stop and remove containers (volumes are kept)
down:
	docker compose down

## Tail logs from all services
logs:
	docker compose logs -f

## Seed the database inside the api container (falls back honestly until app.seed lands)
seed:
	docker compose exec api python -m app.seed || echo "seed: app.seed not implemented yet (backend agent will add it)"

## Restore the pg_dump demo snapshot (<60s per docs/05 §7) — wired to POST /admin/demo-reset later
reset:
	@echo "reset: not implemented yet — will invoke backend demo-reset (POST /api/v1/admin/demo-reset)"

## One command to demo-readiness: stack up + seeded data
demo: up seed

## Run the copilot eval set (docs/07 §6, target >=22/24)
eval-copilot:
	@echo "eval-copilot: not implemented yet — will run backend copilot eval set (docs/07 §6)"

## Format backend code
fmt:
	ruff format backend

## Lint backend (ruff) and frontend (eslint via npm)
lint:
	ruff check backend && cd frontend && npm run lint
