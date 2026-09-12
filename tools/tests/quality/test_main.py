"""Mirror of `tools/quality/__main__.py` (R12).

The exit code is the deliverable. Everything else here is a report; this is
the part that turns the conventions into a build failure, so it is asserted
both in-process and through a real subprocess.
"""

from __future__ import annotations

import sys

from tests.support import repository_root, run
from tools.quality.__main__ import SCOPE, main


def write_offending_module(root):
    """A tree with one module that fails the floor."""
    path = root / "src" / "studyforge" / "nameless.py"
    path.parent.mkdir(parents=True)
    path.write_text("value = 1\n", encoding="utf-8")
    return path


def test_a_clean_tree_exits_zero(tmp_path, capsys):
    assert main(["--root", str(tmp_path)]) == 0
    # ⚠️ Two named lines, not the whole output: notices print above and are
    # deliberately not findings. ⛔ Asserting the whole stream would make "the
    # floor is clean" and "nothing else was worth saying" one claim, and they
    # are not.
    printed = capsys.readouterr().out.strip().splitlines()
    assert printed[-2] == "quality floor: clean"
    assert printed[-1] == SCOPE


def test_the_LAST_line_says_the_floor_is_not_the_suite(tmp_path, capsys):
    # ⛔ `W187/5`, and the position is the whole fix: the floor was GREEN and
    # the suite RED at the same ref, and an office that self-certifies on the
    # floor's last line merged defects. ⭐ Ruling 78 keeps format enforcement in
    # the suite, so the floor cannot close this by checking more — only by
    # saying what it is a verdict ON, below the verdict.
    main(["--root", str(tmp_path)])
    printed = capsys.readouterr().out.strip().splitlines()
    assert printed[-1] is not None and printed[-1] == SCOPE
    assert "tests/test_repository.py" in SCOPE
    assert "SEPARATE gate" in SCOPE
    assert printed.index("quality floor: clean") == len(printed) - 2


def test_a_RED_floor_also_says_what_it_is_a_verdict_on(tmp_path, capsys):
    # ⛔ Both directions. A red floor is not evidence the suite is red too, and
    # a reader who learns the scope only on green learns it from the run that
    # needed it least.
    write_offending_module(tmp_path)
    assert main(["--root", str(tmp_path)]) == 1
    assert capsys.readouterr().out.strip().splitlines()[-1] == SCOPE


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
    printed = result.stdout.strip().splitlines()
    assert printed[-2] == "quality floor: clean"
    assert printed[-1] == SCOPE
