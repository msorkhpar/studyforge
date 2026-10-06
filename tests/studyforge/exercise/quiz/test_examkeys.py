"""Mirror of `src/studyforge/exercise/quiz/examkeys.py` (R12): `select` and `shuffle`."""

from __future__ import annotations

import pytest

from studyforge.exercise import ExerciseError
from studyforge.exercise.quiz import examkeys

WHERE = "demo/unit-01/practice-1"


@pytest.mark.parametrize("value", [2, 3, 10])
def test_select_takes_a_whole_number_of_at_least_two(value):
    assert examkeys.read_select(value, WHERE) == value


@pytest.mark.parametrize("value", [1, 0, -1, True, False, 2.0, "2", None, [2]])
def test_select_refuses_anything_else_and_never_quotes_it(value):
    with pytest.raises(ExerciseError) as raised:
        examkeys.read_select(value, WHERE)
    assert "select" in str(raised.value) and WHERE in str(raised.value)


def test_shuffle_is_only_ever_false():
    assert examkeys.read_shuffle(False, WHERE) is False
    for value in (True, 0, None, "false", []):
        with pytest.raises(ExerciseError):
            examkeys.read_shuffle(value, WHERE)


def test_the_extra_keys_are_written_in_one_stated_order_after_domain():
    assert examkeys.EXTRA_KEYS == ("scenario", "select", "shuffle", "difficulty")
    assert examkeys.MINIMUM_SELECT == 2
