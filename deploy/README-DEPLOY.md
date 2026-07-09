# QALAM — Deployment (docs/25 H5)

**The venue demo runs LOCAL `docker compose` regardless of any of this.** The
public URLs below are for jury follow-up after the pitch — never the thing on
stage (offline-safe law). One command for the stage:

```bash
make demo && make seed     # or: docker compose up -d --build && make seed
```

Answer to «Vercel alone?» — **no**: Vercel can't host FastAPI + Postgres + the
seed job. The working split is **Vercel (frontend) + Render (backend + DB)**.

---

## Backend + DB → Render (Blueprint)

1. Render → **New → Blueprint** → pick this repo. Render reads
   [`deploy/render.yaml`](./render.yaml) and provisions:
   - a managed **Postgres** (`qalam-db`),
   - the **API** web service (`./backend/Dockerfile`, health `/healthz`),
   - `DATABASE_URL` wired from the DB, `SECRET_KEY`/`SERVICE_TOKEN` generated,
     `SEED_ON_BOOT=1`.
2. **Apply.** On first boot the API runs migrations and seeds the 5 login users
   + reference data (radar, deadlines) so login works immediately.
   - `DATABASE_URL` arrives as a bare `postgres://` string; the app coerces it to
     `postgresql+psycopg://` (`app/db.py:normalize_database_url`) — nothing to edit.
   - **Full synthetic dataset** (claims, the 60.8% / 46-позиций numbers) is NOT
     seeded on boot (datagen isn't in the backend image). To load it on the
     hosted DB: `render ssh` into the service → `python -m app.seed` (needs the
     datagen dir), or point a one-off job at the DB. For jury follow-up the
     login + empty-state app is usually enough; say so.
3. After the frontend is up (below), set the API's **`CORS_ORIGINS`** to the
   Vercel origin and redeploy.

## Frontend → Vercel

See [`deploy/vercel.md`](./vercel.md). TL;DR: import the repo with **Root
Directory `frontend/`**, set `NEXT_PUBLIC_API_BASE=https://<render-app>.onrender.com/api/v1`,
deploy.

## Alternative — Railway (all-in-one)

Railway can run backend + Postgres + a static frontend in one project if you
prefer a single dashboard:

1. New Project → **Deploy from repo**.
2. Add a **PostgreSQL** plugin → it injects `DATABASE_URL`.
3. Backend service: root `backend/`, Dockerfile build, set `CORS_ORIGINS`,
   `SEED_ON_BOOT=1`, generate `SECRET_KEY`/`SERVICE_TOKEN`. Health `/healthz`.
4. Frontend service: root `frontend/`, `npm run build`, env
   `NEXT_PUBLIC_API_BASE=https://<backend>.up.railway.app/api/v1`.

Same driver-coercion + CORS notes as Render apply.

## Verified for this pack

- `NEXT_PUBLIC_API_BASE=https://example.invalid/api/v1 npm run build` → green
  (no localhost hardcodes; the API base is env-driven).
- API boots with `SEED_ON_BOOT=1` on a fresh DB (migrations + login/reference
  seed); idempotent on a seeded DB (skips).
- `CORS_ORIGINS` is read from the environment (comma-separated).
