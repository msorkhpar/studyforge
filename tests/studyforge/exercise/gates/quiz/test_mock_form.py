"""The gates over a mock exam that uses the exam form: `P1` for scenarios and difficulties, and
`Q4`/`Q5`/`Q3` for a multiple-response question.

**What it asserts.** The fixture course's pool clears the quiz five and `P1`; each scenario plant
(undeclared, unused, a context too long or too short) turns `P1` red and is named by what it
breaks; a difficulty nobody declared or carries does too; `Q4` holds a multiple-response question
to the count it states, in both directions, and names it; the quiz five are untouched by a scenario
plant; `Q3` owes one judgement per option that is not keyed, which for a two-key question is two
fewer than its options.
"""

from __future__ import annotations

import dataclasses

from studyforge.exercise import Exercise
from studyforge.exercise.gates.quiz import (
    P1,
    Q3,
    check_mock,
    check_quiz,
    cited_for,
    key_total_and_single,
)
from studyforge.exercise.quiz import Scenario
from tests.fixtures.claude_shape import exam_form
from tests.studyforge.exercise.gates.quiz import material
from tests.studyforge.exercise.gates.quiz.material import WHERE


def pool() -> Exercise:
    base = material.exercise()
    origin = base.questions[0].origin
    questions = tuple(dataclasses.replace(q, origin=origin) for q in exam_form.questions())
    return dataclasses.replace(base, questions=questions, mock=exam_form.mock())


def run(exercise: Exercise):
    ledger = material.ledger()
    origins = cited_for(exercise.questions, ledger, WHERE)
    quiz = check_quiz(exercise, material.judgements(exercise.questions), origins, ledger, WHERE)
    return quiz, check_mock(exercise, WHERE)


def scenario_edit(**changes) -> Exercise:
    exercise = pool()
    first, *rest = exercise.mock.scenarios
    edited = (dataclasses.replace(first, **changes), *rest)
    mock = dataclasses.replace(exercise.mock, scenarios=edited)
    return dataclasses.replace(exercise, mock=mock)


def test_the_course_shape_pool_clears_the_quiz_five_and_the_mock_gate():
    quiz, mock = run(pool())
    assert all(v.held for v in quiz), [v.says for v in quiz if not v.held]
    assert mock.id == P1 and mock.held, mock.says


def test_a_question_under_an_undeclared_scenario_is_named_by_its_stem():
    exercise = pool()
    spoiled = dataclasses.replace(exercise.questions[0], scenario="nowhere")
    plant = dataclasses.replace(exercise, questions=(spoiled, *exercise.questions[1:]))
    quiz, mock = run(plant)
    assert not mock.held and "does not declare" in mock.says and spoiled.stem in mock.says
    assert "nowhere" not in mock.says and all(v.held for v in quiz)


def test_a_declared_scenario_with_no_question_is_named_by_its_title():
    exercise = pool()
    extra = Scenario(
        "unused", "A card nobody asks about", "One sentence here. Two sentences there."
    )
    plant = dataclasses.replace(
        exercise,
        mock=dataclasses.replace(exercise.mock, scenarios=(*exercise.mock.scenarios, extra)),
    )
    _, mock = run(plant)
    assert not mock.held and "has no question" in mock.says
    assert "A card nobody asks about" in mock.says


def test_a_scenario_context_is_two_to_four_sentences():
    one = run(scenario_edit(context="Only one sentence here."))[1]
    five = run(scenario_edit(context="A one. B two. C three. D four. E five."))[1]
    assert not one.held and "1 sentence(s)" in one.says
    assert not five.held and "5 sentence(s)" in five.says
    assert run(scenario_edit(context="First here. Second here. Third here. Fourth here."))[1].held
    assert run(scenario_edit(context="Is it so? It is so!"))[1].held


def test_a_difficulty_nobody_declared_or_carries_turns_p1_red():
    exercise = pool()
    spoiled = dataclasses.replace(exercise.questions[0], difficulty="mystery")
    undeclared = run(dataclasses.replace(exercise, questions=(spoiled, *exercise.questions[1:])))[1]
    assert not undeclared.held and "does not declare" in undeclared.says
    labels_none = tuple(dataclasses.replace(q, difficulty=None) for q in exercise.questions)
    unused = run(dataclasses.replace(exercise, questions=labels_none))[1]
    assert not unused.held and "labels no question" in unused.says


def test_q4_holds_a_multiple_response_question_to_the_count_it_states():
    exercise = pool()
    multi = next(q for q in exercise.questions if q.select)
    assert key_total_and_single(exercise.questions).held
    for state in (3, 1):
        wrong = dataclasses.replace(multi, select=state)
        if state == 1:
            wrong = dataclasses.replace(multi, select=None)
        verdict = key_total_and_single((wrong,))
        assert not verdict.held and multi.stem in verdict.says, state
    no_rest = dataclasses.replace(
        multi,
        options=tuple(dataclasses.replace(o, correct=True) for o in multi.options),
        select=len(multi.options),
    )
    assert not key_total_and_single((no_rest,)).held


def test_q4_says_the_count_it_keys_and_a_plain_quiz_keeps_its_old_sentence():
    exercise = pool()
    assert "number of its distinct options it asks" in key_total_and_single(exercise.questions).says
    plain = key_total_and_single(tuple(q for q in exercise.questions if not q.select)).says
    assert "keys exactly 1 of its distinct options" in plain


def test_q3_owes_one_judgement_per_option_that_is_not_keyed():
    exercise = pool()
    multi = next(q for q in exercise.questions if q.select)
    judgements = material.judgements(exercise.questions)
    q3 = [j for j in judgements if j.gate == Q3 and j.question == multi.id]
    assert len(q3) == len(multi.options) - multi.select
    missing = tuple(j for j in judgements if not (j.gate == Q3 and j.question == multi.id))
    ledger = material.ledger()
    origins = cited_for(exercise.questions, ledger, WHERE)
    verdicts = check_quiz(exercise, missing, origins, ledger, WHERE)
    assert any(v.id == Q3 and not v.held for v in verdicts)
