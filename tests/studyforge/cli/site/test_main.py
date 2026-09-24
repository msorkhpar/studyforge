"""Mirror of `src/studyforge/cli/site/__main__.py` (R12).

⛔ Run as a subprocess: the stage stays independently invocable with the
dispatcher absent, and only a real process proves that.
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
    """`python3 -m studyforge.cli.site …`, from the repository root."""
    return subprocess.run(  # noqa: S603 - fixed argv, no shell
        [sys.executable, "-m", "studyforge.cli.site", *argv],
        cwd=repository_root(),
        env={**os.environ, "PYTHONPATH": "src"},
        capture_output=True,
        text=True,
        check=False,
    )


def test_the_stage_runs_on_its_own(tmp_path):
    result = module(str(FIXTURES / "depth1"), "--out", str(tmp_path))
    assert result.returncode == OK
    assert (tmp_path / "index.html").is_file()


def test_it_refuses_without_an_output_directory(tmp_path):
    # ⛔ argparse's own `2` for a missing required flag, which is the same
    # "could not run" code the rest of the command line uses.
    result = module(str(FIXTURES / "depth1"))
    assert result.returncode == UNUSABLE
    assert list(tmp_path.iterdir()) == []


def test_the_module_is_one_implementation_on_top_of_cli_main():
    source = (repository_root() / "src/studyforge/cli/site/__main__.py").read_text("utf-8")
    body = [
        line
        for line in source.splitlines()
        if line.strip() and not line.strip().startswith(("#", '"', "'"))
    ]
    assert any("from studyforge.cli.site.cli import main" in line for line in body)
    assert not any("def " in line for line in body), "this module forwards and defines nothing"


def test_a_refusal_leaves_the_process_as_a_line_and_not_a_traceback(tmp_path):
    # ⛔ Only a real process shows what reaches stderr.
    import json
    import shutil

    root = tmp_path / "corpus"
    shutil.copytree(FIXTURES / "depth1", root)
    path = sorted((root / "archive").rglob("container.json"))[0]
    document = json.loads(path.read_text("utf-8"))
    path.write_text(json.dumps({**document, "note": "/" + "home/jane/x"}), "utf-8")
    (tmp_path / "out").mkdir()
    result = module(str(root), "--out", str(tmp_path / "out"))
    assert result.returncode == UNUSABLE
    assert "Traceback" not in result.stdout + result.stderr
    assert "home path" in result.stdout
