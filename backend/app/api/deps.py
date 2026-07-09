"""Shared FastAPI dependencies for the /api/v1 routers."""

from typing import Annotated

from fastapi import Depends, HTTPException, Query, Request

from app.config import get_settings
from app.schemas.common import ListFilters
from app.services.auth import Principal, load_session

PeriodQuery = Annotated[str | None, Query(description="YYYY-MM")]


def list_filters(
    contract: str | None = None,
    source: str | None = None,
    care_type: str | None = None,
    period: PeriodQuery = None,
) -> ListFilters:
    """Common list filters (docs/05 §5): contract, source, care_type, period."""
    return ListFilters(contract=contract, source=source, care_type=care_type, period=period)


FiltersDep = Annotated[ListFilters, Depends(list_filters)]


# ---------------------------------------------------------------------------
# Auth (EPIC G1) — resolve the request principal from a signed session cookie
# or the service-token header. The cookie carries the identity payload, so no
# DB round-trip is needed to authenticate.
# ---------------------------------------------------------------------------

def get_principal(request: Request) -> Principal | None:
    settings = get_settings()
    token = request.headers.get("X-Service-Token")
    if token and token == settings.service_token:
        return Principal(
            user_id=None, username="service", name="Қызмет",
            role="admin", is_service=True,
        )
    cookie = request.cookies.get(settings.session_cookie)
    if cookie:
        return load_session(cookie)
    return None


OptionalPrincipal = Annotated[Principal | None, Depends(get_principal)]


def require_principal(principal: OptionalPrincipal) -> Principal:
    if principal is None:
        raise HTTPException(status_code=401, detail="кіру қажет")
    return principal


CurrentPrincipal = Annotated[Principal, Depends(require_principal)]


def deny_curator(principal: OptionalPrincipal) -> None:
    """Curator sees only aggregates — 403 on patient/case-level routes (docs/13 §3).

    Anonymous and service principals pass (headless scripts, smoke tests); only a
    logged-in curator is denied.
    """
    if principal is not None and principal.is_curator:
        raise HTTPException(
            status_code=403,
            detail="куратор рөлі жиынтық деректерді ғана көреді (жеке жағдайлар жабық)",
        )


DenyCurator = Depends(deny_curator)
