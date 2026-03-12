import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "tickets.db"


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=wal")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db() -> None:
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tickets (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                subject     TEXT    NOT NULL,
                description TEXT    NOT NULL,
                priority    TEXT    NOT NULL DEFAULT 'medium',
                status      TEXT    NOT NULL DEFAULT 'open'
            )
            """
        )


def create_ticket(subject: str, description: str, priority: str = "medium") -> dict:
    with _connect() as conn:
        cursor = conn.execute(
            "INSERT INTO tickets (subject, description, priority) VALUES (?, ?, ?)",
            (subject, description, priority),
        )
        return get_ticket(cursor.lastrowid)  # type: ignore[arg-type]


def list_tickets() -> list[dict]:
    with _connect() as conn:
        rows = conn.execute("SELECT * FROM tickets").fetchall()
        return [dict(row) for row in rows]


def get_ticket(ticket_id: int) -> dict | None:
    with _connect() as conn:
        row = conn.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,)).fetchone()
        return dict(row) if row else None


def delete_ticket(ticket_id: int) -> bool:
    with _connect() as conn:
        cursor = conn.execute("DELETE FROM tickets WHERE id = ?", (ticket_id,))
        return cursor.rowcount > 0
