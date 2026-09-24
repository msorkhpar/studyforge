"""The page's execution client, `serve/assets/run-client.js`, read as the data it is.

Mirrors no source module — like `render/pageassets/test_progress`, it asserts what a text
can establish about a script, and reads the served bytes over a real socket.

⛔ **No JavaScript runs in this suite** (`QA-03/1`: the pinned image has no engine).
⭐ What is pinned instead: the client's endpoint, modes and stop path are the run
route's own (read from Python, never retyped here); a start sends NO body; the key is
passed verbatim and its pattern — which Python's `re` reads as JavaScript does — accepts
every key `progress.practice_key` mints and refuses every spelling that would reach a
different endpoint; the script draws nothing, because the panel is `SF-24`'s; and it is
served by the run namespace and NEVER written into a built site, whose floor names no
server (R8).
"""

from __future__ import annotations

import re

import pytest

from studyforge.address import parse_unit_key
from studyforge.progress import practice_key
from studyforge.render.pageassets import ASSET_DIR, script
from studyforge.serve.response import API_PREFIX
from studyforge.serve.routes import run
from tests.studyforge.serve.routes.running import runs_over, served_copy, serving
from tests.studyforge.serve.serving import fetch


def text() -> str:
    return run.CLIENT_FILE.read_text(encoding="utf-8")


def uncommented() -> str:
    return re.sub(r"/\*.*?\*/", "", text(), flags=re.DOTALL)


def constant(name: str) -> str:
    found = re.search(rf"var {name} = (.+);", uncommented())
    assert found, f"the client declares no {name}"
    return found.group(1)


def key_pattern() -> re.Pattern:
    literal = constant("KEY")
    assert literal.startswith("/") and literal.endswith("/")
    return re.compile(literal[1:-1])


def test_the_run_namespace_serves_the_client_as_a_script(tmp_path):
    runs, discovered = runs_over(served_copy(tmp_path))
    with serving(runs, discovered) as server:
        status, headers, body = fetch(server, f"{API_PREFIX}/{run.NAMESPACE}/{run.CLIENT}")
        index = fetch(server, f"{API_PREFIX}/{run.NAMESPACE}/")[2].decode()
    assert status == 200 and body.decode() == text()
    assert headers["content-type"] == run.SCRIPT_TYPE
    assert headers["x-content-type-options"] == "nosniff"
    assert f"{API_PREFIX}/{run.NAMESPACE}/{run.CLIENT}" in index
    assert "window.studyforge.run = {" in text()


def test_no_built_page_carries_the_client():
    # ⛔ R8's floor: a built site names no server, and the client names the API on
    # every line that matters. It is not a page asset and not in the page's script.
    assert not (ASSET_DIR / run.CLIENT_FILE.name).exists()
    assert "studyforge.run =" not in script()
    assert constant("BASE").strip("'") not in script()


def test_its_endpoint_modes_and_stop_are_the_run_routes_own():
    assert constant("BASE") == f"'{API_PREFIX}/{run.NAMESPACE}/'"
    assert constant("STOP") == f"'{run.STOP}'"
    modes = re.findall(r"'([a-z]+)'", constant("MODES"))
    assert modes == list(run.MODES)


def test_a_start_is_a_post_with_no_body_and_nothing_else_is_sent():
    body = uncommented()
    # ⭐ Four requests in the whole client and no fifth: the two acts, each a
    # POST that SELECTS; the index — a GET, because asking what this instance
    # offers is a read (`W416`); and one practice's editor windows, a POST
    # because preparing that practice's workspace settings WRITES (`W429`).
    # ⭐ And a fifth, since the server grades quizzes: grading a quiz, a POST that selects a quiz
    # and carries the reader's choices in its PATH (`test_quiz_client.py`).
    assert body.count("fetch(") == 5
    assert body.count("method: 'POST'") == 4
    assert "body:" not in body and "JSON.stringify" not in body
    assert "XMLHttpRequest" not in body and "sendBeacon" not in body


def test_the_editor_word_is_the_run_routes_own_and_is_not_a_mode():
    # ⛔ `W429`: `editor` stands where a mode stands in the path and STARTS
    # NOTHING, so it must not drift into `MODES` and must not be retyped here.
    assert constant("EDITOR") == f"'{run.EDITOR}'"
    assert run.EDITOR not in run.MODES


def test_one_practices_windows_are_asked_for_by_corpus_and_key_and_nothing_else():
    # ⭐ The whole reason this endpoint exists: a FOLDER cannot say which of two
    # windows shows which file, so the ask names ONE practice. ⚠️ The key is the
    # same verbatim string a start carries; nothing here composes or splits one.
    body = uncommented()
    asking = body[body.index("function practice(corpus, key)") :]
    assert "BASE + corpus + '/' + EDITOR + '/' + key" in asking
    # ⛔ Anything but an answer is `null`, never an error a reader sees: the page
    # then shows the sentence it already ships.
    assert "response.ok ? response.json() : null" in asking
    assert "answer && answer.main && answer.main.url ? answer : null" in asking


def test_the_practice_key_is_used_verbatim_never_composed_split_or_encoded():
    body = uncommented()
    for word in ("encodeURIComponent", "encodeURI(", "practice.split", "practice.replace"):
        assert word not in body, word
    assert "'/' + practice" in body


@pytest.mark.parametrize(
    "unit_key,section",
    [("kata/unit-01", "practice-python"), ("basics/01-intro/unit-12", "practice-java")],
)
def test_the_key_pattern_accepts_every_key_the_store_mints(unit_key, section):
    depth = unit_key.count("/")
    address, ordinal = parse_unit_key(unit_key, depth)
    assert key_pattern().fullmatch(practice_key(address, ordinal, section))


@pytest.mark.parametrize(
    "spelled",
    [
        "kata/../stop",
        "kata/./unit-01/practice-python",
        "kata/unit-01/practice-python/",
        "/kata/unit-01/practice-python",
        "kata//unit-01/practice-python",
        "kata/unit-01/Practice-python",
        "kata/unit-01/practice-python?x=1",
        "practice-python",
    ],
)
def test_the_key_pattern_refuses_any_spelling_a_browser_would_resolve_elsewhere(spelled):
    assert key_pattern().fullmatch(spelled) is None


def test_it_draws_nothing_and_types_no_word_a_reader_sees():
    # ⛔ The panel is `SF-24`'s: a control drawn here before it would be a dead button.
    body = uncommented()
    for word in ("document.", "innerHTML", "textContent", "createElement", "alert("):
        assert word not in body, word


def test_over_a_file_it_is_not_available_and_sends_nothing():
    # ⛔ R8: `file://` has no origin. EVERY entry point asks `available()` first
    # — the two acts, where a running editor is (`W416`), and one practice's
    # two editor windows (`W429`) — and grading a quiz.
    body = uncommented()
    assert "location.protocol === 'http:'" in body
    assert body.count("if (!available())") == 5


def test_a_refusal_is_a_rejection_naming_what_was_refused_before_any_request():
    # ⭐ What `SF-24` is told to expect: `{refused: …}`, decided before `fetch`.
    body = uncommented()
    assert "Promise.reject({ refused: reason })" in body
    start = body[body.index("function start(") :]
    before_fetch = start[: start.index("fetch(")]
    for reason in ("'no-origin'", "'mode'", "'practice'"):
        assert f"refused({reason})" in before_fetch, reason


# --- where a running editor is (`W416`) -------------------------------------


def test_it_publishes_where_a_running_editor_is_beside_the_two_acts():
    assert "editor: editor" in text()


def test_the_editor_is_read_off_the_index_under_the_run_routes_own_key():
    # ⭐ One spelling of the key, read from Python rather than retyped here: a
    # second spelling would be a page that finds nothing with nothing failing.
    body = uncommented()
    assert f"answer.{run.EDITOR}" in body
    assert f"answer.{run.EDITOR}[corpus]" in body
    assert "fetch(BASE, {" in body


def test_the_index_is_asked_once_per_page_and_the_answer_is_remembered():
    body = uncommented()
    assert "if (!index) {" in body


def test_an_index_that_cannot_be_read_is_no_editor_and_never_an_error_a_reader_sees():
    body = uncommented()
    editor = body[body.index("function asked()") : body.index("function stop()")]
    assert "return {}" in editor
    assert "found.origin && found.folder ? found : null" in editor


def test_it_neither_builds_an_editor_url_nor_starts_one():
    # ⛔ A client hands back an origin and a folder; what to do with them is the
    # panel's, and starting a development environment is nobody's on this page.
    body = uncommented()
    for word in ("iframe", "?folder=", "docker", "spawn"):
        assert word not in body, word
