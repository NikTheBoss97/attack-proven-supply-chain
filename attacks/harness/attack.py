# Author: Nicola Antonello
"""The contract every attack follows (ADR-0007): what it declares, and how its
outcome is classified. A stopped attack counts only for its expected reason."""

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import StrEnum

from attacks.harness.api import BookmarksApi


class Result(StrEnum):
    SUCCEEDED = "succeeded"
    BLOCKED = "blocked"
    DETECTED = "detected"
    ERROR = "error"


@dataclass(frozen=True)
class Outcome:
    stopped: bool
    reason: str

    @classmethod
    def succeeded(cls, evidence: str) -> Outcome:
        return cls(stopped=False, reason=evidence)

    @classmethod
    def stopped_by(cls, reason: str) -> Outcome:
        return cls(stopped=True, reason=reason)


def _problems(attack: type) -> list[str]:
    """Why an attack's declaration is incomplete, if it is."""

    def text(name: str, pattern: str = r".+") -> bool:
        value = getattr(attack, name, None)
        return isinstance(value, str) and re.fullmatch(pattern, value) is not None

    problems = []
    if not text("id", r"[a-z][a-z0-9_]*"):
        problems.append("id must match [a-z][a-z0-9_]*")
    for name in ("title", "control", "expected_reason"):
        if not text(name):
            problems.append(f"{name} must be non-empty text")
    if not text("control_page", r"docs/controls/[a-z0-9-]+\.md"):
        problems.append("control_page must be docs/controls/<name>.md")
    threats = getattr(attack, "threats", None)
    if not (
        isinstance(threats, tuple)
        and threats
        and all(
            isinstance(t, str) and re.fullmatch(r"T-[A-Z]+-[0-9]+", t) for t in threats
        )
    ):
        problems.append("threats must be a non-empty tuple of IDs like T-API-1")
    if getattr(attack, "stopped_as", None) not in (Result.BLOCKED, Result.DETECTED):
        problems.append("stopped_as must be Result.BLOCKED or Result.DETECTED")
    return problems


class Attack(ABC):
    """One attack, proven by four runs: control off, control on, the nearest
    variant, and the legitimate path."""

    id: str
    title: str
    threats: tuple[str, ...]
    control: str
    control_page: str
    stopped_as: Result
    expected_reason: str

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if problems := _problems(cls):
            raise TypeError(f"{cls.__name__}: {'; '.join(problems)}")

    @abstractmethod
    def attack(self, api: BookmarksApi) -> Outcome: ...

    @abstractmethod
    def variant(self, api: BookmarksApi) -> Outcome: ...

    @abstractmethod
    def legitimate(self, api: BookmarksApi) -> None:
        """Normal use the control must allow: raise AssertionError if it breaks."""


def classify(attack: Attack, outcome: Outcome) -> Result:
    if not outcome.stopped:
        return Result.SUCCEEDED
    if outcome.reason == attack.expected_reason:
        return attack.stopped_as
    return Result.ERROR
