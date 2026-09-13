"""Mirror of `src/studyforge/skills/buildserve/__main__.py` (R12): the skill as a real process.

⛔ Started as a person starts it, answered over loopback, stopped with Ctrl-C's signal.
"""

from __future__ import annotations

import os
import re
import signal
import subprocess
import sys
import threading

from studyforge.validate.report import OK
from tests.fixture_checks import FIXTURES
from tests.studyforge.serve.serving import fetch
from tests.support import repository_root

LISTENING = re.compile(r"^serve http://127\.0\.0\.1:(\d+)/")


class Address:
    """What `fetch` reads off a server that lives in another process."""

    def __init__(self, port: int) -> None:
        self.server_address = ("127.0.0.1", port)


def test_the_module_builds_serves_reports_and_stops_on_interrupt(tmp_path):
    out = tmp_path / "site"
    out.mkdir()
    process = subprocess.Popen(  # noqa: S603 - fixed argv, no shell
        [sys.executable, "-m", "studyforge.skills.buildserve", str(FIXTURES / "depth1")]
        + ["--out", str(out), "--port", "0"],
        cwd=repository_root(),
        env={**os.environ, "PYTHONPATH": "src"},
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    watchdog = threading.Timer(120, process.kill)
    watchdog.start()
    try:
        before = []
        for line in process.stdout:
            before.append(line)
            if found := LISTENING.match(line):
                break
        assert found, f"the skill never listened: {''.join(before)[-600:]}"
        status, _, body = fetch(Address(int(found.group(1))), "/index.html")
        process.send_signal(signal.SIGINT)
        # ⚠️ Read through the SAME text wrapper the loop above read ahead into:
        # `communicate()` reads the raw pipe, so lines already buffered here are lost.
        rest, stderr = process.stdout.read(), process.stderr.read()
        process.wait(timeout=60)
    finally:
        watchdog.cancel()
        if process.poll() is None:
            process.kill()
            process.communicate(timeout=10)
    said = "".join(before) + rest
    assert (status, body) == (200, (out / "index.html").read_bytes())
    assert process.returncode == OK, stderr[-400:]
    assert "partial exercises  missing:" in said
    assert said.splitlines()[-2:] == ["stopped", "step serve exit 0"]
    assert "Traceback" not in said + stderr
