"""Mirror of `src/studyforge/skills/onboarding/verify/__main__.py` (R12): as a real process.

⛔ **Every stub and the reader's document print this invocation**, so it is
started here the way a reader starts it — a subprocess, `python3 -m`, a corpus
root — rather than by calling `main` in-process, which would not catch a
package that cannot be run as a module at all.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys

from studyforge.exitcodes import UNUSABLE
from studyforge.skills.onboarding import library, pin
from studyforge.skills.onboarding.verify import __main__, main
from tests.studyforge.skills.onboarding import corpora
from tests.support import repository_root

#: How long one invocation is given. ⚠️ A bound rather than a hope.
TIMEOUT = 180


def _run(*arguments):
    return subprocess.run(  # noqa: S603 - fixed argv, no shell
        [sys.executable, "-m", "studyforge.skills.onboarding.verify", *arguments],
        cwd=repository_root(),
        env={**os.environ, "PYTHONPATH": "src"},
        capture_output=True,
        text=True,
        timeout=TIMEOUT,
        check=False,
    )


def test_the_entry_point_is_the_packages_main():
    assert __main__.main is main


def test_run_as_a_module_it_verifies_a_pin_and_exits_zero(tmp_path):
    (tmp_path / pin.PIN_DIR).mkdir()
    document = pin.pin_document(corpora.COMMIT, library.version())
    (tmp_path / pin.PIN_FILE).write_text(json.dumps(document), encoding="utf-8")

    done = _run(str(tmp_path))

    assert done.returncode == 0, done.stderr
    assert "the installed version" in done.stdout
    assert done.stderr == "", "a module its package imported would warn here"


def test_run_as_a_module_with_no_pin_it_is_unusable_and_says_why(tmp_path):
    done = _run(str(tmp_path))

    assert done.returncode == UNUSABLE
    assert "there is no pin" in done.stderr
