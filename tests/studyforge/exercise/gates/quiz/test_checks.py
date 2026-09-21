"""The suite: five verdicts always, one shared record, and no path to `authoritative`.

⛔ **`AX-06`'s last two Acceptance clauses are read here:** *no gate is
configurable off*, and *a quiz that cleared every gate is
`generated`/`advisory`, and asserting `authoritative` anywhere in the chain
fails.* ⭐ The second is taken at every height the chain has — the practice
document, a hand-built `Exercise`, and the gate record — rather than at the one
that was easiest to reach.
"""

from __future__ import annotations

import ast
import dataclasses
import inspect

import pytest

from studyforge.exercise import ExerciseError, of
from studyforge.exercise.gates import (
    GateRecord,
    Verdict,
    record_document,
    record_of,
)
from studyforge.exercise.gates.code import CODE
from studyforge.exercise.gates.quiz import (
    QUIZ,
    check_quiz,
    cited_for,
    require_advisory,
    require_quiz,
)
from studyforge.exercise.quiz import QUIZ_PROVENANCE, QUIZ_TRUST
from studyforge.unit.trust import PROVENANCE, TRUST
from tests.studyforge.exercise.gates.quiz import material
from tests.studyforge.exercise.gates.quiz.material import WHERE
from tests.studyforge.exercise.gates.quiz.test_init import quiz_modules
from tests.support import repository_root


def _origins(exercise):
    """The cited passages a record would carry for this exercise, built from the ledger."""
    return cited_for(exercise.questions, material.ledger(), WHERE)


def test_the_suite_answers_all_five_in_the_families_declared_order():
    exercise = material.exercise()
    origins = _origins(exercise)
    read = check_quiz(
        exercise, material.judgements(exercise.questions), origins, material.ledger(), WHERE
    )
    print([(entry.id, entry.held) for entry in read])
    assert [entry.id for entry in read] == list(QUIZ.gates)
    assert all(entry.family == QUIZ.name for entry in read)
    assert all(entry.held for entry in read), [entry.says for entry in read if not entry.held]
    assert all(entry.says.strip() for entry in read)


def test_a_cleared_quiz_makes_a_record_that_round_trips_beside_the_code_familys():
    exercise = material.exercise()
    origins = _origins(exercise)
    record = GateRecord(
        origins=origins,
        verdicts=check_quiz(
            exercise, material.judgements(exercise.questions), origins, material.ledger(), WHERE
        ),
    )
    assert record.clears is True
    document = record_document(record)
    assert record_document(record_of(document, WHERE)) == document

    # ⭐ THE SEAM, read whole: one record carrying two families, ordered by
    # `families.declared_order()` with no line of `record.py` knowing what a
    # quiz is — and half a family still refused.
    both = GateRecord(
        origins=origins,
        verdicts=(
            *(
                Verdict(id=gate, family=CODE.name, held=True, says=f"{gate} was read")
                for gate in CODE.gates
            ),
            *record.verdicts,
        ),
    )
    carried = record_document(both)
    assert record_document(record_of(carried, WHERE)) == carried
    assert [entry["id"] for entry in carried["gates"]] == [*CODE.gates, *QUIZ.gates]

    carried["gates"] = carried["gates"][:-1]
    with pytest.raises(ExerciseError, match="every gate of every family it names"):
        record_of(carried, WHERE)


def test_a_failed_gate_makes_the_record_refuse_the_bundle():
    exercise = material.exercise()
    origins = _origins(exercise)
    read = check_quiz(
        exercise,
        material.judgements(exercise.questions),
        origins,
        material.ledger(material.DRIFTED_PAGE),
        WHERE,
    )
    refused = GateRecord(origins=origins, verdicts=read)
    print(refused.refused_by)
    assert refused.refused_by == ("Q5",)
    assert refused.clears is False


def test_the_suite_takes_no_option_that_asks_for_fewer_gates():
    parameters = inspect.signature(check_quiz).parameters
    assert list(parameters) == ["exercise", "judgements", "origins", "ledger", "where"]
    assert all(entry.default is inspect.Parameter.empty for entry in parameters.values())
    assert not any(
        entry.kind in (inspect.Parameter.VAR_KEYWORD, inspect.Parameter.VAR_POSITIONAL)
        for entry in parameters.values()
    )


def test_a_gate_with_nothing_to_read_does_not_hold():
    # ⛔ The last way to disable a gate is to give it nothing to read, and a
    # gate that passed for want of evidence would be the off switch spelt
    # differently. ⚠️ **Q4 is the exception and it is stated rather than
    # excluded**: its evidence IS the questions, which a quiz always has, so a
    # Q4 that did not hold here would mean the questions were wrong.
    exercise = material.exercise()
    read = check_quiz(exercise, (), (), {}, WHERE)
    print([(entry.id, entry.held) for entry in read])
    assert [entry.id for entry in read] == list(QUIZ.gates)
    assert all(entry.says.strip() for entry in read)
    starved = {entry.id: entry.held for entry in read}
    assert starved == {"Q1": False, "Q2": False, "Q3": False, "Q4": True, "Q5": False}


def test_an_exercise_that_is_not_a_quiz_is_refused_rather_than_gated():
    with pytest.raises(ExerciseError) as raised:
        require_quiz(_code_exercise(), WHERE)
    assert raised.type is ExerciseError
    assert "'code'" in str(raised.value)
    with pytest.raises(ExerciseError, match="read an Exercise"):
        require_quiz({"kind": "quiz"}, WHERE)


def test_a_quiz_that_asks_nothing_is_refused_at_the_boundary():
    empty = dataclasses.replace(material.exercise(), questions=())
    assert empty.questions == ()
    with pytest.raises(ExerciseError, match="asks nothing"):
        require_quiz(empty, WHERE)
    with pytest.raises(ExerciseError, match="asks nothing"):
        check_quiz(empty, (), (), material.ledger(), WHERE)


# --------------------------------------------------------------------------
# ⛔ Asserting `authoritative` fails at every height of the chain
# --------------------------------------------------------------------------


def test_the_cleared_quiz_is_generated_and_advisory_and_says_so():
    exercise = material.exercise()
    assert (exercise.provenance, exercise.trust) == (QUIZ_PROVENANCE, QUIZ_TRUST)
    assert exercise.authoritative is False


def test_the_practice_document_refuses_every_pair_but_the_one():
    # ⛔ Height 1 — the document. Read over EVERY pair `unit.trust` admits,
    # not over the one R5 already refuses, so a fourth provenance added there
    # is refused on a quiz the day it is added.
    for provenance in PROVENANCE:
        for trust in TRUST:
            document = material.practice_document()
            document["exercise"]["provenance"] = provenance
            document["exercise"]["trust"] = trust
            assert document["exercise"]["provenance"] == provenance
            if (provenance, trust) == (QUIZ_PROVENANCE, QUIZ_TRUST):
                assert of(document, WHERE).authoritative is False
                continue
            with pytest.raises(ExerciseError):
                of(document, WHERE)


def test_a_hand_built_exercise_claiming_authoritative_is_refused_by_the_suite():
    # ⛔ Height 2 — the dataclass, which is frozen and NOT validated. This is
    # the path a gate suite is actually reached by at authoring time, and it
    # is the one `of` cannot close.
    claimed = dataclasses.replace(
        material.exercise(), provenance="bundled", trust="authoritative"
    )
    # ⭐ THE PLANT, OBSERVED: the value really is on the exercise handed over.
    print("claimed:", claimed.provenance, claimed.trust, claimed.authoritative)
    assert claimed.authoritative is True

    for call in (
        lambda: require_advisory(claimed, WHERE),
        lambda: require_quiz(claimed, WHERE),
        lambda: check_quiz(claimed, (), (), material.ledger(), WHERE),
    ):
        with pytest.raises(ExerciseError) as raised:
            call()
        assert raised.type is ExerciseError
        assert "may claim to be the source's own grader" in str(raised.value)

    # ⭐ The positive control: the same three calls on the unplanted exercise
    # do not raise, so this is the claim being refused and not the calls.
    exercise = material.exercise()
    require_advisory(exercise, WHERE)
    assert require_quiz(exercise, WHERE) == exercise.questions


def test_every_widening_of_the_pair_is_refused_and_not_only_authoritative():
    # ⛔ A forbidden-pair list is the shape that failed open once (Ruling 35),
    # so the pair is compared WHOLE: `generated` beside a widened trust is
    # refused exactly as `authoritative` is.
    for provenance in (*PROVENANCE, None):
        for trust in (*TRUST, None):
            if (provenance, trust) == (QUIZ_PROVENANCE, QUIZ_TRUST):
                continue
            claimed = dataclasses.replace(
                material.exercise(), provenance=provenance, trust=trust
            )
            with pytest.raises(ExerciseError, match="source's own grader"):
                require_advisory(claimed, WHERE)


def test_no_module_of_the_sub_package_ever_spells_authoritative_or_bundled():
    # ⭐ Height 3 — the record. A verdict cannot widen a claim its own source
    # never spells, and that is a property of the tree rather than of a run.
    # ⛔ Docstrings are excluded and everything else is read: the sweep is over
    # the literals the code could WRITE, never over the prose that explains it.
    spelt: list[str] = []
    for path in quiz_modules():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for text in _literals(tree):
            if "authoritative" in text or "bundled" in text:
                spelt.append(f"{path.name}: {text}")
    print(spelt)
    assert spelt == []

    # ⭐ Inhabitation (Ruling 191): a sweep that read no literal at all would
    # also report none, and "reported none" is this check's pass reading.
    read = [text for path in quiz_modules() for text in _literals(ast.parse(path.read_text()))]
    assert len(read) > 20, len(read)

    # ⛔ And the pair the suite compares against is IMPORTED rather than
    # re-spelt, so a fourth provenance added to `unit.trust` reaches here
    # without anybody deciding.
    checks = ast.parse((_package() / "checks.py").read_text(encoding="utf-8"))
    taken = {
        alias.name
        for node in ast.walk(checks)
        if isinstance(node, ast.ImportFrom) and node.module == "studyforge.exercise.quiz"
        for alias in node.names
    }
    assert {"QUIZ_PROVENANCE", "QUIZ_TRUST"} <= taken


def _package():
    """Where the quiz gates live, found from the repository root rather than the cwd."""
    return repository_root() / "src" / "studyforge" / "exercise" / "gates" / "quiz"


def _literals(tree: ast.Module) -> list[str]:
    """Every string literal in `tree` that is not a docstring."""
    documented = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            first = node.body[0] if node.body else None
            if (
                isinstance(first, ast.Expr)
                and isinstance(first.value, ast.Constant)
                and isinstance(first.value.value, str)
            ):
                documented.add(id(first.value))
    return [
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant)
        and isinstance(node.value, str)
        and id(node) not in documented
    ]


def _code_exercise():
    """A `code` exercise, read the same way every other record in this tree is."""
    document = {
        "kind": "practice",
        "exercise": {
            "main_path": "work/solution.py",
            "test_path": "work/test_solution.py",
            "run_command": ["python3", "work/solution.py"],
            "test_command": ["python3", "-m", "pytest", "-q"],
            "provenance": "generated",
            "trust": "advisory",
        },
    }
    read = of(document, WHERE)
    assert read is not None and read.kind == "code"
    return read
