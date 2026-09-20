"""SQLite persistence: profiles, completed activities, market updates, history.

Every function accepts an optional ``db_path`` so tests can use a temporary
database. If omitted, the ``CAREER_DB_PATH`` environment variable is used,
falling back to ``career_navigator.db`` in the project folder.
"""
from __future__ import annotations

import json
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone

DEFAULT_DB = "career_navigator.db"


def _path(db_path: str | None = None) -> str:
    return str(db_path or os.environ.get("CAREER_DB_PATH", DEFAULT_DB))


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@contextmanager
def _connect(db_path: str | None = None):
    conn = sqlite3.connect(_path(db_path))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db(db_path: str | None = None) -> None:
    with _connect(db_path) as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS profiles (
                name TEXT PRIMARY KEY,
                data TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS progress (
                profile_name TEXT NOT NULL,
                resource_id TEXT NOT NULL,
                skill TEXT,
                completed_at TEXT NOT NULL,
                PRIMARY KEY (profile_name, resource_id)
            );
            CREATE TABLE IF NOT EXISTS market_updates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                career TEXT NOT NULL,
                skill TEXT NOT NULL,
                importance INTEGER NOT NULL,
                required INTEGER NOT NULL,
                note TEXT DEFAULT '',
                created_at TEXT NOT NULL,
                UNIQUE (career, skill)
            );
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_name TEXT NOT NULL,
                match_pct REAL NOT NULL,
                recorded_at TEXT NOT NULL
            );
            """
        )


# ---------------------------------------------------------------- profiles
def save_profile(profile: dict, db_path: str | None = None) -> None:
    name = profile["name"].strip()
    now = _now()
    with _connect(db_path) as conn:
        conn.execute(
            """
            INSERT INTO profiles (name, data, created_at, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET data = excluded.data, updated_at = excluded.updated_at
            """,
            (name, json.dumps(profile), now, now),
        )


def load_profile(name: str, db_path: str | None = None) -> dict | None:
    with _connect(db_path) as conn:
        row = conn.execute("SELECT data FROM profiles WHERE name = ?", (name.strip(),)).fetchone()
    return json.loads(row["data"]) if row else None


def list_profiles(db_path: str | None = None) -> list[str]:
    with _connect(db_path) as conn:
        rows = conn.execute("SELECT name FROM profiles ORDER BY updated_at DESC").fetchall()
    return [r["name"] for r in rows]


def get_profile_created_at(name: str, db_path: str | None = None) -> datetime | None:
    with _connect(db_path) as conn:
        row = conn.execute("SELECT created_at FROM profiles WHERE name = ?", (name.strip(),)).fetchone()
    return datetime.fromisoformat(row["created_at"]) if row else None


def delete_profile(name: str, db_path: str | None = None) -> None:
    with _connect(db_path) as conn:
        for table, column in (("profiles", "name"), ("progress", "profile_name"), ("history", "profile_name")):
            conn.execute(f"DELETE FROM {table} WHERE {column} = ?", (name.strip(),))


# ---------------------------------------------------------------- progress
def mark_completed(name: str, resource_id: str, skill: str | None = None, db_path: str | None = None) -> None:
    with _connect(db_path) as conn:
        conn.execute(
            "INSERT OR IGNORE INTO progress (profile_name, resource_id, skill, completed_at) VALUES (?, ?, ?, ?)",
            (name.strip(), resource_id, skill, _now()),
        )


def unmark_completed(name: str, resource_id: str, db_path: str | None = None) -> None:
    with _connect(db_path) as conn:
        conn.execute(
            "DELETE FROM progress WHERE profile_name = ? AND resource_id = ?", (name.strip(), resource_id)
        )


def get_completed(name: str, db_path: str | None = None) -> set[str]:
    with _connect(db_path) as conn:
        rows = conn.execute("SELECT resource_id FROM progress WHERE profile_name = ?", (name.strip(),)).fetchall()
    return {r["resource_id"] for r in rows}


def reset_progress(name: str, db_path: str | None = None) -> None:
    with _connect(db_path) as conn:
        conn.execute("DELETE FROM progress WHERE profile_name = ?", (name.strip(),))
        conn.execute("DELETE FROM history WHERE profile_name = ?", (name.strip(),))


# ---------------------------------------------------------- market updates
def add_market_update(
    career: str, skill: str, importance: int, required: int, note: str = "", db_path: str | None = None
) -> None:
    with _connect(db_path) as conn:
        conn.execute(
            """
            INSERT INTO market_updates (career, skill, importance, required, note, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(career, skill) DO UPDATE SET
                importance = excluded.importance, required = excluded.required, note = excluded.note
            """,
            (career, skill, int(importance), int(required), note, _now()),
        )


def get_market_updates(career: str | None = None, db_path: str | None = None) -> list[dict]:
    with _connect(db_path) as conn:
        if career:
            rows = conn.execute("SELECT * FROM market_updates WHERE career = ? ORDER BY id", (career,)).fetchall()
        else:
            rows = conn.execute("SELECT * FROM market_updates ORDER BY id").fetchall()
    return [dict(r) for r in rows]


def clear_market_updates(career: str | None = None, db_path: str | None = None) -> None:
    with _connect(db_path) as conn:
        if career:
            conn.execute("DELETE FROM market_updates WHERE career = ?", (career,))
        else:
            conn.execute("DELETE FROM market_updates")


# ----------------------------------------------------------------- history
def record_history(name: str, match_pct: float, db_path: str | None = None) -> None:
    with _connect(db_path) as conn:
        conn.execute(
            "INSERT INTO history (profile_name, match_pct, recorded_at) VALUES (?, ?, ?)",
            (name.strip(), float(match_pct), _now()),
        )


def get_history(name: str, db_path: str | None = None) -> list[dict]:
    with _connect(db_path) as conn:
        rows = conn.execute(
            "SELECT match_pct, recorded_at FROM history WHERE profile_name = ? ORDER BY id", (name.strip(),)
        ).fetchall()
    return [dict(r) for r in rows]
