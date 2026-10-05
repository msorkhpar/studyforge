"""Mirror of `src/studyforge/serve/routes/breakdown.py` (R12): the fold a Submit records.

⭐ **Every report is written at run time under `tmp_path`**, and every declared
path is a workspace path — so no test here names a directory on this machine.
"""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from studyforge.serve.routes.breakdown import (
    CASE_FAILED,
    CASE_LINE,
    CASE_PASSED,
    NO_BREAKDOWN,
    fold,
    said,
)

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


def said_of(case: str, passed: bool) -> str:
    """The line this module says for one case. ⛔ Built from the module's OWN
    constants, so a test that asserted a hand-typed sentence cannot drift from
    the shape the panel parses."""
    return CASE_LINE.format(id=case, verdict=CASE_PASSED if passed else CASE_FAILED)


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
    # ⭐ And what is RECORDED is also what is SAID, in the record's own order
    #: the panel cannot fetch the state namespace — a built page may
    # name no API (R8) — so this stream is the only channel the breakdown has.
    assert said == (said_of(ASK, ask), said_of(EDGE, edge))


def test_a_declared_case_the_report_never_names_is_recorded_as_not_passed(tmp_path):
    # ⭐ A run that stopped early names fewer tests; `edge cases 0/1` is the
    # honest answer and refusing here would tell the reader nothing at all.
    started = time.time()
    write_report(tmp_path, PASSING.format(name=ASK))
    cases, said = fold("test", workspace(), tmp_path, started)
    assert cases == {ASK: True, EDGE: False}
    assert said == (said_of(ASK, True), said_of(EDGE, False))


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


# --------------------------------------------------------------------------
# ⛔ What the panel reads off the stream, and what it cannot
# --------------------------------------------------------------------------


def test_the_line_a_case_is_said_on_is_framed_like_every_other_line_about_the_run():
    # ⭐ `--- exit N ---` and `NO_BREAKDOWN` wear the same frame, and the client
    # already tells such a line from the program's own output by it. ⛔ One line,
    # so a case id carrying a newline could not smuggle a second one — and the
    # ids a record may carry are refused for that before they reach here.
    line = said("test_a_case", passed=True)
    assert line.startswith("--- ") and line.endswith(" ---")
    assert "\n" not in line
    assert said("test_a_case", passed=False) != line


def test_the_two_verdict_words_are_the_module_s_and_are_not_the_run_s_verdict():
    # ⛔ `failed` is a CASE the grader reported against, never a word about the
    # run: `progress.is_pass` is untouched and a reader shown *edge cases 2/3*
    # is looking at an incomplete practice. ⚠️ Asserted so a later
    # rewording cannot quietly turn the breakdown into a second verdict.
    assert CASE_PASSED != CASE_FAILED
    assert CASE_PASSED in said("x", passed=True)
    assert CASE_FAILED in said("x", passed=False)
    assert CASE_LINE.format(id="x", verdict=CASE_PASSED) == said("x", passed=True)


def test_a_run_and_a_practice_with_no_breakdown_say_nothing_at_all(tmp_path):
    # ⛔ Only a Submit produces a grader report, so a Run saying case lines
    # would be a stream no honest writer could have produced. ⭐ Both directions
    # against the same report, so the silence is the MODE and not the harness.
    started = time.time()
    write_report(tmp_path, both(ask=True, edge=True))
    assert fold("run", workspace(), tmp_path, started) == (None, ())
    assert fold("test", None, tmp_path, started) == (None, ())
    assert fold("test", workspace(), tmp_path, started)[1] != ()


def test_a_refusal_says_its_own_sentence_and_no_case_line(tmp_path):
    # ⚠️ The two channels must not be confused: a breakdown that could not be
    # read honestly is a REFUSAL, and a panel handed a case line for it would
    # draw a breakdown of nothing.
    started = time.time()
    write_report(tmp_path, PASSING.format(name="test_nobody_declared"))
    _, refused = fold("test", workspace(), tmp_path, started)
    assert len(refused) == 1
    assert refused[0].startswith(NO_BREAKDOWN.split("{")[0])
    assert CASE_LINE.split("{")[0] not in refused[0]


# --------------------------------------------------------------------------
# The detail lines, which only a page that asked is told
# --------------------------------------------------------------------------

import json  # noqa: E402

from studyforge.serve.routes.breakdown import DETAIL_LINE, DETAIL_VERSION, detail  # noqa: E402

LOGGED = (
    '<testcase classname="practice.check_greet" name="{name}">'
    '<failure message="AssertionError: assert 1 == 2"/>'
    "<system-out>-- Captured Log --\n[log] DEBUG greet: input name=Ada\n"
    "-- Captured Out --\nprinted</system-out></testcase>"
)


def parsed(line: str) -> dict:
    assert line.startswith("--- detail ") and line.endswith(" ---")
    return json.loads(line[len("--- detail ") : -len(" ---")])


def test_detail_says_one_line_per_declared_case_then_one_for_the_run(tmp_path):
    started = time.time()
    write_report(tmp_path, LOGGED.format(name=ASK) + PASSING.format(name=EDGE))
    lines = detail(workspace(), tmp_path, started)
    assert len(lines) == 3
    first, second, run = (parsed(line) for line in lines)
    assert first == {
        "v": DETAIL_VERSION,
        "case": ASK,
        "passed": False,
        "message": "AssertionError: assert 1 == 2",
        "log": ["DEBUG greet: input name=Ada"],
        "out": ["printed"],
        "err": [],
    }
    assert second["case"] == EDGE and second["passed"] is True
    assert run["run"] is True and run["truncated"] is False
    assert all("\n" not in line for line in lines)  # one line each, whatever the text held


def test_detail_is_a_run_as_well_as_a_submit(tmp_path):
    # ⭐ Unlike the fold, the detail does not wait for a Submit: a Run whose command wrote the report
    # is told.
    write_report(tmp_path, LOGGED.format(name=ASK) + PASSING.format(name=EDGE))
    assert detail(workspace(), tmp_path, time.time() - 5)


@pytest.mark.parametrize(
    "record", [workspace(cases=False), workspace(graded=False, cases=False), None]
)
def test_detail_is_nothing_where_there_is_nothing_to_say(tmp_path, record):
    write_report(tmp_path, LOGGED.format(name=ASK) + PASSING.format(name=EDGE))
    assert detail(record, tmp_path, time.time() - 5) == ()


def test_a_stale_report_costs_the_detail_and_never_raises(tmp_path):
    write_report(tmp_path, LOGGED.format(name=ASK) + PASSING.format(name=EDGE))
    assert detail(workspace(), tmp_path, time.time() + 3600) == ()
    assert detail(workspace(), tmp_path / "elsewhere", time.time()) == ()


def test_the_detail_line_has_one_spelling():
    assert DETAIL_LINE.format(json="{}") == "--- detail {} ---"
