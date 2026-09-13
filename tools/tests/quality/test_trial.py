"""Mirror of `tools/quality/trial.py` (R12).

⛔ **Asserted in BOTH directions** (`W168`'s brief). The trial tree yields the
discriminator, and the WRONG tree is refused by name. ⭐ **Every tree here is synthetic**:
a repository and a linked worktree of it in a temp directory, sharing one object store,
which is the harder case, because the trial merge's sha RESOLVES in the wrong tree too.
⛔ **No test calls docker**, and one asserts that the command never does.
"""

from __future__ import annotations

import os
import re
import stat
from pathlib import Path

import pytest

import tools.quality.trial as trial_module
from tests.support import assert_package_contract, git, init_repository, repository_root, run
from tools.quality import CHECKS, NOTICES
from tools.quality.trial import PASSED, REFUSED, UNREAD, main, read_tree, render

#: ⛔ A per-invocation placeholder identity. Nothing is configured, and no name is real.
_IDENTITY = ("-c", "user.name=test", "-c", "user.email=test@example.invalid")


def _git(cwd: Path, *arguments: str) -> str:
    result = run([git(), *_IDENTITY, "-c", "commit.gpgsign=false", *arguments], cwd=cwd)
    assert result.returncode == 0, result.stdout + result.stderr
    return result.stdout.strip()


def _commit(cwd: Path, name: str) -> str:
    (cwd / name).write_text(f"{name}\n", encoding="utf-8")
    _git(cwd, "add", name)
    _git(cwd, "commit", "-q", "-m", name)
    return _git(cwd, "rev-parse", "HEAD")


@pytest.fixture
def trees(tmp_path: Path) -> dict[str, object]:
    """The reviewer's checkout at the branch under review, and a trial merge of it into base."""
    reviewer = init_repository(tmp_path / "reviewer")
    _git(reviewer, "symbolic-ref", "HEAD", "refs/heads/base")
    base = _commit(reviewer, "base.txt")
    _git(reviewer, "checkout", "-q", "-b", "branch")
    _commit(reviewer, "branch.txt")
    _git(reviewer, "checkout", "-q", "base")
    _commit(reviewer, "moved.txt")
    _git(reviewer, "checkout", "-q", "branch")
    # ⛔ The reviewer's own HEAD is a MERGE COMMIT too, as a release checkout's is, so the
    #    sha is the only thing that tells the two trees apart and a parent count cannot.
    _git(reviewer, "merge", "-q", "--no-edit", "--no-ff", "base")
    trial = tmp_path / "trial"
    _git(reviewer, "worktree", "add", "-q", "--detach", str(trial), "base")
    _git(trial, "merge", "--no-edit", "--no-ff", "branch")
    merge = _git(trial, "rev-parse", "HEAD")
    return {"reviewer": reviewer, "trial": trial, "base": base, "merge": merge}


def test_states_its_contract():
    assert_package_contract(trial_module, "tools.quality.trial")


def test_it_is_a_COMMAND_and_not_a_floor_check():
    registered = {function.__module__ for function in (*CHECKS, *NOTICES)}
    assert "tools.quality.trial" not in registered


# --- clause 2: the discriminator, both ways ------------------------------------------


def test_the_TRIAL_tree_declares_the_trial_merge_and_PASSES(trees):
    reading = read_tree(trees["trial"], trees["merge"])
    assert reading.verdict == PASSED
    assert len(reading.parents) == 2
    assert render(reading)[-1].startswith("⭐ PASSED: the mounted tree is the trial merge of ")


def test_an_ABBREVIATED_sha_is_the_same_discriminator(trees):
    assert read_tree(trees["trial"], trees["merge"][:12].upper()).verdict == PASSED


def test_the_REVIEWERS_own_tree_is_REFUSED_by_name_though_the_sha_resolves_there(trees):
    # ⛔ CTO-67/11's shape: the reviewer's wrapper mounts the reviewer's checkout.
    assert _git(trees["reviewer"], "cat-file", "-t", trees["merge"]) == "commit"
    reading = read_tree(trees["reviewer"], trees["merge"])
    assert len(reading.parents) == 2
    assert reading.verdict == REFUSED
    refusal = render(reading)[-1]
    assert "⛔ REFUSED: the mounted tree is ANOTHER tree" in refusal
    assert reading.head[:12] in refusal and "own wrapper" in refusal


def test_a_trial_that_made_NO_MERGE_COMMIT_is_REFUSED_even_at_the_expected_sha(trees, tmp_path):
    # ⚠️ `--no-ff` of a branch already in base makes no commit: HEAD stays at a sha the
    #    reviewer's own release checkout can also be at, so it discriminates nothing.
    empty = tmp_path / "empty-trial"
    _git(trees["reviewer"], "worktree", "add", "-q", "--detach", str(empty), trees["base"])
    reading = read_tree(empty, trees["base"])
    assert reading.verdict == REFUSED
    assert "NOT A MERGE COMMIT" in render(reading)[-1]


@pytest.mark.parametrize("expected", ["", "HEAD", "abc", "g" * 40, "release/m0-foundations"])
def test_a_sha_that_is_not_HEX_is_UNREAD_and_never_the_pass_reading(trees, expected):
    assert read_tree(trees["trial"], expected).verdict == UNREAD


def test_a_tree_git_cannot_read_is_UNREAD(tmp_path):
    assert read_tree(tmp_path, "0" * 40).verdict == UNREAD


# --- the command: its exits, R7, and no docker -------------------------------------


def test_the_COMMAND_exits_on_its_reading_and_prints_no_path(trees, capsys):
    assert main([trees["merge"], "--tree", str(trees["trial"])]) == PASSED
    assert main([trees["merge"], "--tree", str(trees["reviewer"])]) == REFUSED
    out = capsys.readouterr().out
    assert str(trees["trial"].parent) not in out


def test_the_command_NEVER_CALLS_DOCKER(trees, tmp_path, monkeypatch, capsys):
    marker = tmp_path / "docker-was-called"
    stub = tmp_path / "bin" / "docker"
    stub.parent.mkdir()
    stub.write_text(f"#!/bin/sh\ntouch '{marker}'\nexit 0\n", encoding="utf-8")
    stub.chmod(stub.stat().st_mode | stat.S_IEXEC)
    monkeypatch.setenv("PATH", f"{stub.parent}{os.pathsep}{os.environ['PATH']}")
    main([trees["merge"], "--tree", str(trees["trial"])])
    main([trees["merge"], "--tree", str(trees["reviewer"])])
    capsys.readouterr()
    assert not marker.exists()


# --- clause 1: the rubric clause carries the invocation, written out ----------------


def test_the_RUBRIC_clause_writes_out_the_TRIAL_trees_own_wrapper_and_the_discriminator():
    text = (repository_root() / "docs/conventions/review-rubric.md").read_text(encoding="utf-8")
    # ⚠️ Level two or deeper: §0a's own block names `W168` in a bash comment, which is `# `.
    heading = re.search(r"^#{2,6} .*`W168`.*$", text, re.MULTILINE)
    assert heading, "the rubric carries no W168 clause"
    # ⚠️ The section ends at the next heading of level two or deeper. A bash comment in the
    #    fence is `# `, so splitting on a bare `#` ends the section inside its own block.
    section = re.split(r"\n#{2,6} ", text[heading.end() :], maxsplit=1)[0]
    fence = re.search(r"```bash\n(.*?)```", section, re.DOTALL)
    assert fence, "the W168 clause writes out no invocation"
    block = fence.group(1)
    assert 'M=$(git -C "$TRIAL" rev-parse HEAD)' in block
    assert re.search(r'cd "\$TRIAL" && \./docker/dev/check sh -c', block)
    assert 'python3 -m tools.quality.trial "$1" || exit;' in block
    assert block.rstrip().endswith('trial "$M"')
