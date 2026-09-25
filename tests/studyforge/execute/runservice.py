"""The runner's run service, started on the host for a test: `perl`, a loopback port, a work root.

⭐ The real script the package ships (`execute/assets/runservice.pl`), so a test
reads the wire, the allowlist and the kill-by-token the runner runs.
"""

from __future__ import annotations

import contextlib
import os
import re
import shutil
import subprocess
from collections.abc import Iterator
from pathlib import Path

import pytest

from studyforge.execute import Service
from studyforge.execute.published import SCRIPT

#: The service's script, as the package ships it.
SCRIPT_PATH = Path(__file__).resolve().parents[3] / "src/studyforge/execute" / SCRIPT

#: Skips a module whose tests need the service, on a host with no `perl`.
NEEDS_PERL = pytest.mark.skipif(shutil.which("perl") is None, reason="the run service needs perl")


@contextlib.contextmanager
def run_service(work: Path) -> Iterator[Service]:
    """Start the service over `work` on `127.0.0.1` and a free port; stop it afterwards."""
    process = subprocess.Popen(
        ["perl", str(SCRIPT_PATH)],
        env={
            **os.environ,
            "STUDYFORGE_RUN_PORT": "0",
            "STUDYFORGE_RUN_BIND": "127.0.0.1",
            "STUDYFORGE_RUN_WORK": str(work),
        },
        stdin=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        assert process.stderr is not None
        heard = re.search(r"listening on (\d+)", process.stderr.readline())
        assert heard, "the run service did not say where it listens"
        yield Service("127.0.0.1", int(heard.group(1)))
    finally:
        process.kill()
        process.wait(timeout=10)
