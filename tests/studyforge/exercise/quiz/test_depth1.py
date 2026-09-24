"""The quiz shape proved on the prose fixture — the fixture corpora's `depth1/`, end to end.

⭐ **The corpus this shape exists for**: one level, no exercises, nothing
runnable. ⛔ The reading is taken through the bytes a build would write — built
by `archive.document`, rendered, parsed back, read as a record and graded — so
no step is skipped by handing a dict to the next layer.

⛔ **The fixture itself is untouched** (see `depth1.py`), because other tests
pin counts and digests against it.
"""

from __future__ import annotations

import json

from studyforge.archive.document import render
from studyforge.exercise import NONE, UNGRADED, of, state_of
from studyforge.exercise.quiz import completes, grade, normalised
from tests.studyforge.exercise.quiz.depth1 import (
    PAGE,
    container_text,
    fixture_root,
    on_disk,
    passage,
    practice_document,
    question,
    section,
)

WHERE = "depth-one/unit-01/practice-1"


def test_the_quiz_is_built_from_the_page_it_is_attached_to():
    # ⛔ Gate Q1's shape, taken as a fixture check: the answer has to BE on the
    # page. ⚠️ A quiz whose key is nowhere in the material is the failure that
    # gate exists for, and a test fixture that could not be checked against the
    # page would be the same failure wearing a green tick.
    keyed = next(option for option in question()["options"] if option["correct"])
    assert normalised(keyed["text"]) in normalised(passage())


def test_the_origin_names_a_page_the_container_map_declares():
    # ⚠️ Containment, never a read of that map's `origin` key: the one-reader rule holds
    # that key to one reader across `src/` and `tests/`.
    assert PAGE in container_text()
    assert section() in container_text(), "the section is not a heading this unit has"


def test_the_quiz_survives_the_bytes_a_build_would_write():
    built = practice_document()
    text = render(built)
    assert json.loads(text) == built, "the document does not round-trip through its bytes"
    read_back = on_disk()
    assert read_back == built
    exercise = of(read_back, WHERE)
    assert exercise.is_quiz is True
    assert exercise.questions[0].origin.path == PAGE


def test_the_key_and_the_sentences_are_in_the_bytes_that_reach_disk():
    # ⛔ The whole "no container, no network, no model" claim rests on this:
    # everything grading needs is in the document the reader already has.
    # ⚠️ And the key is not hidden — claiming to hide it is the theatre R5
    # exists to prevent.
    text = render(practice_document())
    keyed = next(option for option in question()["options"] if option["correct"])
    assert keyed["text"] in text and keyed["says"] in text
    assert '"correct": true' in text
    for option in question()["options"]:
        assert option["says"] in text, "an option's sentence is not on the reader's disk"


def test_the_prose_corpus_grades_its_reader_with_no_run_at_all():
    document = on_disk()
    exercise = of(document, WHERE)
    answers = {question.id: question.key.id for question in exercise.questions}
    assert completes(exercise.questions, answers) is True
    wrong = next(option for option in exercise.questions[0].options if not option.correct)
    assert completes(exercise.questions, {exercise.questions[0].id: wrong.id}) is False
    # ⛔ And nothing about a RUN changed: this practice names no grader to run.
    assert state_of(document) == UNGRADED
    assert exercise.graded is False


def test_a_reader_is_told_why_whichever_way_they_went():
    exercise = of(on_disk(), WHERE)
    asked = exercise.questions[0]
    for option in asked.options:
        row = grade(exercise.questions, {asked.id: option.id}).answered[0]
        assert row.says == option.says
        assert row.correct is option.correct


def test_a_corpus_with_no_quiz_is_unaffected():
    # ⭐ Read on `depth1` AS IT SHIPS: the quiz shape changes nothing for a
    # corpus carrying no quiz. ⛔ Its archive
    # documents are read here, not the ones this module builds.
    archived = sorted((fixture_root() / "archive").rglob("*.json"))
    documents = [json.loads(path.read_text(encoding="utf-8")) for path in archived]
    raw = [content for content in documents if "raw_api" in content]
    assert len(raw) >= 4, [path.name for path in archived]
    for content in raw:
        assert "exercise" not in content, "depth1 grew an exercise; this reading is stale"
        assert of(content, "depth1") is None
    assert state_of(None) == NONE
    manifest = json.loads((fixture_root() / "corpus.json").read_text(encoding="utf-8"))
    assert manifest["exercises"] is False, "depth1 stopped being the zero-exercise shape"
