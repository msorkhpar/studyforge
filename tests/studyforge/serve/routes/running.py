"""Shared by the run route's tests: the runnable fixture served, a spy runner, a stub run.

⭐ **Every run happens in a temp COPY of `tests/fixtures/runnable/`**, built in place and
discovered from its parent, so the route reads each practice's workspace from the unit
document the way a served instance does. ⭐ Every practice key is spelled by
`progress.practice_key` and never typed (`SF-21/4`).

⭐ `plant_command` rewrites one practice's workspace IN THE COPY's archive — the
generated document is built from it — which is how a test shows the command that runs
follows the document and nothing else.
"""

from __future__ import annotations

import contextlib
import http.client
import json
import threading
from collections.abc import Iterator
from pathlib import Path

from studyforge.address import parse_unit_key
from studyforge.execute import Runner, exit_line
from studyforge.generate import write_site
from studyforge.progress import practice_key
from studyforge.serve.app import ServingServer, make_server
from studyforge.serve.discovery import Discovered, ServedCorpus, discover
from studyforge.serve.routes import run, runs
from studyforge.serve.routes.content import CorpusContent
from tests.studyforge.execute.runnable import RAW, fixture_copy

SOURCE = "runnable-demo"
SECTION = "practice-python"

#: A plant that says it started and then waits to be stopped.
WAIT = "import time\nprint('waiting', flush=True)\ntime.sleep(120)\n"

#: A plant that prints an exit line of its own, then exits 3.
FAKE_EXIT = "print('--- exit 0 ---')\nraise SystemExit(3)\n"


def key(unit: int) -> str:
    """The practice key of unit `unit`'s one practice, as `progress` spells it."""
    address, ordinal = parse_unit_key(f"kata/unit-{unit:02d}", 1)
    return practice_key(address, ordinal, SECTION)


def start_path(unit: int, mode: str) -> str:
    return f"/api/v1/run/{SOURCE}/{mode}/{key(unit)}"


def served_copy(where: Path) -> Path:
    """A built copy of the runnable corpus, with the execute suite's plants and ours."""
    root = fixture_copy(where)
    plants = root / "practice" / "plants"
    (plants / "wait.py").write_text(WAIT, encoding="utf-8")
    (plants / "fake_exit.py").write_text(FAKE_EXIT, encoding="utf-8")
    write_site(root, root)
    return root


def plant_command(root: Path, unit: int, field: str, argv: list[str]) -> None:
    """Rewrite one workspace command in the copy's archive, which the document is built from."""
    path = root / RAW / f"unit-{unit:02d}" / "practice-1.json"
    document = json.loads(path.read_text(encoding="utf-8"))
    document["exercise"][field] = argv
    path.write_text(json.dumps(document, indent=2), encoding="utf-8")


def host_runner(corpus: ServedCorpus) -> Runner:
    """The corpus's runner in host mode, always: no container name, no probe."""
    return Runner(corpus.root, None, grace=0.5)


class Spy:
    """A runner factory that records every argv a run was started with."""

    def __init__(self) -> None:
        self.started: list[list] = []

    def __call__(self, corpus: ServedCorpus) -> Runner:
        spy = self
        real = host_runner(corpus)

        class Recording:
            def start(self, commands, cwd="."):
                spy.started.append([list(command) for command in commands])
                return real.start(commands)

        return Recording()  # type: ignore[return-value]


class StubHandle:
    """A run that yields the lines it is given, raw, then one exit line."""

    def __init__(self, lines: list[str], code: int = 0) -> None:
        self._lines = lines
        self._code = code
        self.returncode: int | None = None
        self.stopped = False

    def lines(self) -> Iterator[str]:
        yield from self._lines
        self.returncode = self._code
        yield exit_line(self._code)

    def stop(self) -> bool:
        self.stopped = True
        return True


class StubEditor:
    """An editor probe that answers what it was given, and forks nothing.

    ⛔ The suite's default is an editor that is NOT up: a real probe would fork
    `docker` per corpus per index fetch, and the pinned gate has no daemon to
    ask (§8.3, and `W416`'s handoff carries the host reading).
    """

    def __init__(self, answer=None) -> None:
        self.answer = answer
        self.asked = 0

    def editor(self):
        self.asked += 1
        return self.answer


class StubEditors:
    """A probe factory that keeps the one probe it made for each corpus."""

    def __init__(self, answer=None) -> None:
        self.answer = answer
        self.made: list[StubEditor] = []

    def __call__(self, corpus: ServedCorpus) -> StubEditor:
        self.made.append(StubEditor(self.answer))
        return self.made[-1]


def stub_runner(handle: StubHandle):
    class Stub:
        def start(self, commands, cwd="."):
            return handle

    return lambda corpus: Stub()


def runs_over(
    root: Path, runner=host_runner, clock=None, editor=None
) -> tuple[runs.Runs, Discovered]:
    discovered = discover(root.parent)
    sources = {served.source: CorpusContent(served.corpus) for served in discovered.corpora}
    live = runs.Runs(
        discovered, sources, runner=runner, clock=clock, editor=editor or StubEditors()
    )
    return live, discovered


@contextlib.contextmanager
def serving(live: runs.Runs, discovered: Discovered) -> Iterator[ServingServer]:
    """The run namespace, served on `127.0.0.1:0`, as the one writer."""
    server = make_server(
        discovered.root,
        CorpusContent(discovered.corpora[0].corpus),
        port=0,
        namespaces={run.NAMESPACE: lambda request, rest: run.route(live, request, rest)},
        writers=(run.NAMESPACE,),
    )
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield server
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def post(server: ServingServer, path: str, body: bytes = b"", headers=None):
    """POST over a real connection; return status, lower-cased headers, body text."""
    connection = http.client.HTTPConnection(*server.server_address[:2], timeout=60)
    try:
        connection.request("POST", path, body=body, headers=headers or {})
        reply = connection.getresponse()
        return reply.status, {k.lower(): v for k, v in reply.getheaders()}, reply.read().decode()
    finally:
        connection.close()


def opened(server: ServingServer, path: str) -> tuple[http.client.HTTPConnection, object]:
    """Start a POST and return the connection and its response, unread."""
    connection = http.client.HTTPConnection(*server.server_address[:2], timeout=60)
    connection.request("POST", path)
    return connection, connection.getresponse()


def entry(corpus: ServedCorpus, unit: int) -> dict | None:
    """The progress record's entry for unit `unit`'s practice."""
    return corpus.progress().read()["practices"].get(key(unit))
