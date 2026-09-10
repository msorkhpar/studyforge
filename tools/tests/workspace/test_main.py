"""Mirror of `tools/workspace/__main__.py` (R12).

⭐ **The exit code is the deliverable**, so it is asserted as a code and not as
a message: everything downstream of this tool reads the number.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from tools.tests.workspace import support
from tools.workspace.__main__ import (
    DEV_CONTAINER,
    DISAGREES,
    NOT_AUTHORITATIVE,
    VERIFIED,
    main,
    repository_root,
    workspace_root,
)

# --------------------------------------------------------------------------
# ⭐ exit 0 when correct, exit 1 naming the component when not
# --------------------------------------------------------------------------


def test_verify_exits_zero_on_a_correct_workspace(tmp_path, capsys):
    root, here = support.workspace(tmp_path / "w")
    assert main(["verify", "--root", str(here), "--workspace", str(root)]) == 0
    assert "every recorded component" in capsys.readouterr().out


def test_verify_exits_one_and_names_the_component_when_a_commit_is_absent(tmp_path, capsys):
    # ⚠️ **Asserts the direction, not only the exit code.** The first version of
    # this test passed with the absent-commit branch deleted, because the stale
    # branch caught it instead — the right number for the wrong reason, found by
    # running the control negatively rather than reading it.
    root, here = support.workspace(tmp_path / "w")
    row = {"name": "Alpha", "where": "sibling", "status": "present", "commit": "0" * 40}
    support.write_pin(here, [row])
    assert main(["verify", "--root", str(here), "--workspace", str(root)]) == 1
    said = capsys.readouterr().err
    assert "Alpha" in said
    assert "is not in that checkout" in said


def test_verify_exits_one_and_names_the_component_when_head_moved(tmp_path, capsys):
    root, here = support.workspace(tmp_path / "w")
    support.commit(root / "Beta", "moved")
    assert main(["verify", "--root", str(here), "--workspace", str(root)]) == 1
    said = capsys.readouterr().err
    assert "Beta" in said
    assert "advance the pin or check the component out" in said


def test_a_pin_file_off_contract_exits_one_rather_than_raising(tmp_path, capsys):
    # ⚠️ A traceback is not a verdict. This is a build gate, so a broken pin
    # file has to arrive as exit 1 with a sentence, like every other failure.
    root, here = support.workspace(tmp_path / "w")
    (here / "workspace.json").write_text("{ not json", encoding="utf-8")
    assert main(["verify", "--root", str(here), "--workspace", str(root)]) == 1
    assert "not valid JSON" in capsys.readouterr().err


def test_record_rewrites_the_commits_and_verify_then_passes(tmp_path):
    root, here = support.workspace(tmp_path / "w")
    support.commit(root / "Alpha", "moved")
    assert main(["verify", "--root", str(here), "--workspace", str(root)]) == 1
    assert main(["record", "--root", str(here), "--workspace", str(root)]) == 0
    assert main(["verify", "--root", str(here), "--workspace", str(root)]) == 0


def test_record_writes_bytes_that_do_not_change_on_a_second_record(tmp_path):
    root, here = support.workspace(tmp_path / "w")
    main(["record", "--root", str(here), "--workspace", str(root)])
    once = (here / "workspace.json").read_bytes()
    main(["record", "--root", str(here), "--workspace", str(root)])
    assert (here / "workspace.json").read_bytes() == once


# --------------------------------------------------------------------------
# ⛔ the workspace root is computed, and a worktree is where the work happens
# --------------------------------------------------------------------------


def test_the_workspace_is_this_repositorys_parent(tmp_path):
    root, here = support.workspace(tmp_path / "w")
    assert workspace_root(here) == root
    assert repository_root(here) == here


def test_a_worktree_resolves_to_the_main_checkouts_parent_not_its_own(tmp_path):
    # ⭐ Agents work in worktrees, which live outside the repository they
    # belong to — so the plain parent is the wrong answer and would report
    # every component missing. `--git-common-dir` names the main checkout.
    root, here = support.workspace(tmp_path / "w")
    elsewhere = tmp_path / "far" / "away"
    elsewhere.parent.mkdir(parents=True)
    support.run(here, "worktree", "add", "-q", "-b", "side", str(elsewhere))
    assert workspace_root(repository_root(elsewhere)) == root


def test_this_repository_verifies_as_a_real_process_or_says_which_component(tmp_path):
    # ⚠️ **Run as the command a person runs**, against a synthetic workspace so
    # it is evidence rather than a skip: the pinned image mounts exactly one
    # directory (FND-03), so the real siblings are not visible from inside it.
    root, here = support.workspace(tmp_path / "w")
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "tools.workspace",
            "verify",
            "--root",
            str(here),
            "--workspace",
            str(root),
        ],
        capture_output=True,
        text=True,
        cwd=Path(__file__).resolve().parents[3],
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


# --------------------------------------------------------------------------
# ⛔ Ruling 53 — a check that cannot be authoritative here refuses
# --------------------------------------------------------------------------


def test_inside_the_pinned_image_verify_refuses_rather_than_answering(
    tmp_path, capsys, monkeypatch
):
    # ⛔ **It used to report all four components absent, "correctly".** That is
    # a plausible, well-formed, *wrong* answer — the failure this session has
    # now found five times — because the image mounts one directory (FND-03)
    # and the siblings are not missing, they are invisible.
    # ⭐ Mounting the workspace would hand the build four sibling repositories:
    # a wider trust boundary bought for a convenience, which Ruling 53 refuses.
    monkeypatch.setenv(DEV_CONTAINER, "1")
    assert main(["verify", "--root", str(tmp_path)]) == NOT_AUTHORITATIVE
    said = capsys.readouterr().err
    assert "host-verified" in said
    assert "mounts one directory" in said


def test_the_refusal_is_neither_pass_nor_fail(monkeypatch, tmp_path):
    # ⚠️ Three answers, three codes. Collapsing this into 1 would read as "the
    # workspace disagrees", and into 0 as "it agrees" — both are claims this
    # run cannot make.
    monkeypatch.setenv(DEV_CONTAINER, "1")
    assert NOT_AUTHORITATIVE not in (VERIFIED, DISAGREES)
    assert main(["record", "--root", str(tmp_path)]) == NOT_AUTHORITATIVE


def test_an_explicit_workspace_is_still_answered_inside_the_image(tmp_path, monkeypatch):
    # ⭐ The seam is *"the computed workspace is not visible"*, not *"we are in
    # a container"*. Naming a tree that IS visible is a decision somebody made,
    # and it is how this suite tests the tool at all.
    monkeypatch.setenv(DEV_CONTAINER, "1")
    root, here = support.workspace(tmp_path / "w")
    assert main(["verify", "--root", str(here), "--workspace", str(root)]) == VERIFIED
