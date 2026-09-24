"""Mirror of `src/studyforge/skills/exercises/quizdoc.py` (R12).

⭐ The document read back is the one `gate_quiz` actually wrote, never one this
test typed, so the reader and the writer are held to one shape. Each refusal is
a copy of that document with one thing moved.
"""

from __future__ import annotations

import json

import pytest

from studyforge.skills.exercises import (
    QUIZ_DOCUMENT,
    QuizRefused,
    gate_quiz,
    quiz_of,
    take,
)
from tests.studyforge.skills.exercises.authoring import Judging, gauge, write_corpus
from tests.studyforge.skills.exercises.test_gating import GAUGE, _brief


def _written(tmp_path):
    """The quiz document `gate_quiz` wrote for the prose page, and its bundle directory."""
    material, graders, pages = write_corpus(tmp_path)
    ledger = take(tmp_path, material, graders, "the ledger")
    brief = _brief(pages[GAUGE], ledger)
    gated = gate_quiz(gauge(brief), brief, ledger, Judging(), where="w")
    assert gated.clears, "the quiz did not clear, so there is nothing to read back"
    where = brief.places.bundle
    return json.loads(dict(gated.files)[f"{where}/{QUIZ_DOCUMENT}"]), where, brief.places


def test_the_document_the_pass_wrote_reads_back_as_the_quiz_it_describes(tmp_path):
    document, where, places = _written(tmp_path)
    quiz = quiz_of(document, where)
    assert quiz.places == places
    assert quiz.title == document["title"]
    assert quiz.record == document["exercise"] and quiz.exercise.is_quiz


@pytest.mark.parametrize("declared", [2, 0, True, "1", None])
def test_a_quiz_api_this_build_does_not_speak_is_refused_through_the_guard(tmp_path, declared):
    # ⛔ `True` is the case a hand-written `!= 1` lets through.
    document, where, _ = _written(tmp_path)
    document["quiz_api"] = declared
    with pytest.raises(QuizRefused, match="quiz_api"):
        quiz_of(document, where)


def test_a_document_whose_keys_moved_is_refused(tmp_path):
    document, where, _ = _written(tmp_path)
    reordered = {"quiz_api": document.pop("quiz_api"), "title": document.pop("title"), **document}
    with pytest.raises(QuizRefused, match="in that order"):
        quiz_of(reordered, where)


def test_an_identity_that_names_another_directory_is_refused(tmp_path):
    document, where, places = _written(tmp_path)
    document["ordinal"] = places.ordinal + 1
    with pytest.raises(QuizRefused, match="nobody can find it by"):
        quiz_of(document, where)


def test_an_identity_of_the_wrong_shape_is_refused(tmp_path):
    document, where, _ = _written(tmp_path)
    document["unit"] = "3"
    with pytest.raises(QuizRefused, match="not an address of segments"):
        quiz_of(document, where)


def test_a_record_that_is_not_a_quiz_is_refused(tmp_path):
    document, where, _ = _written(tmp_path)
    document["exercise"] = {**document["exercise"], "kind": "code"}
    with pytest.raises(ValueError):
        quiz_of(document, where)


def test_a_document_that_is_not_an_object_is_refused():
    with pytest.raises(QuizRefused, match="not a JSON object"):
        quiz_of([], "exercises/kata/python/unit-01/practice-1")
