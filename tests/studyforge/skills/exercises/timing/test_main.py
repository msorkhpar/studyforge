"""Mirror of `src/studyforge/skills/exercises/timing/__main__.py` (R12).

⛔ Run as a subprocess against this checkout's `src`: the module's whole job is the exit
status a person at a terminal gets, so that is what is asserted.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from tests.support import repository_root


def command(*argv: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(  # noqa: S603 - fixed argv, no shell
        [sys.executable, "-m", "studyforge.skills.exercises.timing", *argv],
        cwd=repository_root(),
        env={**os.environ, "PYTHONPATH": "src"},
        capture_output=True,
        text=True,
        check=False,
    )


def test_help_exits_zero_with_the_usage():
    done = command("--help")
    assert done.returncode == 0, done.stderr
    assert done.stdout.startswith("usage: python3 -m studyforge.skills.exercises.timing")


def test_a_missing_argument_is_the_usage_and_status_two_not_a_traceback():
    done = command()
    assert done.returncode == 2
    assert "usage:" in done.stderr and "Traceback" not in done.stderr


def test_a_tree_with_no_short_wait_exits_zero(tmp_path: Path):
    (tmp_path / "a.py").write_text("x = 1\n", encoding="utf-8")
    done = command(str(tmp_path))
    assert done.returncode == 0, done.stderr
    assert "0 short wait(s)" in done.stdout
