"""Mirror of `src/studyforge/progress/lock.py` (R12).

⛔ **The exclusion is shown against a second PROCESS**, because that is the case
the extraction source's `threading.Lock` could not cover; a thread-only test
would pass against exactly the defect this module replaces.
"""

from __future__ import annotations

import os
import subprocess
import sys
import threading

import pytest

from studyforge.progress import lock as lock_module
from studyforge.progress.errors import ProgressError
from studyforge.progress.lock import LOCK_FILENAME, exclusive, supported
from tests.support import ProcessOutput, repository_root

#: Long enough for a child to start and take an unheld lock many times over.
BLOCKED_FOR = 1.0

CHILD = """
import sys
from studyforge.progress.lock import exclusive
print("ready", flush=True)
with exclusive(sys.argv[1]):
    print("held", flush=True)
"""


def child_environment():
    return {**os.environ, "PYTHONPATH": str(repository_root() / "src")}


def test_this_platform_has_the_lock_the_store_needs():
    # ⭐ The pinned image is POSIX; a False here means every test below stood down.
    assert supported()


def test_a_second_process_waits_until_the_lock_is_released(tmp_path):
    path = tmp_path / LOCK_FILENAME
    with exclusive(path):
        child = subprocess.Popen(
            [sys.executable, "-c", CHILD, str(path)],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=child_environment(),
        )
        # ⛔ One reader, from launch to exit: a line handed out here is still in `rest`.
        output = ProcessOutput(child)
        assert output.line(timeout=30) == "ready\n"
        with pytest.raises(subprocess.TimeoutExpired):
            child.wait(timeout=BLOCKED_FOR)
    stdout, stderr = output.rest(timeout=30)
    assert child.wait(timeout=30) == 0, stderr[-400:]
    assert stdout.splitlines() == ["ready", "held"], stderr[-400:]


def test_a_second_thread_waits_too(tmp_path):
    path = tmp_path / LOCK_FILENAME
    held = threading.Event()

    def take():
        with exclusive(path):
            held.set()

    with exclusive(path):
        thread = threading.Thread(target=take)
        thread.start()
        assert not held.wait(timeout=BLOCKED_FOR)
    thread.join(timeout=30)
    assert held.is_set()


def test_a_platform_without_flock_refuses_rather_than_running_unlocked(tmp_path, monkeypatch):
    monkeypatch.setattr(lock_module, "fcntl", None)
    with pytest.raises(ProgressError), exclusive(tmp_path / LOCK_FILENAME):
        pytest.fail("the block ran with no lock held")
    assert not (tmp_path / LOCK_FILENAME).exists()


def test_a_lock_that_cannot_be_opened_names_no_path(tmp_path):
    with pytest.raises(ProgressError) as refused, exclusive(tmp_path / "absent" / LOCK_FILENAME):
        pytest.fail("the block ran with no lock held")
    assert str(tmp_path) not in str(refused.value)
