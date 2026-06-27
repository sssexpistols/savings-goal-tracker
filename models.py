"""
models.py — MetaModel y AbonoModel (CRUD)
"""
import sqlite3
from typing import Optional


class MetaModel:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def create(self, nombre: str, objetivo: float,
               prioridad: str, fecha_limite: Optional[str]) -> dict:
        cur = self.conn.execute(
            """INSERT INTO metas (nombre, objetivo, prioridad, fecha_limite)
               VALUES (?, ?, ?, ?)""",
            (nombre.strip(), round(objetivo, 2), prioridad, fecha_limite),
        )
        self.conn.commit()
        return self.get_by_id(cur.lastrowid)

    def list_all(self) -> list:
        rows = self.conn.execute(
            "SELECT * FROM metas ORDER BY completada, prioridad DESC, id"
        ).fetchall()
        return [dict(r) for r in rows]

    def get_by_id(self, meta_id: int) -> Optional[dict]:
        row = self.conn.execute(
            "SELECT * FROM metas WHERE id = ?", (meta_id,)
        ).fetchone()
        return dict(row) if row else None

    def complete(self, meta_id: int) -> None:
        self.conn.execute(
            "UPDATE metas SET completada = 1 WHERE id = ?", (meta_id,)
        )
        self.conn.commit()

    def delete(self, meta_id: int) -> None:
        self.conn.execute("DELETE FROM metas WHERE id = ?", (meta_id,))
        self.conn.commit()


class AbonoModel:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def create(self, meta_id: int, monto: float, nota: str = "") -> dict:
        cur = self.conn.execute(
            "INSERT INTO abonos (meta_id, monto, nota) VALUES (?, ?, ?)",
            (meta_id, round(monto, 2), nota.strip()),
        )
        self.conn.commit()
        row = self.conn.execute(
            "SELECT * FROM abonos WHERE id = ?", (cur.lastrowid,)
        ).fetchone()
        return dict(row)

    def list_by_meta(self, meta_id: int) -> list:
        rows = self.conn.execute(
            "SELECT * FROM abonos WHERE meta_id = ? ORDER BY fecha DESC",
            (meta_id,),
        ).fetchall()
        return [dict(r) for r in rows]

    def total_ahorrado(self, meta_id: int) -> float:
        row = self.conn.execute(
            "SELECT COALESCE(SUM(monto), 0) FROM abonos WHERE meta_id = ?",
            (meta_id,),
        ).fetchone()
        return round(row[0], 2)
