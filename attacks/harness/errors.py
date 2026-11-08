# Author: Nicola Antonello
"""Errors a run can raise (ADR-0007)."""


class SetupError(Exception):
    """The run could not be set up. It reports `error`, never `blocked`: a
    cluster that did not start says nothing about any control."""


class TraceabilityError(Exception):
    """An attack does not trace to its threats, its control page or its
    control-off patch. It fails the suite's collection: no attack, no claim."""
