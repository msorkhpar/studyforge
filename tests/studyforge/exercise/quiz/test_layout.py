"""Mirror of `src/studyforge/exercise/quiz/layout.py` (R12): how a plain quiz is laid out, both ways."""

from __future__ import annotations

import pytest

from studyforge.exercise import ExerciseError, from_document, to_document
from tests.studyforge.exercise.quiz import mock_exam
from tests.studyforge.exercise.quiz.mock_corpus import ORIGIN

WHERE = "a unit's practice"
QUESTIONS = [{k: v for k, v in one.items() if k != "domain"} for one in mock_exam.questions(ORIGIN)]


def quiz(**more) -> dict:
    return {"kind": "quiz", "questions": QUESTIONS, **more}


def test_a_quiz_that_names_no_layout_carries_none_and_writes_none_back():
    exercise = from_document(quiz(), WHERE)
    assert exercise.layout is None
    assert "layout" not in to_document(exercise)


@pytest.mark.parametrize("layout", ["steps", "page"])
def test_a_layout_a_quiz_names_is_read_and_written_back_in_the_records_order(layout):
    exercise = from_document(quiz(layout=layout), WHERE)
    assert exercise.layout == layout
    written = to_document(exercise)
    assert written["layout"] == layout
    assert list(written)[-1] == "layout", "a new key is appended, never inserted"
    assert from_document(written, WHERE) == exercise


@pytest.mark.parametrize("value", ["exam", "", None, True, ["page"]])
def test_a_layout_that_is_not_one_of_the_two_is_refused(value):
    with pytest.raises(ExerciseError, match="layout"):
        from_document(quiz(layout=value), WHERE)


def test_a_layout_beside_a_mock_or_a_review_is_refused_as_a_key_nothing_reads():
    mocked = quiz(layout="page", mock=mock_exam.mock())
    with pytest.raises(ExerciseError, match="layout"):
        from_document({**mocked, "questions": mock_exam.questions(ORIGIN)}, WHERE)
    with pytest.raises(ExerciseError, match="layout"):
        from_document(quiz(layout="page", review={"intervals_days": [1, 3]}), WHERE)


def test_a_layout_on_a_record_that_is_not_a_quiz_is_refused_by_name():
    code = {"main_path": "a.py", "run_command": ["python3", "a.py"], "layout": "page"}
    with pytest.raises(ExerciseError, match="layout"):
        from_document(code, WHERE)
    deck = {"kind": "flashcards", "cards": [{"id": "c1", "front": "f", "back": "b"}], "layout": "page"}
    with pytest.raises(ExerciseError, match="layout"):
        from_document(deck, WHERE)
