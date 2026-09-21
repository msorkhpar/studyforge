"""One run's reading: the three outcomes, and the check that a gate reads the run it asked for.

⚠️ **The three outcomes are three and not two** because the gates answer
differently for each: *no report at all* is what `G2` needs to see from a
starter that does not build, and *a report that could not be folded* is `G4`'s
defect. ⛔ Collapsing them would make an authoring defect read as a starter
doing its job.
"""

from __future__ import annotations

import time

import pytest

from studyforge.exercise import EDGE, MAIN, Case, Exercise, ExerciseError, Report
from studyforge.exercise.gates import FIRST, REFERENCE, Run, folded, plant_role, require_run

WHERE = "corpus/adding-up/unit-01/practice-1"

ASK = Case(id="test_adds_up", kind=MAIN, says="a basket adds up")
EDGE_CASE = Case(id="test_empty", kind=EDGE, says="an empty basket is zero")

PASSING = """<?xml version="1.0"?>
<testsuite name="pytest" tests="2">
  <testcase classname="t" name="test_adds_up"/>
  <testcase classname="t" name="test_empty"/>
</testsuite>
"""

UNMAPPED = """<?xml version="1.0"?>
<testsuite name="pytest" tests="1">
  <testcase classname="t" name="test_nobody_declared"/>
</testsuite>
"""


def exercise() -> Exercise:
    """A graded record whose report the folds below are taken out of."""
    return Exercise(
        main_path="work/solution.py",
        test_path="work/test_solution.py",
        run_command=("python3", "work/solution.py"),
        test_command=("python3", "-m", "pytest"),
        provenance="generated",
        trust="advisory",
        cases=(ASK, EDGE_CASE),
        report=Report(format="junit", path="reports/report.xml"),
    )


def write(root, text: str) -> float:
    """Write a report as a run would have, and answer the clock read before it."""
    started = time.time()
    (root / "reports").mkdir(exist_ok=True)
    (root / "reports" / "report.xml").write_text(text, encoding="utf-8")
    return started


def test_a_report_this_build_folded_carries_the_ids_that_passed(tmp_path):
    started = write(tmp_path, PASSING)
    run = folded(exercise(), tmp_path, REFERENCE, FIRST, 0, WHERE, started=started)
    assert run.reported and run.refusal is None
    assert run.passed(ASK) and run.passed(EDGE_CASE)
    assert run.exit_code == 0


def test_a_run_that_wrote_no_report_is_neither_a_breakdown_nor_a_refusal(tmp_path):
    run = folded(exercise(), tmp_path, REFERENCE, FIRST, 1, WHERE, started=time.time())
    assert not run.reported
    assert run.refusal is None
    assert not run.passed(ASK)


def test_a_report_that_could_not_be_folded_is_carried_and_never_raised(tmp_path):
    started = write(tmp_path, UNMAPPED)
    run = folded(exercise(), tmp_path, REFERENCE, FIRST, 0, WHERE, started=started)
    assert not run.reported
    assert run.refusal is not None
    assert "does not" in run.refusal


def test_a_case_the_report_did_not_name_did_not_pass(tmp_path):
    started = write(tmp_path, PASSING.replace('<testcase classname="t" name="test_empty"/>', ""))
    run = folded(exercise(), tmp_path, REFERENCE, FIRST, 1, WHERE, started=started)
    assert run.passed(ASK)
    assert not run.passed(EDGE_CASE)


def test_a_gate_reads_the_run_it_asked_for_and_refuses_any_other():
    run = Run(role=REFERENCE, attempt=FIRST, exit_code=0, passed_ids=frozenset())
    assert require_run(run, REFERENCE, FIRST, WHERE) is run
    # ⛔ A caller answering every role with one run would give `G2` the
    # reference's reading and every gate would hold.
    with pytest.raises(ExerciseError, match="handed another run"):
        require_run(run, "starter", FIRST, WHERE)
    with pytest.raises(ExerciseError, match="handed another run"):
        require_run(run, REFERENCE, 2, WHERE)
    with pytest.raises(ExerciseError, match="a gate reads a Run"):
        require_run(None, REFERENCE, FIRST, WHERE)


def test_a_plants_role_names_the_edge_it_is_planted_for():
    assert plant_role(EDGE_CASE) == f"plant:{EDGE_CASE.id}"
