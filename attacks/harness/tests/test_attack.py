# Author: Nicola Antonello
"""What every attack must declare, and how its outcome is classified (ADR-0007)."""

import pytest

from attacks.harness.attack import Outcome, Result, classify
from attacks.harness.tests.fakes import Scripted, declare


def test_a_complete_attack_is_accepted():
    assert declare().id == "bola"


def test_attack_without_threats_is_rejected():
    with pytest.raises(TypeError, match="threats"):
        declare(threats=None)


def test_attack_with_a_malformed_threat_id_is_rejected():
    with pytest.raises(TypeError, match="threats"):
        declare(threats=("API-1",))


def test_attack_cannot_be_stopped_as_succeeded():
    with pytest.raises(TypeError, match="stopped_as"):
        declare(stopped_as=Result.SUCCEEDED)


def test_classify():
    attack = Scripted()
    assert (
        classify(attack, Outcome.succeeded("200 with Alice's URL")) is Result.SUCCEEDED
    )
    assert (
        classify(attack, Outcome.stopped_by("404 bookmark_not_found")) is Result.BLOCKED
    )
    assert classify(attack, Outcome.stopped_by("401 invalid_token")) is Result.ERROR
