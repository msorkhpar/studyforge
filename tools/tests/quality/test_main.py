"""Mirror of `tools/quality/__main__.py` (R12).

The exit code is the deliverable. Everything else here is a report; this is
the part that turns the conventions into a build failure, so it is asserted
both in-process and through a real subprocess.
"""

from __future__ import annotations

import sys

import pytest

from tests.support import repository_root, run
from tools.quality import lint
from tools.quality.__main__ import SCOPE, main
from tools.quality.lint import FLOOR_IN_IMAGE, TOOL, lint_scope

#: A fabricated path for a tool a test wants PRESENT — never a real one, and
#: never one carrying a home directory (R7). Nothing is executed at it: the
#: notice's own attempt to run it is the fourth state, which is what makes this
#: the harder direction to assert.
PLANTED = "/path/to/bin/ruff"


def write_offending_module(root):
    """A tree with one module that fails the floor."""
    path = root / "src" / "studyforge" / "nameless.py"
    path.parent.mkdir(parents=True)
    path.write_text("value = 1\n", encoding="utf-8")
    return path


def without_lint(monkeypatch):
    """Make this run carry no lint signal, whatever the host has installed."""
    monkeypatch.setattr(lint, "_which", lambda name: None)


def with_lint(monkeypatch):
    """Make the linter present, whatever the host has installed."""
    monkeypatch.setattr(lint, "_which", lambda name: PLANTED)


def tail(capsys):
    """The lines this run printed, stripped, as a reader meets them."""
    return capsys.readouterr().out.strip().splitlines()


def test_a_clean_tree_exits_zero(tmp_path, capsys):
    assert main(["--root", str(tmp_path)]) == 0
    # ⚠️ Two named lines, not the whole output: notices print above and are
    # deliberately not findings. ⛔ Asserting the whole stream would make "the
    # floor is clean" and "nothing else was worth saying" one claim, and they
    # are not.
    printed = tail(capsys)
    assert printed[-3] == "quality floor: clean"
    assert printed[-2] == SCOPE
    assert printed[-1] == lint_scope()


def test_the_TAIL_says_the_floor_is_not_the_suite(tmp_path, capsys):
    # ⛔ `W187/5`, and the position is the whole fix: the floor was GREEN and
    # the suite RED at the same ref, and an office that self-certifies on the
    # floor's last line merged defects. ⭐ Ruling 78 keeps format enforcement in
    # the suite, so the floor cannot close this by checking more — only by
    # saying what it is a verdict ON, below the verdict. ⚠️ `W393` put a second
    # qualifier under it; what `W187/5` asked for is BELOW THE VERDICT, and the
    # two lines are the tail a reader meets together.
    main(["--root", str(tmp_path)])
    printed = tail(capsys)
    assert printed[-2] == SCOPE
    assert "tests/test_repository.py" in SCOPE
    assert "SEPARATE gate" in SCOPE
    assert printed.index("quality floor: clean") == len(printed) - 3


def test_a_RED_floor_also_says_what_it_is_a_verdict_on(tmp_path, capsys):
    # ⛔ Both directions. A red floor is not evidence the suite is red too, and
    # a reader who learns the scope only on green learns it from the run that
    # needed it least.
    write_offending_module(tmp_path)
    assert main(["--root", str(tmp_path)]) == 1
    printed = tail(capsys)
    assert printed[-2] == SCOPE
    assert printed[-1] == lint_scope()


def test_the_LAST_line_says_this_run_had_NO_lint_signal(tmp_path, capsys, monkeypatch):
    # ⛔ `W393`, and the measurement is `W388/5`: an office read `quality floor:
    # clean` on a host with no linter and handed back GREEN with the format
    # check unclean. ⭐ The absence notice was printing the whole time — ABOVE
    # the verdict. This is the same fact in the position an office copies.
    without_lint(monkeypatch)
    assert main(["--root", str(tmp_path)]) == 0
    last = tail(capsys)[-1]
    assert "NO LINT SIGNAL" in last
    assert f"`{FLOOR_IN_IMAGE}`" in last
    assert "not lint-clean" in last.lower()


def test_the_LAST_line_says_this_run_DID_have_a_lint_signal(tmp_path, capsys, monkeypatch):
    # ⛔ The other way (R12). A line that only ever fired on absence would leave
    # a reader unable to tell "this run had the signal" from "this run did not
    # say" — Ruling 48's argument, and the reason the absent notice exists.
    with_lint(monkeypatch)
    assert main(["--root", str(tmp_path)]) == 0
    last = tail(capsys)[-1]
    assert "NO LINT SIGNAL" not in last
    assert f"{TOOL} is installed here" in last


def test_the_lint_scope_cannot_change_the_exit_code(tmp_path, capsys):
    # ⛔ Ruling 77's half, asserted on the line that now carries the warning: a
    # floor whose verdict moved with `pip install` is the fix this row may not
    # make. ⭐ The same tree, both states of the linter, one exit code.
    write_offending_module(tmp_path)
    codes = set()
    for state in (without_lint, with_lint):
        with pytest.MonkeyPatch().context() as patch:
            state(patch)
            codes.add(main(["--root", str(tmp_path)]))
            assert tail(capsys)[-1] == lint_scope()
    assert codes == {1}


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
    assert printed[-3] == "quality floor: clean"
    assert printed[-2] == SCOPE
    # ⭐ `W393`: taken from the process, not in-process — this is the tail an
    # office actually copies, and it is what THIS environment has to say about
    # its own lint signal. Either state is a pass; a missing line is not.
    assert printed[-1].startswith("lint scope: ")
    assert printed[-1] == lint_scope()
