"""Mirror of `src/studyforge/exercise/quiz/exam.py` (R12): scenarios, difficulties, sittings, scale.

The mock's own reading of them, with the questions beside, is `test_mock_form.py`.
"""

from __future__ import annotations

import pytest

from studyforge.exercise import ExerciseError
from studyforge.exercise.quiz import exam

WHERE = "demo/unit-01/practice-1"


def refused(call, *args) -> str:
    with pytest.raises(ExerciseError) as raised:
        call(*args, WHERE)
    return str(raised.value)


def test_a_scenario_is_a_token_a_title_and_a_context_and_nothing_else():
    one = {"id": "s1", "title": "T", "context": "One. Two."}
    assert exam.scenarios_of([one], WHERE)[0].context == "One. Two."
    assert "scenario" in refused(exam.scenarios_of, [{**one, "extra": 1}])
    assert "scenario" in refused(exam.scenarios_of, [{"id": "s1", "title": "T"}])
    assert "more than once" in refused(exam.scenarios_of, [one, one])
    assert "scenarios" in refused(exam.scenarios_of, [])


def test_a_sitting_draws_questions_or_scenarios_never_both_and_counts_are_whole():
    ok = exam.sittings_of([{"id": "a", "title": "A", "questions": 3, "minutes": 5}], WHERE)[0]
    assert (ok.questions, ok.scenarios, ok.minutes) == (3, None, 5)
    assert exam.sittings_of([{"id": "a", "title": "A"}], WHERE)[0].questions is None
    assert "both" in refused(exam.sittings_of, [{"id": "a", "title": "A", "questions": 1,
                                                  "scenarios": 1}])
    for count in (0, -1, 1.5, True, "3"):
        assert "sitting" in refused(exam.sittings_of, [{"id": "a", "title": "A",
                                                         "questions": count}])


def test_a_sitting_is_written_back_with_only_the_keys_it_carries():
    sitting = exam.Sitting("a", "A", questions=3)
    assert exam.sitting_document(sitting) == {"id": "a", "title": "A", "questions": 3}


def test_the_scale_is_linear_rounded_and_refuses_a_pass_outside_it():
    scale = exam.scale_of({"min": 200, "max": 800, "pass": 500}, WHERE)
    assert [scale.scaled(r, 4) for r in range(5)] == [200, 350, 500, 650, 800]
    assert scale.scaled(1, 3) == 400 and scale.scaled(0, 0) == 200
    for bad in ({"min": 0, "max": 0, "pass": 0}, {"min": 1, "max": 5, "pass": 6},
                {"min": -1, "max": 5, "pass": 2}, {"min": 1, "max": 5}):
        assert "scale" in refused(exam.scale_of, bad)


def test_minutes_and_layout_have_their_own_ranges():
    assert exam.minutes_of(90, "a mock exam's", WHERE) == 90
    for bad in (0, 1441, True, 1.5):
        assert "minutes" in refused(exam.minutes_of, bad, "a mock exam's")
    assert exam.layout_of("exam", WHERE) == "exam"
    assert "layout" in refused(exam.layout_of, "page")


def test_difficulties_are_distinct_tokens_with_a_title():
    found = exam.difficulties_of([{"id": "a", "title": "A"}, {"id": "b", "title": "B"}], WHERE)
    assert [one.id for one in found] == ["a", "b"]
    assert "more than once" in refused(exam.difficulties_of, [{"id": "a", "title": "A"}] * 2)
    assert exam.SCENARIO_SENTENCES == (2, 4)
