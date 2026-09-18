"""Mirror of `src/studyforge/skills/onboarding/__main__.py` (R12): the module as a real process.

⛔ **The reader's document prints this invocation** (`W332`), so it is started
here the way a reader starts it — a subprocess, `python3 -m`, a corpus root —
rather than by calling `main` in-process, which would not catch a package that
cannot be run as a module at all.
"""

from __future__ import annotations

import os
import subprocess
import sys

from studyforge.exitcodes import UNUSABLE
from studyforge.skills.onboarding import __main__, cli
from tests.studyforge.generate.corpora import a_corpus
from tests.support import repository_root

#: How long one invocation is given. ⚠️ A bound rather than a hope.
TIMEOUT = 180

MODULE = "studyforge.skills.onboarding"


def _run(*arguments):
    return subprocess.run(  # noqa: S603 - fixed argv, no shell
        [sys.executable, "-m", MODULE, *arguments],
        cwd=repository_root(),
        env={**os.environ, "PYTHONPATH": "src"},
        capture_output=True,
        text=True,
        timeout=TIMEOUT,
        check=False,
    )


def test_the_module_reports_where_a_corpus_stands_and_exits_zero(tmp_path):
    done = _run(str(a_corpus(tmp_path, "depth1")))

    assert done.returncode == 0, done.stderr[-400:]
    assert "- units: " in done.stdout and "- narrated: " in done.stdout
    assert "Traceback" not in done.stdout + done.stderr


def test_the_module_run_with_no_root_refuses_without_a_traceback():
    # ⛔ Both ways: `test_authoring_reference` runs every commanded module bare,
    # and a parser error there must read as a refusal, never as a crash.
    done = _run()

    assert done.returncode == UNUSABLE
    assert "usage: python3 -m studyforge.skills.onboarding" in done.stderr
    assert "Traceback" not in done.stdout + done.stderr


def test_the_module_entry_point_is_the_command_and_not_a_second_implementation():
    # ⭐ One implementation: the four-line module imports exactly what a caller
    # importing `cli` gets, so the two cannot come to disagree.
    assert __main__.main is cli.main
