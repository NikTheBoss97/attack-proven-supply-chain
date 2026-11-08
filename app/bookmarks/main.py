# Author: Nicola Antonello
"""The bookmarks API's endpoints (ADR-0004, ADR-0006)."""

from datetime import datetime
from typing import Annotated
from urllib.parse import urlsplit
from uuid import UUID

from fastapi import FastAPI, Query
from pydantic import BaseModel, StringConstraints, field_validator

from bookmarks import auth, errors, store
from bookmarks.auth import CurrentUser
from bookmarks.db import Connection

app = FastAPI(title="bookmarks")
errors.install(app)


class NewBookmark(BaseModel):
    url: Annotated[str, StringConstraints(max_length=2048)]
    title: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=1, max_length=300)
    ]

    @field_validator("url")
    @classmethod
    def absolute_web_url(cls, url: str) -> str:
        """Only absolute http and https URLs, so no client renders a script link."""
        parts = urlsplit(url)
        if parts.scheme not in ("http", "https") or not parts.hostname:
            raise ValueError("must be an absolute http or https URL")
        return url


class Bookmark(BaseModel):
    """What the API returns for a bookmark: never its owner."""

    id: UUID
    url: str
    title: str
    created_at: datetime


@app.get("/healthz")
def healthz() -> dict[str, str]:
    """Answer Kubernetes' probes without touching the database."""
    return {"status": "ok"}


@app.post("/users", status_code=201)
def create_user(conn: Connection) -> dict[str, str]:
    """Create a user and return its token, the only time it is ever shown."""
    token = auth.new_token()
    user_id = store.create_user(conn, auth.token_digest(token))
    return {"id": str(user_id), "token": token}


@app.post("/bookmarks", status_code=201)
def save_bookmark(new: NewBookmark, user: CurrentUser, conn: Connection) -> Bookmark:
    return Bookmark(**store.add_bookmark(conn, user, new.url, new.title))


@app.get("/bookmarks")
def list_bookmarks(
    user: CurrentUser,
    conn: Connection,
    q: Annotated[str | None, Query(max_length=100)] = None,
) -> list[Bookmark]:
    """The caller's newest 100 bookmarks, or those matching q."""
    return [Bookmark(**row) for row in store.list_bookmarks(conn, user, q)]
