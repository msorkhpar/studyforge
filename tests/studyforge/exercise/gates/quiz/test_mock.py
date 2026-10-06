"""Mirror of `src/studyforge/exercise/gates/quiz/mock.py` (R12): the mock family and `P1`.

**What it asserts.** `Q4` and `Q5` run on every question of a mock exam unchanged and name the
question that fails; `Q1` to `Q3` are owed and recorded per question; `P1` holds for a sound mock
exam and is red for each of its three plants, each a real edit to the exam and each named by what it
breaks; the mock family is registered beside the quiz family and makes a record complete only with
`P1`; a quiz that is not a mock exam is gated by the five it always was.
"""

from __future__ import annotations

import dataclasses

import pytest

from studyforge.exercise import Exercise, ExerciseError
from studyforge.exercise.gates import GateRecord, record_document, record_of
from studyforge.exercise.gates.families import declared_order, family_of
from studyforge.exercise.gates.quiz import (
    MOCK,
    P1,
    Q4,
    Q5,
    QUIZ,
    check_mock,
    check_quiz,
    cited_for,
    key_total_and_single,
)
from studyforge.exercise.quiz import Domain, Mock, Question
from tests.studyforge.exercise.gates.quiz import material
from tests.studyforge.exercise.gates.quiz.material import WHERE

SOUND = "a sound mock exam"
NO_DOMAIN = "a question names no domain"
UNDECLARED = "a question names a domain the exam does not declare"
UNUSED = "a declared domain has no question"
TWO_KEYED = "a question of the exam keys two options"
SPREAD = "a question of the exam cites a passage the source has changed"


def domains(*ids: str) -> tuple[Domain, ...]:
    return tuple(Domain(one, f"Domain {one}") for one in ids)


def exam(plant: str = SOUND) -> Exercise:
    """Two questions over two domains, with one real edit applied for the plant named."""
    base = material.exercise()
    first, second = base.questions
    first = dataclasses.replace(first, domain="D1")
    second = dataclasses.replace(second, domain="D2")
    declared = domains("D1", "D2")
    if plant == NO_DOMAIN:
        second = dataclasses.replace(second, domain=None)
    elif plant == UNDECLARED:
        second = dataclasses.replace(second, domain="ZZ")
    elif plant == UNUSED:
        declared = domains("D1", "D2", "D3")
    elif plant == TWO_KEYED:
        first = dataclasses.replace(
            first, options=tuple(dataclasses.replace(o, correct=True) for o in first.options)
        )
    return dataclasses.replace(
        base, questions=(first, second), mock=Mock(pass_mark=60, domains=declared)
    )


def gates(plant: str = SOUND):
    exercise = exam(plant)
    ledger = material.ledger(material.DRIFTED_PAGE if plant == SPREAD else material.NONE)
    origins = cited_for(exercise.questions, material.ledger(), WHERE)
    quiz = check_quiz(exercise, material.judgements(exercise.questions), origins, ledger, WHERE)
    return exercise, quiz, check_mock(exercise, WHERE)


def test_a_sound_mock_exam_clears_the_quiz_five_and_the_mock_gate():
    _, quiz, mock = gates()
    assert [entry.id for entry in quiz] == list(QUIZ.gates)
    assert all(entry.held for entry in quiz), [entry.says for entry in quiz if not entry.held]
    assert mock.id == P1 and mock.family == MOCK.name and mock.held, mock.says


@pytest.mark.parametrize("plant", [NO_DOMAIN, UNDECLARED, UNUSED])
def test_each_domain_plant_turns_the_mock_gate_red_and_names_what_is_wrong(plant):
    _, quiz, mock = gates(plant)
    assert not mock.held
    assert all(entry.held for entry in quiz), "a domain plant must not touch the quiz five"
    assert "finding" in mock.says


def test_the_domain_plants_are_named_by_what_they_break():
    assert "names no domain" in gates(NO_DOMAIN)[2].says
    assert "does not declare" in gates(UNDECLARED)[2].says
    assert "has no question" in gates(UNUSED)[2].says


def test_a_question_is_named_by_its_stem_and_a_domain_by_its_title_never_by_an_id():
    says = gates(NO_DOMAIN)[2].says
    assert exam().questions[1].stem in says
    assert "q-2" not in says
    assert "Domain D3" in gates(UNUSED)[2].says


def test_every_finding_is_reported_at_once_not_the_first():
    exercise = exam()
    first, second = exercise.questions
    both = dataclasses.replace(
        exercise,
        questions=(
            dataclasses.replace(first, domain=None),
            dataclasses.replace(second, domain="ZZ"),
        ),
    )
    says = check_mock(both, WHERE).says
    assert says.startswith("4 finding(s)"), says  # two questions, and D1 and D2 now unused


def test_q4_is_red_on_the_question_that_keys_two_options_and_names_it_in_an_exam():
    exercise, quiz, mock = gates(TWO_KEYED)
    q4 = next(entry for entry in quiz if entry.id == Q4)
    assert not q4.held and exercise.questions[0].stem in q4.says
    assert exercise.questions[1].stem not in q4.says, "Q4 named the question that is sound"
    assert mock.held, "the keys are not the mock gate's to read"


def test_q4_reads_every_question_of_a_larger_exam_and_counts_the_ones_that_fail():
    many = [dataclasses.replace(material.exercise().questions[1], id=f"x{n}") for n in range(30)]

    def keyed_twice(q):
        return dataclasses.replace(
            q, options=tuple(dataclasses.replace(o, correct=True) for o in q.options)
        )

    spoiled = [keyed_twice(q) if n in (3, 11, 29) else q for n, q in enumerate(many)]
    verdict = key_total_and_single(tuple(spoiled))
    assert not verdict.held and verdict.says.startswith("3 of this quiz's 30 questions")


def test_q5_is_still_per_question_in_an_exam():
    _, quiz, _ = gates(SPREAD)
    q5 = next(entry for entry in quiz if entry.id == Q5)
    assert not q5.held and "no longer" in q5.says


def test_the_judgements_are_owed_per_question_and_a_missing_one_is_refused():
    exercise = exam()
    origins = cited_for(exercise.questions, material.ledger(), WHERE)
    owed = material.judgements(exercise.questions)
    per_question = {judgement.question for judgement in owed}
    assert per_question == {question.id for question in exercise.questions}
    first = exercise.questions[0].id
    short = tuple(j for j in owed if not (j.question == first and j.gate == "Q1"))
    held = check_quiz(exercise, short, origins, material.ledger(), WHERE)
    assert not next(entry for entry in held if entry.id == "Q1").held


# ------------------------------------------------------------------ the family


def test_the_mock_family_is_registered_with_one_gate_and_owns_it():
    assert MOCK.gates == (P1,)
    assert family_of(P1) == "mock" and family_of("Q4") == "quiz"
    assert ("mock", P1) in declared_order()


def in_declared_order(verdicts):
    """A record writes its verdicts family by name, then gate by its family's own order."""
    order = {pair: at for at, pair in enumerate(declared_order())}
    return tuple(sorted(verdicts, key=lambda v: order[(v.family, v.id)]))


def test_a_mock_record_carries_both_families_and_is_complete_only_with_the_mock_gate():
    exercise, quiz, mock = gates()
    origins = cited_for(exercise.questions, material.ledger(), WHERE)
    whole = GateRecord(inputs=(), origins=origins, verdicts=in_declared_order((*quiz, mock)))
    assert whole.clears
    read = record_of(record_document(whole), WHERE)
    assert [v.id for v in read.verdicts] == ["P1", "Q1", "Q2", "Q3", "Q4", "Q5"]
    # ⚠️ A record names a family by carrying one of its verdicts, so one with `P1` deleted names
    # only the quiz family and reads complete. `validate` owes the exercise its `P1` for that
    # (`tests/studyforge/validate/test_exercises.py`).
    deleted = record_document(whole)
    deleted["gates"] = [v for v in deleted["gates"] if v["id"] != P1]
    assert [v.id for v in record_of(deleted, WHERE).verdicts] == ["Q1", "Q2", "Q3", "Q4", "Q5"]


def test_a_quiz_that_names_only_its_own_family_is_complete_without_the_mock_gate():
    exercise = material.exercise()
    origins = cited_for(exercise.questions, material.ledger(), WHERE)
    quiz = check_quiz(
        exercise, material.judgements(exercise.questions), origins, material.ledger(), WHERE
    )
    record = GateRecord(inputs=(), origins=origins, verdicts=quiz)
    assert record_of(record_document(record), WHERE).clears


def test_a_record_that_names_the_mock_family_without_its_gate_is_impossible_to_write():
    # The family has one gate, so naming it IS carrying it: a verdict of the mock family is `P1`.
    exercise, quiz, mock = gates()
    assert {v.family for v in (*quiz, mock)} == {"quiz", "mock"}
    assert len([v for v in (*quiz, mock) if v.family == "mock"]) == 1


# ------------------------------------------------------------------ what it refuses


def test_the_mock_gate_refuses_a_quiz_that_declares_no_mock():
    with pytest.raises(ExerciseError, match="declares none"):
        check_mock(material.exercise(), WHERE)


def test_the_mock_gate_refuses_what_is_not_a_quiz():
    code = Exercise("p/x.py", None, ("python3", "p/x.py"), None, None, None)
    with pytest.raises(ExerciseError):
        check_mock(code, WHERE)


def test_a_quiz_that_is_not_a_mock_exam_is_gated_by_the_five_it_always_was():
    exercise = material.exercise()
    origins = cited_for(exercise.questions, material.ledger(), WHERE)
    read = check_quiz(
        exercise, material.judgements(exercise.questions), origins, material.ledger(), WHERE
    )
    assert [entry.id for entry in read] == ["Q1", "Q2", "Q3", "Q4", "Q5"]
    assert {entry.family for entry in read} == {"quiz"}


def test_a_questions_domain_is_data_and_never_changes_what_q4_says():
    plain = key_total_and_single(material.exercise().questions)
    tagged = key_total_and_single(exam().questions)
    assert plain.held and tagged.held
    assert Question.__dataclass_fields__["domain"].default is None
