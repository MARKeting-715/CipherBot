from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass(frozen=True)
class User:
    id: int
    telegram_id: int
    username: str | None
    created_at: str
    operations_count: int


@dataclass(frozen=True)
class HistoryRecord:
    id: int
    user_id: int
    operation_type: str
    algorithm: str
    input_text: str
    output_text: str
    created_at: str


class Database:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def init(self) -> None:
        with self.connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_id INTEGER NOT NULL UNIQUE,
                    username TEXT,
                    created_at TEXT NOT NULL,
                    operations_count INTEGER NOT NULL DEFAULT 0
                );

                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    operation_type TEXT NOT NULL,
                    algorithm TEXT NOT NULL,
                    input_text TEXT NOT NULL,
                    output_text TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
                );
                """
            )

    def upsert_user(self, telegram_id: int, username: str | None) -> User:
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO users (telegram_id, username, created_at)
                VALUES (?, ?, ?)
                ON CONFLICT(telegram_id) DO UPDATE SET username = excluded.username
                """,
                (telegram_id, username, utc_now()),
            )
            row = conn.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,)).fetchone()
        return self._user(row)

    def get_user(self, telegram_id: int) -> User | None:
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,)).fetchone()
        return self._user(row) if row else None

    def add_history(
        self,
        telegram_id: int,
        operation_type: str,
        algorithm: str,
        input_text: str,
        output_text: str,
    ) -> int:
        user = self.get_user(telegram_id)
        if user is None:
            raise ValueError("User must be registered before adding history.")

        with self.connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO history (user_id, operation_type, algorithm, input_text, output_text, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (user.id, operation_type, algorithm, input_text, output_text, utc_now()),
            )
            conn.execute(
                "UPDATE users SET operations_count = operations_count + 1 WHERE id = ?",
                (user.id,),
            )
            return int(cur.lastrowid)

    def list_history(self, telegram_id: int, page: int, page_size: int = 5) -> tuple[list[HistoryRecord], int]:
        user = self.get_user(telegram_id)
        if user is None:
            return [], 0

        with self.connect() as conn:
            total = conn.execute("SELECT COUNT(*) FROM history WHERE user_id = ?", (user.id,)).fetchone()[0]
            rows = conn.execute(
                """
                SELECT * FROM history
                WHERE user_id = ?
                ORDER BY id DESC
                LIMIT ? OFFSET ?
                """,
                (user.id, page_size, max(page, 0) * page_size),
            ).fetchall()
        return [self._history(row) for row in rows], int(total)

    def get_history_record(self, telegram_id: int, record_id: int) -> HistoryRecord | None:
        user = self.get_user(telegram_id)
        if user is None:
            return None

        with self.connect() as conn:
            row = conn.execute(
                "SELECT * FROM history WHERE user_id = ? AND id = ?",
                (user.id, record_id),
            ).fetchone()
        return self._history(row) if row else None

    def delete_history_record(self, telegram_id: int, record_id: int) -> bool:
        user = self.get_user(telegram_id)
        if user is None:
            return False

        with self.connect() as conn:
            cur = conn.execute("DELETE FROM history WHERE user_id = ? AND id = ?", (user.id, record_id))
            return cur.rowcount > 0

    def clear_history(self, telegram_id: int) -> int:
        user = self.get_user(telegram_id)
        if user is None:
            return 0

        with self.connect() as conn:
            cur = conn.execute("DELETE FROM history WHERE user_id = ?", (user.id,))
            return cur.rowcount

    def export_history(self, telegram_id: int) -> list[dict[str, Any]]:
        user = self.get_user(telegram_id)
        if user is None:
            return []

        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT id, operation_type, algorithm, input_text, output_text, created_at
                FROM history
                WHERE user_id = ?
                ORDER BY id DESC
                """,
                (user.id,),
            ).fetchall()
        return [dict(row) for row in rows]

    def favorite_algorithm(self, telegram_id: int) -> str:
        user = self.get_user(telegram_id)
        if user is None:
            return "нет данных"

        with self.connect() as conn:
            row = conn.execute(
                """
                SELECT algorithm, COUNT(*) AS cnt
                FROM history
                WHERE user_id = ?
                GROUP BY algorithm
                ORDER BY cnt DESC, algorithm ASC
                LIMIT 1
                """,
                (user.id,),
            ).fetchone()
        return row["algorithm"] if row else "нет данных"

    @staticmethod
    def _user(row: sqlite3.Row) -> User:
        return User(
            id=row["id"],
            telegram_id=row["telegram_id"],
            username=row["username"],
            created_at=row["created_at"],
            operations_count=row["operations_count"],
        )

    @staticmethod
    def _history(row: sqlite3.Row) -> HistoryRecord:
        return HistoryRecord(
            id=row["id"],
            user_id=row["user_id"],
            operation_type=row["operation_type"],
            algorithm=row["algorithm"],
            input_text=row["input_text"],
            output_text=row["output_text"],
            created_at=row["created_at"],
        )
