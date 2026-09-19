"""Mirror of `src/studyforge/serve/routes/run.py` (R12) — Run and Submit, over a real socket.

⭐ **E05 SF-22's acceptance, each clause both ways, against the runnable fixture, in
host mode** — which `SF-20` made a full execution mode; the container reading is the
register's (`SF-20/1`). *Run streams program output. Submit streams grader output and,
on success, completes the practice. Run never completes a practice. A stopped run is
recorded as stopped. Output is gated on the wire.* ⛔ And the epic's own sentence:
**nothing a browser sends ever becomes a command.**
"""

from __future__ import annotations

import dataclasses
import json
import threading
import time

import pytest

from studyforge.archive.scrub import scrub
from studyforge.progress import IGNORE_FILENAME, store_dir
from studyforge.serve.instance import instance_of
from studyforge.serve.response import Request
from studyforge.serve.routes import run
from studyforge.serve.routes.runs import NOT_RECORDED
from studyforge.serve.routes.state import corpus_state
from tests.studyforge.execute.runnable import FOREIGN_HOME
from tests.studyforge.serve.routes.running import (
    SOURCE,
    Spy,
    StubHandle,
    entry,
    key,
    opened,
    plant_command,
    post,
    runs_over,
    served_copy,
    serving,
    start_path,
    stub_runner,
)
from tests.studyforge.serve.serving import fetch

EXIT_0 = "--- exit 0 ---"


def lines_of(text: str) -> list[str]:
    return text.splitlines()


@pytest.fixture
def root(tmp_path):
    return served_copy(tmp_path)


def settle(condition, within: float = 15.0) -> bool:
    deadline = time.monotonic() + within
    while time.monotonic() < deadline:
        if condition():
            return True
        time.sleep(0.05)
    return False


# --- registration (W230) ----------------------------------------------------


def test_instance_of_registers_run_as_the_one_writer_and_it_runs(root):
    discovered = runs_over(root)[1]
    server = instance_of(discovered, port=0)
    try:
        assert run.NAMESPACE in server.namespaces
        assert server.writers == frozenset({run.NAMESPACE})
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        status, _, body = post(server, start_path(1, run.RUN))
        index = fetch(server, "/api/v1/run/")
    finally:
        server.shutdown()
        server.server_close()
    assert (status, lines_of(body)) == (200, ["Hello, reader", EXIT_0])
    assert index[0] == 200


# --- Run and Submit ------------------------------------------------------------


def test_run_streams_program_output_and_never_completes_a_practice(root):
    runs, discovered = runs_over(root)
    with serving(runs, discovered) as server:
        status, headers, body = post(server, start_path(1, run.RUN))
    assert (status, lines_of(body)) == (200, ["Hello, reader", EXIT_0])
    assert headers["content-type"].startswith("text/plain")
    assert headers["cache-control"] == "no-store"
    recorded = entry(discovered.corpora[0], 1)
    assert recorded["last"]["mode"] == run.RUN and recorded["last"]["exit"] == 0
    assert recorded["first_passed_at"] is None and recorded["last"]["passed"] is False


def test_submit_streams_grader_output_and_completes_the_practice_on_success(root):
    runs, discovered = runs_over(root)
    with serving(runs, discovered) as server:
        status, _, body = post(server, start_path(1, run.TEST))
    said = lines_of(body)
    assert status == 200 and said[-1] == EXIT_0
    assert any("1 passed" in line for line in said), said
    recorded = entry(discovered.corpora[0], 1)
    assert recorded["last"]["mode"] == run.TEST and recorded["last"]["passed"] is True
    assert recorded["first_passed_at"] is not None


@pytest.mark.parametrize("unit", [2, 4], ids=["a failing grader", "a file that does not compile"])
def test_submit_on_a_failing_grader_streams_it_and_completes_nothing(root, unit):
    runs, discovered = runs_over(root)
    with serving(runs, discovered) as server:
        _, _, body = post(server, start_path(unit, run.TEST))
    assert lines_of(body)[-1] != EXIT_0
    recorded = entry(discovered.corpora[0], unit)
    assert recorded["last"]["mode"] == run.TEST and recorded["last"]["exit"] != 0
    assert recorded["first_passed_at"] is None


def test_a_run_that_exits_0_never_completes_what_a_submit_that_exits_0_does(root):
    # ⭐ The two acts, side by side on one practice: the same exit, two outcomes.
    runs, discovered = runs_over(root)
    corpus = discovered.corpora[0]
    with serving(runs, discovered) as server:
        post(server, start_path(1, run.RUN))
        after_run = entry(corpus, 1)["first_passed_at"]
        post(server, start_path(1, run.TEST))
    assert after_run is None
    assert entry(corpus, 1)["first_passed_at"] is not None


def test_the_exit_line_is_told_by_the_handle_not_by_a_line_a_program_printed(root):
    plant_command(root, 1, "test_command", ["python3", "practice/plants/fake_exit.py"])
    runs, discovered = runs_over(root)
    with serving(runs, discovered) as server:
        _, _, body = post(server, start_path(1, run.TEST))
    assert lines_of(body) == [EXIT_0, "--- exit 3 ---"]
    recorded = entry(discovered.corpora[0], 1)
    assert (recorded["last"]["exit"], recorded["first_passed_at"]) == (3, None)


# --- stopped ---------------------------------------------------------------


def waiting(root):
    plant_command(root, 1, "run_command", ["python3", "practice/plants/wait.py"])
    return runs_over(root)


def test_a_stopped_run_is_recorded_as_stopped(root):
    runs, discovered = waiting(root)
    with serving(runs, discovered) as server:
        connection, reply = opened(server, start_path(1, run.RUN))
        assert reply.readline() == b"waiting\n"
        live = fetch(server, "/api/v1/run/")[2]
        stopped = post(server, "/api/v1/run/stop")
        rest = reply.read().decode()
        connection.close()
        assert settle(lambda: runs.live is None)
    assert key(1) in live.decode()
    assert stopped[0] == 200 and '"stopped": true' in stopped[2]
    assert lines_of(rest) == ["--- exit stopped ---"]
    assert entry(discovered.corpora[0], 1)["last"]["exit"] == "stopped"


def test_a_stop_with_nothing_live_stops_nothing_and_a_finished_run_keeps_its_status(root):
    runs, discovered = runs_over(root)
    with serving(runs, discovered) as server:
        nothing = post(server, "/api/v1/run/stop")
        post(server, start_path(1, run.RUN))
    assert '"stopped": false' in nothing[2]
    assert entry(discovered.corpora[0], 1)["last"]["exit"] == 0


def test_a_page_that_hangs_up_stops_its_run_records_it_stopped_and_frees_the_slot(root):
    runs, discovered = waiting(root)
    with serving(runs, discovered) as server:
        connection, reply = opened(server, start_path(1, run.RUN))
        assert reply.readline() == b"waiting\n"
        busy = post(server, start_path(2, run.RUN))
        reply.close()  # ⚠️ the response holds the socket open until it is closed too
        connection.close()
        assert settle(lambda: runs.live is None)
        again = post(server, start_path(2, run.RUN))
    assert busy[0] == 409 and run.BUSY in busy[2]
    assert entry(discovered.corpora[0], 1)["last"]["exit"] == "stopped"
    assert again[0] == 200


# --- output is gated on the wire --------------------------------------------


def test_a_home_path_a_program_prints_never_reaches_the_wire(root):
    plant_command(root, 1, "run_command", ["python3", "practice/plants/talk.py"])
    runs, discovered = runs_over(root)
    with serving(runs, discovered) as server:
        _, _, body = post(server, start_path(1, run.RUN))
    assert "home" in body and FOREIGN_HOME not in body
    assert str(root) not in body


def test_the_wire_gates_a_line_even_when_the_runner_did_not(root):
    leak = f"at {FOREIGN_HOME}/secret.txt"
    assert scrub(leak) != leak, "the plant carries nothing the gate would change"
    runs, discovered = runs_over(root, runner=stub_runner(StubHandle([leak + "\n"])))
    with serving(runs, discovered) as server:
        _, _, body = post(server, start_path(1, run.RUN))
    assert lines_of(body) == [scrub(leak), EXIT_0]


# --- nothing a client sends becomes a command -------------------------------


@pytest.mark.parametrize("mode", [run.RUN, run.TEST])
def test_the_command_that_runs_is_the_documents_whatever_the_client_sends(root, mode):
    spy = Spy()
    runs, discovered = runs_over(root, runner=spy)
    marker = "planted-by-the-client"
    with serving(runs, discovered) as server:
        status, _, body = post(
            server,
            start_path(1, mode) + f"?command=echo+{marker}&argv={marker}",
            body=f'{{"command": ["echo", "{marker}"]}}'.encode(),
            headers={"Content-Type": "application/json", "X-Command": f"echo {marker}"},
        )
    field = run.COMMAND_OF[mode]
    expected = _workspace(runs, 1)[field]
    assert status == 200 and spy.started == [[expected]]
    assert marker not in body


def test_the_command_follows_the_document_when_the_document_changes(root):
    # ⭐ The other way: the argv that runs moves with the generated document.
    plant_command(root, 1, "run_command", ["python3", "practice/untested/hello.py"])
    spy = Spy()
    runs, discovered = runs_over(root, runner=spy)
    with serving(runs, discovered) as server:
        post(server, start_path(1, run.RUN))
    assert spy.started == [[["python3", "practice/untested/hello.py"]]]


REFUSED = [
    (f"{SOURCE}/shell/{{key}}", 404),
    (f"{SOURCE}/run_command/{{key}}", 404),
    (f"{SOURCE}/RUN/{{key}}", 404),
    (f"{SOURCE}/run/kata/unit-1/practice-python", 404),
    (f"{SOURCE}/run/kata/unit-01/practice-python/", 404),
    (f"{SOURCE}/run/kata/unit-01/practice-python/extra", 404),
    (f"{SOURCE}/run/kata/unit-01/practice-java", 404),
    (f"{SOURCE}/run/kata/unit-05/practice-python", 404),
    (f"{SOURCE}/test/kata/unit-03/practice-python", 409),
    ("another-corpus/run/{key}", 404),
]


@pytest.mark.parametrize("path,status", REFUSED)
def test_anything_but_a_declared_practice_and_mode_starts_nothing(root, path, status):
    spy = Spy()
    runs, discovered = runs_over(root, runner=spy)
    with serving(runs, discovered) as server:
        answer = post(server, "/api/v1/run/" + path.format(key=key(1)))
    assert answer[0] == status
    assert spy.started == []
    assert entry(discovered.corpora[0], 1) is None


class RunOnly:
    """The corpus's own documents, except unit 1's workspace names no test (`W357`'s shape)."""

    def __init__(self, source):
        self.source = source

    def unit(self, unit_key):
        text = self.source.unit(unit_key)
        if unit_key != "kata/unit-01":
            return text
        document = json.loads(text)
        for section in document["sections"]:
            if section["workspace"] is not None:
                section["workspace"] = {
                    name: value
                    for name, value in section["workspace"].items()
                    if name not in ("test_path", "test_command")
                }
        return json.dumps(document)

    def declares(self, unit_key):
        return self.source.declares(unit_key)

    def toc(self):
        return self.source.toc()


def test_a_workspace_that_names_no_test_offers_run_and_refuses_submit(root):
    # ⭐ `W357`: a file with no test carries `main_path` and `run_command` alone. Taken
    # through a stand-in source because this base's archive reader refuses that record;
    # the route reads the generated document either way.
    spy = Spy()
    runs, discovered = runs_over(root, runner=spy)
    runs.sources[SOURCE] = RunOnly(runs.sources[SOURCE])
    with serving(runs, discovered) as server:
        submitted = post(server, start_path(1, run.TEST))
        ran = post(server, start_path(1, run.RUN))
    assert submitted[0] == 409 and run.NO_SUCH_COMMAND in submitted[2]
    assert ran[0] == 200 and lines_of(ran[2]) == ["Hello, reader", EXIT_0]
    assert spy.started == [[["python3", "practice/passes/greet.py"]]]
    assert entry(discovered.corpora[0], 1)["last"]["mode"] == run.RUN


def test_run_on_the_file_with_no_test_follows_whether_its_record_names_a_command(root):
    # ⭐ Holds on both shapes of unit 3: no workspace at all (before `W357`), or a
    # workspace naming only its run command (after) — Run starts exactly when it does.
    spy = Spy()
    runs, discovered = runs_over(root, runner=spy)
    workspace = _workspace(runs, 3)
    with serving(runs, discovered) as server:
        status = post(server, start_path(3, run.RUN))[0]
    named = workspace is not None and workspace.get("run_command") is not None
    assert status == (200 if named else 409)
    assert spy.started == ([[workspace["run_command"]]] if named else [])


@pytest.mark.parametrize(
    "method,headers,status",
    [
        ("GET", {}, 405),
        ("HEAD", {}, 405),
        ("POST", {"Origin": "null"}, 403),
        ("POST", {"Sec-Fetch-Site": "cross-site"}, 403),
        ("POST", {"Origin": "http://evil.example"}, 403),
        ("POST", {"Content-Length": str(10**6)}, 413),
    ],
)
def test_a_start_by_any_other_method_or_from_any_other_site_starts_nothing(
    root, method, headers, status
):
    spy = Spy()
    runs, discovered = runs_over(root, runner=spy)
    with serving(runs, discovered) as server:
        answer = fetch(server, start_path(1, run.RUN), headers=headers, method=method)
        control = post(server, start_path(1, run.RUN))
    assert answer[0] == status
    if method == "GET":
        assert answer[1]["allow"] == "POST"
    assert control[0] == 200 and len(spy.started) == 1


def test_a_stop_from_a_file_is_refused_and_the_same_stop_from_the_origin_is_not(root):
    runs, discovered = runs_over(root)
    with serving(runs, discovered) as server:
        refused = post(server, "/api/v1/run/stop", headers={"Origin": "null"})
        control = post(server, "/api/v1/run/stop")
    assert (refused[0], control[0]) == (403, 200)
    assert run.NOT_FROM_A_FILE in refused[2]


def test_the_route_is_given_no_body_and_no_query_to_read():
    assert [field.name for field in dataclasses.fields(Request)] == ["method", "path", "headers"]


# --- the practice is named by progress.practice_key --------------------------


def test_the_outcome_is_recorded_under_the_key_the_page_named_and_state_reads_it(root):
    runs, discovered = runs_over(root)
    with serving(runs, discovered) as server:
        post(server, start_path(1, run.TEST))
    practices = discovered.corpora[0].progress().read()["practices"]
    assert list(practices) == [key(1)]
    assert corpus_state(discovered.corpora[0])["practices"][key(1)]["passed"] is True


# --- the index, the record's edges ------------------------------------------


def test_the_index_names_the_modes_and_the_endpoints_and_a_post_to_it_is_405(root):
    runs, discovered = runs_over(root)
    with serving(runs, discovered) as server:
        status, _, raw = fetch(server, "/api/v1/run/")
        posted = post(server, "/api/v1/run/")
    document = json.loads(raw)
    assert status == 200 and document["modes"] == ["run", "test"]
    assert document["live"] is None and document["stop"] == "/api/v1/run/stop"
    assert posted[0] == 405


def test_an_outcome_the_store_refuses_is_said_and_the_exit_line_stays_last(root):
    ignore = store_dir(root) / IGNORE_FILENAME
    ignore.parent.mkdir(parents=True)
    ignore.write_text("!keep\n", encoding="utf-8")
    runs, discovered = runs_over(root)
    with serving(runs, discovered) as server:
        _, _, body = post(server, start_path(1, run.RUN))
    assert lines_of(body) == ["Hello, reader", NOT_RECORDED, EXIT_0]


def _workspace(runs, unit: int) -> dict:
    return run.workspace_of(runs.sources[SOURCE], f"kata/unit-{unit:02d}", "practice-python")
