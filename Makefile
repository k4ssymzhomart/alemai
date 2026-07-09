# IGERIM — hackathon monorepo make targets (docs/05 §1: `make up seed reset demo`)

.PHONY: up down logs seed reset demo-reset demo eval-copilot fmt lint

## Bring up the whole stack (db + api + web), rebuilding images
up:
	docker compose up -d --build

## Stop and remove containers (volumes are kept)
down:
	docker compose down

## Tail logs from all services
logs:
	docker compose logs -f

## Seed the database inside the api container (migrations + datagen + COPY + MV refresh)
seed:
	docker compose exec api python -m app.seed

reset: demo-reset

## Deterministic demo reset (<60s): re-seed the full gp14 dataset + verify.
## seed is idempotent (TRUNCATE + COPY) with a fixed RNG, so this restores the
## exact demo state mid-presentation if anything gets clicked into a bad place.
demo-reset:
	@start=$$(date +%s); \
	docker compose exec -T api python -m app.seed >/dev/null && \
	docker compose exec -T api sh -c 'M=$$(find / -name manifest.json 2>/dev/null | grep igerim_seed | head -1); python scripts/assert_seed_integrity.py "$$M" >/dev/null' && \
	echo "demo-reset OK — full gp14 restored + integrity green in $$(( $$(date +%s) - start ))s"

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
