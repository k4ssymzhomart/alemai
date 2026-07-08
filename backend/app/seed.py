"""Seed the database from datagen output — ``python -m app.seed``.

Pipeline: ``alembic upgrade head`` → run datagen (same interpreter, unless
``--skip-generate``) → TRUNCATE data tables CASCADE → COPY CSVs via psycopg
(FK-safe order, one transaction) → REFRESH mv_line_execution → VACUUM ANALYZE
claims → verify per-table row counts against ``manifest.json``.

The datagen manifest stays at ``<out>/manifest.json`` (default
``/tmp/igerim_seed/manifest.json``) — ``scripts/assert_seed_integrity.py``
reads control sums from there.

Idempotent: re-running produces the same row counts (truncate before load).
Nothing here runs at import time — the API keeps booting without a database.

Usage:
    python -m app.seed [--datagen-dir D] [--out O] [--sample] [--skip-generate]

Datagen dir resolution: --datagen-dir > $DATAGEN_DIR > /datagen (container
volume) > <repo>/datagen (host checkout).
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

from alembic import command as alembic_command
from alembic.config import Config as AlembicConfig
from sqlalchemy import text
from sqlalchemy.engine import Connection

from app.db import get_engine
from app.services.metrics.refresh import refresh_line_execution

BACKEND_DIR = Path(__file__).resolve().parents[1]
REPO_DIR = BACKEND_DIR.parent
DEFAULT_OUT_DIR = Path("/tmp/igerim_seed")

# FK-safe load order; each name is both the CSV stem and the table name.
# service_group_map (service_code → service_group) has no FKs and feeds the
# fact-side join in mv_line_execution — the datagen emits it (МРТ line, EPIC B).
LOAD_ORDER: tuple[str, ...] = (
    "organizations",
    "contracts",
    "contract_versions",
    "contract_lines",
    "service_group_map",
    "patients",
    "doctors",
    "claims",
    "forecasts",
    "risk_assessments",
)

# All model data tables — truncated before every load so reseeding is idempotent.
DATA_TABLES: tuple[str, ...] = (
    "alerts",
    "audit_log",
    "claims",
    "contract_lines",
    "contract_versions",
    "contracts",
    "deadlines",
    "doctors",
    "findings",
    "forecasts",
    "import_files",
    "organizations",
    "package_mapping",
    "patients",
    "quarantine_rows",
    "reg_chunks",
    "reg_documents",
    "risk_assessments",
    "rule_runs",
    "rules",
    "service_group_map",
    "users",
)


def resolve_datagen_dir(cli_value: Path | None) -> Path:
    """CLI arg > env DATAGEN_DIR > /datagen (container) > <repo>/datagen (host)."""
    if cli_value is not None:
        return cli_value
    env_value = os.environ.get("DATAGEN_DIR")
    if env_value:
        return Path(env_value)
    container_dir = Path("/datagen")
    if (container_dir / "generate.py").exists():
        return container_dir
    return REPO_DIR / "datagen"


def run_migrations() -> None:
    """``alembic upgrade head`` with config resolution that works from any cwd."""
    config = AlembicConfig(str(BACKEND_DIR / "alembic.ini"))
    alembic_command.upgrade(config, "head")


def run_datagen(datagen_dir: Path, out_dir: Path, sample: bool) -> None:
    """Run generate.py with the current interpreter, writing CSVs into out_dir."""
    generate = datagen_dir / "generate.py"
    if not generate.exists():
        raise FileNotFoundError(f"datagen script not found: {generate}")
    cmd = [
        sys.executable,
        str(generate),
        "--config",
        str(datagen_dir / "config.yaml"),
        "--out",
        str(out_dir),
    ]
    if sample:
        cmd.append("--sample")
    subprocess.run(cmd, check=True)


def copy_table(connection: Connection, table: str, csv_path: Path) -> int:
    """COPY one CSV into a table (psycopg fast path); returns rows copied."""
    driver_connection = connection.connection.driver_connection  # psycopg.Connection
    with csv_path.open("r", encoding="utf-8", newline="") as fh:
        columns = fh.readline().strip().split(",")  # headers are plain identifiers
        sql = f"COPY {table} ({', '.join(columns)}) FROM STDIN WITH (FORMAT csv)"
        with driver_connection.cursor() as cursor:
            with cursor.copy(sql) as copy:
                while chunk := fh.read(1 << 20):
                    copy.write(chunk)
            return cursor.rowcount


def load_tables(connection: Connection, out_dir: Path) -> dict[str, int]:
    """Truncate all data tables, then COPY the datagen CSVs in FK-safe order."""
    connection.execute(text(f"TRUNCATE {', '.join(DATA_TABLES)} CASCADE"))
    copied: dict[str, int] = {}
    for table in LOAD_ORDER:
        started = time.monotonic()
        copied[table] = copy_table(connection, table, out_dir / f"{table}.csv")
        print(f"seed: COPY {table}: {copied[table]:,} rows in {time.monotonic() - started:.1f}s")
    return copied


def verify_counts(connection: Connection, expected_rows: dict[str, int]) -> bool:
    """Compare live per-table counts to the manifest; print a report."""
    ok = True
    for table in LOAD_ORDER:
        actual = connection.execute(text(f"SELECT count(*) FROM {table}")).scalar_one()
        expected = int(expected_rows[table])
        status = "OK" if actual == expected else "MISMATCH"
        if actual != expected:
            ok = False
        print(f"seed: {table:<20} db={actual:>10,}  manifest={expected:>10,}  {status}")
    return ok


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--datagen-dir", type=Path, default=None,
                        help="datagen directory (default: $DATAGEN_DIR, /datagen, <repo>/datagen)")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT_DIR,
                        help=f"datagen output directory (default: {DEFAULT_OUT_DIR})")
    parser.add_argument("--sample", action="store_true",
                        help="quick run: ~1k claims, small patient sample")
    parser.add_argument("--skip-generate", action="store_true",
                        help="reuse existing CSVs + manifest.json in --out")
    args = parser.parse_args(argv)

    started = time.monotonic()
    datagen_dir = resolve_datagen_dir(args.datagen_dir)
    out_dir: Path = args.out

    print("seed: alembic upgrade head")
    run_migrations()

    if args.skip_generate:
        print(f"seed: --skip-generate, reusing CSVs in {out_dir}")
    else:
        print(f"seed: generating data ({datagen_dir} -> {out_dir})")
        run_datagen(datagen_dir, out_dir, args.sample)

    manifest_path = out_dir / "manifest.json"
    if not manifest_path.exists():
        print(f"seed: FAIL — manifest not found: {manifest_path}", file=sys.stderr)
        return 1
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    engine = get_engine()
    # One transaction: truncate + load + MV refresh commit atomically.
    with engine.begin() as connection:
        load_tables(connection, out_dir)
        print("seed: REFRESH MATERIALIZED VIEW mv_line_execution")
        refresh_line_execution(connection)

    with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as connection:
        connection.execute(text("VACUUM ANALYZE claims"))
    print("seed: VACUUM ANALYZE claims done")

    with engine.connect() as connection:
        counts_ok = verify_counts(connection, manifest["rows"])
        mv_rows = connection.execute(
            text("SELECT count(*) FROM mv_line_execution")
        ).scalar_one()
    print(f"seed: mv_line_execution rows: {mv_rows:,}")
    print(f"seed: manifest at {manifest_path}")

    elapsed = time.monotonic() - started
    if not counts_ok:
        print(f"seed: FAIL — row counts do not match manifest ({elapsed:.1f}s)", file=sys.stderr)
        return 1
    print(f"seed: DONE in {elapsed:.1f}s (mode={manifest['mode']}, seed={manifest['seed']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
