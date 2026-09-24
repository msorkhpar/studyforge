"""Mirror of `tests/harness/treestate.py`: the delta engine, against a real throwaway repository.

⭐ The tooling original's tests, carried with the product's copy, so the suite's exit
condition keeps its assertions and its plants in a checkout with no tooling in it.

⛔ Every assertion here runs `git` in a `tmp_path` repository. A parser tested
against strings the test wrote itself measures the test's idea of porcelain v1,
which is the idea most likely to be wrong.
"""

from __future__ import annotations

import subprocess

import pytest

from tests.harness import treestate
from tests.support import git, init_repository

# ---------------------------------------------------------------------------
# The snapshot
# ---------------------------------------------------------------------------


def test_a_clean_repository_snapshots_empty(tmp_path):
    repository = init_repository(tmp_path)
    assert treestate.snapshot(repository) == {}


def test_a_directory_git_cannot_answer_for_is_none_and_not_empty(tmp_path):
    # ⛔ The distinction the whole check rests on: "clean" and "no answer" are
    # different readings, and a mapping cannot carry the second.
    outside = tmp_path / "not-a-repository"
    outside.mkdir()
    result = subprocess.run(  # noqa: S603 - fixed argv, no shell
        [git(), "status"], cwd=outside, capture_output=True, text=True, check=False
    )
    if result.returncode == 0:  # pragma: no cover - a repository above tmp_path
        pytest.skip("tmp_path sits inside a git repository, so there is nothing git refuses")
    assert treestate.snapshot(outside) is None


def test_an_untracked_file_is_reported_with_its_code(tmp_path):
    repository = init_repository(tmp_path)
    (repository / "alpha").write_text("stray", encoding="utf-8")
    assert treestate.snapshot(repository) == {"alpha": treestate.UNTRACKED}


def test_a_path_with_a_space_survives_the_walk(tmp_path):
    # ⚠️ Why `-z`: the text form quotes this one, and an un-quoting parser is a
    # second implementation of git's escaping rules.
    repository = init_repository(tmp_path)
    (repository / "a file").write_text("stray", encoding="utf-8")
    assert treestate.snapshot(repository) == {"a file": treestate.UNTRACKED}


def test_a_rename_does_not_smear_its_origin_onto_the_next_entry(tmp_path):
    # ⛔ A rename entry spends two NUL fields. If the origin were read as a
    # record of its own, the code of the *following* entry would land on it.
    repository = init_repository(tmp_path)
    (repository / "before.txt").write_text("body", encoding="utf-8")
    subprocess.run([git(), "add", "."], cwd=repository, check=True)  # noqa: S603
    subprocess.run(  # noqa: S603
        [git(), "-c", "user.name=t", "-c", "user.email=t@example.invalid", "commit", "-qm", "x"],
        cwd=repository,
        check=True,
    )
    subprocess.run(  # noqa: S603
        [git(), "mv", "before.txt", "after.txt"], cwd=repository, check=True
    )
    found = treestate.snapshot(repository)
    assert set(found) == {"after.txt"}
    assert "R" in found["after.txt"]


# ---------------------------------------------------------------------------
# The delta — and watch it fire
# ---------------------------------------------------------------------------


def test_a_file_that_appeared_during_the_run_is_the_finding(tmp_path):
    # ⭐ THE PLANT. A run that left a stray file behind, reduced to its shape: a file named
    # `alpha` that was not there when the run began.
    repository = init_repository(tmp_path)
    before = treestate.snapshot(repository)
    (repository / "alpha").write_text("stray", encoding="utf-8")
    moved = treestate.changes(before, treestate.snapshot(repository))
    assert [change.path for change in moved] == ["alpha"]
    assert moved[0].before is None
    assert moved[0].after == treestate.UNTRACKED
    assert "alpha" in treestate.report(moved)


def test_a_nested_stray_is_reported_by_its_file_and_not_its_directory(tmp_path):
    # ⭐ The nested shape: `alpha/alpha`. ⚠️ git names the *directory* for an
    # untracked tree unless `-uall` is passed, which is why it is passed.
    repository = init_repository(tmp_path)
    before = treestate.snapshot(repository)
    (repository / "alpha").mkdir()
    (repository / "alpha" / "alpha").write_text("stray", encoding="utf-8")
    moved = treestate.changes(before, treestate.snapshot(repository))
    assert [change.path for change in moved] == ["alpha/alpha"]


def test_a_file_that_was_already_dirty_before_the_run_is_not_a_finding(tmp_path):
    # ⛔ The false-positive this design exists to avoid: a contributor runs the
    # suite with edits in flight, and that is not a defect of the suite.
    repository = init_repository(tmp_path)
    (repository / "work-in-progress.py").write_text("edits", encoding="utf-8")
    before = treestate.snapshot(repository)
    moved = treestate.changes(before, treestate.snapshot(repository))
    assert moved == []


def test_a_file_edited_during_the_run_is_a_finding_even_though_it_existed(tmp_path):
    # ⭐ The other half: appearing is not the only way to dirty a tree.
    repository = init_repository(tmp_path)
    (repository / "alpha").write_text("one", encoding="utf-8")
    subprocess.run([git(), "add", "."], cwd=repository, check=True)  # noqa: S603
    before = treestate.snapshot(repository)
    (repository / "alpha").write_text("two", encoding="utf-8")
    moved = treestate.changes(before, treestate.snapshot(repository))
    assert [change.path for change in moved] == ["alpha"]


def test_a_missing_snapshot_propagates_rather_than_reading_as_clean(tmp_path):
    del tmp_path
    assert treestate.changes(None, {}) is None
    assert treestate.changes({}, None) is None


def test_an_ignored_path_is_the_stated_blind_spot(tmp_path):
    # ⚠️ Asserted rather than described. `--ignored` is not passed because
    # `__pycache__/` moves on every run; the price is this, and it is paid
    # knowingly.
    repository = init_repository(tmp_path)
    (repository / ".gitignore").write_text("noise/\n", encoding="utf-8")
    subprocess.run([git(), "add", ".gitignore"], cwd=repository, check=True)  # noqa: S603
    before = treestate.snapshot(repository)
    (repository / "noise").mkdir()
    (repository / "noise" / "stray").write_text("x", encoding="utf-8")
    assert treestate.changes(before, treestate.snapshot(repository)) == []


# ---------------------------------------------------------------------------
# The one exemption
# ---------------------------------------------------------------------------


def test_a_capture_directory_inside_the_checkout_is_exempt(tmp_path):
    captures = tmp_path / "captures"
    prefixes = treestate.exempt_prefixes(tmp_path, {treestate.CAPTURE_VARIABLE: str(captures)})
    assert prefixes == ("captures/",)
    before = {"captures/one.png": treestate.UNTRACKED}
    assert treestate.changes({}, before, prefixes) == []
    assert treestate.changes({}, {"elsewhere.png": treestate.UNTRACKED}, prefixes) != []


def test_an_unset_or_outside_capture_directory_exempts_nothing(tmp_path):
    assert treestate.exempt_prefixes(tmp_path, {}) == ()
    assert treestate.exempt_prefixes(tmp_path, {treestate.CAPTURE_VARIABLE: "  "}) == ()
    assert treestate.exempt_prefixes(tmp_path, {treestate.CAPTURE_VARIABLE: "/elsewhere"}) == ()
