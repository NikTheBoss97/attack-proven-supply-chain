# Author: Nicola Antonello
"""Helpers for the database tests, which run through `tools/run.sh test-db`.

psql runs in a container of its own on the database's network. The image trusts
connections from inside the database's container, so a test connecting from
there would pass without a password (ADR-0010).
"""

import os
import subprocess

import pytest


def env(name: str) -> str:
    """Return a variable that with-db sets. A missing one fails the test."""
    value = os.environ.get(name)
    if not value:
        pytest.fail(f"{name} is not set: run these tests with tools/run.sh test-db")
    return value


def psql(query: str, password: str | None = None) -> subprocess.CompletedProcess[str]:
    """Run one query as bookmarks_api, with its own password unless given another."""
    secret = env("BOOKMARKS_API_PASSWORD") if password is None else password
    return subprocess.run(
        [
            "docker",
            "run",
            "--rm",
            "--network",
            env("DB_NETWORK"),
            # The password travels in the environment, never in the arguments.
            "--env",
            "PGPASSWORD",
            env("DB_IMAGE"),
            "psql",
            "-h",
            env("DB_CONTAINER"),
            "-U",
            "bookmarks_api",
            "-d",
            "bookmarks",
            "-v",
            "ON_ERROR_STOP=1",
            "-tAc",
            query,
        ],
        env={**os.environ, "PGPASSWORD": secret},
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )


def sql(query: str) -> str:
    """Run one query as bookmarks_api, check it succeeded, and return its output."""
    result = psql(query)
    assert result.returncode == 0, result.stderr
    return result.stdout.strip()
