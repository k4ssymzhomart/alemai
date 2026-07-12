# IGERIM — hackathon monorepo make targets (docs/05 §1: `make up seed reset demo`)

.PHONY: up down logs seed seed-remote reset demo-reset demo eval-copilot fmt lint

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

## Seed a REMOTE database (e.g. the hosted Render Postgres) with the FULL dataset.
## Data is generated locally in a throwaway api container (py3.12 + datagen mounted;
## no free-tier RAM limit) and COPYed to the remote DB over the network (~a few min).
## Idempotent (TRUNCATE + COPY). Requires Docker running + the EXTERNAL connection
## string from the Render dashboard (qalam-db -> Connect -> External Connection String).
## Usage:
##   make seed-remote DATABASE_URL='postgres://user:pass@dpg-xxxx.oregon-postgres.render.com/dbname'
## If it errors on SSL, append '?sslmode=require' to the URL. If it errors on disk,
## the free 1 GB DB is full — upgrade to basic-256mb (render.yaml) or use --sample.
seed-remote:
	@test -n "$(DATABASE_URL)" || { echo "ERROR: set DATABASE_URL to the Render EXTERNAL url"; exit 1; }
	docker compose run --rm --no-deps -e DATABASE_URL='$(DATABASE_URL)' api python -m app.seed

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
