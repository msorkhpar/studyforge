"""Mirror of `src/studyforge/exercise/quiz/options.py` (R12): reading one question's options."""

from __future__ import annotations

import pytest

from studyforge.exercise import ExerciseError
from studyforge.exercise.quiz.options import (
    normalised,
    options_of,
    read_id,
    read_text,
    require_distinct,
)

WHERE = "demo/unit-01/practice-1"


def option(identifier: str, correct: bool, text: str | None = None) -> dict:
    return {"id": identifier, "text": text or f"Option {identifier}", "correct": correct,
            "says": f"Why {identifier}."}


def refused(value, select=None) -> str:
    with pytest.raises(ExerciseError) as raised:
        options_of(value, WHERE, select)
    return str(raised.value)


def test_one_key_is_read_and_none_or_two_are_refused():
    assert [o.id for o in options_of([option("a", True), option("b", False)], WHERE)] == ["a", "b"]
    assert "keys 0" in refused([option("a", False), option("b", False)])
    assert "keys 2" in refused([option("a", True), option("b", True), option("c", False)])


def test_a_stated_select_is_the_number_keyed_and_leaves_one_to_rule_out():
    three = [option("a", True), option("b", True), option("c", False)]
    assert len(options_of(three, WHERE, 2)) == 3
    assert "choose 3" in refused(three, 3)
    assert "choose 2" in refused([option("a", True), option("b", True)], 2)
    assert "choose 2" in refused([option("a", True), option("b", False), option("c", False)], 2)


def test_two_options_that_say_the_same_after_normalisation_are_refused():
    same = [option("a", True, "Same  words"), option("b", False, "same words")]
    assert "identical" in refused(same)
    assert normalised("Ｓame  Words") == "same words"
    assert normalised("1,000") != normalised("1000")


def test_an_id_repeated_and_fewer_than_two_options_are_refused():
    assert "option id more than once" in refused([option("a", True), option("a", False, "Other")])
    assert "at least 2" in refused([option("a", True)])


def test_ids_are_plain_tokens_and_texts_are_not_blank():
    assert read_id("a.b-c_1", "an option's", WHERE) == "a.b-c_1"
    for bad in ("", " a", "a b", "a\n", 3, None):
        with pytest.raises(ExerciseError):
            read_id(bad, "an option's", WHERE)
    with pytest.raises(ExerciseError):
        read_text("  ", "a text", WHERE)
    with pytest.raises(ExerciseError):
        require_distinct(["a", "a"], WHERE, "{count} repeated")
