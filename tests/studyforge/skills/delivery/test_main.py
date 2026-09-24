"""Mirror of `src/studyforge/skills/delivery/__main__.py` (R12).

⭐ The module is the skill's first command, so it is run the way a reader runs it: as a
subprocess, from a directory that holds nothing, with only the source on the path.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from studyforge.exitcodes import UNUSABLE
from studyforge.skills.delivery import offer
from tests.support import repository_root


def run(cwd: Path, *argv: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(  # noqa: S603
        [sys.executable, "-m", "studyforge.skills.delivery", *argv],
        cwd=cwd,
        env={"PYTHONPATH": str(repository_root() / "src"), "PATH": "/usr/bin:/bin"},
        capture_output=True,
        timeout=60,
        check=False,
    )


def test_the_module_prints_the_installed_offer_from_an_empty_directory(tmp_path: Path) -> None:
    done = run(tmp_path)
    assert done.returncode == 0, done.stderr.decode("utf-8", "replace")
    assert done.stdout == offer.Offer.installed().render().encode("utf-8")
    assert not any(tmp_path.iterdir()), "the command wrote into the directory it ran in"


def test_the_module_refuses_an_argument(tmp_path: Path) -> None:
    done = run(tmp_path, "docs/tasks")
    assert done.returncode == UNUSABLE
    assert done.stdout == b""
    assert offer.USAGE.encode() in done.stderr
