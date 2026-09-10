"""Mirror of `tools/quality/__main__.py` (R12).

The exit code is the deliverable. Everything else here is a report; this is
the part that turns the conventions into a build failure, so it is asserted
both in-process and through a real subprocess.
"""

from __future__ import annotations

import sys

from tests.support import repository_root, run
from tools.quality.__main__ import main


def write_offending_module(root):
    """A tree with one module that fails the floor."""
    path = root / "src" / "studyforge" / "nameless.py"
    path.parent.mkdir(parents=True)
    path.write_text("value = 1\n", encoding="utf-8")
    return path


def test_a_clean_tree_exits_zero(tmp_path, capsys):
    assert main(["--root", str(tmp_path)]) == 0
    # ⚠️ The last line, not the whole output: FND-07's index notice prints
    # above it and is deliberately not a finding. ⛔ Asserting the whole
    # stream would make "the floor is clean" and "nothing else was worth
    # saying" one claim, and they are not.
    assert capsys.readouterr().out.strip().splitlines()[-1] == "quality floor: clean"


def test_findings_exit_one_and_are_printed(tmp_path, capsys):
    write_offending_module(tmp_path)
    assert main(["--root", str(tmp_path)]) == 1
    printed = capsys.readouterr().out
    assert "src/studyforge/nameless.py" in printed
    assert "quality floor:" in printed


def test_the_repository_itself_passes_through_a_real_process():
    # ⭐ In-process is not the same claim. This is the command a contributor
    # or a container actually runs, with the module resolved off the path the
    # way it will be resolved there.
    root = repository_root()
    result = run([sys.executable, "-m", "tools.quality"], cwd=root)
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout.strip().splitlines()[-1] == "quality floor: clean"
