"""Mirror of `src/studyforge/serve/routes/quiz.py` (R12) — the server grades a quiz.

⭐ **Every reading is taken over a real connection to `studyforge serve`'s own
instance** (`quizzing.served_instance`), on the prose fixture with a quiz added,
so the guards in front of the route are the ones a reader's page meets.

⛔ **Both directions, always**: a right answer and a wrong one, a complete quiz
and one that is not, a same-origin page and a file page — a route that answered
"right" to everything would pass every one-sided reading here.
"""

from __future__ import annotations

import ast
import inspect
import json

import pytest

from studyforge.progress import Progress
from studyforge.serve.routes import quiz
from tests.studyforge.serve.routes.quizzing import (
    KEYED,
    QUESTIONS,
    WRONG,
    grade_path,
    practice_of,
    quiz_corpus,
    says,
    served_instance,
    source_of,
)
from tests.studyforge.serve.serving import fetch


@pytest.fixture(scope="module")
def corpus(tmp_path_factory: pytest.TempPathFactory):
    """The built prose fixture with its quiz, its source and the quiz's practice key."""
    root = quiz_corpus(tmp_path_factory.mktemp("quiz-route"))
    return root, source_of(root), practice_of(root)


@pytest.fixture(scope="module")
def server(corpus):
    """One real instance over the corpus, for the whole module."""
    with served_instance(corpus[0]) as running:
        yield running


def graded(server, corpus, answers: dict[str, str], headers=None) -> tuple[int, dict]:
    """POST `answers` to the grading endpoint; return the status and the parsed body."""
    _, source, practice = corpus
    status, _, body = fetch(
        server, grade_path(source, practice, answers), method="POST", headers=headers
    )
    return status, json.loads(body)


def rows(verdict: dict) -> dict[str, dict]:
    return {row["id"]: row for row in verdict["questions"]}


def test_every_question_answered_right_completes_and_each_row_carries_its_own_sentence(
    server, corpus
):
    status, verdict = graded(server, corpus, KEYED)
    assert status == 200
    assert verdict["resource"] == "quiz-verdict"
    assert (verdict["asked"], verdict["right"], verdict["complete"]) == (len(QUESTIONS), 2, True)
    for question, option in KEYED.items():
        row = rows(verdict)[question]
        assert (row["answered"], row["chosen"], row["correct"]) == (True, option, True)
        assert row["says"] == says(question, option)


def test_a_wrong_answer_is_wrong_says_why_and_never_names_the_key(server, corpus):
    # ⭐ The explanation is the CHOSEN option's sentence. ⛔ And nothing in the
    # verdict names the keyed option or carries its sentence — a wrong answer
    # teaches why it is wrong, it does not hand over the right one.
    answers = {**KEYED, "q-2": WRONG["q-2"]}
    status, verdict = graded(server, corpus, answers)
    assert status == 200
    assert (verdict["right"], verdict["complete"]) == (1, False)
    row = rows(verdict)["q-2"]
    assert (row["answered"], row["chosen"], row["correct"]) == (True, WRONG["q-2"], False)
    assert row["says"] == says("q-2", WRONG["q-2"])
    assert says("q-2", KEYED["q-2"]) not in json.dumps(verdict)
    assert set(row) == {"id", "answered", "chosen", "correct", "says"}


def test_an_unanswered_question_is_not_a_correct_one_and_says_nothing(server, corpus):
    status, verdict = graded(server, corpus, {"q-1": KEYED["q-1"]})
    assert status == 200
    assert (verdict["right"], verdict["complete"]) == (1, False)
    assert rows(verdict)["q-2"] == {
        "id": "q-2",
        "answered": False,
        "chosen": None,
        "correct": False,
        "says": "",
    }


def test_an_option_or_question_the_quiz_does_not_have_is_simply_not_a_correct_answer(
    server, corpus
):
    # ⭐ `exercise.quiz.grade` is TOTAL, and so is this route over it.
    status, verdict = graded(server, corpus, {"q-1": "zz", "q-9": "a"})
    assert status == 200
    assert (verdict["right"], verdict["complete"]) == (0, False)
    assert [row["answered"] for row in verdict["questions"]] == [False, False]


def test_grading_is_a_post_and_the_index_is_a_get(server, corpus):
    _, source, practice = corpus
    status, headers, _ = fetch(server, grade_path(source, practice, KEYED))
    assert (status, headers["allow"]) == (405, "POST")
    status, _, body = fetch(server, "/api/v1/quiz/")
    assert status == 200
    assert json.loads(body)["resource"] == "quiz-index"
    assert fetch(server, "/api/v1/quiz/", method="POST")[0] == 405


def test_the_guards_refuse_a_file_page_a_cross_site_page_and_a_foreign_host(server, corpus):
    # ⛔ R8: `serve.app`'s gate stands in front of this route like every other,
    # and a file page — `Origin: null` — is refused here as the run route
    # refuses it. ⭐ The same request with none of those answers 200.
    assert graded(server, corpus, KEYED)[0] == 200
    assert graded(server, corpus, KEYED, headers={"Origin": "null"})[0] == 403
    assert graded(server, corpus, KEYED, headers={"Sec-Fetch-Site": "cross-site"})[0] == 403
    assert graded(server, corpus, KEYED, headers={"Origin": "http://evil.example"})[0] == 403
    _, source, practice = corpus
    path = grade_path(source, practice, KEYED)
    assert fetch(server, path, method="POST", host="evil.example")[0] == 403


def test_a_corpus_a_practice_or_answers_the_route_cannot_read_are_refused(server, corpus):
    _, source, practice = corpus
    post = lambda path: fetch(server, path, method="POST")[0]  # noqa: E731
    assert post(grade_path("no-such-corpus", practice, KEYED)) == 404
    assert post(grade_path(source, "depth-one/unit-09/practice-prose", KEYED)) == 404
    assert post(grade_path(source, "depth-one/unit-01/practice-nope", KEYED)) == 404
    assert post(f"/api/v1/quiz/{source}/{practice}/q-1=a/q-1=b") == 400
    assert post(f"/api/v1/quiz/{source}/{practice}/q-1=a/stray") == 400
    assert post(f"/api/v1/quiz/{source}/{practice}/q-1=%2e%2e") == 400
    assert post(f"/api/v1/quiz/{source}/{practice}/q-1==a") == 400


def test_a_practice_that_is_not_a_quiz_is_not_graded_here(tmp_path):
    # ⭐ The other shape, read through the same wiring: the runnable fixture's
    # code practice carries a workspace and no questions.
    from tests.studyforge.serve.routes.running import SOURCE, key, served_copy

    root = served_copy(tmp_path)
    with served_instance(root) as server:
        status, _, body = fetch(server, f"/api/v1/quiz/{SOURCE}/{key(1)}/q-1=a", method="POST")
    assert status == 409
    assert quiz.NOT_A_QUIZ in json.loads(body)["error"]


def test_grading_records_nothing_and_writes_nothing(server, corpus):
    # ⛔ A quiz produces no run: the progress store — which holds RUN outcomes —
    # is not written by a verdict, right or wrong.
    root = corpus[0]
    before = sorted(path.relative_to(root) for path in root.rglob("*"))
    for answers in (KEYED, WRONG):
        assert graded(server, corpus, answers)[0] == 200
    assert sorted(path.relative_to(root) for path in root.rglob("*")) == before
    assert Progress(root, 1).read()["practices"] == {}


def test_the_route_imports_nothing_that_runs_reaches_or_asks_anything():
    # ⛔ No model, no network, no container (spec §8.3). ⭐ Read off
    # the module's own imports, because a promise in a docstring is not a
    # property of the code.
    tree = ast.parse(inspect.getsource(quiz))
    imported = {
        node.module if isinstance(node, ast.ImportFrom) else alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import | ast.ImportFrom)
        for alias in node.names
    }
    for forbidden in ("execute", "subprocess", "socket", "http", "urllib", "docker"):
        assert not any(forbidden in (name or "") for name in imported), forbidden
