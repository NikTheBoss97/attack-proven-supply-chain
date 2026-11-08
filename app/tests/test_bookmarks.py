# Author: Nicola Antonello
"""Saving and listing bookmarks, each user seeing only their own (ADR-0006)."""

import pytest
from conftest import new_user

from bookmarks import store

FIELDS = {"id", "url", "title", "created_at"}


def bearer(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def save(client, token, url="https://example.com/", title="Example"):
    return client.post(
        "/bookmarks", json={"url": url, "title": title}, headers=bearer(token)
    )


def titles(response) -> list[str]:
    assert response.status_code == 200, response.text
    return [bookmark["title"] for bookmark in response.json()]


def test_save_bookmark_returns_it(client):
    _, token = new_user(client)
    response = save(client, token, "https://example.com/article", "An article")
    assert response.status_code == 201
    body = response.json()
    assert set(body) == FIELDS
    assert (body["url"], body["title"]) == ("https://example.com/article", "An article")


def test_saving_needs_a_token(client):
    response = client.post(
        "/bookmarks", json={"url": "https://example.com/", "title": "x"}
    )
    assert response.status_code == 401
    assert response.json() == {"error": "invalid_token"}
    assert response.headers["www-authenticate"] == "Bearer"


@pytest.mark.parametrize(
    "header",
    [
        "",
        "Bearer",
        "Bearer ",
        "Basic dXNlcjpwYXNz",
        "Token abc",
        "Bearer not-a-real-token",
        "Bearer a b",
    ],
)
def test_malformed_authorization_is_rejected(client, header):
    response = client.post(
        "/bookmarks",
        json={"url": "https://example.com/", "title": "x"},
        headers={"Authorization": header},
    )
    assert response.status_code == 401
    assert response.json() == {"error": "invalid_token"}


def test_lowercase_bearer_works(client):
    _, token = new_user(client)
    response = client.post(
        "/bookmarks",
        json={"url": "https://example.com/", "title": "x"},
        headers={"Authorization": f"bearer {token}"},
    )
    assert response.status_code == 201


@pytest.mark.parametrize(
    ("url", "title"),
    [
        ("ftp://example.com/x", "x"),
        ("javascript:alert(1)", "x"),
        ("not a url", "x"),
        ("https://example.com/" + "a" * 2029, "x"),  # 2049 characters
        ("https://example.com/", ""),
        ("https://example.com/", "   "),
        ("https://example.com/", "x" * 301),
    ],
)
def test_invalid_bookmarks_are_rejected(client, url, title):
    _, token = new_user(client)
    assert save(client, token, url, title).status_code == 422


def test_boundary_lengths_are_accepted(client):
    _, token = new_user(client)
    url = "https://example.com/" + "a" * 2028
    assert len(url) == 2048
    assert save(client, token, url, "x" * 300).status_code == 201


def test_list_shows_only_the_callers_bookmarks_newest_first(client):
    _, alice = new_user(client)
    _, bob = new_user(client)
    save(client, alice, title="A")
    save(client, alice, title="B")
    save(client, bob, title="C")
    response = client.get("/bookmarks", headers=bearer(alice))
    assert titles(response) == ["B", "A"]
    assert all(set(bookmark) == FIELDS for bookmark in response.json())
    assert titles(client.get("/bookmarks", headers=bearer(bob))) == ["C"]


def test_list_returns_the_newest_100(client):
    _, token = new_user(client)
    for n in range(101):
        save(client, token, title=f"bookmark {n}")
    listed = titles(client.get("/bookmarks", headers=bearer(token)))
    assert len(listed) == 100
    assert listed[0] == "bookmark 100"
    assert "bookmark 0" not in listed


def test_search_matches_title_or_url_ignoring_case(client):
    _, token = new_user(client)
    save(client, token, "https://example.com/Python-tips", "Tips")
    save(client, token, "https://example.com/news", "PYTHON news")
    save(client, token, "https://example.com/other", "Other")
    response = client.get("/bookmarks", params={"q": "python"}, headers=bearer(token))
    assert sorted(titles(response)) == ["PYTHON news", "Tips"]


@pytest.mark.parametrize(
    ("q", "expected"),
    [("100%", ["100% done"]), ("snake_case", ["snake_case"]), ("\\", ["back\\slash"])],
)
def test_search_treats_wildcards_literally(client, q, expected):
    _, token = new_user(client)
    for title in [
        "100% done",
        "100 percent",
        "snake_case",
        "snakeXcase",
        "back\\slash",
        "backslash",
    ]:
        save(client, token, title=title)
    response = client.get("/bookmarks", params={"q": q}, headers=bearer(token))
    assert titles(response) == expected


def test_search_text_over_100_characters_is_rejected(client):
    _, token = new_user(client)
    response = client.get("/bookmarks", params={"q": "x" * 101}, headers=bearer(token))
    assert response.status_code == 422


def test_like_pattern_escapes_wildcards():
    assert store.like_pattern("a%b_c\\d") == "%a\\%b\\_c\\\\d%"
