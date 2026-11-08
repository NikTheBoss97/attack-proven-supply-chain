# Author: Nicola Antonello
"""Bearer tokens: random, shown once, and stored only as a digest (ADR-0006)."""

import hashlib
import secrets

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
