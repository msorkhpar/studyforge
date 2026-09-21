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
from pathlib import Path

import pytest

from studyforge.archive.scrub import scrub
from studyforge.execute import Editor, EditorProbe, editor_container_for, workbench
from studyforge.progress import IGNORE_FILENAME, store_dir
from studyforge.serve.instance import instance_of
from studyforge.serve.response import API_VERSION, Request
from studyforge.serve.routes import run
from studyforge.serve.routes.runs import NOT_RECORDED, editor_for
from studyforge.serve.routes.state import corpus_state
from tests.studyforge.execute.runnable import FOREIGN_HOME
from tests.studyforge.serve.routes.running import (
    SOURCE,
    Spy,
    StubEditors,
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


# --- where a running editor is (`W416`) -------------------------------------

#: An editor that is up. ⚠️ The folder is a made-up container path: the probe
#: reads the real one back out of the container and never composes one.
UP = Editor(origin="http://127.0.0.1:8443", folder="/w/sources", base="practice")


def index_of(root, editor=None) -> dict:
    runs, discovered = runs_over(root, editor=editor)
    with serving(runs, discovered) as server:
        return json.loads(fetch(server, "/api/v1/run/")[2])


def test_an_editor_that_is_not_up_is_absent_rather_than_a_frame_pointing_nowhere(root):
    assert index_of(root)[run.EDITOR] == {}


def test_the_index_says_where_a_running_editor_is_under_the_corpus_it_belongs_to(root):
    where = index_of(root, StubEditors(UP))[run.EDITOR]
    assert where == {SOURCE: {"origin": UP.origin, "folder": UP.folder}}


def test_the_index_names_an_origin_and_a_port_that_no_built_page_could_have(root):
    # ⛔ R8's floor is why this is on a SERVED answer at all: the editor's host
    # port is per-project, so the one place it can be true is the origin the
    # reader is reading at.
    assert ":8443" in json.dumps(index_of(root, StubEditors(UP)))


def test_one_probe_is_kept_per_corpus_so_a_page_does_not_fork_docker_per_fetch(root):
    editors = StubEditors(UP)
    runs, discovered = runs_over(root, editor=editors)
    with serving(runs, discovered) as server:
        fetch(server, "/api/v1/run/")
        fetch(server, "/api/v1/run/")
    # ⭐ ONE probe, KEPT — that is the whole economy, because a fork happens
    # inside a probe and its TTL bounds how often. ⛔ **Still two after `W427`**:
    # the frame policy READS this probe and never asks it (`W427`), so composing
    # a policy on every response adds no fork at all.
    assert len(editors.made) == 1 and editors.made[0].asked == 2


def test_the_response_that_publishes_an_editor_also_admits_framing_it(root):
    # ⛔ **`W427`, and `W416/2` is why it is asserted on ONE response.** Framing is
    # two-sided: the index may say where the editor is while this server's own
    # `frame-src` forbids embedding it, which is exactly what shipped.
    live, discovered = runs_over(root, editor=StubEditors(UP))
    with serving(live, discovered) as server:
        # ⭐ The index ASKS, so this one response both learns the editor and is
        # served under the policy that ask composed (`W427`).
        _, headers, raw = fetch(server, "/api/v1/run/")
    published = json.loads(raw)[run.EDITOR]
    policy = dict(item.split(" ", 1) for item in headers["content-security-policy"].split("; "))
    assert published == {SOURCE: {"origin": UP.origin, "folder": UP.folder}}
    assert policy["frame-src"] == UP.origin
    assert policy["frame-ancestors"] == "'none'"
    assert headers["x-frame-options"] == "DENY"


def test_composing_a_frame_policy_reads_the_probe_and_never_asks_it(root):
    # ⛔ **Spec §8.3** (`W427`): `origins()` is on the path of EVERY response, so a
    # version that asked would fork `docker` to render a static page. The host arm
    # in `tests/studyforge/cli/test_serve_process.py` is what measures this on a
    # real process against a decoy socket; this is its unit-level twin.
    editors = StubEditors(UP)
    live, discovered = runs_over(root, editor=editors)
    assert live.origins() == ()
    assert editors.made and editors.made[0].asked == 0
    assert set(live.editors())
    assert live.origins() == (UP.origin,)


def test_the_probe_an_instance_makes_asks_docker_about_the_compose_container(root):
    corpus = runs_over(root)[1].corpora[0]
    probe = editor_for(corpus)
    assert isinstance(probe, EditorProbe)
    assert probe.container == editor_container_for(SOURCE)
    assert probe.source_root == corpus.root


# --- one practice's two windows (`W429`) ------------------------------------


def settings_in(root) -> Path:
    """Where the editor's own settings land for `UP`: inside the part of the
    source root it mounts — the HOST side of its bind, which the index never
    carries, because that path is a home (R7)."""
    return root / UP.base / workbench.SETTINGS_DIR / workbench.SETTINGS_FILE


def ask_editor(root, unit=1, editor=None, path=None):
    live, discovered = runs_over(root, editor=editor or StubEditors(UP))
    with serving(live, discovered) as server:
        return post(server, path or f"/api/v1/run/{SOURCE}/{run.EDITOR}/{key(unit)}")


def test_the_index_says_how_to_address_one_practices_files_and_not_only_a_folder(root):
    # ⭐ `W416` published `{origin, folder}` and a folder cannot say which of two
    # windows shows which file. ⛔ The template is the route's own spelling,
    # composed from the namespace and the word — never retyped.
    published = index_of(root)["practice_editor"]
    assert published == f"/api/v1/run/{{corpus}}/{run.EDITOR}/{{practice}}"
    assert run.EDITOR not in run.MODES


def test_a_practice_answers_a_url_for_each_of_its_two_windows(root):
    status, _, body = ask_editor(root)
    answered = json.loads(body)
    assert status == 200
    main, test = answered["main"], answered["test"]
    # ⭐ The WHOLE document, so a key that appeared or vanished is red here.
    # ⚠️ Compared as a document rather than key by key because `W109` holds
    # `origin` to one reader across `src/` and `tests/`, and a subscript of it
    # would be a second one (`AX-05` resolved the same clash the same way).
    assert answered == {
        "api": API_VERSION,
        "resource": "run-editor",
        "origin": UP.origin,
        "main": main,
        "test": test,
    }
    # ⛔ **THE property the whole URL design exists for**: two windows of ONE
    # editor showing two DIFFERENT files, told apart by nothing but their own
    # URLs. ⚠️ Asserted as a difference between the two answers, so a composer
    # that ignored its argument cannot pass.
    assert main["url"] != test["url"]
    assert main["path"] == "passes/greet.py"
    assert test["path"] == "passes/check_greet.py"
    assert main["path"] in main["url"].replace("%2F", "/")
    assert test["path"] in test["url"].replace("%2F", "/")


def test_asking_for_a_practices_windows_writes_that_practices_workspace_settings(root):
    assert not settings_in(root).exists()
    ask_editor(root)
    held = json.loads(settings_in(root).read_text(encoding="utf-8"))
    # ⭐ Everything read-only, the practice's own source excluded back out — and
    # the TEST left read-only on purpose: it is the statement of what *done*
    # means, and a reader who can edit it can make it say anything.
    assert held[workbench.READONLY_INCLUDE] == {workbench.EVERYTHING: True}
    assert held[workbench.READONLY_EXCLUDE] == {"passes/greet.py": True}
    assert "passes/check_greet.py" not in held[workbench.READONLY_EXCLUDE]
    assert held["files.hotExit"] == "off"


def test_no_editor_up_is_a_404_and_writes_nothing_at_all(root):
    # ⛔ Both halves matter: a page told an editor is there would frame a dead
    # origin, and a settings file written for an editor nobody started would be
    # this framework leaving a file in a corpus for no reason.
    status, _, _ = ask_editor(root, editor=StubEditors(None))
    assert status == 404
    assert not settings_in(root).exists()


def test_an_editor_that_does_not_hold_this_practices_file_is_a_404_not_a_url(root):
    # ⚠️ Naming an unmounted path opens an empty, dirty buffer titled with the
    # file's own name — it looks exactly like a corrupted file and is not one.
    elsewhere = Editor(origin=UP.origin, folder=UP.folder, base="docs")
    assert ask_editor(root, editor=StubEditors(elsewhere))[0] == 404


def test_a_settings_file_this_framework_did_not_write_is_a_409_and_is_left_alone(root):
    mine = '{"editor.fontSize": 18}\n'
    settings_in(root).parent.mkdir(parents=True)
    settings_in(root).write_text(mine, encoding="utf-8")
    status, _, body = ask_editor(root)
    assert status == 409
    assert settings_in(root).read_text(encoding="utf-8") == mine
    # ⛔ The refusal's own sentence names a file and an errno; the wire gets the
    # route's constant, which carries neither (R7).
    assert json.loads(body)["error"] == run.WORKSPACE_REFUSED
    assert str(root) not in body


def test_a_practice_with_no_file_to_open_is_a_409_and_no_window(root):
    # ⛔ A quiz carries questions in place of a workspace: no file, no window,
    # no Run and no Submit (`AX-05`). ⭐ Read here as the shape it is — a
    # workspace naming no `main_path` — because that is what the route sees.
    live, discovered = runs_over(root, editor=StubEditors(UP))
    answered = run.editor(live, discovered.corpora[0], {"run_command": ["true"]})
    assert answered.status == 409
    assert run.NO_FILE.encode() in answered.body


def test_addressing_the_editor_is_a_post_and_a_page_opened_from_a_file_cannot(root):
    # ⭐ A POST because it WRITES: it prepares that practice's workspace. ⛔ And
    # `Origin: null` — a page opened from a file — is refused like every other
    # act in this namespace.
    live, discovered = runs_over(root, editor=StubEditors(UP))
    path = f"/api/v1/run/{SOURCE}/{run.EDITOR}/{key(1)}"
    with serving(live, discovered) as server:
        assert fetch(server, path)[0] == 405
        assert post(server, path, headers={"Origin": "null"})[0] == 403


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
