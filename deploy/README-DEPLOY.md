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

### Free-tier caveats (current default in `render.yaml`)

Both resources are `plan: free` so the Blueprint applies at **zero cost**, even on
a workspace whose card is declined (the "Payment failed" state). Know these:

- **One free Postgres per workspace.** If the workspace already has a free DB, the
  Blueprint sync collides — **delete the existing free DB** in the Render dashboard
  first, or `qalam-db` won't provision.
- **The free DB expires 30 days after creation** (with a 14-day grace to upgrade
  before data is deleted). Fine for the pitch — just don't be surprised on day 30+.
- **Free web spins down after 15 min idle** → first hit after idle is a ~30–60 s
  cold start. Warm it before sharing the link with a juror.
- **Legacy plans are rejected.** Since Render's Oct-2024 flexible-plans migration,
  `starter/standard/pro` can't back a NEW database. Valid DB instance types are
  `free`, `basic-256mb`, `basic-1gb`, `basic-4gb`, `pro-*`, `accelerated-*`.

**Upgrade path (once the card works / for production):** set the DB to
`plan: basic-256mb` (optional `diskSizeGB: 15`) and the web service to
`plan: starter` — no 30-day expiry, no cold starts. Both are left as inline
comments in `render.yaml`.

**Fallback — reuse an external Postgres (no Render DB at all):** if the card stays
blocked or you already run a DB, delete the whole `databases:` block from
`render.yaml`, change the web service's `DATABASE_URL` to `sync: false`, and paste a
free external connection string at deploy time. Supabase and Neon free tiers both
hand you a bare `postgres://…` and the app coerces the driver
(`app/db.py:normalize_database_url`). Do **not** add `ipAllowList` on the external
route — that field is for Render-managed DBs only.

> Lead action (not the agent's): the "Payment failed" banner is a workspace billing
> state — resolve it in the dashboard or deploy into a fresh free/Hobby workspace.
> This Blueprint is already valid + zero-cost, so it applies the moment the
> workspace is unblocked.

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
