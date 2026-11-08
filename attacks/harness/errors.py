# Author: Nicola Antonello
"""Errors a run can raise (ADR-0007)."""


class SetupError(Exception):
    """The run could not be set up. It reports `error`, never `blocked`: a
    cluster that did not start says nothing about any control."""
