"""Mirror of `src/studyforge/skills/buildserve/__main__.py` (R12): the skill as a real process.

⛔ Started as a person starts it, answered over loopback, stopped with Ctrl-C's signal.

⛔ **One reader of the process's output** (`W237`): `tests.support.ProcessOutput`, from
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
from tests.studyforge.cli.serving import LISTENING, Address
from tests.studyforge.serve.serving import fetch
from tests.support import ProcessOutput, repository_root

#: How long a process may run before it is killed. ⚠️ A backstop, never the reading's wait.
WATCHDOG = 120

#: Four times Linux's default pipe capacity, so a child writing this blocks unless it is read.
FLOOD = 4 * 65536

#: A stand-in for the skill that fills `stderr` BEFORE it prints its listening line.
FLOODING = """
import signal, sys
signal.signal(signal.SIGINT, lambda *_: (print("stopped", flush=True), sys.exit(0)))
sys.stderr.write("x" * int(sys.argv[1]))
sys.stderr.flush()
print("serve http://127.0.0.1:9/  flooded", flush=True)
signal.pause()
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
    assert (status, body) == (200, (out / "index.html").read_bytes())
    assert session.code == OK, session.errors[-400:]
    assert "partial exercises  missing:" in session.said
    assert session.said.splitlines()[-2:] == ["stopped", "step serve exit 0"]
    assert "Traceback" not in session.said + session.errors


def test_a_child_that_fills_its_stderr_pipe_before_it_listens_does_not_block_the_reading():
    # ⛔ `W237`: `stdout` read to its end before `stderr` blocks here until the watchdog.
    with served([sys.executable, "-c", FLOODING, str(FLOOD)]) as session:
        assert session.port == 9
    assert session.code == 0, session.errors[-400:]
    assert (len(session.errors), set(session.errors)) == (FLOOD, {"x"})
    assert session.said.splitlines() == ["serve http://127.0.0.1:9/  flooded", "stopped"]
