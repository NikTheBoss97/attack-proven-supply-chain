# Author: Nicola Antonello
"""A client for the bookmarks API, used the way a user or an attacker would."""

import httpx

from attacks.harness.errors import SetupError


def bearer(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def error_code(response: httpx.Response) -> str:
    """The response's `error` field, or "" when it has none."""
    try:
        body = response.json()
    except ValueError:
        return ""
    return body.get("error", "") if isinstance(body, dict) else ""


class BookmarksApi:
    def __init__(self, base_url: str):
        self.client = httpx.Client(base_url=base_url, timeout=10)

    def create_user(self) -> str:
        """Create a user and return its token. Anything but 201 is broken setup."""
        response = self.client.post("/users")
        if response.status_code != 201:
            raise SetupError(f"POST /users returned {response.status_code}")
        return response.json()["token"]

    def add_bookmark(self, token: str, url: str, title: str) -> dict:
        """Save a bookmark and return it. Anything but 201 is broken setup."""
        response = self.client.post(
            "/bookmarks", json={"url": url, "title": title}, headers=bearer(token)
        )
        if response.status_code != 201:
            raise SetupError(f"POST /bookmarks returned {response.status_code}")
        return response.json()

    def get_bookmark(self, token: str, bookmark_id: str) -> httpx.Response:
        return self.client.get(f"/bookmarks/{bookmark_id}", headers=bearer(token))

    def delete_bookmark(self, token: str, bookmark_id: str) -> httpx.Response:
        return self.client.delete(f"/bookmarks/{bookmark_id}", headers=bearer(token))

    def list_bookmarks(self, token: str, q: str | None = None) -> httpx.Response:
        params = {} if q is None else {"q": q}
        return self.client.get("/bookmarks", params=params, headers=bearer(token))
