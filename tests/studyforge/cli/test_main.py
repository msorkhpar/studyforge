"""Mirror of `src/studyforge/cli/__main__.py` (R12).

⛔ Run as a subprocess. `python3 -m studyforge.cli` is what a reader who has not
installed the package types, and importing the module proves nothing about it.
"""

from __future__ import annotations

import os
import subprocess
import sys

from studyforge.validate.cli import UNUSABLE
from studyforge.validate.report import OK
from tests.fixture_checks import FIXTURES
from tests.support import repository_root


def module(*argv) -> subprocess.CompletedProcess[str]:
    """`python3 -m studyforge.cli …`, from the repository root."""
    return subprocess.run(  # noqa: S603 - fixed argv, no shell
        [sys.executable, "-m", "studyforge.cli", *argv],
        cwd=repository_root(),
        env={**os.environ, "PYTHONPATH": "src"},
        capture_output=True,
        text=True,
        check=False,
    )


def test_the_installed_command_runs_a_verb_without_being_installed():
    result = module("plan", str(FIXTURES / "depth1"))
    assert result.returncode == OK
    assert result.stdout.startswith("plan depth1-demo")


def test_it_forwards_the_unusable_exit_code_for_an_unknown_verb():
    assert module("frobnicate").returncode == UNUSABLE


def test_the_module_is_one_implementation_on_top_of_dispatch_main():
    # ⛔ Four lines on top of `dispatch.main`, so what a reader gets before
    # installing and what they get after cannot come to disagree.
    source = (repository_root() / "src/studyforge/cli/__main__.py").read_text("utf-8")
    body = [
        line
        for line in source.splitlines()
        if line.strip() and not line.strip().startswith(("#", '"', "'"))
    ]
    assert any("from studyforge.cli.dispatch import main" in line for line in body)
    assert not any("def " in line for line in body), "this module forwards and defines nothing"
