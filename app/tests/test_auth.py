# Author: Nicola Antonello
"""Reading bearer tokens from a header, and hashing them (ADR-0006)."""

import hashlib

import pytest

from bookmarks.auth import bearer_token, token_digest
from bookmarks.errors import ApiError


@pytest.mark.parametrize("header", ["Bearer abc", "bearer abc", "BEARER abc"])
def test_bearer_token_accepts_any_case(header):
    assert bearer_token(header) == "abc"


@pytest.mark.parametrize(
    "header", [None, "", "Bearer", "Bearer ", "Basic abc", "Token abc", "Bearer a b"]
)
def test_bearer_token_rejects_malformed_headers(header):
    with pytest.raises(ApiError) as error:
        bearer_token(header)
    assert (error.value.status, error.value.code) == (401, "invalid_token")


def test_token_digest_is_sha256():
    assert token_digest("abc") == hashlib.sha256(b"abc").digest()
