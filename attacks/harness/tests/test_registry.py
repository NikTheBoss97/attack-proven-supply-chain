# Author: Nicola Antonello
"""Every attack traces to its threats, its control page and its control-off
patch, and every patch still applies to today's code (ADR-0007)."""

from pathlib import Path

import pytest

from attacks.harness.errors import TraceabilityError
from attacks.harness.images import patched_copy
from attacks.harness.registry import check_traceability, discover
from attacks.harness.tests.fakes import Scripted

REPO = Path(__file__).resolve().parents[3]


def make_repo(root: Path, threat_row=True, control_page=True, patch=True) -> Path:
    docs = root / "docs"
    (docs / "controls").mkdir(parents=True)
    rows = "| T-API-1 | Has their own account | Reads another user's bookmark |\n"
    (docs / "THREAT_MODEL.md").write_text(
        "| ID | Attacker position | Action and impact |\n| --- | --- | --- |\n"
        + (rows if threat_row else "")
    )
    if control_page:
        (docs / "controls" / "ownership-check.md").write_text("# Ownership check\n")
    if patch:
        (root / "attacks" / "bola").mkdir(parents=True)
        (root / "attacks" / "bola" / "control-off.patch").write_text("")
    return root


def test_traceability_accepts_a_complete_attack(tmp_path):
    check_traceability(Scripted, make_repo(tmp_path))


def test_traceability_rejects_an_unknown_threat_id(tmp_path):
    with pytest.raises(TraceabilityError, match="T-API-1"):
        check_traceability(Scripted, make_repo(tmp_path, threat_row=False))


def test_traceability_rejects_a_missing_control_page(tmp_path):
    with pytest.raises(TraceabilityError, match="ownership-check.md"):
        check_traceability(Scripted, make_repo(tmp_path, control_page=False))


def test_traceability_requires_a_control_off_patch(tmp_path):
    with pytest.raises(TraceabilityError, match="control-off.patch"):
        check_traceability(Scripted, make_repo(tmp_path, patch=False))


def test_every_control_off_patch_applies_to_the_current_code(tmp_path):
    for attack in discover(REPO / "attacks"):
        workdir = tmp_path / attack.id
        workdir.mkdir()
        patch = REPO / "attacks" / attack.id / "control-off.patch"
        patched_copy(REPO / "app", patch, workdir)
