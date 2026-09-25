"""Mirror of `src/studyforge/execute/published.py` (R12): what a published compose hands in.

⭐ The declared editor is asked over HTTP, so its health is a real loopback
server here, answering `200` or `503` as each test needs.
"""

from __future__ import annotations

import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

from studyforge.execute import ALLOWED_FILE, Editor, RunRefused, Service, write_allowed
from studyforge.execute.published import (
    EDITOR_BINDS,
    EDITOR_HEALTH,
    EDITOR_ORIGIN,
    RUN_SERVICE,
    DeclaredEditorProbe,
    allowed_bytes,
    from_environment,
    run_service_script,
)

DECLARED = {
    EDITOR_ORIGIN: "http://127.0.0.1:18505/",
    EDITOR_BINDS: "practice=/r/practice;code=/r/sources",
    EDITOR_HEALTH: "http://editor:8080/healthz",
    RUN_SERVICE: "runner",
}


@pytest.fixture
def health():
    status = {"code": 200}

    class Answer(BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802 - the handler's own spelling
            self.send_response(status["code"])
            self.end_headers()

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Answer)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{server.server_address[1]}/healthz", status
    server.shutdown()
    server.server_close()


def test_nothing_declared_is_no_published_config():
    assert from_environment({}) is None
    assert from_environment({"UNRELATED": "1"}) is None


def test_the_four_values_are_read_as_declared():
    config = from_environment(DECLARED)
    assert config is not None
    assert config.origin == "http://127.0.0.1:18505"
    assert config.binds == (
        ("practice", "/r/practice"),
        ("code", "/r/sources"),
    )
    assert config.health == "http://editor:8080/healthz"
    assert config.service == Service("runner", 7123)


def test_a_run_service_may_name_its_port():
    assert from_environment({RUN_SERVICE: "runner:9000"}).service == Service("runner", 9000)


@pytest.mark.parametrize(
    "origin",
    [
        "http://0.0.0.0:18505",
        "http://192.0.2.1:18505",
        "https://127.0.0.1:18505",
        "http://127.0.0.1",
        "http://127.0.0.1:18505/path",
        "http://user@127.0.0.1:18505",
    ],
)
def test_an_origin_a_page_would_frame_off_loopback_is_refused(origin):
    with pytest.raises(RunRefused, match="loopback"):
        from_environment({**DECLARED, EDITOR_ORIGIN: origin})


@pytest.mark.parametrize("binds", ["../up=/x", "/abs=/x", "code=relative", "noequals", "a//b=/x"])
def test_a_bind_that_is_not_corpus_relative_to_absolute_is_refused(binds):
    with pytest.raises(RunRefused):
        from_environment({**DECLARED, EDITOR_BINDS: binds})


@pytest.mark.parametrize("value", [":7123", "runner:", "runner:port"])
def test_a_run_service_that_is_not_host_and_port_is_refused(value):
    with pytest.raises(RunRefused):
        from_environment({**DECLARED, RUN_SERVICE: value})


def test_the_declared_editor_is_answered_while_its_health_answers(health):
    url, status = health
    probe = DeclaredEditorProbe("http://127.0.0.1:18505", [("code", "/r/src"), ("a", "/r/a")], url)
    assert probe.known() is None, "nothing is known before it is asked"
    assert probe.editor() == Editor(
        origin="http://127.0.0.1:18505", folder="/r/a", base="a", others=(("code", "/r/src"),)
    )
    assert probe.known() == probe.editor()


def test_an_editor_whose_health_does_not_answer_is_no_editor(health):
    url, status = health
    status["code"] = 503
    assert DeclaredEditorProbe("http://127.0.0.1:1", [("a", "/r")], url).editor() is None
    gone = url.rsplit(":", 1)[0] + ":1/healthz"
    assert DeclaredEditorProbe("http://127.0.0.1:1", [("a", "/r")], gone).editor() is None


def test_a_config_with_no_editor_declared_offers_no_probe():
    assert from_environment({RUN_SERVICE: "runner"}).editor_probe() is None


def test_the_allowlist_is_sorted_without_repeats_and_nul_framed():
    entries = [(".", ["mvn", "test"]), (".", ["mvn", "compile"]), (".", ["mvn", "test"])]
    assert allowed_bytes(entries) == b".\x00mvn\x00compile\x00\x00.\x00mvn\x00test\x00\x00"


def test_an_entry_carrying_a_nul_cannot_be_framed_and_is_left_out():
    assert allowed_bytes([(".", ["sh", "a\x00b"])]) == b""


def test_the_allowlist_is_written_whole_where_the_runner_reads_it(tmp_path: Path):
    written = write_allowed(tmp_path, [(".", ["sh", "one"])])
    assert written == tmp_path / ALLOWED_FILE
    write_allowed(tmp_path, [(".", ["sh", "two"])])
    assert written.read_bytes() == b".\x00sh\x00two\x00\x00", "rewritten whole, never appended"
    assert not (written.parent / ".runs.next").exists()


def test_the_service_script_ships_with_the_package():
    script = run_service_script()
    assert script.startswith("#!/usr/bin/perl")
    assert ".studyforge/execution/allowed/runs" in script
