"""`python3 -m studyforge.validate` — the command, before SF-28 registers it.

⚠️ **Run as a real process, deliberately.** The module entry point exists so
that an adapter author has a command *today*, and a command is only a command
if a shell can run it and read its exit status. Calling `main()` in-process
would test everything except the part SF-28 is going to depend on.
"""

import os
import subprocess
import sys

from studyforge.validate.cli import UNUSABLE
from studyforge.validate.report import INVALID, OK
from tests.studyforge.validate import corpora
from tests.support import repository_root


def invoke(*argv):
    """Run the module as a subprocess, returning the completed process."""
    # ⛔ `PYTHONPATH=src`, never an absolute path built from the environment: a
    # captured command line ends up in a failure message, and a home directory
    # in a failure message is personal data (R7). The repository root is the
    # working directory, so `src` is relative to it.
    return subprocess.run(  # noqa: S603 - fixed argv, no shell
        [sys.executable, "-m", "studyforge.validate", *argv],
        cwd=repository_root(),
        env={**os.environ, "PYTHONPATH": "src"},
        capture_output=True,
        text=True,
        check=False,
    )


def test_the_module_runs_as_a_command_and_exits_zero_on_a_valid_corpus(tmp_path):
    result = invoke(str(corpora.one_unit(tmp_path / "c")))
    assert result.returncode == OK, result.stdout + result.stderr
    assert "valid:" in result.stdout


def test_it_exits_one_on_an_invalid_corpus(tmp_path):
    result = invoke(str(corpora.one_unit(tmp_path / "c", blocks=[])))
    assert result.returncode == INVALID
    assert "NOT valid:" in result.stdout


def test_it_exits_two_when_it_could_not_run_at_all(tmp_path):
    result = invoke(str(tmp_path / "nowhere"))
    assert result.returncode == UNUSABLE
    assert "not a directory" in result.stdout


def test_it_exits_two_when_given_no_argument():
    # ⚠️ `argparse`'s own usage error is also a "could not run", and it happens
    # to use the same code — asserted rather than assumed, because a script
    # branching on the number should not have to read argparse's source.
    assert invoke().returncode == UNUSABLE


def test_the_module_is_one_implementation_on_top_of_cli_main():
    # ⛔ Four lines on top of `cli.main`, so the module entry point and the
    # console script SF-28 registers cannot come to disagree about what the
    # command does. Asserted on the source, because that is where the
    # duplication would appear.
    source = (repository_root() / "src/studyforge/validate/__main__.py").read_text("utf-8")
    body = [
        line
        for line in source.splitlines()
        if line.strip() and not line.strip().startswith(("#", '"', "'"))
    ]
    assert any("from studyforge.validate.cli import main" in line for line in body)
    assert not any("def " in line for line in body)
