"""Mirror of `src/studyforge/skills/catalogue/__main__.py` (R12).

⛔ Run as a subprocess against this checkout's `src`, never an installed copy: what is
asserted is what a reader's `python3 -m studyforge.skills.catalogue` prints.
"""

from __future__ import annotations

import os
import subprocess
import sys

from studyforge.skills.catalogue import read_line
from tests.support import repository_root


def command(*argv: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(  # noqa: S603 - fixed argv, no shell
        [sys.executable, "-m", "studyforge.skills.catalogue", *argv],
        cwd=repository_root(),
        env={**os.environ, "PYTHONPATH": "src"},
        capture_output=True,
        text=True,
        check=False,
    )


def test_the_command_prints_the_catalogue_then_the_line():
    done = command()
    assert done.returncode == 0, done.stderr
    assert done.stdout.startswith("# The integration catalogue")
    assert done.stdout.rstrip().endswith(read_line())


def test_the_line_alone():
    done = command("--line")
    assert (done.returncode, done.stdout) == (0, read_line() + "\n")


def test_an_unknown_argument_is_refused():
    done = command("--all")
    assert done.returncode == 2 and "usage" in done.stderr
