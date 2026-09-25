"""Mirror of `src/studyforge/exercise/concepts.py` (R12).

⭐ What an exercise practises rides in its record's optional `concepts` key:
read where carried, refused where malformed, and written only where carried —
so every record written before the key round-trips to the bytes it was read
from.
"""

from __future__ import annotations

import pytest

from studyforge.exercise import ExerciseError, from_document, to_document
from studyforge.exercise.concepts import CONCEPTS, concepts_in
from tests.studyforge.exercise.test_record import RECORD, WHERE
from tests.studyforge.render.page.test_practice import QUIZ


def test_a_record_that_says_nothing_carries_nothing_and_writes_nothing():
    assert concepts_in(RECORD, WHERE) is None
    read = from_document(dict(RECORD), WHERE)
    assert read.concepts is None
    assert CONCEPTS not in to_document(read)
    assert to_document(read) == RECORD


def test_a_record_that_says_what_it_practises_carries_it_and_writes_it_back():
    said = {**RECORD, CONCEPTS: ["a record is final", "equals compares components"]}
    read = from_document(dict(said), WHERE)
    assert read.concepts == ("a record is final", "equals compares components")
    assert to_document(read) == said


def test_a_quiz_carries_what_it_practises_too():
    said = {**QUIZ, CONCEPTS: ["what a class declaration opens"]}
    read = from_document(dict(said), WHERE)
    assert read.is_quiz and read.concepts == ("what a class declaration opens",)
    assert to_document(read)[CONCEPTS] == ["what a class declaration opens"]


@pytest.mark.parametrize("value", [[], "one idea", [""], ["  "], [1], None, {"a": "b"}])
def test_anything_but_a_list_of_sentences_is_refused_naming_the_record(value):
    with pytest.raises(ExerciseError, match=f"{WHERE}: 'concepts' is a non-empty list"):
        concepts_in({CONCEPTS: value}, WHERE)
    with pytest.raises(ExerciseError):
        from_document({**RECORD, CONCEPTS: value}, WHERE)
