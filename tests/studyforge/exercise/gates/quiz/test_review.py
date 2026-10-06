"""Mirror of `src/studyforge/exercise/gates/quiz/review.py` (R12): `S1`, the review bank's gate."""

from __future__ import annotations

import pytest

from studyforge.exercise import Exercise, ExerciseError
from studyforge.exercise.gates.quiz import REVIEW, S1, check_review
from studyforge.exercise.quiz import Review
from tests.studyforge.skills.exercises.authoring import gauge_questions

WHERE = "here"


def _bank(steps: tuple[int, ...]) -> Exercise:
    return Exercise(
        None,
        None,
        None,
        None,
        "generated",
        "advisory",
        kind="quiz",
        questions=gauge_questions(),
        review=Review(steps),
    )


def test_s1_holds_when_the_bank_has_a_question_for_every_step():
    held = check_review(_bank((1, 3)), WHERE)
    assert held.id == S1 and held.family == REVIEW.name and held.held
    short = check_review(_bank((1, 3, 7)), WHERE)
    assert not short.held and "at least as many questions" in short.says


def test_s1_refuses_a_quiz_that_declares_no_schedule():
    plain = Exercise(
        None, None, None, None, "generated", "advisory", kind="quiz", questions=gauge_questions()
    )
    with pytest.raises(ExerciseError):
        check_review(plain, WHERE)
