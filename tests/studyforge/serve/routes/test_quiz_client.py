"""The served client's quiz half, `window.studyforge.quiz`, read as the data it is.

Mirrors no source module — like `test_run_client.py`, whose file it reads: the
quiz half lives in `serve/assets/run-client.js`, the ONE script a serving
process adds to a page (`W370`).

⛔ **No JavaScript runs in this suite**; the browser reading is
`tests/visual/test_practice_quiz.py`'s. ⭐ What a text can establish is pinned
here: the endpoint and the joining character are the quiz route's own (read
from Python, never retyped), the id pattern is `exercise.quiz.QUIZ_ID`'s, a
grade sends NO body, and nothing about the quiz reaches a built page.
"""

from __future__ import annotations

import re

import pytest

from studyforge.exercise.quiz import QUIZ_ID
from studyforge.render.pageassets import script
from studyforge.serve.response import API_PREFIX
from studyforge.serve.routes import quiz, run


def uncommented() -> str:
    return re.sub(r"/\*.*?\*/", "", run.CLIENT_FILE.read_text(encoding="utf-8"), flags=re.DOTALL)


def constant(name: str) -> str:
    found = re.search(rf"var {name} = (.+);", uncommented())
    assert found, f"the client declares no {name}"
    return found.group(1)


def test_its_endpoint_and_its_joining_character_are_the_quiz_routes_own():
    assert constant("QUIZ_BASE") == f"'{API_PREFIX}/{quiz.NAMESPACE}/'"
    assert constant("CHOSE") == f"'{quiz.CHOSE}'"


def test_its_id_pattern_is_the_records_own():
    # ⭐ Python's `re` reads this literal as JavaScript does; the two must agree,
    # or the client would refuse an id the record admits — or send one the
    # route refuses.
    literal = constant("QUIZ_ID")
    assert literal.startswith("/") and literal.endswith("/")
    assert literal[1:-1].replace("^", r"\A").replace("$", r"\Z") == QUIZ_ID.pattern


@pytest.mark.parametrize("spelled", ["q-1", "a", "Q.2", "opt_3"])
def test_the_id_pattern_admits_what_the_record_admits(spelled):
    literal = constant("QUIZ_ID")[1:-1]
    assert re.fullmatch(literal.strip("^$"), spelled) and QUIZ_ID.match(spelled)


@pytest.mark.parametrize("spelled", ["..", ".", "a=b", "a/b", "", "%2e"])
def test_the_id_pattern_refuses_what_would_reach_another_endpoint(spelled):
    literal = constant("QUIZ_ID")[1:-1]
    assert not re.fullmatch(literal.strip("^$"), spelled)


def test_a_grade_is_a_post_with_no_body_published_apart_from_run():
    # ⛔ A quiz produces no run, so its client is not under `studyforge.run`.
    body = uncommented()
    grading = body[body.index("function grade(") : body.index("window.studyforge = ")]
    assert "method: 'POST'" in grading
    assert "body:" not in grading and "JSON.stringify" not in grading
    assert "window.studyforge.quiz = { available: available, grade: grade };" in body
    assert "grade:" not in body[body.index("window.studyforge.run = {") :]


def test_nothing_about_the_quiz_client_reaches_a_built_page():
    # ⛔ R8's floor: the served client is added by the server, never built in.
    assert "studyforge.quiz =" not in script()
    assert constant("QUIZ_BASE").strip("'") not in script()
