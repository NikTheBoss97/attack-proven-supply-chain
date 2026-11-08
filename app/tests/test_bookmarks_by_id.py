# Author: Nicola Antonello
"""Reading and deleting one bookmark by its ID: only its owner can, and to
anyone else it looks exactly like a bookmark that does not exist (ADR-0006)."""

from uuid import uuid4

import pytest
from conftest import new_user

NOT_FOUND = {"error": "bookmark_not_found"}


def bearer(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def saved(client, token) -> dict:
    response = client.post(
        "/bookmarks",
        json={"url": "https://example.com/alice", "title": "Alice's"},
        headers=bearer(token),
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_owner_reads_their_bookmark(client):
    _, alice = new_user(client)
    bookmark = saved(client, alice)
    response = client.get(f"/bookmarks/{bookmark['id']}", headers=bearer(alice))
    assert response.status_code == 200
    assert response.json() == bookmark


def test_owner_deletes_their_bookmark(client):
    _, alice = new_user(client)
    bookmark = saved(client, alice)
    response = client.delete(f"/bookmarks/{bookmark['id']}", headers=bearer(alice))
    assert response.status_code == 204
    assert response.content == b""
    gone = client.get(f"/bookmarks/{bookmark['id']}", headers=bearer(alice))
    assert gone.status_code == 404
    assert gone.json() == NOT_FOUND


def test_another_users_bookmark_looks_missing(client):
    _, alice = new_user(client)
    _, bob = new_user(client)
    bookmark = saved(client, alice)
    theirs = client.get(f"/bookmarks/{bookmark['id']}", headers=bearer(bob))
    unknown = client.get(f"/bookmarks/{uuid4()}", headers=bearer(bob))
    assert theirs.status_code == unknown.status_code == 404
    assert theirs.json() == NOT_FOUND
    assert theirs.content == unknown.content
    assert theirs.headers["content-type"] == unknown.headers["content-type"]


def test_another_user_cannot_delete(client):
    _, alice = new_user(client)
    _, bob = new_user(client)
    bookmark = saved(client, alice)
    response = client.delete(f"/bookmarks/{bookmark['id']}", headers=bearer(bob))
    assert response.status_code == 404
    assert response.json() == NOT_FOUND
    still_there = client.get(f"/bookmarks/{bookmark['id']}", headers=bearer(alice))
    assert still_there.status_code == 200


@pytest.mark.parametrize("method", ["GET", "DELETE"])
def test_ids_must_be_uuids(client, method):
    _, token = new_user(client)
    response = client.request(method, "/bookmarks/not-a-uuid", headers=bearer(token))
    assert response.status_code == 422


@pytest.mark.parametrize("method", ["GET", "DELETE"])
def test_reads_and_deletes_need_a_token(client, method):
    response = client.request(method, f"/bookmarks/{uuid4()}")
    assert response.status_code == 401
    assert response.json() == {"error": "invalid_token"}
