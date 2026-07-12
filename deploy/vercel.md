# Vercel — QALAM frontend (docs/25 H5)

Vercel hosts the **frontend only** (Next.js). The FastAPI backend + Postgres
live on Render (`render.yaml` at the repo root) — Vercel can't run the API, the
seed job, or a database.

## Import

1. Vercel → **Add New… → Project** → import this repo.
2. **Root Directory: `frontend/`** (important — the Next app is not at the repo
   root). Framework preset auto-detects **Next.js**.
3. **Environment Variables** (⚠️ the #1 gotcha — set this BEFORE the build):
   - `NEXT_PUBLIC_API_BASE = https://qalam-api.onrender.com/api/v1`
   - It is a **build-time** var (Next.js inlines `NEXT_PUBLIC_*` into the client
     bundle), so setting it later has **no effect until you redeploy**. If it is
     missing, the bundle falls back to `http://localhost:8800/api/v1` — which
     both points at nothing in production and is blocked as **mixed content**
     (an HTTPS page cannot call `http://`). Symptom: login does nothing / network
     error in the console.
4. **Deploy.** (After changing this env var later, **Redeploy** — do not just
   "Redeploy from existing build"; force a fresh build so the new value inlines.)

## After both are up

- Copy the Vercel production URL (e.g. `https://qalam.vercel.app`).
- On Render, set the API's `CORS_ORIGINS` to that URL (comma-separated for
  multiple), then redeploy the API — session cookies are cross-origin and need
  the exact origin allow-listed (`allow_credentials=true` forbids `*`).

`deploy/vercel.json` (framework/build/install) can be dropped at the repo root or
kept here for reference — with Root Directory set to `frontend/`, Vercel's
Next.js preset already does the right thing.
