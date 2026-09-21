"""Mirror of `src/studyforge/serve/routes/runs.py` (R12) — the slot, the stream, the record.

⭐ Over the route's own entry point and a real host run, with no socket: what a started
run IS until it ends. The wire-level readings are `test_run.py`'s.
"""

from __future__ import annotations

import json
import os
import time

import pytest

from studyforge.execute import EDITOR_TTL, Editor, EditorProbe, editor_container_for, exit_line
from studyforge.serve.response import Request
from studyforge.serve.routes import run
from studyforge.serve.routes.runs import verdict
from tests.studyforge.execute.runnable import RAW
from tests.studyforge.execute.test_mode import fake_docker
from tests.studyforge.serve.routes.running import (
    SOURCE,
    StubEditors,
    StubHandle,
    entry,
    key,
    plant_command,
    runs_over,
    served_copy,
    serving,
    stub_runner,
)
from tests.studyforge.serve.serving import fetch

POST = Request("POST", "/api/v1/run/", {})
CLOCK = "2026-09-18T10:00:00+00:00"


@pytest.fixture
def root(tmp_path):
    return served_copy(tmp_path)


def started(runs, unit: int = 1, mode: str = run.RUN):
    return run.route(runs, POST, f"{SOURCE}/{mode}/{key(unit)}")


def test_a_stream_closed_before_its_first_chunk_still_stops_records_and_frees(root):
    # ⚠️ A plain generator closed before it started runs none of its body — the
    # reason the body is a class. The slot, the run and the record are all settled.
    plant_command(root, 1, "run_command", ["python3", "practice/plants/wait.py"])
    runs, discovered = runs_over(root)
    response = started(runs)
    assert runs.live is not None
    response.stream.close()
    assert runs.live is None
    assert entry(discovered.corpora[0], 1)["last"]["exit"] == "stopped"


def test_a_stream_read_to_its_end_records_its_status_and_frees_the_slot(root):
    runs, discovered = runs_over(root, clock=lambda: CLOCK)
    response = started(runs)
    body = b"".join(response.stream)
    response.stream.close()
    assert body == b"Hello, reader\n--- exit 0 ---\n"
    assert runs.live is None
    recorded = entry(discovered.corpora[0], 1)
    assert (recorded["last"]["exit"], recorded["last"]["at"]) == (0, CLOCK)
    assert recorded["last"]["commands"] == ["python3 practice/passes/greet.py"]


def test_cancel_stops_the_run_and_it_ends_recorded_stopped(root):
    plant_command(root, 1, "run_command", ["python3", "practice/plants/wait.py"])
    runs, discovered = runs_over(root)
    response = started(runs)
    chunks = iter(response.stream)
    assert next(chunks) == b"waiting\n"
    response.stream.cancel()
    assert list(chunks) == [b"--- exit stopped ---\n"]
    response.stream.close()
    assert entry(discovered.corpora[0], 1)["last"]["exit"] == "stopped"


def test_the_slot_holds_one_run_and_is_released_only_by_that_run(root):
    handle = StubHandle(["one\n"])
    runs, _ = runs_over(root, runner=stub_runner(handle))
    first = started(runs)
    assert started(runs).status == 409
    assert runs.stop() is True and handle.stopped
    first.stream.close()
    assert runs.live is None and runs.stop() is False


@pytest.mark.parametrize(
    "code,last,recorded",
    [(0, "--- exit 0 ---", 0), (2, "--- exit 2 ---", 2), (-9, "--- exit -9 ---", 137)],
)
def test_a_status_is_recorded_as_the_record_takes_it(code, last, recorded):
    handle = StubHandle([], code)
    handle.returncode = code
    assert verdict(handle, last) == recorded


@pytest.mark.parametrize("word", ["stopped", "timeout"])
def test_a_stopped_or_timed_out_run_is_recorded_by_its_word(word):
    handle = StubHandle([], -15)
    handle.returncode = -15
    assert verdict(handle, f"--- exit {word} ---") == word


# --- ⛔ `W430`: the record the frame policy composes from does NOT expire -----
#
# ⛔ **Every reading below CROSSES `EDITOR_TTL`, and that is the point of the
# row.** A `frame-src` read straight through `EditorProbe.known()` named the
# editor for ten seconds after anything asked and `'none'` from then on, which a
# reader is essentially never inside — and the reading that missed it was taken
# inside the TTL and never crossed its boundary. ⭐ So each case here AGES the
# probe's own cache and ASSERTS that it went cold before reading the policy.

#: The origin a probe discovers below. ⚠️ Loopback and a port, which is all a
#: `frame-src` may ever name; nothing here is a path inside anybody's container.
EDITOR_ORIGIN = "http://127.0.0.1:8443"

#: An editor up over this corpus's `practice/` directory, as a probe answers it.
UP = Editor(origin=EDITOR_ORIGIN, folder="/w/sources", base="practice")


def framed(headers) -> str:
    """The `frame-src` a real response carried, read back as a browser reads it."""
    policy = dict(item.split(" ", 1) for item in headers["content-security-policy"].split("; "))
    return policy["frame-src"]


def real_probes(docker, now, ttl: float = EDITOR_TTL):
    """One REAL `EditorProbe` per corpus, over a fake `docker` and a clock a test moves."""

    def made(corpus):
        return EditorProbe(
            corpus.root,
            editor_container_for(corpus.source),
            docker=str(docker),
            clock=lambda: now[0],
            ttl=ttl,
        )

    return made


def test_an_origin_outlives_the_real_probes_own_cache_going_cold_under_it(root, tmp_path):
    # ⛔ **THE reading of this row, against the REAL probe.** What expires here
    # is the cache the policy used to read through, not a stub's imitation of
    # one — so the boundary crossed is `EDITOR_TTL`'s own.
    now = [100.0]
    answer = "\n".join(("true", "port\t127.0.0.1\t8443", f"mount\t{root}\t/w/sources"))
    live, _ = runs_over(root, editor=real_probes(fake_docker(tmp_path, answer), now))
    assert live.origins() == (), "a cold instance frames nothing, and that is still true"
    assert set(live.editors()) == {SOURCE}
    assert live.origins() == (EDITOR_ORIGIN,)
    now[0] += EDITOR_TTL * 10
    # ⭐ The aged state is ASSERTED and not assumed: a probe that had not gone
    # cold here would make the line below pass while measuring nothing.
    assert live.found(ask=False) == {}, "the probe's cache is still warm, so nothing was crossed"
    assert live.origins() == (EDITOR_ORIGIN,)


def test_a_page_served_long_after_the_ask_still_names_the_editor_on_the_wire(root):
    # ⛔ **The reader's own defect, on a real socket.** The index is the reader
    # that may ask; the page afterwards is served with the probe's cache aged
    # past the TTL, and it is what the browser reads.
    editors = StubEditors(UP)
    live, discovered = runs_over(root, editor=editors)
    with serving(live, discovered) as server:
        warm = fetch(server, "/api/v1/run/")[1]
        aged = editors.expire()
        cold = [probe.known() for probe in aged]
        page = fetch(server, f"/{root.name}/index.html")
    assert aged and cold == [None] * len(aged), "no reading expired, so none was crossed"
    assert framed(warm) == EDITOR_ORIGIN
    assert (page[0], framed(page[1])) == (200, EDITOR_ORIGIN)


def test_the_practice_editor_route_fills_the_record_the_policy_composes_from(root):
    # ⭐ A panel asks for its OWN practice's windows, which is an explicitly
    # requested route and may fork (`W427`, `W429`). ⛔ So a reader who never
    # loaded the index still gets a policy that admits the editor they were just
    # handed — and it is still admitted once that ask has aged out.
    editors = StubEditors(UP)
    live, discovered = runs_over(root, editor=editors)
    assert live.origins() == ()
    assert live.practice_editor(discovered.corpora[0], "practice/passes/greet.py", None)
    aged = editors.expire()
    assert aged and [probe.known() for probe in aged] == [None] * len(aged)
    assert live.origins() == (EDITOR_ORIGIN,)


# --------------------------------------------------------------------------
# `AX-02` — a Submit is recorded with its breakdown, and a Run never is
# --------------------------------------------------------------------------

ASK = "test_the_greeting_names_who_it_greets"
UNNAMED = "test_a_name_with_no_letters_in_it"
REPORT = "reports/greet.xml"


def plant_breakdown(root, unit: int = 1, path: str = REPORT) -> None:
    """Declare a breakdown on one practice and make its grader write the report.

    ⭐ Planted into the COPY's archive, which the unit document is built from —
    the same seam `plant_command` uses, so the record the route reads is the
    record an adapter would have written.
    """
    document = json.loads((root / RAW / f"unit-{unit:02d}" / "practice-1.json").read_text())
    exercise = document["exercise"]
    exercise["test_command"] = [*exercise["test_command"], f"--junit-xml={path}"]
    exercise["cases"] = [
        {"id": ASK, "kind": "main", "says": "it greets whoever it is given"},
        {"id": UNNAMED, "kind": "edge", "says": "a name with no letters is refused"},
    ]
    exercise["report"] = {"format": "junit", "path": path}
    (root / RAW / f"unit-{unit:02d}" / "practice-1.json").write_text(
        json.dumps(document, indent=2), encoding="utf-8"
    )


def submitted(root, unit: int = 1):
    """Submit unit `unit` over a real host run, read to its end; return body and entry."""
    runs, discovered = runs_over(root, clock=lambda: CLOCK)
    answer = run.route(runs, POST, f"{SOURCE}/{run.TEST}/{key(unit)}")
    body = b"".join(answer.stream).decode()
    return body, entry(discovered.corpora[0], unit)


def test_a_submit_records_one_verdict_per_declared_case(root):
    plant_breakdown(root)
    body, recorded = submitted(root)
    # ⛔ The plant is OBSERVED before the record is read: the grader really did
    # write a report, so a green reading below is a fold and not an absence.
    assert (root / REPORT).is_file()
    assert recorded["last"]["cases"] == {ASK: True, UNNAMED: False}
    assert "could not be read" not in body


def test_the_pass_rule_is_untouched_by_a_breakdown_that_is_incomplete(root):
    # ⛔ AX-02's one clause: the grader exited zero, so the practice passed —
    # the unnamed edge is a REPORT about the run and never a second verdict.
    plant_breakdown(root)
    _, recorded = submitted(root)
    assert recorded["last"]["passed"] is True and recorded["first_passed_at"] == CLOCK
    assert recorded["last"]["cases"][UNNAMED] is False


def test_a_submit_whose_practice_declares_no_breakdown_records_none(root):
    _, recorded = submitted(root)
    assert "cases" not in recorded["last"] and recorded["last"]["passed"] is True


def test_a_run_records_no_breakdown_even_after_a_submit_wrote_a_report(root):
    plant_breakdown(root)
    submitted(root)
    assert (root / REPORT).is_file()
    runs, discovered = runs_over(root, clock=lambda: CLOCK)
    answer = run.route(runs, POST, f"{SOURCE}/{run.RUN}/{key(1)}")
    b"".join(answer.stream)
    assert "cases" not in entry(discovered.corpora[0], 1)["last"]


def test_a_submit_that_wrote_no_report_records_no_breakdown_and_says_nothing(root):
    # ⚠️ The grader is declared to write a report and is then pointed at a
    # command that writes none — a compile failure's shape, without a compiler.
    plant_breakdown(root)
    plant_command(root, 1, "test_command", ["python3", "practice/untested/hello.py"])
    body, recorded = submitted(root)
    assert not (root / REPORT).exists()
    assert "cases" not in recorded["last"] and "could not be read" not in body


def test_a_report_the_run_did_not_write_is_refused_on_the_stream_and_not_recorded(root):
    """⛔ The stale clause, end to end, and the reason this task takes a clock.

    ⚠️ **The previous Submit's report is AGED rather than left at the instant
    the first run wrote it**, because `report.CLOCK_SLACK` is two seconds wide
    and two runs in one test are milliseconds apart. ⭐ A real previous run's
    report is minutes or hours old, which is exactly what is modelled here —
    and the two seconds it does not catch is `AX-02/1` in the handoff.
    """
    plant_breakdown(root)
    submitted(root)
    stale = root / REPORT
    assert stale.is_file()
    minutes_ago = time.time() - 600
    os.utime(stale, (minutes_ago, minutes_ago))
    plant_command(root, 1, "test_command", ["python3", "practice/untested/hello.py"])
    body, recorded = submitted(root)
    assert stale.is_file()  # the plant: the previous run's report is still there
    assert "cases" not in recorded["last"]
    assert "could not be read" in body and "older than the run" in body
    assert body.splitlines()[-1] == exit_line(0)
