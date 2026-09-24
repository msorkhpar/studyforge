"""Mirror of `src/studyforge/serve/routes/run.py`'s editor route: two practices at once.

⛔ **Over a real socket**: a page with two practices fires two
`POST …/editor/…` at once, and neither may answer `409` with no editor in its
panel. ⭐ Here both are fired at once and both must answer `200`, each with the
practice's OWN folder and a lock naming its OWN file — ⛔ with the interleaving
FORCED (every settings `replace` waits for the other request to reach it), so a
green run is about the design and not about the scheduler's luck.
"""

from __future__ import annotations

import json
import os
import threading
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import pytest

from studyforge.execute import Editor, workbench
from studyforge.serve.routes import run
from tests.studyforge.serve.routes.running import (
    SOURCE,
    StubEditors,
    key,
    post,
    runs_over,
    served_copy,
    serving,
)

#: An editor up over the fixture's practice workspaces. ⚠️ A made-up container
#: path: the probe reads the real one out of the container (R7).
UP = Editor(origin="http://127.0.0.1:8443", folder="/w/practice", base="practice")

#: Unit 1's and unit 2's practices, as the fixture's records name them.
PRACTICES = {
    1: ("passes", "greet.py", "check_greet.py"),
    2: ("fails", "total.py", "check_total.py"),
}


@pytest.fixture
def root(tmp_path):
    return served_copy(tmp_path)


@pytest.fixture
def forced(monkeypatch):
    meet, broken = threading.Barrier(2, timeout=5), []
    real = os.replace

    def replace(source, target, *args, **kwargs):
        if Path(target).name == workbench.SETTINGS_FILE:
            try:
                meet.wait()
            except threading.BrokenBarrierError:
                broken.append(target)
        return real(source, target, *args, **kwargs)

    monkeypatch.setattr(workbench.os, "replace", replace)
    return broken


def at_once(root, units) -> list[tuple[int, dict]]:
    live, discovered = runs_over(root, editor=StubEditors(UP))
    answers: list = [None] * len(units)
    with serving(live, discovered) as server:

        def ask(index, unit):
            status, _, body = post(server, f"/api/v1/run/{SOURCE}/{run.EDITOR}/{key(unit)}")
            answers[index] = (status, json.loads(body))

        threads = [threading.Thread(target=ask, args=pair) for pair in enumerate(units)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(20)
    return answers


def lock(root, directory: str) -> dict:
    target = root / "practice" / directory / workbench.SETTINGS_DIR / workbench.SETTINGS_FILE
    return json.loads(target.read_text(encoding="utf-8"))[workbench.READONLY_EXCLUDE]


def folder_of(url: str) -> str:
    return parse_qs(urlsplit(url).query)["folder"][0]


def test_two_practices_asked_at_once_both_answer_with_their_own_folder(root, forced):
    answers = at_once(root, [1, 2])
    assert [status for status, _ in answers] == [200, 200], answers
    assert forced == [], "the two requests never met: this reading forced nothing"
    for (_, answered), unit in zip(answers, (1, 2), strict=True):
        directory, main, test = PRACTICES[unit]
        assert folder_of(answered["main"]["url"]) == f"/w/practice/{directory}"
        assert folder_of(answered["test"]["url"]) == f"/w/practice/{directory}"
        # ⭐ Its OWN main editable, its test locked — whichever landed last.
        assert lock(root, directory) == {main: True}
        assert test not in lock(root, directory)


def test_the_same_practice_asked_twice_at_once_answers_twice(root, forced):
    answers = at_once(root, [1, 1])
    assert [status for status, _ in answers] == [200, 200], answers
    assert forced == [], "the two requests never met: this reading forced nothing"
    assert lock(root, "passes") == {"greet.py": True}


def test_opening_one_practice_after_another_leaves_the_first_ones_lock_alone(root):
    assert [status for status, _ in at_once(root, [1])] == [200]
    first = lock(root, "passes")
    assert [status for status, _ in at_once(root, [2])] == [200]
    assert lock(root, "passes") == first == {"greet.py": True}
    assert not (root / "practice" / workbench.SETTINGS_DIR).exists()


# --- ⭐ the route passes the files a command names -----------------------------

#: A Maven practice: its build file beside `src/`, named only by its commands.
MAVEN = "practice/maven"
MAVEN_MAIN = f"{MAVEN}/src/main/java/Kata.java"
MAVEN_TEST = f"{MAVEN}/src/test/java/KataTest.java"


@pytest.mark.parametrize("field", ["run_command", "test_command"])
def test_the_route_opens_the_directory_holding_the_build_file_a_command_names(root, field):
    # ⛔ Without the command's files the folder is `…/maven/src`, two loose
    # source trees with no project. Driven through `editor()` itself, so the
    # route's half of the rule is guarded and not only `practice_folder`'s.
    for path in (MAVEN_MAIN, MAVEN_TEST, f"{MAVEN}/pom.xml"):
        (root / path).parent.mkdir(parents=True, exist_ok=True)
        (root / path).write_text("x\n", encoding="utf-8")
    workspace = {
        "main_path": MAVEN_MAIN,
        "test_path": MAVEN_TEST,
        field: ["mvn", "-o", "-q", "-f", f"{MAVEN}/pom.xml", "test"],
    }
    live, discovered = runs_over(root, editor=StubEditors(UP))
    answered = run.editor(live, discovered.corpora[0], workspace)
    assert answered.status == 200
    body = json.loads(answered.body)
    assert folder_of(body["main"]["url"]) == folder_of(body["test"]["url"]) == "/w/practice/maven"
    assert body["main"]["path"] == "src/main/java/Kata.java"
    settings = root / MAVEN / workbench.SETTINGS_DIR / workbench.SETTINGS_FILE
    assert settings.is_file()
    assert not (root / MAVEN / "src" / workbench.SETTINGS_DIR).exists()
