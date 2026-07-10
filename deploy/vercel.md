# Vercel — QALAM frontend (docs/25 H5)

Vercel hosts the **frontend only** (Next.js). The FastAPI backend + Postgres
live on Render (`render.yaml` at the repo root) — Vercel can't run the API, the
seed job, or a database.

## Import

1. Vercel → **Add New… → Project** → import this repo.
2. **Root Directory: `frontend/`** (important — the Next app is not at the repo
   root). Framework preset auto-detects **Next.js**.
3. **Environment Variables:**
   - `NEXT_PUBLIC_API_BASE = https://<your-render-app>.onrender.com/api/v1`
4. **Deploy.**

## After both are up

- Copy the Vercel production URL (e.g. `https://qalam.vercel.app`).
- On Render, set the API's `CORS_ORIGINS` to that URL (comma-separated for
  multiple), then redeploy the API — session cookies are cross-origin and need
  the exact origin allow-listed (`allow_credentials=true` forbids `*`).

`deploy/vercel.json` (framework/build/install) can be dropped at the repo root or
kept here for reference — with Root Directory set to `frontend/`, Vercel's
Next.js preset already does the right thing.
