"""Seed-on-boot for cloud deploys (EPIC H5) — idempotent, never blocks startup.

Runs migrations, then seeds auth users + reference data (deadlines, radar) on an
EMPTY database so a fresh Render instance boots with a working login. The full
synthetic dataset (claims) still needs ``python -m app.seed`` with datagen
present — the public URL is for jury follow-up, not the stage (docs/25 H5).
"""

from __future__ import annotations

import os

from sqlalchemy import text

from app.db import get_engine


def bootstrap_on_boot() -> None:
    """No-op unless SEED_ON_BOOT=1. Failures are swallowed so the API still serves."""
    if os.environ.get("SEED_ON_BOOT") != "1":
        return
    try:
        from app.seed import run_migrations, seed_deadlines, seed_users
        from app.services.radar import seed_initial as seed_radar

        run_migrations()
        engine = get_engine()
        with engine.begin() as conn:
            seeded = conn.execute(text("SELECT count(*) FROM users")).scalar_one()
            if seeded:
                print("bootstrap: DB already seeded — SEED_ON_BOOT skip")
                return
            seed_users(conn)
            seed_deadlines(conn)
            seed_radar(conn)
        print("bootstrap: SEED_ON_BOOT — seeded users + reference data")
    except Exception as exc:  # noqa: BLE001 — never block the app from serving
        print(f"bootstrap: SEED_ON_BOOT skipped ({type(exc).__name__}: {exc})")
