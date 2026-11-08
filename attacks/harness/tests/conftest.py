# Author: Nicola Antonello
"""A fake command runner, so the harness's tests create no cluster."""

import pytest

from attacks.harness.errors import SetupError


class FakeRunner:
    """Records each command instead of running it, and fails the ones told to."""

    def __init__(self):
        self.commands: list[list[str]] = []
        self.failing: list[list[str]] = []

    def fail(self, *prefix: str) -> None:
        """Make every command that starts with prefix raise SetupError."""
        self.failing.append(list(prefix))

    def __call__(self, args, stdin=None) -> str:
        args = list(args)
        self.commands.append(args)
        if any(args[: len(prefix)] == prefix for prefix in self.failing):
            raise SetupError(f"{args[0]} failed")
        if args[:3] == ["kind", "get", "kubeconfig"]:
            return "apiVersion: v1\nkind: Config\n"
        return ""

    @property
    def cluster_name(self) -> str:
        create = next(
            c for c in self.commands if c[:3] == ["kind", "create", "cluster"]
        )
        return create[create.index("--name") + 1]


@pytest.fixture
def fake(monkeypatch) -> FakeRunner:
    monkeypatch.setenv("TOOLBOX_CONTAINER", "apsc-toolbox-test")
    return FakeRunner()
