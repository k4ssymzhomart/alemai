"""IGERIM API entrypoint.

Starts without a database: the SQLAlchemy engine is created lazily in
``app.db`` and nothing connects on import or startup (docs/05 §7).
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import api_router
from app.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="Clinic-side control loop for ГОБМП/ОСМС contracts (docs/04).",
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @application.get("/healthz", tags=["health"])
    def healthz() -> dict[str, str]:
        return {"status": "ok"}

    application.include_router(api_router, prefix=settings.api_v1_prefix)
    return application


app = create_app()
