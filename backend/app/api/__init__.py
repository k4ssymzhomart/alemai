"""Router aggregation for /api/v1 (docs/05 §5)."""

from fastapi import APIRouter

from app.api import (
    admin,
    alerts,
    anomalies,
    auth,
    city,
    contracts,
    copilot,
    documents,
    events,
    exports,
    forecasts,
    imports,
    metrics,
    objections,
    ops,
    radar,
    reconcile,
    reports,
    risks,
    rules,
)

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(events.router)
api_router.include_router(imports.router)
api_router.include_router(exports.router)
api_router.include_router(contracts.router)
api_router.include_router(metrics.router)
api_router.include_router(reconcile.router)
api_router.include_router(rules.router)
api_router.include_router(objections.router)
api_router.include_router(forecasts.router)
api_router.include_router(risks.router)
api_router.include_router(alerts.router)
api_router.include_router(anomalies.router)
api_router.include_router(copilot.router)
api_router.include_router(documents.router)
api_router.include_router(reports.router)
api_router.include_router(city.router)
api_router.include_router(admin.router)
api_router.include_router(ops.router)
api_router.include_router(radar.router)
