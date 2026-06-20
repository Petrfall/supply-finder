"""SQLite cache keyed by a hash of the normalized query.

Two jobs:
  1. Avoid paying for the same LLM web search twice.
  2. Let the demo work with no API key — pre-warmed queries are committed into
     the DB, so HR can open the prototype and get real answers offline.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Optional

from .models import ScoredSupplier, SearchRequest

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "cache.sqlite3"


def query_key(req: SearchRequest) -> str:
    payload = {
        "category": req.category.strip().lower(),
        "region": (req.region or "").strip().lower(),
        "needs_certificates": req.filters.needs_certificates,
        "keyword": (req.filters.keyword or "").strip().lower(),
        "lang": req.lang,
    }
    blob = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]


def _connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS query_cache (
            key        TEXT PRIMARY KEY,
            category   TEXT,
            region     TEXT,
            summary    TEXT,
            suppliers  TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        )
        """
    )
    return conn


def get(req: SearchRequest) -> Optional[tuple[list[ScoredSupplier], str | None]]:
    conn = _connect()
    try:
        row = conn.execute(
            "SELECT suppliers, summary FROM query_cache WHERE key = ?",
            (query_key(req),),
        ).fetchone()
    finally:
        conn.close()
    if not row:
        return None
    suppliers = [ScoredSupplier(**s) for s in json.loads(row[0])]
    return suppliers, row[1]


def put(
    req: SearchRequest, suppliers: list[ScoredSupplier], summary: str | None
) -> None:
    conn = _connect()
    try:
        conn.execute(
            """
            INSERT INTO query_cache (key, category, region, summary, suppliers)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(key) DO UPDATE SET
                summary = excluded.summary,
                suppliers = excluded.suppliers,
                created_at = datetime('now')
            """,
            (
                query_key(req),
                req.category,
                req.region or "",
                summary,
                json.dumps([s.model_dump() for s in suppliers], ensure_ascii=False),
            ),
        )
        conn.commit()
    finally:
        conn.close()
