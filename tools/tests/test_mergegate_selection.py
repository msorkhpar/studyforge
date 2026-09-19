"""`W366` through the real merge gate: the suite takes what a change reaches, and the audit.

⭐ **Every merge here is real** — a throwaway repository laid out like this one, staged with
`git merge --no-commit` by `stage_and_read` — and the suite gate is a REAL `pytest` run in
that repository, through the gate's own default runner. ⛔ Nothing reaches docker: the one
gate is a HOST gate, so nothing here waits on or takes the shared container lock.

⭐ **The planted hidden dependency (clause 5).** `tests/test_hidden.py` reaches `pkg.low`
through `importlib` with a name built at run time, which no import map can see. The branch
breaks `pkg.low`. ⚠️ A TARGETED run does not take that test and reads GREEN — the blind spot,
measured rather than assumed — and ⭐ the FULL run that audits the selection is RED and NAMES
it as the failure the selection would have missed.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from tests.support import git, init_repository, run
from tools.gates import HOST, Gate
from tools.mergegate import MERGED, REFUSED, render, stage_and_read

_IDENTITY = ("-c", "user.name=test", "-c", "user.email=test@example.invalid")

#: ⭐ A real pytest in the throwaway repository; no cache written, no plugin of ours loaded.
SUITE = Gate(
    "suite",
    HOST,
    (sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "-p", "no:xdist"),
    "the throwaway repository's own tests",
)

TREE = {
    "pytest.ini": "[pytest]\npythonpath = src .\ntestpaths = tests\n",
    "src/pkg/__init__.py": "",
    "src/pkg/low.py": "VALUE = 1\n",
    "src/pkg/alone.py": "OTHER = 2\n",
    "tests/__init__.py": "",
    "tests/test_visible.py": (
        "from pkg import low\n\ndef test_the_module_imports():\n    assert hasattr(low, 'VALUE')\n"
    ),
    "tests/test_alone.py": "from pkg.alone import OTHER\n\ndef test_alone():\n    assert OTHER\n",
    # ⛔ THE PLANT: a dependency the import map cannot see — the name is built at run time.
    "tests/test_hidden.py": (
        "import importlib\n\n"
        "def test_the_hidden_value():\n"
        "    assert importlib.import_module('pk' + 'g.low').VALUE == 1\n"
    ),
}


def _git(cwd: Path, *arguments: str) -> str:
    result = run([git(), *_IDENTITY, "-c", "commit.gpgsign=false", *arguments], cwd=cwd)
    assert result.returncode == 0, result.stdout + result.stderr
    return result.stdout.strip()


def _commit_all(cwd: Path, message: str) -> None:
    _git(cwd, "add", "-A")
    _git(cwd, "commit", "-q", "-m", message)


def _branch_writes(root: Path, files: dict[str, str]) -> None:
    _git(root, "checkout", "-q", "-b", "branch")
    for relative, text in files.items():
        (root / relative).parent.mkdir(parents=True, exist_ok=True)
        (root / relative).write_text(text, encoding="utf-8")
    _commit_all(root, "the branch")
    _git(root, "checkout", "-q", "release")


@pytest.fixture
def release(tmp_path: Path) -> Path:
    """A clean `release` tip holding `TREE`, whose own suite is green."""
    root = init_repository(tmp_path / "release")
    # ⛔ This THROWAWAY repository's own config: `stage_and_read` runs `git merge` itself.
    _git(root, "config", "user.name", "test")
    _git(root, "config", "user.email", "test@example.invalid")
    _git(root, "symbolic-ref", "HEAD", "refs/heads/release")
    for relative, text in TREE.items():
        (root / relative).parent.mkdir(parents=True, exist_ok=True)
        (root / relative).write_text(text, encoding="utf-8")
    (root / ".gitignore").write_text("__pycache__/\n", encoding="utf-8")
    _commit_all(root, "base")
    return root


def _suite_line(lines: list[str]) -> str:
    return next(line for line in lines if " suite [host]" in line)


def test_the_PLANT_a_TARGETED_run_does_not_see_it_and_reads_GREEN(release, capsys):
    # ⚠️ The blind spot, MEASURED: the selection takes `test_visible` and not the plant.
    _branch_writes(release, {"src/pkg/low.py": "VALUE = 2\n"})
    outcome = stage_and_read(release, "branch", None, (SUITE,))
    capsys.readouterr()
    lines = render(outcome)
    assert outcome.verdict == MERGED, lines
    assert "SELECTED 1 whole test file(s)" in _suite_line(lines)
    assert lines[-1].endswith("the suite read a SELECTION, not the full suite")
    _git(release, "merge", "--abort")


def test_the_PLANT_the_AUDIT_is_RED_and_NAMES_the_test_the_selection_missed(release, capsys):
    _branch_writes(release, {"src/pkg/low.py": "VALUE = 2\n"})
    outcome = stage_and_read(release, "branch", None, (SUITE,), full="milestone close")
    capsys.readouterr()
    lines = render(outcome)
    assert outcome.verdict == REFUSED, lines
    assert "FULL, AUDITING the selection" in _suite_line(lines)
    assert (
        "    ⛔ AUDIT RED [host]: the selection would have MISSED "
        "tests/test_hidden.py::test_the_hidden_value"
    ) in lines, lines
    assert outcome.restored


def test_a_failure_INSIDE_the_selection_is_caught_and_never_called_missed(release, capsys):
    # ⭐ The other direction: a visible dependency breaks, and the audit says it was caught.
    _branch_writes(release, {"src/pkg/alone.py": "OTHER = 0\n"})
    outcome = stage_and_read(release, "branch", None, (SUITE,), full="milestone close")
    capsys.readouterr()
    lines = render(outcome)
    assert outcome.verdict == REFUSED, lines
    assert any("every failure lies inside the selection" in line for line in lines), lines
    assert not any("MISSED" in line for line in lines)


def test_a_TARGETED_run_that_breaks_a_VISIBLE_dependency_is_RED(release, capsys):
    _branch_writes(release, {"src/pkg/alone.py": "OTHER = 0\n"})
    outcome = stage_and_read(release, "branch", None, (SUITE,))
    capsys.readouterr()
    assert outcome.verdict == REFUSED, render(outcome)
    assert "SELECTED" in _suite_line(render(outcome))


def test_a_DOCUMENT_only_branch_takes_NO_test_file_and_the_scope_is_FULL_when_empty(release):
    # ⛔ This tree has no tree readers, so a document reaches nothing — and an EMPTY selection
    #    is read as the full suite, never as a pass over nothing (Ruling 191).
    _branch_writes(release, {"docs/note.md": "a note\n"})
    seen: list[tuple[str, ...]] = []
    outcome = stage_and_read(release, "branch", lambda g, r: seen.append(g.argv) or 0, (SUITE,))
    assert seen == [SUITE.argv]
    assert "scope: FULL" in outcome.scope[0] and "empty" in outcome.scope[1]
    _git(release, "merge", "--abort")


def test_a_SHARED_change_takes_the_full_suite_with_NO_path_appended(release):
    _branch_writes(release, {"tests/conftest.py": ""})
    seen: list[tuple[str, ...]] = []
    outcome = stage_and_read(release, "branch", lambda g, r: seen.append(g.argv) or 0, (SUITE,))
    assert seen == [SUITE.argv]
    assert outcome.scope[1] == "  why: tests/conftest.py: shared machinery"
    _git(release, "merge", "--abort")


def test_a_TARGETED_run_appends_exactly_the_selection_to_the_argv(release):
    _branch_writes(release, {"src/pkg/alone.py": "OTHER = 3\n"})
    seen: list[tuple[str, ...]] = []
    stage_and_read(release, "branch", lambda g, r: seen.append(g.argv) or 0, (SUITE,))
    assert seen == [(*SUITE.argv, "tests/test_alone.py")]
    _git(release, "merge", "--abort")


def test_a_gate_that_is_NOT_a_suite_is_never_scoped(release):
    _branch_writes(release, {"src/pkg/alone.py": "OTHER = 3\n"})
    floor = Gate("floor", HOST, ("true",), "the floor")
    seen: list[tuple[str, ...]] = []
    outcome = stage_and_read(release, "branch", lambda g, r: seen.append(g.argv) or 0, (floor,))
    assert seen == [("true",)] and outcome.scope == ()
    _git(release, "merge", "--abort")
