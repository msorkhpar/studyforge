"""Mirror of `src/studyforge/serve/routes/live.py` (R12): the reader's key, one live run.

⭐ Over a real connection, with a stand-in for the live runner's launcher: what is established is
what the route does with a request, never what a live runner does. ⛔ The key in every case is a
FAKE one (`sk-test-` and random hex); no real key exists and no API is reached.
"""

from __future__ import annotations

import base64
import contextlib
import http.client
import json
import secrets
import threading
import urllib.parse
from collections.abc import Iterator
from pathlib import Path

import pytest

from studyforge.execute import Service
from studyforge.generate import write_site
from studyforge.serve.app import ServingServer, make_server
from studyforge.serve.instance import (
    RunNamespace,
    bodies_for,
    client_for,
    live_client_for,
    writers_for,
)
from studyforge.serve.response import BodyRequest, Request
from studyforge.serve.routes import live, run
from studyforge.serve.routes.content import CorpusContent
from tests.studyforge.serve.routes.running import (
    SOURCE,
    StubEditors,
    StubHandle,
    key,
    runs_over,
    served_copy,
)
from tests.studyforge.serve.routes.test_runs import declare_runtimes

PRACTICE = key(1)
EXAMPLE = {"path": "lib/greet.py", "command": ["python3", "lib/greet.py"]}
HEADERS = {
    "Content-Type": "application/json",
    live.HEADER: live.HEADER_VALUE,
    "Sec-Fetch-Site": "same-origin",
}


def fake_key() -> str:
    return "sk-test-" + secrets.token_hex(12)


def declare_live(root: Path, block: dict | None = None) -> None:
    """Rewrite the copy's manifest to declare live runs, then build it again."""
    declare_runtimes(root, ["python"])
    manifest = root / "corpus.json"
    document = json.loads(manifest.read_text(encoding="utf-8"))
    document["corpus_api"] = 8
    document["live"] = block or {
        "host": "api.example.test",
        "key_variable": "EXAMPLE_API_KEY",
        "examples": [EXAMPLE],
        "practices": [PRACTICE],
    }
    manifest.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    write_site(root, root)


class Launches:
    """The launcher's stand-in: records what it was asked, and answers a stub run."""

    def __init__(self, lines=None, code=0) -> None:
        self.calls: list[tuple] = []
        self.lines = lines or ["a live line"]
        self.code = code
        self.handle = None

    def __call__(self, service, argv, key_, **options):
        self.calls.append((service, list(argv), key_))
        self.handle = StubHandle(list(self.lines), self.code)
        return self.handle


@contextlib.contextmanager
def serving_live(root: Path, launches: Launches, reachable=True) -> Iterator[ServingServer]:
    runs, discovered = runs_over(root, editor=StubEditors())
    offered = live.LiveRuns(
        runs, Service("live-runner", 7124), start=launches, reachable=lambda: reachable
    )
    namespaces = {run.NAMESPACE: RunNamespace(runs), live.NAMESPACE: offered}
    server = make_server(
        discovered.root,
        CorpusContent(discovered.corpora[0].corpus),
        port=0,
        namespaces=namespaces,
        writers=writers_for(namespaces),
        bodies=bodies_for(namespaces),
        client=client_for(namespaces),
        live=live_client_for(namespaces),
        frames=runs.origins,
    )
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield server
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def send(server, path, body=b"", headers=None, method="POST", origin="same"):
    """One request over a real connection; its status, headers and text."""
    host, port = server.server_address[:2]
    sent = dict(headers if headers is not None else HEADERS)
    if origin == "same":
        sent["Origin"] = f"http://{host}:{port}"
    elif origin is not None:
        sent["Origin"] = origin
    connection = http.client.HTTPConnection(host, port, timeout=30)
    try:
        connection.request(method, path, body=body, headers=sent)
        reply = connection.getresponse()
        return reply.status, {k.lower(): v for k, v in reply.getheaders()}, reply.read().decode()
    finally:
        connection.close()


def ask(corpus=SOURCE, kind="example", target=EXAMPLE["path"], key_=None) -> bytes:
    return json.dumps(
        {"corpus": corpus, "kind": kind, "target": target, "key": key_ or fake_key()}
    ).encode()


@pytest.fixture
def root(tmp_path: Path) -> Path:
    made = served_copy(tmp_path / "corpora")
    declare_live(made)
    return made


def test_the_index_lists_what_a_corpus_declares_and_whether_the_runner_answers(root):
    with serving_live(root, Launches(), reachable=False) as server:
        status, _, text = send(server, live.RUN_PATH.rsplit("/", 1)[0] + "/", method="GET")
    answer = json.loads(text)
    assert status == 200 and answer["resource"] == "live-index" and answer["enabled"] is False
    assert answer["corpora"] == {
        SOURCE: {
            "host": "api.example.test",
            "key_variable": "EXAMPLE_API_KEY",
            "examples": [EXAMPLE["path"]],
            "practices": [PRACTICE],
        }
    }
    assert answer["run"] == live.RUN_PATH and answer["header"] == [live.HEADER, "1"]
    # ⭐ The index names the variable, never a value.
    assert "sk-" not in text


def test_the_client_is_served_as_a_script_by_this_namespace(root):
    with serving_live(root, Launches()) as server:
        status, headers, text = send(server, live.CLIENT_PATH, method="GET")
    assert status == 200 and text == live.CLIENT_FILE.read_text(encoding="utf-8")
    assert headers["content-type"] == live.SCRIPT_TYPE


def test_a_declared_example_runs_its_own_argv_with_the_key_handed_to_the_launcher(root):
    launches = Launches(["hello from the live run"])
    secret = fake_key()
    with serving_live(root, launches) as server:
        status, _, text = send(server, live.RUN_PATH, ask(key_=secret))
    assert status == 200 and text.splitlines()[0] == "hello from the live run"
    assert text.splitlines()[-1] == "--- exit 0 ---"
    service, argv, given = launches.calls[0]
    assert (service, argv, given) == (Service("live-runner", 7124), EXAMPLE["command"], secret)
    assert secret not in text


def test_a_declared_practice_runs_the_command_its_record_names(root):
    launches = Launches()
    with serving_live(root, launches) as server:
        status, _, _ = send(server, live.RUN_PATH, ask(kind="practice", target=PRACTICE))
    assert status == 200
    assert launches.calls[0][1][0] == "python3" and launches.calls[0][1] != EXAMPLE["command"]


def test_what_a_stream_says_of_the_key_in_any_form_is_replaced(root):
    secret = fake_key()
    forms = [
        secret,
        urllib.parse.quote(secret, safe=""),
        base64.b64encode(secret.encode()).decode(),
        base64.b64encode(("user:" + secret).encode()).decode(),
        "Authorization: Bearer " + secret,
    ]
    with serving_live(root, Launches(forms)) as server:
        _, _, text = send(server, live.RUN_PATH, ask(key_=secret))
    assert secret not in text and base64.b64encode(secret.encode()).decode() not in text
    # ⭐ The key alone, in every encoding, is gone whole; the key in a longer encoding can leave a
    # character or two at the run's ends (stated in `execute.live.redactions`).
    assert text.splitlines()[:3] == [live.LIVE_MARKER] * 3
    assert text.count(live.LIVE_MARKER) >= 4 and "Bearer " + secret not in text


@pytest.mark.parametrize(
    "drop",
    [live.HEADER, "Content-Type"],
)
def test_a_request_without_the_header_or_the_json_type_is_refused_with_a_constant(root, drop):
    headers = {k: v for k, v in HEADERS.items() if k != drop}
    launches = Launches()
    secret = fake_key()
    with serving_live(root, launches) as server:
        status, _, text = send(server, live.RUN_PATH, ask(key_=secret), headers)
    assert status == 403 and launches.calls == [] and secret not in text


@pytest.mark.parametrize(
    "origin", [None, "null", "http://evil.example", "http://127.0.0.1:1", "https://127.0.0.1"]
)
def test_a_request_from_another_origin_is_refused(root, origin):
    launches = Launches()
    with serving_live(root, launches) as server:
        status, _, text = send(server, live.RUN_PATH, ask(), origin=origin)
    assert status == 403 and launches.calls == []
    assert json.loads(text)["error"] in (live.NOT_FROM_HERE, "cross-origin requests are refused")


def test_a_request_the_browser_calls_cross_site_is_refused(root):
    launches = Launches()
    headers = {**HEADERS, "Sec-Fetch-Site": "cross-site"}
    with serving_live(root, launches) as server:
        status, _, _ = send(server, live.RUN_PATH, ask(), headers)
    assert status == 403 and launches.calls == []


BAD_KEYS = [
    "",
    "short",
    "a" * 300,
    "sk-test-abc\ndef12345",
    "sk-test-abc def12345",
    "sk-test-abc;rm -rf /",
    "sk-test-$(id)abcdef",
    "sk-test-'quote'abc",
    "sk-test-\x00nul12345",
    "sk-test-`tick`12345",
]


@pytest.mark.parametrize("bad", BAD_KEYS)
def test_a_key_of_the_wrong_shape_is_refused_and_never_echoed(root, bad):
    launches = Launches()
    body = json.dumps(
        {"corpus": SOURCE, "kind": "example", "target": EXAMPLE["path"], "key": bad}
    ).encode()
    with serving_live(root, launches) as server:
        status, _, text = send(server, live.RUN_PATH, body)
    assert status == 400 and launches.calls == []
    assert json.loads(text)["error"] == live.LIVE_BAD_KEY
    assert bad == "" or bad not in text


@pytest.mark.parametrize(
    "body",
    [
        b"",
        b"not json",
        b"[]",
        b'{"corpus": "x"}',
        json.dumps({"corpus": SOURCE, "kind": "example", "target": "a", "key": 3}).encode(),
        json.dumps(
            {"corpus": SOURCE, "kind": "example", "target": "a", "key": "x" * 9, "extra": 1}
        ).encode(),
        b"\xff\xfe",
    ],
)
def test_a_body_that_is_not_a_live_request_is_refused_without_quoting_it(root, body):
    launches = Launches()
    with serving_live(root, launches) as server:
        status, _, text = send(server, live.RUN_PATH, body)
    assert status == 400 and json.loads(text)["error"] == live.NOT_A_REQUEST
    assert launches.calls == []


def test_a_target_the_corpus_did_not_declare_is_never_run(root):
    launches = Launches()
    other = ["lib/tests/test_greet.py", "../../etc/passwd", "lib/greet.py ", "python3 -c x"]
    with serving_live(root, launches) as server:
        for target in other:
            assert send(server, live.RUN_PATH, ask(target=target))[0] == 404
        assert send(server, live.RUN_PATH, ask(kind="practice", target="a-b/c-d"))[0] == 404
        assert send(server, live.RUN_PATH, ask(kind="command", target="rm"))[0] == 404
        assert send(server, live.RUN_PATH, ask(corpus="no-such"))[0] == 404
    assert launches.calls == []


def test_a_runner_that_does_not_answer_is_said_not_started_and_nothing_starts(root):
    launches = Launches()
    with serving_live(root, launches, reachable=False) as server:
        status, _, text = send(server, live.RUN_PATH, ask())
    assert status == 503 and json.loads(text)["error"] == live.NOT_STARTED
    assert launches.calls == []


def test_a_second_live_run_while_one_is_live_is_refused(root):
    class Held(Launches):
        def __call__(self, service, argv, key_, **options):
            self.calls.append((service, list(argv), key_))
            self.handle = Waiting()
            return self.handle

    class Waiting(StubHandle):
        def __init__(self):
            super().__init__([])
            self.gate = threading.Event()

        def lines(self):
            self.gate.wait(10)
            yield from ()

    launches = Held()
    with serving_live(root, launches) as server:
        host, port = server.server_address[:2]
        first = http.client.HTTPConnection(host, port, timeout=30)
        first.request(
            "POST", live.RUN_PATH, ask(),
            {**HEADERS, "Origin": f"http://{host}:{port}"},
        )
        while not launches.calls:
            threading.Event().wait(0.05)
        status, _, text = send(server, live.RUN_PATH, ask())
        launches.handle.gate.set()
        first.getresponse().read()
        first.close()
    assert status == 409 and json.loads(text)["error"] == live.BUSY


def test_a_get_to_the_run_path_acts_on_nothing(root):
    launches = Launches()
    with serving_live(root, launches) as server:
        status, _, _ = send(server, live.RUN_PATH, method="GET", headers={}, origin=None)
    assert status == 405 and launches.calls == []


def test_the_allowlist_holds_the_live_capable_argv_and_no_other(root):
    from studyforge.execute import ALLOWED_DIR

    with serving_live(root, Launches()):
        text = (root / ALLOWED_DIR / "live").read_bytes()
    assert b"lib/greet.py\x00" in text
    assert b"test_greet" not in text and b"pytest" not in text


def test_a_request_never_prints_its_body():
    secret = fake_key()
    request = BodyRequest("POST", live.RUN_PATH, {}, ask(key_=secret))
    assert secret not in repr(request) and secret not in str(request)
    assert request == BodyRequest("POST", live.RUN_PATH, {})
    # ⛔ A plain `Request` has no field for a client's bytes at all.
    assert not hasattr(Request("POST", live.RUN_PATH, {}), "body")


def test_the_route_log_of_a_run_holds_no_key(root, capfd):
    secret = fake_key()
    lines: list[str] = []
    runs, discovered = runs_over(root, editor=StubEditors())
    offered = live.LiveRuns(runs, Service("l", 7124), start=Launches(), reachable=lambda: True)
    namespaces = {run.NAMESPACE: RunNamespace(runs), live.NAMESPACE: offered}
    server = make_server(
        discovered.root,
        CorpusContent(discovered.corpora[0].corpus),
        port=0,
        namespaces=namespaces,
        writers=writers_for(namespaces),
        bodies=bodies_for(namespaces),
        log=lines.append,
    )
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        send(server, live.RUN_PATH, ask(key_=secret))
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
    assert lines and not any(secret in line for line in lines)
    seen = capfd.readouterr()  # nothing the route wrote to the process's own streams
    assert secret not in seen.out and secret not in seen.err
