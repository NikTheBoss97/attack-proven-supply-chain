# Author: Nicola Antonello
"""The suite's images: built from this repository, loaded only into its own
cluster, never pushed or signed, and removed afterwards (ADR-0007)."""

import shutil
import sys
from collections.abc import Iterable
from pathlib import Path

from attacks.harness.commands import Runner, subprocess_runner
from attacks.harness.errors import SetupError


def build(
    context: Path,
    tag: str,
    target: str | None = None,
    run: Runner = subprocess_runner,
) -> str:
    args = ["docker", "build", "--quiet", "--tag", tag]
    if target:
        args += ["--target", target]
    run([*args, str(context)])
    return tag


def patched_copy(
    source: Path, patch: Path, workdir: Path, run: Runner = subprocess_runner
) -> Path:
    """Copy source into workdir and apply patch to the copy, never to the
    working tree. git apply refuses a patch that no longer fits the code, so an
    attack cannot go stale silently: that raises SetupError."""
    copy = workdir / source.name
    shutil.copytree(source, copy)
    run(["git", "-C", str(workdir), "apply", "--verbose", str(patch.resolve())])
    return copy


def remove(tags: Iterable[str], run: Runner = subprocess_runner) -> None:
    """Remove images. It never raises."""
    tags = list(tags)
    if not tags:
        return
    try:
        run(["docker", "image", "rm", "--force", *tags])
    except (SetupError, OSError) as error:
        print(f"could not remove images {tags}: {error}", file=sys.stderr)
