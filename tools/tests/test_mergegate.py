"""Mirror of `tools/mergegate.py` (R12), asserted in BOTH directions and against a real git.

⛔ **Every tree here is a throwaway repository in `tmp_path`.** A merge gate tested against
strings would measure this module's idea of `git merge --no-commit`, which is the idea most
likely to be wrong — and the whole row turns on what `--no-commit` and `--abort` actually do.

⛔ **NO TEST CALLS DOCKER**, and one asserts it: the real `GATES` name `docker/dev/check`,
so every reading here is taken through an injected runner, and a stub on `PATH` proves the
daemon was never reached.

⭐ **The row's two load-bearing properties are asserted directly** — the gates read the
MERGED tree rather than `HEAD`, and a red reading leaves the tree exactly where it started.
"""

from __future__ import annotations

import os
import stat
from pathlib import Path

import pytest

import tools.mergegate as mergegate_module
from tests.support import assert_package_contract, git, init_repository, repository_root, run
from tools.mergegate import (
    GATES,
    HOST,
    IMAGE,
    MERGED,
    REFUSED,
    UNREAD,
    Gate,
    main,
    render,
    stage_and_read,
)
from tools.quality import CHECKS, NOTICES

#: ⛔ A per-invocation placeholder identity. Nothing is configured, and no name is real.
_IDENTITY = ("-c", "user.name=test", "-c", "user.email=test@example.invalid")

#: The file the branch adds. ⭐ It exists ONLY on the merged tree, which is what makes it a
#: discriminator between reading the merge and reading `HEAD`.
BRANCH_FILE = "from-the-branch.txt"

#: ⛔ `W308`: a FABRICATED stand-in for a real, configured MACHINE identity — the shape a
#: REGISTER round's own commits carry. It names nobody, and its domain carries NO DOT, so the
#: floor's own email shape cannot match it (R7). ⭐ The standing ruling PERMITS this on a
#: local commit, so the gate never refuses it.
_MACHINE = ("-c", "user.name=Jane Doe", "-c", "user.email=jane.doe@workstation")

#: ⛔ A SECOND office. The `release` fixture's own commits are `test <test@example.invalid>`,
#: so one of these on `branch` is TWO office identities in one merge — the row's subject.
_OTHER_OFFICE = ("-c", "user.name=dev9", "-c", "user.email=dev9@example.invalid")


def _git(cwd: Path, *arguments: str) -> str:
    result = run([git(), *_IDENTITY, "-c", "commit.gpgsign=false", *arguments], cwd=cwd)
    assert result.returncode == 0, result.stdout + result.stderr
    return result.stdout.strip()


def _commit(cwd: Path, name: str, body: str = "") -> str:
    (cwd / name).write_text(body or f"{name}\n", encoding="utf-8")
    _git(cwd, "add", name)
    _git(cwd, "commit", "-q", "-m", name)
    return _git(cwd, "rev-parse", "HEAD")


def _commit_as(cwd: Path, identity: tuple[str, ...], name: str) -> None:
    """Commit `name` under `identity`, passed PER INVOCATION and configured nowhere."""
    (cwd / name).write_text(f"{name}\n", encoding="utf-8")
    _git(cwd, "add", name)
    result = run([git(), *identity, "-c", "commit.gpgsign=false", "commit", "-q", "-m", name], cwd)
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.fixture
def release(tmp_path: Path) -> Path:
    """A release checkout at a clean tip, with an unmerged `branch` adding one file."""
    root = init_repository(tmp_path / "release")
    # ⛔ Configured in THIS THROWAWAY repository's OWN config, never in a shared one.
    #    `tools.mergegate` runs `git merge` and `git commit` ITSELF, so a `-c` on the
    #    test's own invocations cannot reach them. ⚠️ MEASURED: the pinned image configures
    #    NO identity (`git config --get user.name` exits 1), so without this every merge
    #    here passes on the host and fails in the image — this row's own defect, wearing a
    #    test. ⭐ Both halves are placeholders and name nobody (R7).
    _git(root, "config", "user.name", "test")
    _git(root, "config", "user.email", "test@example.invalid")
    _git(root, "symbolic-ref", "HEAD", "refs/heads/release")
    _commit(root, "base.txt")
    _git(root, "checkout", "-q", "-b", "branch")
    _commit(root, BRANCH_FILE)
    _git(root, "checkout", "-q", "release")
    _commit(root, "moved.txt")
    return root


def _green(gate: Gate, root: Path) -> int:
    return 0


def _red(gate: Gate, root: Path) -> int:
    return 1


ONE_GATE = (Gate("probe", HOST, ("true",), "the mirror's own gate"),)


# --- the contract, and that it is a COMMAND ------------------------------------------


def test_states_its_contract():
    assert_package_contract(mergegate_module, "tools.mergegate")


def test_it_is_a_COMMAND_and_not_a_floor_check():
    # ⛔ Ruling 80: a floor check may not read a branch position. The argument is in the
    #    module docstring; this is what stops somebody wiring it in anyway.
    registered = {function.__module__ for function in (*CHECKS, *NOTICES)}
    assert "tools.mergegate" not in registered


def test_it_reads_NO_HISTORY(tmp_path):
    # ⛔ Clause 4: the gate reads the tree being merged, never landed tips. A report over
    #    frozen tips is a backlog no office may clear.
    # ⚠️ `W308`'s authorship read is BOUNDED to `HEAD..<branch>` and lives in
    #    `tools/authorship.py`, so THIS file stays clear of every history verb below. ⛔ The
    #    bound is not claimed by grepping the sibling — it is asserted BEHAVIOURALLY, by a
    #    plant, in `test_W308_a_foreign_author_line_ALREADY_LANDED_does_not_refuse`.
    source = (repository_root() / "tools/mergegate.py").read_text(encoding="utf-8")
    for verb in ('"log"', '"rev-list"', '"shortlog"', '"blame"'):
        assert verb not in source, f"the gate reads history through {verb}"


# --- the declared pair -----------------------------------------------------------------


def test_BOTH_environments_are_declared_and_the_list_is_inhabited():
    # ⛔ Ruling 191: an empty population is never the pass reading, so the pair is asserted
    #    to be inhabited rather than assumed.
    assert GATES, "no gate is declared"
    assert {gate.environment for gate in GATES} == {IMAGE, HOST}


def test_every_image_gate_runs_through_the_PINNED_WRAPPER_and_the_host_gate_does_not():
    # ⛔ `docker/dev/check` is the only spelling of the pinned environment this repository
    #    has (Ruling 238): a bare `pytest` in an image slot would silently be a host reading.
    for gate in GATES:
        runs_wrapper = gate.argv[0] == "docker/dev/check"
        assert runs_wrapper == (gate.environment == IMAGE), gate


def test_every_gate_says_what_only_it_can_answer():
    # ⚠️ This is what makes removing one visibly a removed READING rather than a tidier list.
    for gate in GATES:
        assert len(gate.answers) > 20, gate


def test_the_image_suite_is_what_carries_the_lint_enforcement():
    # ⛔ Ruling 78 puts enforcement in tests/test_repository.py, which the host SKIPS. The
    #    gate never restates a lint rule and names no linter binary — it runs the suite.
    suite = next(g for g in GATES if g.environment == IMAGE and g.name == "suite")
    assert "ruff" in suite.answers
    assert "ruff" not in " ".join(suite.argv)


# --- clause 1: the gates read the MERGED tree, never HEAD ------------------------------


def test_the_gate_reads_the_MERGED_tree_and_a_HEAD_reading_would_have_PASSED_it(release):
    # ⛔ THE ROW'S FIRST PROPERTY. Most of `PO-92/1`'s population ARRIVED WITH CARRIERS, so a
    #    HEAD-side reading would have passed every one of them. This gate refuses only what
    #    the merge introduces, and `HEAD` does not carry it.
    assert not (release / BRANCH_FILE).exists(), "the file must not be on the release tip"
    seen: list[bool] = []

    def refuse_what_the_branch_adds(gate: Gate, root: Path) -> int:
        seen.append((root / BRANCH_FILE).exists())
        return 1 if (root / BRANCH_FILE).exists() else 0

    outcome = stage_and_read(release, "branch", refuse_what_the_branch_adds, ONE_GATE)
    assert seen == [True], "the gate did not see the merged tree"
    assert outcome.verdict == REFUSED


# --- clause 3, both ways: a deviation is refused, a clean tree passes -------------------


def test_a_GREEN_reading_leaves_the_merge_STAGED_and_commits_nothing_by_itself(release):
    tip = _git(release, "rev-parse", "HEAD")
    outcome = stage_and_read(release, "branch", _green, ONE_GATE)
    assert outcome.verdict == MERGED
    assert all(reading.green for reading in outcome.readings)
    # ⭐ Staged, not committed: `stage_and_read` never makes a commit, so the caller decides.
    assert _git(release, "rev-parse", "HEAD") == tip
    assert (release / BRANCH_FILE).exists()


def test_a_RED_reading_commits_NOTHING_and_the_tree_is_restored_EXACTLY(release):
    tip = _git(release, "rev-parse", "HEAD")
    outcome = stage_and_read(release, "branch", _red, ONE_GATE)
    assert outcome.verdict == REFUSED
    assert outcome.restored is True
    # ⛔ The restore is verified BY READING THE TREE, never by the abort's own exit code.
    assert _git(release, "rev-parse", "HEAD") == tip
    assert _git(release, "status", "--porcelain", "--untracked-files=no") == ""
    assert not (release / BRANCH_FILE).exists(), "the merged content survived the abort"


def test_a_RED_gate_STOPS_the_run_and_the_gates_NOT_TAKEN_are_NAMED(release):
    # ⭐ A refusal is complete at the first red, so the rest is spent time that cannot
    #    change the answer. ⛔ But an untaken gate is NAMED: a shorter list must never be
    #    confusable with a list that all passed.
    taken: list[str] = []

    def refuse_the_first(gate: Gate, root: Path) -> int:
        taken.append(gate.name)
        return 1 if gate.name == "first" else 0

    gates = (
        Gate("first", IMAGE, ("true",), "the mirror's first gate"),
        Gate("second", HOST, ("true",), "the mirror's second gate"),
    )
    outcome = stage_and_read(release, "branch", refuse_the_first, gates)
    assert taken == ["first"], "a gate after the refusal was still taken"
    # ⛔ The untaken gate carries its ENVIRONMENT: the shipped GATES hold two gates named
    #    `suite`, so a bare name cannot say which reading was not taken (Ruling 326).
    assert outcome.not_taken == (f"second [{HOST}]",)
    assert outcome.verdict == REFUSED
    assert "NOT TAKEN" in "\n".join(render(outcome))
    assert _git(release, "status", "--porcelain", "--untracked-files=no") == ""


def test_ONE_red_gate_among_green_ones_still_refuses(release):
    def only_the_last_refuses(gate: Gate, root: Path) -> int:
        return 1 if gate.name == "second" else 0

    gates = (
        Gate("first", HOST, ("true",), "the mirror's first gate"),
        Gate("second", IMAGE, ("true",), "the mirror's second gate"),
    )
    outcome = stage_and_read(release, "branch", only_the_last_refuses, gates)
    assert outcome.verdict == REFUSED
    assert [r.gate.name for r in outcome.red] == ["second"]
    assert _git(release, "status", "--porcelain", "--untracked-files=no") == ""


# --- the third state: nothing read is never a pass -------------------------------------


def test_an_EMPTY_gate_list_is_UNREAD_and_never_MERGED(release):
    # ⛔ Ruling 191 in its own shape: a run that read no gate must not return the pass code.
    outcome = stage_and_read(release, "branch", _green, ())
    assert outcome.verdict == UNREAD
    assert "no gate is declared" in render(outcome)[0]


def test_a_DIRTY_tracked_tree_is_UNREAD_and_no_merge_is_attempted(release):
    (release / "base.txt").write_text("edited\n", encoding="utf-8")
    outcome = stage_and_read(release, "branch", _green, ONE_GATE)
    assert outcome.verdict == UNREAD
    assert not (release / BRANCH_FILE).exists(), "a merge was staged over uncommitted work"


def test_a_git_with_NO_COMMITTER_IDENTITY_is_UNREAD_and_NAMES_that(release, monkeypatch):
    # ⛔ MEASURED: the pinned image configures NO identity at all, so a gate that did not ask
    #    reported a mysterious staging failure instead of the cause. ⭐ Both ways, because a
    #    synthesised control owes its own positive row (Ruling 191(c)).
    real = mergegate_module._git

    def without_identity(root, *arguments):
        if arguments[:2] == ("var", "GIT_COMMITTER_IDENT"):
            return 1, ""
        return real(root, *arguments)

    monkeypatch.setattr(mergegate_module, "_git", without_identity)
    outcome = stage_and_read(release, "branch", _green, ONE_GATE)
    assert outcome.verdict == UNREAD
    assert "no committer identity" in render(outcome)[0]
    assert not (release / BRANCH_FILE).exists(), "a merge was staged with no committer"

    # ⭐ THE POSITIVE ROW: with git's own answer restored, the very same call proceeds.
    monkeypatch.undo()
    assert stage_and_read(release, "branch", _green, ONE_GATE).verdict == MERGED
    _git(release, "merge", "--abort")


def test_a_tree_git_cannot_read_is_UNREAD(tmp_path):
    outcome = stage_and_read(tmp_path, "branch", _green, ONE_GATE)
    assert outcome.verdict == UNREAD


def test_a_branch_that_does_not_MERGE_CLEANLY_is_UNREAD_and_the_tree_is_left_clean(release):
    _git(release, "checkout", "-q", "-b", "conflicting", "branch")
    _commit(release, "moved.txt", "the branch's own body\n")
    _git(release, "checkout", "-q", "release")
    tip = _git(release, "rev-parse", "HEAD")
    outcome = stage_and_read(release, "conflicting", _green, ONE_GATE)
    assert outcome.verdict == UNREAD
    assert _git(release, "rev-parse", "HEAD") == tip
    assert _git(release, "status", "--porcelain", "--untracked-files=no") == ""


def test_an_UNVERIFIABLE_restore_is_UNREAD_rather_than_a_clean_REFUSAL(release, monkeypatch):
    # ⛔ Ruling 287: a restore whose result nobody read is not a restore. A refusal that
    #    cannot prove the tree is back must not read as the ordinary red.
    real = mergegate_module._git

    def lying_git(root, *arguments):
        if arguments[:1] == ("merge",) and "--abort" in arguments:
            return 0, ""  # the abort "succeeds" and changes nothing
        return real(root, *arguments)

    monkeypatch.setattr(mergegate_module, "_git", lying_git)
    outcome = stage_and_read(release, "branch", _red, ONE_GATE)
    assert outcome.restored is False
    assert outcome.verdict == UNREAD
    assert "THE RESTORE COULD NOT BE VERIFIED" in "\n".join(render(outcome))
    monkeypatch.undo()
    _git(release, "merge", "--abort")


# --- what the reading says -------------------------------------------------------------


def test_every_printed_reading_NAMES_ITS_ENVIRONMENT(release):
    # ⛔ Ruling 326: a reading is quoted with its environment or it is not a measurement.
    outcome = stage_and_read(release, "branch", _green, GATES[:1])
    printed = "\n".join(render(outcome))
    assert IMAGE in printed
    assert "on the MERGED tree, never on HEAD" in printed


def test_a_refusal_NAMES_THE_GATE_and_says_nothing_was_committed(release):
    outcome = stage_and_read(release, "branch", _red, ONE_GATE)
    printed = "\n".join(render(outcome))
    assert "⛔ REFUSED: probe [host]" in printed
    assert "nothing was committed" in printed
    assert "⭐ RESTORED" in printed


# --- `W308`: WHO WROTE the commits this merge introduces --------------------------------


def _plant_a_second_office(release: Path) -> None:
    """Put one commit by a SECOND office on `branch`, and go back to the release tip."""
    _git(release, "checkout", "-q", "branch")
    _commit_as(release, _OTHER_OFFICE, "planted.txt")
    _git(release, "checkout", "-q", "release")


def test_W308_a_SECOND_OFFICE_on_the_carrier_is_REFUSED_BEFORE_anything_is_staged(release):
    # ⛔ The refusal is free: no merge was staged, so there is no tree to restore and no
    #    gate was spent. ⭐ The population is asserted INHABITED first (Ruling 191).
    _plant_a_second_office(release)
    outcome = stage_and_read(release, "branch", _green, ONE_GATE)
    assert outcome.authorship.population == 2, "the plant did not take"
    assert outcome.authorship.offices == 2
    assert outcome.verdict == REFUSED
    assert len(outcome.authorship.crossed) == 1
    assert outcome.readings == (), "a gate was run after authorship had already refused"
    assert not (release / BRANCH_FILE).exists(), "a merge was staged over a refused carrier"
    assert _git(release, "status", "--porcelain", "--untracked-files=no") == ""


def test_W308_the_refusal_NAMES_THE_COMMIT_and_never_the_identity(release):
    _plant_a_second_office(release)
    outcome = stage_and_read(release, "branch", _green, ONE_GATE)
    printed = "\n".join(render(outcome))
    assert outcome.authorship.crossed[0] in printed
    # ⚠️ The identifying halves — both offices' names — must not appear. ⭐ The reserved
    #    DOMAIN does, in the generic remedy template `<office>@example.invalid`, which is a
    #    form rather than anybody's address.
    for value in ("dev9", "test@"):
        assert value not in printed, "the merge gate printed the author line it refused"


def test_W308_a_REGISTER_merge_under_a_REAL_identity_PASSES(release):
    # ⛔ THE DIRECTION THAT MUST NOT INVERT, and the one the first form of this gate got
    #    wrong: a round branch's own commits are the coordinator's, under the machine's real
    #    identity, which the standing ruling PERMITS because nothing is ever pushed.
    #    ⚠️ Refusing this would wedge the merge path — the repair for `mergegate` could not
    #    itself be merged through `mergegate`.
    _git(release, "checkout", "-q", "-b", "chore/round")
    _commit_as(release, _MACHINE, "round.txt")
    _git(release, "checkout", "-q", "release")
    outcome = stage_and_read(release, "chore/round", _green, ONE_GATE)
    assert outcome.authorship.population == 1, "the round is empty, so its green says nothing"
    assert outcome.authorship.offices == 0, "a person's line was counted as an office's"
    assert outcome.verdict == MERGED
    _git(release, "merge", "--abort")


def test_W308_a_second_office_ALREADY_LANDED_does_not_refuse(release):
    # ⛔ The gate is not a report over landed tips: a backlog no office may clear.
    _commit_as(release, _OTHER_OFFICE, "landed.txt")
    outcome = stage_and_read(release, "branch", _green, ONE_GATE)
    assert outcome.authorship.population == 1, "the release line entered the population"
    assert outcome.verdict == MERGED
    _git(release, "merge", "--abort")


def test_W308_a_branch_that_INTRODUCES_NOTHING_is_UNREAD_and_never_MERGED(release):
    # ⛔ Ruling 191: a gate that read no commit must not return the pass code.
    _git(release, "checkout", "-q", "-b", "nothing-new")
    _git(release, "checkout", "-q", "release")
    outcome = stage_and_read(release, "nothing-new", _green, ONE_GATE)
    assert outcome.verdict == UNREAD
    assert "introduces no commit" in render(outcome)[0]
    assert not (release / BRANCH_FILE).exists()


def test_W308_a_GREEN_run_still_PRINTS_what_authorship_read(release):
    # ⛔ FND-07's rule: "nothing was printed" and "there was nothing to say" must not be the
    #    same line. A silent authorship gate is indistinguishable from an absent one.
    outcome = stage_and_read(release, "branch", _green, ONE_GATE)
    printed = "\n".join(render(outcome))
    assert "authorship: 1 commit(s)" in printed
    assert "ONE OFFICE AT MOST" in printed
    _git(release, "merge", "--abort")


# --- the command -----------------------------------------------------------------------


def test_the_COMMAND_commits_a_green_merge_with_the_body_it_is_given(release, tmp_path, capsys):
    body = tmp_path / "body.txt"
    body.write_text("Merge branch (W302): the gate is a tree artifact\n", encoding="utf-8")
    monkey = _stub_runner(_green)
    tip = _git(release, "rev-parse", "HEAD")
    try:
        assert main(["branch", "--body", str(body), "--root", str(release)]) == MERGED
    finally:
        monkey()
    capsys.readouterr()
    assert _git(release, "rev-parse", "HEAD") != tip
    assert _git(release, "log", "-1", "--format=%s") == (
        "Merge branch (W302): the gate is a tree artifact"
    )
    assert len(_git(release, "rev-list", "--parents", "-n", "1", "HEAD").split()) == 3


def test_the_COMMAND_returns_REFUSED_and_commits_nothing_on_a_red_gate(release, tmp_path, capsys):
    body = tmp_path / "body.txt"
    body.write_text("Merge branch (W302): refused\n", encoding="utf-8")
    tip = _git(release, "rev-parse", "HEAD")
    monkey = _stub_runner(_red)
    try:
        assert main(["branch", "--body", str(body), "--root", str(release)]) == REFUSED
    finally:
        monkey()
    capsys.readouterr()
    assert _git(release, "rev-parse", "HEAD") == tip


def test_STAGE_ONLY_leaves_a_green_merge_uncommitted(release, capsys):
    tip = _git(release, "rev-parse", "HEAD")
    monkey = _stub_runner(_green)
    try:
        assert main(["branch", "--stage-only", "--root", str(release)]) == MERGED
    finally:
        monkey()
    capsys.readouterr()
    assert _git(release, "rev-parse", "HEAD") == tip
    assert (release / BRANCH_FILE).exists()
    _git(release, "merge", "--abort")


def test_a_body_is_REQUIRED_unless_the_merge_is_only_staged(release, capsys):
    with pytest.raises(SystemExit):
        main(["branch", "--root", str(release)])
    capsys.readouterr()


def _stub_runner(runner):
    """Swap the module's real `run_gate` for `runner`; return the undo."""
    original = mergegate_module.run_gate
    mergegate_module.run_gate = runner

    def undo():
        mergegate_module.run_gate = original

    return undo


def test_NO_TEST_IN_THIS_MODULE_REACHES_DOCKER(release, tmp_path, monkeypatch, capsys):
    # ⭐ The real GATES name `docker/dev/check`; a stub earlier on PATH would be touched by
    #    any run that actually took them. Nothing here may.
    marker = tmp_path / "docker-was-called"
    stub = tmp_path / "bin" / "docker"
    stub.parent.mkdir()
    stub.write_text(f"#!/bin/sh\ntouch '{marker}'\nexit 0\n", encoding="utf-8")
    stub.chmod(stub.stat().st_mode | stat.S_IEXEC)
    monkeypatch.setenv("PATH", f"{stub.parent}{os.pathsep}{os.environ['PATH']}")
    stage_and_read(release, "branch", _green, ONE_GATE)
    stage_and_read(release, "branch", _red, ONE_GATE)
    capsys.readouterr()
    assert not marker.exists()
    _git(release, "merge", "--abort")


# --- the convention carries the invocation ---------------------------------------------


def test_the_BOARD_convention_writes_out_the_invocation_and_names_the_pair():
    text = (repository_root() / "docs/conventions/board.md").read_text(encoding="utf-8")
    assert "`W302`" in text, "the board convention carries no W302 clause"
    assert "python3 -m tools.mergegate" in text
