# Author: Nicola Antonello
"""Fixtures for the service's tests, which run in the service's own test image
against a real database (ADR-0010): `tools/run.sh test-app`."""

from collections.abc import Iterator

import psycopg
import pytest
from fastapi.testclient import TestClient
from psycopg.rows import dict_row

from bookmarks.main import app


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def db() -> Iterator[psycopg.Connection]:
    # Like the service, it takes its settings from libpq's PG* variables.
    with psycopg.connect(autocommit=True, row_factory=dict_row) as conn:
        yield conn


def new_user(client: TestClient) -> tuple[str, str]:
    """Create a user through the API, and return its ID and token."""
    response = client.post("/users")
    assert response.status_code == 201, response.text
    body = response.json()
    return body["id"], body["token"]
