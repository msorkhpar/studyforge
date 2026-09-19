"""Mirror of `src/studyforge/serve/routes/runs.py` (R12) — the slot, the stream, the record.

⭐ Over the route's own entry point and a real host run, with no socket: what a started
run IS until it ends. The wire-level readings are `test_run.py`'s.
"""

from __future__ import annotations

import pytest

from studyforge.serve.response import Request
from studyforge.serve.routes import run
from studyforge.serve.routes.runs import verdict
from tests.studyforge.serve.routes.running import (
    SOURCE,
    StubHandle,
    entry,
    key,
    plant_command,
    runs_over,
    served_copy,
    stub_runner,
)

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
