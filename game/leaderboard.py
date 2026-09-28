"""SQLite 로컬 리더보드. (Streamlit Community Cloud 는 재시작 시 파일이 초기화될 수 있음)"""

import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "leaderboard.db"


def _conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.execute(
        """CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            officer TEXT NOT NULL,
            mode TEXT NOT NULL,
            score INTEGER NOT NULL,
            processed INTEGER NOT NULL,
            accuracy REAL NOT NULL,
            caught INTEGER NOT NULL,
            created_at TEXT NOT NULL
        )"""
    )
    return con


def add_score(officer: str, mode: str, score: int, processed: int, accuracy: float, caught: int) -> None:
    with _conn() as con:
        con.execute(
            "INSERT INTO scores (officer, mode, score, processed, accuracy, caught, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (officer[:20], mode, score, processed, accuracy, caught, datetime.now().strftime("%Y-%m-%d %H:%M")),
        )


def top_scores(mode: str, limit: int = 20) -> list[dict]:
    with _conn() as con:
        con.row_factory = sqlite3.Row
        rows = con.execute(
            "SELECT officer, score, processed, accuracy, caught, created_at FROM scores WHERE mode = ? ORDER BY score DESC, accuracy DESC LIMIT ?",
            (mode, limit),
        ).fetchall()
    return [dict(r) for r in rows]
