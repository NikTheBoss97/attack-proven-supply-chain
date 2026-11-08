# Author: Nicola Antonello
"""Bearer tokens: random, shown once, and stored only as a digest (ADR-0006)."""

import hashlib
import secrets
from typing import Annotated
from uuid import UUID

from fastapi import Depends, Header

from bookmarks import store
from bookmarks.db import Connection
from bookmarks.errors import invalid_token


def new_token() -> str:
    """32 random bytes, which the Python documentation considers sufficient."""
    return secrets.token_urlsafe(32)


def token_digest(token: str) -> bytes:
    """A fast hash is enough for a value nobody can guess."""
    return hashlib.sha256(token.encode()).digest()


def bearer_token(authorization: str | None) -> str:
    """Return the token from `Bearer <token>`, with the scheme in any case."""
    scheme, _, token = (authorization or "").partition(" ")
    if scheme.lower() != "bearer" or not token or " " in token:
        raise invalid_token()
    return token


def current_user(
    conn: Connection, authorization: Annotated[str | None, Header()] = None
) -> UUID:
    """The caller: the user whose token digest matches the bearer token."""
    user_id = store.user_for_digest(conn, token_digest(bearer_token(authorization)))
    if user_id is None:
        raise invalid_token()
    return user_id


CurrentUser = Annotated[UUID, Depends(current_user)]
