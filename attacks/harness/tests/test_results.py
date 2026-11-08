# Author: Nicola Antonello
"""The README's results table comes only from a run's results (ADR-0007)."""

import json

import pytest

from attacks.harness.results import END, START, Recorder, main, render, replace_table
from attacks.harness.runs import RunReport
from attacks.harness.tests.fakes import Scripted

EXPECTED = (
    "| Attack | Threats | Control | Control off | Control on | Variant | Legitimate |\n"
    "| --- | --- | --- | --- | --- | --- | --- |\n"
    "| [Broken object-level authorization](attacks/bola/attack.py) | T-API-1"
    " | [Ownership check](docs/controls/ownership-check.md)"
    " | succeeded | blocked | blocked | works |\n"
    "\n"
    "Normal use with every control on: works."
)
REPORTS = [
    RunReport("control_off", "succeeded", "", True),
    RunReport("control_on", "blocked", "", True),
    RunReport("variant", "blocked", "", True),
    RunReport("legitimate", "works", "", True),
]


def recorded(reports) -> dict:
    recorder = Recorder()
    for report in reports:
        recorder.record(report, Scripted)
    recorder.record(RunReport("normal_use", "works", "", True))
    return recorder.as_dict()


@pytest.mark.parametrize("reports", [REPORTS, REPORTS[::-1]])
def test_render_is_exact_and_ignores_order(reports):
    assert render(recorded(reports)) == EXPECTED


def test_missing_runs_render_as_error():
    recorder = Recorder()
    recorder.record(REPORTS[0], Scripted)
    table = render(recorder.as_dict())
    assert "| succeeded | error | error | error |" in table
    assert table.endswith("Normal use with every control on: error.")


def write_files(tmp_path, table: str):
    readme = tmp_path / "README.md"
    readme.write_text(f"# Title\n\n{START}\n{table}\n{END}\n\nAfter.\n")
    results = tmp_path / "results.json"
    results.write_text(json.dumps(recorded(REPORTS)))
    return readme, results


def test_check_reports_a_difference(tmp_path, capsys):
    stale = EXPECTED.replace("| succeeded | blocked |", "| succeeded | succeeded |")
    readme, results = write_files(tmp_path, stale)
    assert main(["check", str(readme), str(results)]) == 1
    diff = capsys.readouterr().out
    assert "-| [Broken" in diff
    assert "+| [Broken" in diff


def test_write_replaces_only_between_the_markers(tmp_path):
    readme, results = write_files(tmp_path, "an old table")
    assert main(["write", str(readme), str(results)]) == 0
    assert readme.read_text() == (f"# Title\n\n{START}\n{EXPECTED}\n{END}\n\nAfter.\n")
    assert main(["check", str(readme), str(results)]) == 0


def test_missing_markers_raise():
    with pytest.raises(ValueError, match="attack-results"):
        replace_table("# A README without markers\n", EXPECTED)
