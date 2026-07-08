"""Refresh hook for mv_line_execution — call after imports, seed or rule runs.

The dashboard reads only the materialized view (docs/05 §4, NFR <2s), so every
write path that touches claims or contract_lines must call this afterwards.
"""

from sqlalchemy import text
from sqlalchemy.engine import Connection
from sqlalchemy.orm import Session


def refresh_line_execution(connection_or_session: Connection | Session) -> None:
    """Execute REFRESH MATERIALIZED VIEW mv_line_execution on the given handle.

    Accepts either a Core connection or an ORM session; the caller owns the
    transaction (commit/rollback).
    """
    connection_or_session.execute(text("REFRESH MATERIALIZED VIEW mv_line_execution"))
