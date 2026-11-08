# Author: Nicola Antonello
"""How the harness runs commands, so its tests can fake them."""

import shlex
import subprocess
from collections.abc import Callable, Sequence

from attacks.harness.errors import SetupError

# Runs a command with optional standard input and returns its output.
Runner = Callable[..., str]


def subprocess_runner(args: Sequence[str], stdin: str | None = None) -> str:
    """Run a command. A failure raises SetupError with the command's own error
    output. Secrets never go in args, only in stdin, so the message is safe."""
    result = subprocess.run(
        list(args), input=stdin, capture_output=True, text=True, check=False
    )
    if result.returncode != 0:
        raise SetupError(
            f"{shlex.join(args)} exited {result.returncode}: {result.stderr.strip()}"
        )
    return result.stdout
