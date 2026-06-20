"""Per-client persistence: saved suppliers and message-builder presets.

Scoped by an opaque client_id the browser generates and stores locally — a
lightweight "account" without registration. Same SQLite file as the query cache.
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "cache.sqlite3"


def _connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS saved (
            client_id  TEXT NOT NULL,
            name       TEXT NOT NULL,
            supplier   TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now')),
            PRIMARY KEY (client_id, name)
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS presets (
            client_id  TEXT NOT NULL,
            name       TEXT NOT NULL,
            preset     TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now')),
            PRIMARY KEY (client_id, name)
        )
        """
    )
    return conn


# ---- saved suppliers -------------------------------------------------------

def list_saved(client_id: str) -> list[dict[str, Any]]:
    conn = _connect()
    try:
        rows = conn.execute(
            "SELECT supplier FROM saved WHERE client_id = ? ORDER BY created_at DESC",
            (client_id,),
        ).fetchall()
    finally:
        conn.close()
    return [json.loads(r[0]) for r in rows]


def save_supplier(client_id: str, supplier: dict[str, Any]) -> None:
    conn = _connect()
    try:
        conn.execute(
            """
            INSERT INTO saved (client_id, name, supplier) VALUES (?, ?, ?)
            ON CONFLICT(client_id, name) DO UPDATE SET supplier = excluded.supplier
            """,
            (client_id, supplier.get("name", ""), json.dumps(supplier, ensure_ascii=False)),
        )
        conn.commit()
    finally:
        conn.close()


def delete_saved(client_id: str, name: str) -> None:
    conn = _connect()
    try:
        conn.execute(
            "DELETE FROM saved WHERE client_id = ? AND name = ?", (client_id, name)
        )
        conn.commit()
    finally:
        conn.close()


# ---- message presets -------------------------------------------------------

def list_presets(client_id: str) -> list[dict[str, Any]]:
    conn = _connect()
    try:
        rows = conn.execute(
            "SELECT preset FROM presets WHERE client_id = ? ORDER BY created_at DESC",
            (client_id,),
        ).fetchall()
    finally:
        conn.close()
    return [json.loads(r[0]) for r in rows]


def save_preset(client_id: str, preset: dict[str, Any]) -> None:
    conn = _connect()
    try:
        conn.execute(
            """
            INSERT INTO presets (client_id, name, preset) VALUES (?, ?, ?)
            ON CONFLICT(client_id, name) DO UPDATE SET preset = excluded.preset
            """,
            (client_id, preset.get("name", ""), json.dumps(preset, ensure_ascii=False)),
        )
        conn.commit()
    finally:
        conn.close()


def delete_preset(client_id: str, name: str) -> None:
    conn = _connect()
    try:
        conn.execute(
            "DELETE FROM presets WHERE client_id = ? AND name = ?", (client_id, name)
        )
        conn.commit()
    finally:
        conn.close()
