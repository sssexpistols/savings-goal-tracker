"""
db.py — Inicialización SQLite para Savings Goal Tracker
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "ahorro.db"


def init_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS metas (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre       TEXT    NOT NULL,
            objetivo     REAL    NOT NULL,
            prioridad    TEXT    NOT NULL DEFAULT 'media',
            fecha_limite TEXT,
            completada   INTEGER NOT NULL DEFAULT 0,
            created_at   TEXT    NOT NULL DEFAULT (datetime('now','localtime'))
        );
        CREATE TABLE IF NOT EXISTS abonos (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            meta_id  INTEGER NOT NULL REFERENCES metas(id) ON DELETE CASCADE,
            monto    REAL    NOT NULL,
            nota     TEXT    NOT NULL DEFAULT '',
            fecha    TEXT    NOT NULL DEFAULT (date('now','localtime'))
        );
    """)
    conn.commit()
    return conn
