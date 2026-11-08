# Author: Nicola Antonello
"""Creating users, and how their tokens are stored (ADR-0006)."""

import hashlib
import re
from uuid import UUID

from conftest import new_user


def test_create_user_returns_its_id_and_token(client):
    response = client.post("/users")
    body = response.json()
    assert response.status_code == 201
    assert set(body) == {"id", "token"}
    UUID(body["id"])
    assert re.fullmatch(r"[A-Za-z0-9_-]{43}", body["token"])


def test_each_user_gets_a_different_token(client):
    assert new_user(client)[1] != new_user(client)[1]


def test_token_is_stored_only_as_its_sha256_digest(client, db):
    user_id, token = new_user(client)
    row = db.execute(
        "SELECT token_sha256, row_to_json(u)::text AS everything"
        " FROM app.users u WHERE id = %s",
        (user_id,),
    ).fetchone()
    assert bytes(row["token_sha256"]) == hashlib.sha256(token.encode()).digest()
    assert token not in row["everything"]
