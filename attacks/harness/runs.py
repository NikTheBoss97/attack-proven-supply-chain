# Author: Nicola Antonello
"""The four runs that prove a control (ADR-0007). In any run, an exception is
`error`: broken setup never passes as a stopped attack."""

from collections.abc import Callable
from dataclasses import dataclass

from attacks.harness.api import BookmarksApi
from attacks.harness.attack import Attack, Outcome, Result, classify


@dataclass(frozen=True)
class RunReport:
    run: str
    result: str
    detail: str
    passed: bool


def error(run: str, exception: Exception) -> RunReport:
    return RunReport(
        run, Result.ERROR, f"{type(exception).__name__}: {exception}", False
    )


def control_off(attack: Attack, api: BookmarksApi) -> RunReport:
    """With the control removed, the attack and its variant must both succeed:
    a variant that could never work proves nothing when it is stopped."""
    try:
        outcomes = {"attack": attack.attack(api), "variant": attack.variant(api)}
    except Exception as exception:
        return error("control_off", exception)
    for name, outcome in outcomes.items():
        result = classify(attack, outcome)
        if result is not Result.SUCCEEDED:
            detail = f"the {name} was not stopped by anything, yet got {result}: {outcome.reason}"
            return RunReport("control_off", result, detail, False)
    return RunReport("control_off", Result.SUCCEEDED, outcomes["attack"].reason, True)


def stopped(run: str, attack: Attack, play: Callable[[], Outcome]) -> RunReport:
    """With the control on, the attack must be stopped, for the expected reason."""
    try:
        outcome = play()
    except Exception as exception:
        return error(run, exception)
    result = classify(attack, outcome)
    if result is attack.stopped_as:
        return RunReport(run, result, outcome.reason, True)
    if result is Result.SUCCEEDED:
        detail = f"it succeeded: {outcome.reason}"
    else:
        detail = f"stopped by {outcome.reason!r}, not {attack.expected_reason!r}"
    return RunReport(run, result, detail, False)


def control_on(attack: Attack, api: BookmarksApi) -> RunReport:
    return stopped("control_on", attack, lambda: attack.attack(api))


def variant(attack: Attack, api: BookmarksApi) -> RunReport:
    return stopped("variant", attack, lambda: attack.variant(api))


def legitimate(attack: Attack, api: BookmarksApi) -> RunReport:
    return checked("legitimate", lambda: attack.legitimate(api))


def checked(run: str, check: Callable[[], None]) -> RunReport:
    """Normal use: `works`, `fails` on an AssertionError, or `error`."""
    try:
        check()
    except AssertionError as failure:
        return RunReport(run, "fails", str(failure) or "an assertion failed", False)
    except Exception as exception:
        return error(run, exception)
    return RunReport(run, "works", "", True)
