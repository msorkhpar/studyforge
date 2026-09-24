"""Mirror of `src/studyforge/skills/buildserve/__main__.py` (R12): the skill as a real process.

⛔ Started as a person starts it, answered over loopback, stopped with Ctrl-C's signal.

⛔ **One reader of the process's output**: `tests.support.ProcessOutput`, from
launch to exit, so both pipes are drained together. A child that fills its `stderr` pipe
before it prints the listening line cannot block the reading, and a stand-in child that
does exactly that is run below.
"""

from __future__ import annotations

import contextlib
import os
import signal
import subprocess
import sys
import threading
from collections.abc import Iterator
from dataclasses import dataclass

import pytest

from studyforge.validate.report import OK
from tests.fixture_checks import FIXTURES
from tests.studyforge.cli.serving import LISTENING, Address, served_page
from tests.studyforge.serve.serving import fetch
from tests.support import ProcessOutput, repository_root

#: How long a process may run before it is killed. ⚠️ A backstop, never the reading's wait.
WATCHDOG = 120

#: Four times Linux's default pipe capacity, so a child writing this blocks unless it is read.
FLOOD = 4 * 65536

#: A stand-in for the skill that fills `stderr` BEFORE it prints its listening line.
#:
#: ⛔ **It BLOCKS `SIGINT` before it listens and TAKES it with `sigwait`.** A Python
#: handler followed by `signal.pause()` lost the signal whenever it landed after the
#: interpreter's last signal check and before `pause()` entered the kernel: the handler's flag
#: was set, `pause()` then waited for a second signal that never came, and the reading ran out
#: its output timeout. A loaded parallel suite preempts the child in exactly that window. A
#: blocked signal stays PENDING until `sigwait` takes it, so no arrival time can lose it.
#: A second argument HOLDS it after it listens until one byte arrives on `stdin`.
FLOODING = """
import os, signal, sys
signal.pthread_sigmask(signal.SIG_BLOCK, {signal.SIGINT})
sys.stderr.write("x" * int(sys.argv[1]))
sys.stderr.flush()
print("serve http://127.0.0.1:9/  flooded", flush=True)
if sys.argv[2:]:
    os.read(0, 1)
signal.sigwait({signal.SIGINT})
print("stopped", flush=True)
"""


@dataclass
class Served:
    """The port a process printed; after the block, everything it printed and its exit code."""

    port: int
    said: str = ""
    errors: str = ""
    code: int | None = None


@contextlib.contextmanager
def served(argv: list[str]) -> Iterator[Served]:
    """Start `argv`; yield once it listens; then interrupt it and read both pipes to their end."""
    with subprocess.Popen(  # noqa: S603 - fixed argv, no shell
        argv,
        cwd=repository_root(),
        env={**os.environ, "PYTHONPATH": "src"},
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ) as process:
        output = ProcessOutput(process)
        watchdog = threading.Timer(WATCHDOG, process.kill)
        watchdog.start()
        try:
            found = None
            while found is None and (line := output.line(timeout=WATCHDOG)):
                found = LISTENING.match(line)
            if found is None:
                process.kill()
                said, errors = output.rest(timeout=10)
                pytest.fail(f"it never listened: {said[-600:]!r} {errors[-400:]!r}")
            result = Served(int(found.group(1)))
            yield result
            process.send_signal(signal.SIGINT)
            # ⭐ 60 s is what a child is given to END once told to — the skill's shutdown,
            # or the stand-in waking from `sigwait` — on a machine the parallel suite loads. It
            # is a backstop, never a wait for work: neither child has work left to do here.
            result.said, result.errors = output.rest(timeout=60)
            result.code = process.wait(timeout=60)
        finally:
            watchdog.cancel()
            if process.poll() is None:
                process.kill()
                output.rest(timeout=10)


def test_the_module_builds_serves_reports_and_stops_on_interrupt(tmp_path):
    out = tmp_path / "site"
    out.mkdir()
    argv = [sys.executable, "-m", "studyforge.skills.buildserve", str(FIXTURES / "depth1")]
    with served([*argv, "--out", str(out), "--port", "0"]) as session:
        status, _, body = fetch(Address(session.port), "/index.html")
    assert (status, body) == (200, served_page((out / "index.html").read_bytes()))
    assert session.code == OK, session.errors[-400:]
    assert "partial exercises  missing:" in session.said
    assert session.said.splitlines()[-2:] == ["stopped", "step serve exit 0"]
    assert "Traceback" not in session.said + session.errors


def test_a_child_that_fills_its_stderr_pipe_before_it_listens_does_not_block_the_reading():
    # ⛔ `stdout` read to its end before `stderr` blocks here until the watchdog.
    with served([sys.executable, "-c", FLOODING, str(FLOOD)]) as session:
        assert session.port == 9
    assert session.code == 0, session.errors[-400:]
    assert (len(session.errors), set(session.errors)) == (FLOOD, {"x"})
    assert session.said.splitlines() == ["serve http://127.0.0.1:9/  flooded", "stopped"]


@contextlib.contextmanager
def held() -> Iterator[tuple[subprocess.Popen, ProcessOutput]]:
    """The stand-in, HELD after it listens until a byte arrives on its `stdin`."""
    argv = [sys.executable, "-c", FLOODING, "0", "hold"]
    pipes = {"stdout": subprocess.PIPE, "stderr": subprocess.PIPE}
    with subprocess.Popen(argv, stdin=subprocess.PIPE, **pipes) as process:  # noqa: S603
        output = ProcessOutput(process)
        try:
            assert output.line(timeout=WATCHDOG) == "serve http://127.0.0.1:9/  flooded\n"
            yield process, output
        finally:
            if process.poll() is None:
                process.kill()
                output.rest(timeout=10)


def blocked_and_pending(pid: int) -> tuple[bool, bool]:
    """Whether `SIGINT` is in the process's blocked mask, and in its pending set, per `/proc`."""
    fields = dict(line.split(":\t", 1) for line in open(f"/proc/{pid}/status").read().splitlines())
    bit = 1 << (signal.SIGINT - 1)
    return bool(int(fields["SigBlk"], 16) & bit), bool(int(fields["ShdPnd"], 16) & bit)


def test_an_interrupt_that_lands_before_the_stand_in_waits_for_it_still_stops_it():
    # ⛔ The signal is sent while the stand-in is held short of `sigwait`, where the
    # handler-and-`pause()` stand-in could lose it. It is read back as BLOCKED and PENDING —
    # `kill` queues it before it returns — and it is then taken, not lost.
    with held() as (process, output):
        process.send_signal(signal.SIGINT)
        assert blocked_and_pending(process.pid) == (True, True)
        process.stdin.write(b"!")
        process.stdin.close()
        said, _ = output.rest(timeout=60)
        assert (process.wait(timeout=60), said.splitlines()[-1]) == (0, "stopped")


def test_the_stand_in_released_without_an_interrupt_does_not_stop():
    # ⛔ The other way: releasing the hold alone does not end it, so the stop above is the signal's.
    with held() as (process, output):
        process.stdin.write(b"!")
        process.stdin.close()
        with pytest.raises(TimeoutError):
            output.rest(timeout=1)
        assert process.poll() is None
