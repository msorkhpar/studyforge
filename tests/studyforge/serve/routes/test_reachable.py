"""Mirror of `src/studyforge/serve/routes/reachable.py` (R12): whether a corpus can run now.

⭐ Read three ways: over stand-in runners (who is asked, and how often), over the
runnable fixture with its runner DECLARED and down (the index says `False`, a
Run is refused and nothing runs on the host), and with it declared by nothing
(the host runs it, as it always did).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

from studyforge.execute import RunRefused
from studyforge.execute.instance import COMPOSE_FILE
from studyforge.serve.routes import run
from studyforge.serve.routes.reachable import Reachable
from studyforge.serve.routes.runs import runner_for
from tests.studyforge.serve.routes.running import (
    post,
    runs_over,
    served_copy,
    serving,
    start_path,
)
from tests.studyforge.serve.serving import fetch

#: Where this interpreter lives, which a host run finds `python3` in.
PYTHON_DIR = Path(sys.executable).parent


class Stand:
    """A runner stand-in: required or not, up or not, counting every ask."""

    def __init__(self, required: bool, up: bool) -> None:
        self.required, self.up, self.asked = required, up, 0

    def mode(self) -> str:
        self.asked += 1
        if not self.up:
            raise RunRefused("down")
        return "container"


class Corpus:
    def __init__(self, source: str) -> None:
        self.source = source


def test_a_required_runner_that_is_down_is_not_runnable_and_one_that_is_up_is():
    made = {"down": Stand(True, False), "up": Stand(True, True)}
    reach = Reachable(lambda corpus: made[corpus.source])
    assert reach.runnable([Corpus("down"), Corpus("up")]) == {"down": False, "up": True}


def test_a_runner_nobody_declared_is_runnable_and_never_asked():
    stand = Stand(False, False)
    assert Reachable(lambda corpus: stand).runnable([Corpus("free")]) == {"free": True}
    assert stand.asked == 0, "a corpus that declares no runner is not probed"


def test_one_runner_is_held_per_corpus_so_its_own_cache_is_what_answers():
    made = []

    def make(corpus):
        made.append(Stand(True, True))
        return made[-1]

    reach = Reachable(make)
    for _ in range(3):
        reach.runnable([Corpus("one")])
    assert len(made) == 1 and made[0].asked == 3


def test_a_seam_that_refuses_to_make_a_runner_is_not_runnable():
    def refuse(corpus):
        raise RunRefused("no service declared")

    assert Reachable(refuse).runnable([Corpus("x")]) == {"x": False}


@pytest.fixture
def declared(tmp_path, monkeypatch) -> Path:
    """The runnable fixture, its runner declared, and no `docker` that can answer up."""
    root = served_copy(tmp_path)
    (root / COMPOSE_FILE).parent.mkdir(parents=True, exist_ok=True)
    (root / COMPOSE_FILE).write_text("services: {}\n", encoding="utf-8")
    monkeypatch.setenv("PATH", str(tmp_path / "no-docker-here"))
    return root


def test_with_a_declared_runner_down_the_index_says_so_and_a_run_runs_nowhere(declared):
    live, discovered = runs_over(declared, runner=runner_for)
    planted = declared / "planted"
    with serving(live, discovered) as server:
        status, _, body = fetch(server, "/api/v1/run/")
        refused = post(server, start_path(1, run.RUN))
    assert status == 200
    assert b'"runnable": {\n    "runnable-demo": false\n  }' in body
    assert refused[0] == 422, "a declared runner that is down refuses the run"
    assert not planted.exists()


def test_with_no_runner_declared_the_host_runs_it_as_before(tmp_path, monkeypatch):
    root = served_copy(tmp_path)
    # ⭐ The interpreter's own directory, so the fixture's `python3` is found and no
    # `docker` beside it answers for a container.
    monkeypatch.setenv("PATH", str(tmp_path / "no-docker") + os.pathsep + str(PYTHON_DIR))
    live, discovered = runs_over(root, runner=runner_for)
    with serving(live, discovered) as server:
        body = fetch(server, "/api/v1/run/")[2]
        status, _, said = post(server, start_path(1, run.RUN))
    assert b'"runnable-demo": true' in body
    assert status == 200 and said.splitlines()[-1] == "--- exit 0 ---"
