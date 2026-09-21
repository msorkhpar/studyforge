"""The run list is derived from the case map, so no caller can ask for a suite missing one.

⭐ **This is where *no gate can be skipped* is structural rather than
promised**: `Evidence.taken` has no argument naming a role, a gate or a subset,
and `required_roles` reads the exercise's own cases. ⚠️ A signature that
accepted *which runs to take* would make a suite that skipped `G3` a legal call
rather than a defect.
"""

from __future__ import annotations

import inspect

import pytest

from studyforge.exercise import EDGE, MAIN, Case, Exercise, ExerciseError, Report
from studyforge.exercise.gates import (
    FIRST,
    REFERENCE,
    SECOND,
    STARTER,
    Evidence,
    Run,
    declared_cases,
    edges,
    plant_role,
    required_roles,
)

WHERE = "corpus/adding-up/unit-01/practice-1"

ASK = Case(id="test_adds_up", kind=MAIN, says="a basket adds up")
ONE = Case(id="test_empty", kind=EDGE, says="an empty basket is zero")
TWO = Case(id="test_negative", kind=EDGE, says="a negative price is refused")


def exercise(*cases: Case) -> Exercise:
    """A graded record carrying exactly these cases."""
    return Exercise(
        main_path="work/solution.py",
        test_path="work/test_solution.py",
        run_command=("python3", "work/solution.py"),
        test_command=("python3", "-m", "pytest"),
        provenance="generated",
        trust="advisory",
        cases=cases,
        report=Report(format="junit", path="reports/report.xml"),
    )


def test_the_run_list_is_the_reference_twice_the_starter_and_one_plant_per_edge():
    assert required_roles(exercise(ASK, ONE, TWO), WHERE) == (
        (REFERENCE, FIRST),
        (REFERENCE, SECOND),
        (STARTER, FIRST),
        (plant_role(ONE), FIRST),
        (plant_role(TWO), FIRST),
    )
    # ⛔ Per case: a third edge is a third plant, with nothing else changed.
    third = Case(id="test_huge", kind=EDGE, says="a very long basket still adds up")
    assert len(required_roles(exercise(ASK, ONE, TWO, third), WHERE)) == 6


def test_taken_asks_for_every_role_and_takes_no_argument_that_selects_fewer():
    asked: list[tuple[str, int]] = []

    def attempt(role: str, number: int) -> Run:
        asked.append((role, number))
        return Run(role=role, attempt=number, exit_code=0, passed_ids=frozenset())

    record = exercise(ASK, ONE, TWO)
    evidence = Evidence.taken(record, attempt, WHERE)
    assert tuple(asked) == required_roles(record, WHERE)
    assert len(evidence.runs) == len(asked)

    # ⛔ Asserted on the signature too, because the property is about what a
    # caller CAN ask for: three positional parameters and nothing else.
    parameters = inspect.signature(Evidence.taken).parameters
    assert list(parameters) == ["exercise", "attempt", "where"]
    assert not any(entry.default is not inspect.Parameter.empty for entry in parameters.values())
    assert not any(entry.kind is inspect.Parameter.VAR_KEYWORD for entry in parameters.values())


def test_a_caller_answering_one_run_for_every_role_is_refused():
    one = Run(role=REFERENCE, attempt=FIRST, exit_code=0, passed_ids=frozenset())
    with pytest.raises(ExerciseError, match="handed another run"):
        Evidence.taken(exercise(ASK, ONE), lambda role, number: one, WHERE)


def test_an_exercise_the_gates_cannot_be_read_over_is_refused():
    bare = Exercise(
        main_path="work/solution.py",
        test_path="work/test_solution.py",
        run_command=("python3", "work/solution.py"),
        test_command=("python3", "-m", "pytest"),
        provenance="generated",
        trust="advisory",
    )
    for call in (required_roles, edges, declared_cases):
        with pytest.raises(ExerciseError, match="answering nothing"):
            call(bare, WHERE)


def test_the_edges_are_the_edges_in_the_order_the_corpus_wrote_them():
    assert edges(exercise(ASK, TWO, ONE), WHERE) == (TWO, ONE)
    assert declared_cases(exercise(ASK, TWO), WHERE) == (ASK, TWO)


def test_a_run_that_was_never_taken_is_none_rather_than_an_invented_reading():
    evidence = Evidence(runs=())
    assert evidence.of(REFERENCE, FIRST) is None
