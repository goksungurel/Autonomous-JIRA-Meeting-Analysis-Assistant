import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "meetings.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS meetings (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at  TEXT    NOT NULL,
                file_name   TEXT,
                transcript  TEXT,
                action_items TEXT,
                jira_output TEXT
            )
        """)


def save_meeting(file_name: str, transcript: str, action_items: str, jira_output: str) -> int:
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO meetings (created_at, file_name, transcript, action_items, jira_output)
            VALUES (?, ?, ?, ?, ?)
            """,
            (datetime.now().strftime("%Y-%m-%d %H:%M"), file_name, transcript, action_items, jira_output),
        )
        return cursor.lastrowid


def get_all_meetings():
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        return conn.execute(
            "SELECT id, created_at, file_name, action_items FROM meetings ORDER BY id DESC"
        ).fetchall()


def get_meeting(meeting_id: int):
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        return conn.execute(
            "SELECT * FROM meetings WHERE id = ?", (meeting_id,)
        ).fetchone()


def delete_meeting(meeting_id: int):
    with get_connection() as conn:
        conn.execute("DELETE FROM meetings WHERE id = ?", (meeting_id,))
