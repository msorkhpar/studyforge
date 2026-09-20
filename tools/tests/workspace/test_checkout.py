"""Mirror of `tools/workspace/checkout.py` (R12), and `W402`'s own control.

⛔ **Synthetic repositories only** (`support`). The measured incident was a real
sibling left in an abandoned merge, and dirtying a real sibling to reproduce it
would break every other office's gate — so every state asserted here is built
with `git init` in `tmp_path`, where a merge conflict and a stopped rebase are
a few commands each.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from tools.tests.workspace import support
from tools.workspace import git, read, record, render, verify
from tools.workspace.__main__ import DISAGREES, VERIFIED, main
from tools.workspace.checkout import NAMED, uncommitted


def repin(root: Path, here: Path) -> None:
    """Re-record the pin, so the WORKING TREE is the only thing under test.

    ⚠️ Several of these fixtures have to commit in a sibling to set a state up
    — a branch to conflict with, an ignore file to be ignored by. Without this,
    every such test would also be asserting the stale-pin finding, and the
    control for *"the pin is fine and the tree is not"* would not exist.
    """
    (here / "workspace.json").write_text(render(record(root, here)), encoding="utf-8")


def conflicted_merge(directory: Path) -> None:
    """Leave this checkout in an abandoned conflicted merge — the incident."""
    support.run(directory, "checkout", "-q", "-b", "side")
    support.commit(directory, "theirs")
    support.run(directory, "checkout", "-q", "main")
    support.commit(directory, "ours")
    subprocess.run(
        ["git", "-C", str(directory), *support.AUTHOR, "merge", "--no-edit", "side"],
        capture_output=True,
        check=False,
    )


def said(findings: list[str], fragment: str) -> list[str]:
    """Every finding carrying `fragment` — asserted on, so a miss prints them all."""
    return [finding for finding in findings if fragment in finding]


# --------------------------------------------------------------------------
# ⭐ R12 both ways — a clean checkout at its pin is still green
# --------------------------------------------------------------------------


def test_a_clean_workspace_at_its_pin_still_verifies_clean(tmp_path):
    # ⛔ The control this row is most able to break: the new question is asked
    # of every sibling on every run, so a false positive here is a gate the
    # register reads as red every round.
    root, here = support.workspace(tmp_path / "w")
    assert verify(root, here) == []
    assert main(["verify", "--root", str(here), "--workspace", str(root)]) == VERIFIED


def test_a_clean_sibling_reports_no_state_of_its_own(tmp_path):
    root, _ = support.workspace(tmp_path / "w")
    assert uncommitted(root / "Alpha", git) == []


# --------------------------------------------------------------------------
# ⛔ clause 1 — a dirty checkout fails, naming the component and what is uncommitted
# --------------------------------------------------------------------------


def test_a_sibling_with_a_modified_tracked_file_is_named(tmp_path):
    root, here = support.workspace(tmp_path / "w")
    (root / "Alpha" / "file.txt").write_text("edited", encoding="utf-8")
    found = verify(root, here)
    assert said(found, "Alpha: ") == found, found
    assert said(found, "modified and not staged"), found
    assert said(found, "file.txt"), found


def test_a_sibling_with_work_staged_and_not_committed_is_named(tmp_path):
    # ⛔ **The half of the incident that carried the whole task.** Every file of
    # a task staged and none committed: `HEAD` is exactly the pinned commit, so
    # everything else this tool reads says the workspace is reproducible.
    root, here = support.workspace(tmp_path / "w")
    (root / "Alpha" / "added.py").write_text("x = 1\n", encoding="utf-8")
    support.run(root / "Alpha", "add", "added.py")
    found = verify(root, here)
    assert said(found, "staged and not committed"), found
    assert said(found, "added.py"), found
    assert support.run(root / "Alpha", "rev-parse", "HEAD") == _pinned(here, "Alpha")


def test_a_sibling_with_an_untracked_file_is_named(tmp_path):
    # ⭐ The decision, asserted rather than argued: untracked-but-not-ignored is
    # dirt. A module nobody added is work on no ref, and nothing else sees it.
    root, here = support.workspace(tmp_path / "w")
    (root / "Beta" / "new_module.py").write_text("x = 1\n", encoding="utf-8")
    found = verify(root, here)
    assert said(found, "untracked and not ignored"), found
    assert said(found, "new_module.py"), found


def test_an_ignored_file_is_not_dirt(tmp_path):
    # ⭐ The other half of that decision, and it is what keeps the check usable:
    # `.scratch/`, `__pycache__/` and generated artifacts are what an ignore
    # file is for, and the ignore file is where that decision already lives.
    root, here = support.workspace(tmp_path / "w")
    alpha = root / "Alpha"
    (alpha / ".gitignore").write_text("junk/\n", encoding="utf-8")
    support.run(alpha, "add", ".gitignore")
    support.run(alpha, "commit", "-qm", "ignore junk")
    repin(root, here)
    (alpha / "junk").mkdir()
    (alpha / "junk" / "log.txt").write_text("noise", encoding="utf-8")
    assert verify(root, here) == []


def test_a_dirty_sibling_at_its_pin_exits_one_and_names_the_component(tmp_path, capsys):
    # ⛔ **The incident, as the command a person runs.** It read exit 0.
    root, here = support.workspace(tmp_path / "w")
    (root / "Alpha" / "file.txt").write_text("edited", encoding="utf-8")
    assert main(["verify", "--root", str(here), "--workspace", str(root)]) == DISAGREES
    assert "Alpha" in capsys.readouterr().err


def test_a_sibling_wrong_in_both_ways_is_named_for_both(tmp_path):
    # ⚠️ Two questions, not one: the tree is checked IN ADDITION to the pin
    # comparison, so a component off its pin AND dirty does not hide either.
    root, here = support.workspace(tmp_path / "w")
    support.commit(root / "Beta", "moved")
    (root / "Beta" / "loose.txt").write_text("x", encoding="utf-8")
    found = verify(root, here)
    assert said(found, "untracked and not ignored"), found
    assert said(found, "advance the pin or check the component out"), found


# --------------------------------------------------------------------------
# ⛔ clause 2 — mid-merge, mid-rebase and a conflicted path are each NAMED
# --------------------------------------------------------------------------


def test_an_abandoned_merge_names_the_merge_and_the_conflicted_path_separately(tmp_path):
    # ⛔ **Exactly the measured state**: a merge head present, one path left
    # unmerged, and `HEAD` on a commit — so every `rev-parse` reading is fine.
    root, here = support.workspace(tmp_path / "w")
    conflicted_merge(root / "Alpha")
    repin(root, here)
    found = verify(root, here)
    assert said(found, "a merge is in progress (MERGE_HEAD)"), found
    assert said(found, "conflicted and unresolved"), found
    assert said(found, "file.txt"), found
    # ⭐ Named separately, never folded into one word: they are two repairs.
    assert said(found, "MERGE_HEAD") != said(found, "conflicted and unresolved")


def test_a_stopped_rebase_is_named_as_a_rebase(tmp_path):
    # ⚠️ A stopped rebase detaches `HEAD`, so the pin disagrees too — asserted
    # by presence rather than by count, because both findings are correct.
    root, here = support.workspace(tmp_path / "w")
    alpha = root / "Alpha"
    support.run(alpha, "checkout", "-q", "-b", "side")
    support.commit(alpha, "theirs")
    support.run(alpha, "checkout", "-q", "main")
    support.commit(alpha, "ours")
    subprocess.run(
        ["git", "-C", str(alpha), *support.AUTHOR, "rebase", "side"],
        capture_output=True,
        check=False,
    )
    found = verify(root, here)
    assert said(found, "a rebase is in progress"), found


@pytest.mark.parametrize(
    ("marker", "fragment"),
    [
        ("MERGE_HEAD", "a merge is in progress (MERGE_HEAD)"),
        ("CHERRY_PICK_HEAD", "a cherry-pick is in progress (CHERRY_PICK_HEAD)"),
        ("REVERT_HEAD", "a revert is in progress (REVERT_HEAD)"),
        ("rebase-merge", "a rebase is in progress (rebase-merge)"),
        ("rebase-apply", "a rebase is in progress (rebase-apply)"),
    ],
)
def test_every_unfinished_operation_git_can_leave_behind_is_named(tmp_path, marker, fragment):
    # ⭐ Driven through the runner seam rather than through five real conflicts:
    # the marker IS the state, and this asserts all five without five fixtures.
    git_dir = tmp_path / "gitdir"
    git_dir.mkdir()
    if marker.startswith("rebase"):
        (git_dir / marker).mkdir()
    else:
        (git_dir / marker).touch()
    found = uncommitted(tmp_path, _runner({"rev-parse": str(git_dir), "status": ""}))
    assert found == [fragment]


# --------------------------------------------------------------------------
# ⛔ `self` is exempt — the decision, asserted so it is not only prose
# --------------------------------------------------------------------------


def test_a_dirty_self_checkout_is_not_a_finding(tmp_path):
    # ⭐ Argued in `checkout.py`: `self` is the tree the reader is standing in
    # and editing, and `record` itself writes an uncommitted pin file — so the
    # normal working state would make a gate that runs every round always red.
    root, here = support.workspace(tmp_path / "w")
    (here / "file.txt").write_text("edited", encoding="utf-8")
    (here / "untracked.py").write_text("x = 1\n", encoding="utf-8")
    assert verify(root, here) == []


def test_the_exemption_is_the_row_and_not_the_directory(tmp_path):
    # ⚠️ The control that catches the exemption being written as "skip the
    # first row" or "skip whatever `--root` points at": the same tree, read
    # through a `sibling` row, IS checked.
    root, here = support.workspace(tmp_path / "w")
    (root / "Alpha" / "loose.txt").write_text("x", encoding="utf-8")
    assert said(verify(root, here), "Alpha: ")


# --------------------------------------------------------------------------
# ⭐ the porcelain parse, asserted directly
# --------------------------------------------------------------------------


def _pinned(here: Path, name: str) -> str:
    """The commit the pin file records for `name` — read through the contract."""
    return [c.commit for c in read(here) if c.name == name][0]


def _runner(answers: dict[str, str]):
    """A fake `git`, keyed on the subcommand, so a parse is asserted without a repository."""

    def run(directory, *arguments):
        return subprocess.CompletedProcess(
            args=arguments, returncode=0, stdout=answers.get(arguments[0], ""), stderr=""
        )

    return run


def _parse(status: str) -> list[str]:
    """Run `uncommitted` over one porcelain answer and no unfinished operation."""
    return uncommitted(Path("."), _runner({"rev-parse": "", "status": status}))


def test_a_path_staged_and_modified_at_once_lands_in_both_repairs():
    # ⚠️ `MM` is one path needing two things done to it, and a bucket that
    # claimed it once would name the wrong repair half the time.
    found = _parse("MM file.txt\0")
    assert said(found, "staged and not committed"), found
    assert said(found, "modified and not staged"), found


def test_a_rename_names_its_destination_once_and_not_its_source():
    # ⛔ `-z` writes a rename's source as a SECOND field. Counted, it would
    # double every rename and name a path that no longer exists.
    found = _parse("R  new.py\0old.py\0")
    assert found == ["1 path(s) staged and not committed: new.py"]


def test_a_path_holding_a_newline_survives_the_parse():
    # ⭐ Why `-z` rather than the quoted form: the non-`-z` output escapes this
    # into a shape that would have to be un-escaped here, by hand.
    found = _parse("?? odd\nname.txt\0")
    assert found == ["1 path(s) untracked and not ignored: odd\nname.txt"]


def test_every_unmerged_code_reads_as_conflicted():
    for code in ("UU", "AA", "DD", "AU", "UD"):
        assert said(_parse(f"{code} file.txt\0"), "conflicted and unresolved"), code


def test_the_count_is_printed_so_the_cap_cannot_read_as_the_total():
    # ⛔ A finding that named three paths and stopped would read as "that is
    # all there was", which is the shape of every under-report this project has
    # had to correct.
    status = "".join(f"?? file{index}.txt\0" for index in range(NAMED + 2))
    found = _parse(status)
    assert found == [
        f"{NAMED + 2} path(s) untracked and not ignored: "
        + ", ".join(f"file{index}.txt" for index in range(NAMED))
        + ", and 2 more"
    ]


def test_a_directory_that_is_not_a_checkout_reports_nothing():
    # ⚠️ `verify` already says "no checkout found beside this repository"; a
    # second finding saying the same thing differently is noise.
    def refuses(directory, *arguments):
        return subprocess.CompletedProcess(args=arguments, returncode=128, stdout="", stderr="")

    assert uncommitted(Path("."), refuses) == []
