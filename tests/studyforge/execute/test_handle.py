"""Mirror of `src/studyforge/execute/handle.py` (R12): the sequence, the stream, the exit line.

⭐ Real host processes, driven through the host launcher with argv this module
chooses (`python3 -c …`): the handle does not check commands — `Runner.start`
does, before a handle exists — so these cases can say exactly what each command
does. Both modes' acceptance is `test_acceptance.py`'s.
"""

from __future__ import annotations

import sys
import time

import pytest

from studyforge.execute import EXIT_STOPPED, EXIT_TIMEOUT, HOST, LineGate, RunHandle, exit_line
from studyforge.execute.runner import HostLauncher

PY = sys.executable


def handle(tmp_path, *commands, timeout=30.0, grace=0.5) -> RunHandle:
    return RunHandle(
        commands, HostLauncher(tmp_path, "."), LineGate([]), mode=HOST, timeout=timeout, grace=grace
    )


def says(text: str, status: int = 0) -> list[str]:
    return [PY, "-c", f"import sys; print({text!r}); sys.exit({status})"]


def test_the_exit_line_is_spelled_once_here():
    assert exit_line(0) == "--- exit 0 ---"
    assert exit_line(EXIT_TIMEOUT) == "--- exit timeout ---"
    assert exit_line(EXIT_STOPPED) == "--- exit stopped ---"


def test_every_command_runs_in_order_when_each_succeeds(tmp_path):
    lines = list(handle(tmp_path, says("one"), says("two")).lines())
    assert lines == ["one", "two", exit_line(0)]


def test_the_first_failure_ends_the_run(tmp_path):
    lines = list(handle(tmp_path, says("one", 3), says("two")).lines())
    assert lines == ["one", exit_line(3)]


def test_a_program_that_cannot_start_is_a_line_and_127_never_a_raise(tmp_path):
    lines = list(handle(tmp_path, says("one"), ["no-such-program-anywhere"], says("three")).lines())
    assert lines[0] == "one"
    assert lines[1].startswith("no-such-program-anywhere: ")
    assert lines[2:] == [exit_line(127)]


def test_a_first_command_that_cannot_start_is_the_same(tmp_path):
    assert list(handle(tmp_path, ["no-such-program-anywhere"]).lines())[-1] == exit_line(127)


def test_the_gate_sees_every_line(tmp_path):
    run = RunHandle(
        (says("secret"),),
        HostLauncher(tmp_path, "."),
        lambda raw: raw.strip().upper(),
        mode=HOST,
        timeout=30.0,
        grace=0.5,
    )
    assert list(run.lines()) == ["SECRET", exit_line(0)]


def test_a_timeout_ends_the_run_with_the_timeout_line(tmp_path):
    started = time.monotonic()
    lines = list(handle(tmp_path, [PY, "-c", "import time; time.sleep(60)"], timeout=0.5).lines())
    assert lines == [exit_line(EXIT_TIMEOUT)]
    assert time.monotonic() - started < 10


def test_a_run_inside_its_timeout_is_not_timed_out(tmp_path):
    assert list(handle(tmp_path, says("quick"), timeout=30.0).lines()) == ["quick", exit_line(0)]


def test_stop_ends_the_run_with_the_stopped_line_and_only_once(tmp_path):
    run = handle(tmp_path, [PY, "-c", "import time; time.sleep(60)"], says("never"))
    assert run.running
    assert run.stop() is True
    assert run.stop() is False
    assert list(run.lines()) == [exit_line(EXIT_STOPPED)]
    assert not run.running


def test_a_finished_run_cannot_be_stopped(tmp_path):
    run = handle(tmp_path, says("done"))
    list(run.lines())
    assert run.stop() is False
    assert run.returncode == 0


def test_abandoning_the_stream_kills_the_live_command(tmp_path):
    run = handle(tmp_path, [PY, "-u", "-c", "import time; print('up'); time.sleep(60)"])
    process = run._first
    stream = run.lines()
    assert next(stream) == "up"
    stream.close()
    assert process.wait(timeout=10) != 0


@pytest.mark.parametrize("status", [0, 1, 2, 5])
def test_the_exit_line_carries_the_last_status(tmp_path, status):
    assert list(handle(tmp_path, says("x", status)).lines())[-1] == exit_line(status)
