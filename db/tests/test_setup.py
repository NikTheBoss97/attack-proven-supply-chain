# Author: Nicola Antonello
"""Setup fails closed when the service's password is missing (ADR-0010)."""

import os
import secrets
import subprocess

from conftest import env


def test_setup_fails_without_the_api_password():
    name = f"apsc-db-setup-{secrets.token_hex(4)}"
    subprocess.run(
        [
            "docker",
            "run",
            "--detach",
            "--name",
            name,
            "--read-only",
            "--tmpfs",
            "/var/run/postgresql",
            "--tmpfs",
            "/tmp",
            "--mount",
            "type=tmpfs,destination=/var/lib/postgresql",
            "--env",
            "POSTGRES_DB=bookmarks",
            "--env",
            "POSTGRES_PASSWORD",
            env("DB_IMAGE"),
        ],
        env={**os.environ, "POSTGRES_PASSWORD": secrets.token_urlsafe(24)},
        capture_output=True,
        text=True,
        check=True,
    )
    try:
        waited = subprocess.run(
            ["docker", "wait", name],
            capture_output=True,
            text=True,
            timeout=60,
            check=True,
        )
        logs = subprocess.run(
            ["docker", "logs", name], capture_output=True, text=True, check=True
        )
        assert int(waited.stdout) != 0
        assert "syntax error" in logs.stdout + logs.stderr
    finally:
        subprocess.run(
            ["docker", "rm", "--force", name], capture_output=True, check=False
        )
