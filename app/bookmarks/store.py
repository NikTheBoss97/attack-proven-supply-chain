# Author: Nicola Antonello
"""Every query the service runs, each with its values passed as parameters."""

from uuid import UUID

import psycopg


def create_user(conn: psycopg.Connection, digest: bytes) -> UUID:
    row = conn.execute(
        "INSERT INTO app.users (token_sha256) VALUES (%s) RETURNING id", (digest,)
    ).fetchone()
    return row["id"]


def user_for_digest(conn: psycopg.Connection, digest: bytes) -> UUID | None:
    row = conn.execute(
        "SELECT id FROM app.users WHERE token_sha256 = %s", (digest,)
    ).fetchone()
    return row["id"] if row else None


def add_bookmark(conn: psycopg.Connection, user_id: UUID, url: str, title: str) -> dict:
    return conn.execute(
        "INSERT INTO app.bookmarks (user_id, url, title) VALUES (%s, %s, %s)"
        " RETURNING id, url, title, created_at",
        (user_id, url, title),
    ).fetchone()


def like_pattern(text: str) -> str:
    """A pattern for ILIKE ... ESCAPE '\\' that matches text literally, anywhere."""
    escaped = text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


def list_bookmarks(
    conn: psycopg.Connection, user_id: UUID, q: str | None, limit: int = 100
) -> list[dict]:
    """The caller's bookmarks, newest first, or only those whose title or URL
    contains q, ignoring case."""
    if q is None:
        return conn.execute(
            "SELECT id, url, title, created_at FROM app.bookmarks"
            " WHERE user_id = %s ORDER BY created_at DESC LIMIT %s",
            (user_id, limit),
        ).fetchall()
    pattern = like_pattern(q)
    return conn.execute(
        "SELECT id, url, title, created_at FROM app.bookmarks"
        " WHERE user_id = %s"
        " AND (title ILIKE %s ESCAPE '\\' OR url ILIKE %s ESCAPE '\\')"
        " ORDER BY created_at DESC LIMIT %s",
        (user_id, pattern, pattern, limit),
    ).fetchall()
