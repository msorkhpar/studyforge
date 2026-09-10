"""Mirror of `src/studyforge/cli/plan/__main__.py` (R12).

⛔ Run as a subprocess, which is the only way the module entry point is
actually exercised — importing it proves nothing about `python3 -m`.
"""

from __future__ import annotations

import os
import subprocess
import sys

from studyforge.validate.report import INVALID, OK
from tests.fixture_checks import FIXTURES
from tests.support import repository_root


def module(*argv) -> subprocess.CompletedProcess[str]:
    """`python3 -m studyforge.cli.plan …`, from the repository root."""
    return subprocess.run(  # noqa: S603 - fixed argv, no shell
        [sys.executable, "-m", "studyforge.cli.plan", *argv],
        cwd=repository_root(),
        env={**os.environ, "PYTHONPATH": "src"},
        capture_output=True,
        text=True,
        check=False,
    )


def test_the_module_entry_point_plans_a_corpus_and_exits_zero():
    result = module(str(FIXTURES / "depth1"))
    assert result.returncode == OK
    assert result.stdout.startswith("plan depth1-demo")


def test_the_module_entry_point_forwards_the_failing_exit_code(tmp_path):
    result = module(str(tmp_path))
    assert result.returncode == INVALID


def test_it_is_the_same_implementation_as_the_console_script_will_register():
    # ⚠️ Four lines on top of `cli.main`, so the module entry point and the
    # installed console script cannot come to disagree about the command.
    source = (repository_root() / "src/studyforge/cli/plan/__main__.py").read_text("utf-8")
    assert "from studyforge.cli.plan.cli import main" in source
