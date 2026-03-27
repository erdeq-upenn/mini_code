"""SQLite persistence layer."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from .models import ValuationResult

DEFAULT_DB_PATH = Path(__file__).parents[3] / "data" / "option_valuator.db"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS valuations (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at        TEXT    NOT NULL,
    ticker            TEXT    NOT NULL,
    quote_date        TEXT    NOT NULL,
    expiry_date       TEXT    NOT NULL,
    option_type       TEXT    NOT NULL,
    spot              REAL    NOT NULL,
    strike            REAL    NOT NULL,
    risk_free_rate    REAL    NOT NULL,
    option_price      REAL    NOT NULL,
    time_to_expiry    REAL    NOT NULL,
    implied_vol       REAL    NOT NULL,
    theoretical_price REAL    NOT NULL,
    delta                   REAL    NOT NULL,
    gamma                   REAL    NOT NULL,
    theta                   REAL    NOT NULL,
    vega                    REAL    NOT NULL,
    rho                     REAL    NOT NULL,
    seller_collateral       REAL    NOT NULL,
    seller_simple_return    REAL    NOT NULL,
    seller_annualized_return REAL   NOT NULL
);
"""


def _connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Path = DEFAULT_DB_PATH) -> None:
    with _connect(db_path) as conn:
        conn.executescript(_SCHEMA)


def insert_valuation(result: ValuationResult, db_path: Path = DEFAULT_DB_PATH) -> int:
    init_db(db_path)
    row = result.model_dump()
    row["quote_date"] = str(row["quote_date"])
    row["expiry_date"] = str(row["expiry_date"])
    cols = ", ".join(k for k in row if k != "id")
    placeholders = ", ".join("?" for k in row if k != "id")
    values = [v for k, v in row.items() if k != "id"]
    with _connect(db_path) as conn:
        cur = conn.execute(f"INSERT INTO valuations ({cols}) VALUES ({placeholders})", values)
        return cur.lastrowid


def fetch_history(limit: int = 20, db_path: Path = DEFAULT_DB_PATH) -> list[dict]:
    init_db(db_path)
    with _connect(db_path) as conn:
        rows = conn.execute(
            "SELECT * FROM valuations ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
    return [dict(r) for r in rows]
