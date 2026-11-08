# Author: Nicola Antonello
"""The four runs: what each must report to pass, and that an exception is an
error, never a stopped attack (ADR-0007)."""

import httpx
import pytest

from attacks.harness import runs
from attacks.harness.attack import Outcome
from attacks.harness.errors import SetupError
from attacks.harness.tests.fakes import Scripted

WORKED = Outcome.succeeded("200 with Alice's URL")
STOPPED = Outcome.stopped_by("404 bookmark_not_found")
WRONG_REASON = Outcome.stopped_by("500 ")


@pytest.mark.parametrize(
    ("attack_ok", "variant_ok", "passed"),
    [
        (True, True, True),
        (True, False, False),
        (False, True, False),
        (False, False, False),
    ],
)
def test_control_off_passes_only_when_attack_and_variant_both_succeed(
    attack_ok, variant_ok, passed
):
    attack = Scripted(
        attack=WORKED if attack_ok else STOPPED,
        variant=WORKED if variant_ok else STOPPED,
    )
    report = runs.control_off(attack, api=None)
    assert report.passed is passed
    assert report.result == ("succeeded" if passed else "blocked")


def test_control_on_passes_only_for_the_expected_reason():
    stopped = runs.control_on(Scripted(attack=STOPPED), api=None)
    assert (stopped.result, stopped.passed) == ("blocked", True)
    wrong = runs.control_on(Scripted(attack=WRONG_REASON), api=None)
    assert (wrong.result, wrong.passed) == ("error", False)
    assert "500" in wrong.detail
    worked = runs.control_on(Scripted(attack=WORKED), api=None)
    assert (worked.result, worked.passed) == ("succeeded", False)


@pytest.mark.parametrize(
    "exc", [SetupError("x"), httpx.ConnectError("x"), ValueError("x")]
)
def test_exceptions_report_error_never_blocked(exc):
    attack = Scripted(attack=exc, variant=exc, legitimate=exc)
    for run in (runs.control_off, runs.control_on, runs.variant, runs.legitimate):
        report = run(attack, api=None)
        assert (report.result, report.passed) == ("error", False), run.__name__


def test_legitimate_reports_works_fails_or_error():
    works = runs.legitimate(Scripted(legitimate=None), api=None)
    assert (works.result, works.passed) == ("works", True)
    broken = AssertionError("Alice cannot read her own bookmark")
    fails = runs.legitimate(Scripted(legitimate=broken), api=None)
    assert (fails.result, fails.passed) == ("fails", False)
    assert "Alice cannot read" in fails.detail
    error = runs.legitimate(Scripted(legitimate=SetupError("x")), api=None)
    assert (error.result, error.passed) == ("error", False)
