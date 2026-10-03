"""The exam-form mock as raw record values, written from `depth1`'s page, for the record and
browser tests: the fixture course's pool (`tests.fixtures.claude_shape.exam_form`) re-addressed to
the page a built corpus really has. Mirrors no source module (R12): material, not a test.
"""

from __future__ import annotations

from studyforge.exercise.quiz import mock_document, questions_document
from tests.fixtures.claude_shape import exam_form


def questions(origin: dict) -> list[dict]:
    """The pool's twelve questions, each written from `origin`."""
    return [{**one, "origin": origin} for one in questions_document(exam_form.questions())]


def mock(**changes) -> dict:
    """The record's `mock` key, with `changes` applied."""
    return {**mock_document(exam_form.mock()), **changes}


def keyed(pool: list[dict]) -> dict:
    """`{question id: key}`: an option id, or the list of ids for a multiple-response question."""
    made = {}
    for one in pool:
        keys = [o["id"] for o in one["options"] if o["correct"]]
        made[one["id"]] = keys if "select" in one else keys[0]
    return made
