# Author: Nicola Antonello
"""Every query the service runs, each with its values passed as parameters."""

from uuid import UUID

import psycopg


def create_user(conn: psycopg.Connection, digest: bytes) -> UUID:
    row = conn.execute(
        "INSERT INTO app.users (token_sha256) VALUES (%s) RETURNING id", (digest,)
    ).fetchone()
    return row["id"]
