"""Mirror of `src/studyforge/serve/routes/breakdown.py` (R12): the fold a Submit records.

⭐ **Every report is written at run time under `tmp_path`**, and every declared
path is a workspace path — so no test here names a directory on this machine.
"""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from studyforge.serve.routes.breakdown import NO_BREAKDOWN, fold

ASK = "test_the_greeting_names_who_it_greets"
EDGE = "test_an_empty_name_is_refused"
SAYS_EDGE = "an empty name is refused"
DECLARED = "reports/greet.xml"

PASSING = '<testcase classname="practice.check_greet" name="{name}"/>'
FAILING = '<testcase classname="practice.check_greet" name="{name}"><failure/></testcase>'


def workspace(cases=True, report=True, graded=True) -> dict:
    """The practice's workspace exactly as the unit document holds it."""
    record: dict = {"main_path": "practice/greet.py", "run_command": ["python3", "greet.py"]}
    if graded:
        record |= {
            "test_path": "practice/check_greet.py",
            "test_command": ["python3", "-m", "pytest", "practice/check_greet.py"],
            "provenance": "bundled",
            "trust": "authoritative",
        }
    if cases and report:
        record |= {
            "cases": [
                {"id": ASK, "kind": "main", "says": "it greets who it greets"},
                {"id": EDGE, "kind": "edge", "says": SAYS_EDGE},
            ],
            "report": {"format": "junit", "path": DECLARED},
        }
    return record


def write_report(root: Path, body: str, declared: str = DECLARED) -> Path:
    """Write one JUnit document at the declared workspace path, and return it."""
    path = root / declared
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"<testsuite>{body}</testsuite>", encoding="utf-8")
    return path


def both(ask: bool, edge: bool) -> str:
    return (PASSING if ask else FAILING).format(name=ASK) + (PASSING if edge else FAILING).format(
        name=EDGE
    )


# --------------------------------------------------------------------------
# What a Submit records
# --------------------------------------------------------------------------


@pytest.mark.parametrize(("ask", "edge"), [(True, True), (True, False), (False, True)])
def test_a_submit_records_one_verdict_per_declared_case(tmp_path, ask, edge):
    started = time.time()
    write_report(tmp_path, both(ask, edge))
    cases, said = fold("test", workspace(), tmp_path, started)
    assert cases == {ASK: ask, EDGE: edge}
    assert said == ()


def test_a_declared_case_the_report_never_names_is_recorded_as_not_passed(tmp_path):
    # ⭐ A run that stopped early names fewer tests; `edge cases 0/1` is the
    # honest answer and refusing here would tell the reader nothing at all.
    started = time.time()
    write_report(tmp_path, PASSING.format(name=ASK))
    cases, said = fold("test", workspace(), tmp_path, started)
    assert cases == {ASK: True, EDGE: False}
    assert said == ()


def test_the_counts_a_reader_is_shown_are_derivable_from_what_is_recorded(tmp_path):
    # ⛔ The per-case verdicts are recorded and the counts are not, so *edge
    # cases n/m* has exactly one place it can disagree with: none.
    started = time.time()
    write_report(tmp_path, both(ask=True, edge=False))
    cases, _ = fold("test", workspace(), tmp_path, started)
    declared = workspace()["cases"]
    edges = [case["id"] for case in declared if case["kind"] == "edge"]
    assert sum(cases[edge] for edge in edges) == 0
    assert len(edges) == 1
    assert [case["says"] for case in declared if not cases[case["id"]]] == [SAYS_EDGE]


# --------------------------------------------------------------------------
# The three quiet answers, and none of them is a failure
# --------------------------------------------------------------------------


def test_a_run_folds_nothing_even_where_a_report_is_sitting_there(tmp_path):
    # ⚠️ Run is not Submit: the file on disk is some previous Submit's.
    started = time.time()
    write_report(tmp_path, both(ask=True, edge=True))
    assert fold("run", workspace(), tmp_path, started) == (None, ())


@pytest.mark.parametrize(
    ("mode", "space", "started"),
    [
        ("test", None, 1.0),
        ("test", "declared", None),
        ("run", "declared", 1.0),
    ],
)
def test_a_caller_with_no_breakdown_to_record_says_so_by_omission(tmp_path, mode, space, started):
    given = workspace() if space == "declared" else None
    assert fold(mode, given, tmp_path, started) == (None, ())


@pytest.mark.parametrize("record", [workspace(cases=False), workspace(graded=False, cases=False)])
def test_a_record_that_declares_no_breakdown_folds_nothing_and_raises_nothing(tmp_path, record):
    assert fold("test", record, tmp_path, time.time()) == (None, ())


def test_a_run_that_wrote_no_report_records_no_breakdown(tmp_path):
    # ⭐ The Acceptance's third clause: a compile failure writes no report, and
    # that is a run that happened rather than a failure of this module.
    assert fold("test", workspace(), tmp_path, time.time()) == (None, ())
    (tmp_path / "reports").mkdir()
    assert fold("test", workspace(), tmp_path, time.time()) == (None, ())


# --------------------------------------------------------------------------
# A refusal is said, never swallowed
# --------------------------------------------------------------------------


def said_once(result) -> str:
    cases, said = result
    assert cases is None and len(said) == 1
    return said[0]


def test_a_report_older_than_the_run_is_refused_and_the_reason_is_said(tmp_path):
    report = write_report(tmp_path, both(ask=True, edge=True))
    stale = time.time() + 600
    line = said_once(fold("test", workspace(), tmp_path, stale))
    assert line.startswith("--- ") and line.endswith(" ---")
    assert "older than the" in line and DECLARED in line
    # ⚠️ The plant is OBSERVED: the same report folds when the clock is the
    # run's own, so the RED above is staleness and not an unreadable file.
    assert report.exists()
    assert fold("test", workspace(), tmp_path, stale - 1200)[0] == {ASK: True, EDGE: True}


def test_a_report_that_is_not_readable_junit_is_a_named_failure(tmp_path):
    started = time.time()
    (tmp_path / "reports").mkdir()
    (tmp_path / DECLARED).write_text("<testsuite><testcase", encoding="utf-8")
    line = said_once(fold("test", workspace(), tmp_path, started))
    assert "not well-formed" in line and DECLARED in line


def test_a_test_the_case_map_does_not_name_is_refused_rather_than_counted(tmp_path):
    started = time.time()
    write_report(tmp_path, both(True, True) + PASSING.format(name="test_something_else"))
    line = said_once(fold("test", workspace(), tmp_path, started))
    assert "does not" in line


def test_a_workspace_this_reader_cannot_parse_costs_the_breakdown_and_not_the_run(tmp_path):
    started = time.time()
    write_report(tmp_path, both(True, True))
    broken = workspace() | {"test_command": "not an argv"}
    line = said_once(fold("test", broken, tmp_path, started))
    assert line.startswith("--- the case breakdown could not be read: ")


def test_every_line_said_is_the_one_template_and_carries_no_absolute_path(tmp_path):
    started = time.time()
    (tmp_path / "reports").mkdir()
    (tmp_path / DECLARED).write_text("<nothing/>", encoding="utf-8")
    line = said_once(fold("test", workspace(), tmp_path, started))
    head, _, tail = NO_BREAKDOWN.partition("{reason}")
    assert line.startswith(head) and line.endswith(tail)
    assert str(tmp_path) not in line and "/home/" not in line
