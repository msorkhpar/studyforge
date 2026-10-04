"""Mirror of `src/studyforge/exercise/quiz/review.py` (R12): what makes a quiz a review bank."""

from __future__ import annotations

import pytest

from studyforge.exercise import ExerciseError, from_document, to_document
from studyforge.exercise.quiz import MOST_DAYS, MOST_STEPS, Review, due, review_document, review_of

WHERE = "here"
QUESTION = {
    "id": "q-1",
    "stem": "What is asked?",
    "options": [
        {"id": "a", "text": "This", "correct": True, "says": "The page says so."},
        {"id": "b", "text": "That", "correct": False, "says": "The page says otherwise."},
    ],
    "origin": "notes/page.md",
}


def bank(**extra):
    review = {"intervals_days": [1, 3, 7]}
    return {"kind": "quiz", "questions": [QUESTION], "review": review, **extra}


def test_a_schedule_reads_and_writes_back_the_same_object():
    review = review_of({"intervals_days": [1, 3, 7, 14, 30]}, WHERE)
    assert review == Review((1, 3, 7, 14, 30))
    assert review_document(review) == {"intervals_days": [1, 3, 7, 14, 30]}


@pytest.mark.parametrize(
    "value",
    [
        [],
        "1,3",
        {},
        {"intervals_days": []},
        {"intervals_days": [3, 1]},
        {"intervals_days": [1, 1]},
        {"intervals_days": [0, 2]},
        {"intervals_days": [1, True]},
        {"intervals_days": [1.5]},
        {"intervals_days": [MOST_DAYS + 1]},
        {"intervals_days": list(range(1, MOST_STEPS + 2))},
        {"intervals_days": [1], "extra": 1},
    ],
)
def test_a_schedule_that_is_not_strictly_growing_whole_days_is_refused(value):
    with pytest.raises(ExerciseError):
        review_of(value, WHERE)


def test_a_quiz_record_carries_the_schedule_and_round_trips_with_it():
    record = bank()
    exercise = from_document(record, WHERE)
    assert exercise.is_quiz and exercise.review == Review((1, 3, 7))
    assert to_document(exercise)["review"] == {"intervals_days": [1, 3, 7]}
    assert list(to_document(exercise))[-1] == "review"


def test_a_quiz_without_the_key_is_the_quiz_it_always_was():
    plain = from_document({"kind": "quiz", "questions": [QUESTION]}, WHERE)
    assert plain.review is None and "review" not in to_document(plain)


def test_a_bank_is_never_a_mock_exam_and_a_record_that_is_not_a_quiz_has_no_schedule():
    with pytest.raises(ExerciseError):
        from_document(
            bank(mock={"pass_mark": 70, "domains": [{"id": "d", "title": "D"}]}), WHERE
        )
    with pytest.raises(ExerciseError):
        from_document(
            {"main_path": "a.py", "run_command": ["true"], "review": {"intervals_days": [1]}}, WHERE
        )


def test_the_rule_the_page_implements_is_this_one():
    review = Review((1, 3, 7))
    assert due(review, 0, 10, 10) and due(review, 0, 0, 0)
    assert not due(review, 1, 10, 10) and due(review, 1, 10, 11)
    assert not due(review, 2, 10, 12) and due(review, 2, 10, 13)
    # a streak past the last step keeps the longest wait
    assert not due(review, 9, 10, 16) and due(review, 9, 10, 17)
