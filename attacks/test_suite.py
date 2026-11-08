# Author: Nicola Antonello
"""The attack suite (ADR-0007), run by `tools/run.sh attacks`. Every attack in
attacks/<id>/ must pass four runs. An attack that does not trace to its threats,
its control page and its control-off patch fails collection, before any run."""

from pathlib import Path

import pytest

from attacks.harness import runs
from attacks.harness.registry import check_traceability, discover
from attacks.normal_use import exercise

REPO = Path(__file__).resolve().parents[1]
ATTACKS = discover(REPO / "attacks")
for found in ATTACKS:
    check_traceability(found, REPO)

each_attack = pytest.mark.parametrize(
    "attack", ATTACKS, ids=[attack.id for attack in ATTACKS]
)


def test_normal_use_with_every_control_on(stacks, record_result):
    report = runs.checked("normal_use", lambda: exercise(stacks.on.api))
    record_result(report)
    assert report.passed, report.detail


@each_attack
def test_control_off(attack, stacks, record_result):
    patch = REPO / "attacks" / attack.id / "control-off.patch"
    report = runs.control_off(attack(), stacks.off(attack.id, patch).api)
    record_result(report, attack)
    assert report.passed, report.detail


@each_attack
def test_control_on(attack, stacks, record_result):
    report = runs.control_on(attack(), stacks.on.api)
    record_result(report, attack)
    assert report.passed, report.detail


@each_attack
def test_variant(attack, stacks, record_result):
    report = runs.variant(attack(), stacks.on.api)
    record_result(report, attack)
    assert report.passed, report.detail


@each_attack
def test_legitimate(attack, stacks, record_result):
    report = runs.legitimate(attack(), stacks.on.api)
    record_result(report, attack)
    assert report.passed, report.detail
