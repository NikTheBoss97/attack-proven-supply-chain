# Author: Nicola Antonello
"""The results table: written from a real run of the suite, never by hand
(ADR-0007). A pytest plugin records each run, and a command line writes the
table into the README or checks that it matches:
  python -m attacks.harness.results check|write README.md RESULTS
"""

import argparse
import difflib
import json
import sys
from pathlib import Path

import pytest

START = "<!-- attack-results:start -->"
END = "<!-- attack-results:end -->"
RUNS = ("control_off", "control_on", "variant", "legitimate")
HEADER = (
    "| Attack | Threats | Control | Control off | Control on | Variant | Legitimate |\n"
    "| --- | --- | --- | --- | --- | --- | --- |"
)


class Recorder:
    """Every run's result, by attack, plus the normal-use test's."""

    def __init__(self):
        self.attacks: dict[str, dict] = {}
        self.normal_use: str | None = None

    def record(self, report, attack=None) -> None:
        if attack is None:
            self.normal_use = str(report.result)
            return
        entry = self.attacks.setdefault(
            attack.id,
            {
                "id": attack.id,
                "title": attack.title,
                "threats": list(attack.threats),
                "control": attack.control,
                "control_page": attack.control_page,
                "runs": {},
            },
        )
        entry["runs"][report.run] = str(report.result)

    def as_dict(self) -> dict:
        attacks = sorted(self.attacks.values(), key=lambda attack: attack["id"])
        return {"attacks": attacks, "normal_use": self.normal_use}


def render(results: dict) -> str:
    """The table, sorted by attack ID. A run with no result shows as error."""
    rows = [HEADER]
    for attack in sorted(results["attacks"], key=lambda attack: attack["id"]):
        cells = [
            f"[{attack['title']}](attacks/{attack['id']}/attack.py)",
            ", ".join(attack["threats"]),
            f"[{attack['control']}]({attack['control_page']})",
            *(attack["runs"].get(run, "error") for run in RUNS),
        ]
        rows.append(f"| {' | '.join(cells)} |")
    normal_use = results.get("normal_use") or "error"
    return "\n".join(rows) + f"\n\nNormal use with every control on: {normal_use}."


def replace_table(readme: str, table: str) -> str:
    start, end = readme.find(START), readme.find(END)
    if start < 0 or end < start:
        raise ValueError(f"the README needs {START} and {END}, in that order")
    return f"{readme[: start + len(START)]}\n{table}\n{readme[end:]}"


# The pytest plugin, loaded with `-p attacks.harness.results`.

RECORDER = pytest.StashKey[Recorder]()


def pytest_addoption(parser) -> None:
    parser.addoption("--results", metavar="PATH", help="write the run's results here")


def pytest_configure(config) -> None:
    config.stash[RECORDER] = Recorder()


@pytest.fixture
def record_result(request):
    """record_result(report, attack=None): None means the normal-use test."""
    return request.config.stash[RECORDER].record


def pytest_sessionfinish(session) -> None:
    path = session.config.getoption("--results")
    if path:
        results = session.config.stash[RECORDER].as_dict()
        Path(path).write_text(json.dumps(results, indent=2))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("action", choices=["check", "write"])
    parser.add_argument("readme", type=Path)
    parser.add_argument("results", type=Path)
    args = parser.parse_args(argv)
    current = args.readme.read_text()
    table = render(json.loads(args.results.read_text()))
    expected = replace_table(current, table)
    if args.action == "write":
        args.readme.write_text(expected)
        return 0
    if current == expected:
        return 0
    sys.stdout.writelines(
        difflib.unified_diff(
            current.splitlines(keepends=True),
            expected.splitlines(keepends=True),
            "README.md (committed)",
            "README.md (from this run)",
        )
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
