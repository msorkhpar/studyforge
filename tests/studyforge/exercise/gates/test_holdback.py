"""Mirror of `src/studyforge/exercise/gates/holdback.py` (R12): the `holdback` family and `H1`.

**What it asserts.** `H1` refuses a project step whose copied candidate (the starter with every
change its page shows applied) passes every case, and names the files the page gave away; it holds
when one case fails on that candidate, and holds without a run when the page shows none of the
step's changes; a run that left no report holds only when it exited non-zero. The family is
registered, writes after `code`, and a record that names it is complete only with `H1`.
"""

from __future__ import annotations

import pytest

from studyforge.exercise import EDGE, KEPT, MAIN, Case, ExerciseError
from studyforge.exercise.gates import GateRecord, record_document, record_of
from studyforge.exercise.gates.families import declared_order, family_of
from studyforge.exercise.gates.holdback import COPIED, H1, HOLDBACK, check_holdback
from studyforge.exercise.gates.runs import Run

WHERE = "corpus/seeds/unit-01/practice-1"

CASES = (
    Case("tests/test_model.py::test_main", MAIN, "a must-ship lot is always chosen"),
    Case("tests/test_model.py::test_edge", EDGE, "an over-heavy must-ship set is refused"),
    Case("tests/test_model.py::test_kept", KEPT, "an empty crate carries nothing"),
)

SHOWN = ("seedcrate/model.py", "seedcrate/report.py")


def copied_run(*passed: str) -> Run:
    """The copied candidate's one run, passing exactly `passed`."""
    return Run(role=COPIED, attempt=1, exit_code=0, passed_ids=frozenset(passed))


def test_a_copied_candidate_that_passes_every_case_is_refused_naming_the_files():
    verdict = check_holdback(CASES, copied_run(*(case.id for case in CASES)), SHOWN, WHERE)
    assert (verdict.id, verdict.family, verdict.held) == (H1, HOLDBACK.name, False)
    assert "seedcrate/model.py" in verdict.says and "seedcrate/report.py" in verdict.says
    assert "Hold back at least one piece the tests grade" in verdict.says


def test_a_copied_candidate_that_fails_one_case_holds_and_says_how_many():
    verdict = check_holdback(CASES, copied_run(CASES[1].id, CASES[2].id), SHOWN, WHERE)
    assert verdict.held, verdict.says
    assert "1 of 3 case(s) fail" in verdict.says


def test_a_page_that_shows_none_of_the_changes_holds_without_a_run():
    verdict = check_holdback(CASES, None, (), WHERE)
    assert verdict.held and "shows none" in verdict.says


def test_a_run_that_left_no_report_and_exited_zero_is_not_read_as_a_hold():
    unread = Run(role=COPIED, attempt=1, exit_code=0)
    verdict = check_holdback(CASES, unread, SHOWN, WHERE)
    assert not verdict.held and "no report" in verdict.says


def test_a_run_that_failed_before_its_tests_reported_holds():
    broken = Run(role=COPIED, attempt=1, exit_code=2, refusal="collection failed")
    verdict = check_holdback(CASES, broken, SHOWN, WHERE)
    assert verdict.held and "fails before its tests report" in verdict.says


def test_another_role_s_run_is_refused():
    with pytest.raises(ExerciseError):
        check_holdback(CASES, Run(role="reference", attempt=1, exit_code=0), SHOWN, WHERE)


def test_the_family_is_registered_and_written_after_the_code_family():
    assert family_of(H1) == HOLDBACK.name
    order = [family for family, _ in declared_order()]
    assert order.index("holdback") > order.index("code")


def test_a_record_naming_the_family_is_complete_only_with_h1():
    verdict = check_holdback(CASES, None, (), WHERE)
    record = GateRecord(inputs=(), origins=(), verdicts=(verdict,))
    assert record_of(record_document(record), WHERE).verdicts == (verdict,)
