# Author: Nicola Antonello
"""The attack suite (ADR-0007), run by `tools/run.sh attacks`."""

from attacks.normal_use import exercise


def test_normal_use_with_every_control_on(stacks):
    exercise(stacks.on.api)
