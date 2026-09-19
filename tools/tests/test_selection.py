"""Mirror of `tools/selection.py` (R12): what a change selects, and the audit (`W366`).

⭐ Every clause is asserted BOTH WAYS. The decisions are read against throwaway trees in
`tmp_path`, and the git half — the merge base against the tip, the merge counter — against
real throwaway repositories, never against this module's idea of what git answers.
⛔ No identity is configured anywhere: every commit passes a placeholder per invocation.
"""

from __future__ import annotations

from pathlib import Path

import pytest

import tools.selection as selection_module
from tests.support import assert_package_contract, git, init_repository, run
from tools.selection import (
    SHARED,
    Scope,
    changed_paths,
    decide,
    describe,
    failed_ids,
    merge_number,
    missed,
    select,
)

_IDENTITY = ("-c", "user.name=test", "-c", "user.email=test@example.invalid")

TREE = {
    "src/pkg/__init__.py": "",
    "src/pkg/low.py": "VALUE = 1\n",
    "src/pkg/alone.py": "OTHER = 2\n",
    "src/pkg/style.css": "body {}\n",
    "tests/support.py": "from pathlib import Path\ndef repository_root():\n    return Path()\n",
    "tests/test_low.py": "from pkg.low import VALUE\ndef test_low():\n    assert VALUE\n",
    "tests/test_alone.py": "from pkg.alone import OTHER\ndef test_alone():\n    assert OTHER\n",
    "tests/test_docs.py": (
        "from tests.support import repository_root\n"
        "def test_reads():\n    assert repository_root()\n"
        "def test_pure():\n    assert 1\n"
    ),
}


def _tree(root: Path, files: dict[str, str] = TREE) -> Path:
    for relative, text in files.items():
        (root / relative).parent.mkdir(parents=True, exist_ok=True)
        (root / relative).write_text(text, encoding="utf-8")
    return root


def _git(cwd: Path, *arguments: str) -> str:
    result = run([git(), *_IDENTITY, "-c", "commit.gpgsign=false", *arguments], cwd=cwd)
    assert result.returncode == 0, result.stdout + result.stderr
    return result.stdout.strip()


def _commit_all(cwd: Path, message: str) -> None:
    _git(cwd, "add", "-A")
    _git(cwd, "commit", "-q", "-m", message)


@pytest.fixture
def repository(tmp_path: Path) -> Path:
    """A `release` tip holding `TREE`, and a `branch` cut from it."""
    root = _tree(init_repository(tmp_path / "repo"))
    _git(root, "symbolic-ref", "HEAD", "refs/heads/release")
    _commit_all(root, "base")
    _git(root, "branch", "branch")
    return root


def _on_branch(root: Path, relative: str, text: str) -> None:
    _git(root, "checkout", "-q", "branch")
    (root / relative).parent.mkdir(parents=True, exist_ok=True)
    (root / relative).write_text(text, encoding="utf-8")
    _commit_all(root, relative)
    _git(root, "checkout", "-q", "release")


def test_states_its_contract():
    assert_package_contract(selection_module, "tools.selection")


# --- clause 2: shared machinery selects EVERYTHING -------------------------------------


@pytest.mark.parametrize(
    "path",
    [
        "conftest.py",
        "tests/visual/conftest.py",
        "pyproject.toml",
        "docker/dev/check",
        "tools/quality/size.py",
        "tools/gates.py",
        "tests/fixtures/depth1/a.md",
        "tools/selection.py",
        "tools/testmap.py",
        "tools/treereaders.py",
    ],
)
def test_SHARED_machinery_selects_the_FULL_suite(tmp_path, path):
    scope = select(_tree(tmp_path), [path])
    assert scope.full and "shared machinery" in scope.why[0]


def test_the_row_names_every_shared_prefix_and_the_list_is_the_unit():
    for prefix in ("pyproject.toml", "docker/dev/", "tools/quality/", "tools/gates.py"):
        assert prefix in SHARED, prefix
    assert "tests/fixtures/" in SHARED


def test_a_path_of_UNKNOWN_kind_selects_everything_and_says_so(tmp_path):
    scope = select(_tree(tmp_path), ["workspace.json"])
    assert scope.full and "cannot scope" in scope.why[0]


# --- clause 1: what a path selects when it is not shared --------------------------------


def test_a_DOCUMENT_selects_the_tree_readers_ONLY_and_by_NAME(tmp_path):
    scope = select(_tree(tmp_path), ["docs/tasks/BOARD.md"])
    assert not scope.full
    assert scope.tests == ("tests/test_docs.py::test_reads",)


def test_a_MODULE_selects_its_importers_AND_the_tree_readers_and_nothing_else(tmp_path):
    scope = select(_tree(tmp_path), ["src/pkg/low.py"])
    assert scope.tests == ("tests/test_docs.py::test_reads", "tests/test_low.py")
    assert "tests/test_alone.py" not in scope.tests


def test_PACKAGE_DATA_selects_what_its_packages_modules_select(tmp_path):
    scope = select(_tree(tmp_path), ["src/pkg/style.css"])
    assert {"tests/test_low.py", "tests/test_alone.py"} <= set(scope.tests)


def test_a_file_the_map_takes_WHOLE_is_not_named_again_test_by_test(tmp_path):
    scope = select(_tree(tmp_path), ["tests/test_docs.py"])
    assert scope.tests == ("tests/test_docs.py",)


def test_an_EMPTY_selection_is_the_full_suite_and_never_a_pass(tmp_path):
    # ⛔ Ruling 191: no tree readers, and a module nothing imports — zero tests.
    files = {k: v for k, v in TREE.items() if k != "tests/test_docs.py"}
    scope = select(_tree(tmp_path, files), ["docs/x.md"])
    assert scope.full and "empty" in scope.why[0]


# --- the git half -----------------------------------------------------------------------


def test_the_changed_paths_are_the_BRANCHS_OWN_and_never_the_targets(repository):
    _on_branch(repository, "docs/a.md", "a\n")
    (repository / "src/pkg/alone.py").write_text("OTHER = 3\n", encoding="utf-8")
    _commit_all(repository, "the target moved on")
    assert changed_paths(repository, "branch") == ("docs/a.md",)


def test_a_branch_git_cannot_resolve_is_UNREAD_and_the_scope_is_FULL(repository):
    assert changed_paths(repository, "no-such-branch") is None
    scope = decide(repository, "no-such-branch")
    assert scope.full and "git could not" in scope.why[0]


def test_the_merge_counter_names_the_NEXT_merge(repository):
    assert merge_number(repository) == 1
    _on_branch(repository, "docs/a.md", "a\n")
    _git(repository, "merge", "--no-ff", "-q", "-m", "one", "branch")
    assert merge_number(repository) == 2


# --- clause 4: the cadence --------------------------------------------------------------


def test_the_Nth_merge_AUDITS_and_the_one_before_it_does_NOT(repository):
    _on_branch(repository, "docs/a.md", "a\n")
    targeted = decide(repository, "branch", every=2)
    assert not targeted.full and not targeted.audit
    _git(repository, "merge", "--no-ff", "-q", "-m", "one", "branch")
    _on_branch(repository, "docs/b.md", "b\n")
    audited = decide(repository, "branch", every=2)
    assert audited.full and audited.audit == "merge 2 is a multiple of 2"
    # ⭐ The audit keeps the selection it is auditing.
    assert audited.tests == ("tests/test_docs.py::test_reads",)


def test_a_REQUESTED_full_run_audits_and_says_why(repository):
    _on_branch(repository, "docs/a.md", "a\n")
    scope = decide(repository, "branch", requested="M5 closes", every=1000)
    assert scope.full and scope.audit == "requested: M5 closes"


def test_a_change_that_is_ALREADY_full_is_not_called_an_audit(repository):
    _on_branch(repository, "pyproject.toml", "x\n")
    scope = decide(repository, "branch", requested="M5 closes")
    assert scope.full and not scope.audit


# --- clause 3: the reading SAYS what it selected ----------------------------------------


def test_a_TARGETED_scope_says_it_is_NOT_a_full_reading():
    lines = describe(Scope(False, ("a.py", "b.py::test_x"), 9, ("docs/x.md: a document",)))
    assert "SELECTED" in lines[0] and "NOT a full-suite reading" in lines[0]
    assert "1 whole test file(s) and 1 test(s) named from 1 other(s), of 9" in lines[0]
    assert lines[1] == "  why: docs/x.md: a document"


def test_a_FULL_scope_never_says_selected_and_an_AUDIT_says_what_it_audits():
    assert describe(Scope(True, (), 9, ("x: shared machinery",)))[0] == (
        "scope: FULL — every test file"
    )
    audit = describe(Scope(True, ("a.py",), 9, (), "merge 5 is a multiple of 5"))[0]
    assert audit.startswith("scope: FULL, AUDITING the selection (merge 5 is a multiple of 5)")


def test_a_long_list_of_reasons_is_SUMMARISED_rather_than_dropped():
    why = tuple(f"docs/{n}.md: a document" for n in range(20))
    lines = describe(Scope(False, ("a.py",), 1, why))
    assert lines[-1] == "  why: … and 8 more"


# --- the audit's arithmetic -------------------------------------------------------------


def test_failed_ids_are_read_from_the_short_summary_spaces_in_brackets_included():
    lines = [
        "FAILED tests/test_a.py::test_x - AssertionError: no",
        "ERROR tests/test_b.py - ImportError",
        "FAILED tests/test_c.py::test_y[a b] - x",
        "tests/test_d.py::test_z PASSED",
    ]
    assert failed_ids(lines) == (
        "tests/test_a.py::test_x",
        "tests/test_b.py",
        "tests/test_c.py::test_y[a b]",
    )


def test_a_failure_is_MISSED_only_when_neither_its_file_nor_its_test_was_taken():
    selection = ("tests/test_a.py", "tests/test_b.py::test_named")
    failed = (
        "tests/test_a.py::test_anything",
        "tests/test_b.py::test_named[param]",
        "tests/test_b.py::test_other",
        "tests/test_c.py::test_z",
    )
    assert missed(selection, failed) == ("tests/test_b.py::test_other", "tests/test_c.py::test_z")
