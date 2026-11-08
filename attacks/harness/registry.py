# Author: Nicola Antonello
"""Finding the attacks, and checking that each one traces to its threats, its
control page and its control-off patch (ADR-0007)."""

import importlib
import re
from pathlib import Path

from attacks.harness.attack import Attack
from attacks.harness.errors import TraceabilityError

ROW_ID = re.compile(r"^\| (T-[A-Z]+-[0-9]+) \|", re.MULTILINE)


def discover(root: Path) -> list[type[Attack]]:
    """Import attacks.<dir>.attack for every directory of root with an
    attack.py. Each defines exactly one Attack, whose id is its directory."""
    found = []
    for directory in sorted(root.iterdir()):
        if directory.name == "harness" or not (directory / "attack.py").is_file():
            continue
        module = importlib.import_module(f"attacks.{directory.name}.attack")
        classes = [
            value
            for value in vars(module).values()
            if isinstance(value, type)
            and issubclass(value, Attack)
            and value.__module__ == module.__name__
        ]
        if len(classes) != 1:
            raise TraceabilityError(
                f"attacks/{directory.name}/attack.py defines {len(classes)} attacks, not 1"
            )
        if classes[0].id != directory.name:
            raise TraceabilityError(
                f"attack {classes[0].id!r} must live in attacks/{classes[0].id}/"
            )
        found.append(classes[0])
    return found


def check_traceability(attack: type[Attack], repo: Path) -> None:
    model = repo / "docs" / "THREAT_MODEL.md"
    rows = set(ROW_ID.findall(model.read_text())) if model.is_file() else set()
    if unknown := [threat for threat in attack.threats if threat not in rows]:
        raise TraceabilityError(f"{attack.id}: {unknown} are not threats in {model}")
    if not (repo / attack.control_page).is_file():
        raise TraceabilityError(f"{attack.id}: {attack.control_page} does not exist")
    patch = repo / "attacks" / attack.id / "control-off.patch"
    if not patch.is_file():
        raise TraceabilityError(f"{attack.id}: {patch} does not exist")
