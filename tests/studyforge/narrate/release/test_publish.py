"""Mirror of `src/studyforge/narrate/release/publish.py` (R12): the dry run and the owner's command.

- the repository is read from the checkout's own git configuration, in each
  spelling git records and through a worktree's `.git` file, and a checkout
  with no GitHub origin is refused;
- the dry run lists every volume with its real size and digest, then the one
  `gh release create` command, which parses back to exactly its argv;
- ⛔ a volume that no longer matches `SHA256SUMS`, a missing volume, restore
  scripts written for another tag or edited by hand, and a clip signal that
  does not say `released` are each refused;
- ⛔ planning a publish starts no process: `subprocess` is made to refuse, and
  the plan is still made.
"""

from __future__ import annotations

import hashlib
import shlex
import shutil
import subprocess
from pathlib import Path

import pytest

from studyforge.narrate.release import (
    CLIP_SUMS,
    SIGNAL,
    VOLUME_SUMS,
    pack,
    scripts,
    write_release_record,
    write_scripts,
    write_signal,
)
from studyforge.narrate.release.publish import (
    NOTES,
    TITLE,
    PublishRefused,
    plan_publish,
    repository_of,
)
from studyforge.narrate.release.volumes import SUMS
from studyforge.render.pageassets import ABSENT, PRESENT
from tests.studyforge.cli.narrate.plant import released_corpus
from tests.support import git, init_repository, run

#: The user an SSH remote logs in as: a remote's login name, not anybody's address.
SSH_USER = "git"

#: The placeholder every test's origin names.
REPO = "example-owner/example-course"
TAG = "narration-1.0.0"


def with_origin(root: Path, url: str = f"https://github.com/{REPO}.git") -> Path:
    """Make `root` a checkout whose `origin` is `url`."""
    init_repository(root)
    added = run([git(), "remote", "add", "origin", url], cwd=root)
    assert added.returncode == 0, added.stderr
    return root


def packed(tmp_path: Path, tag: str = TAG) -> tuple[Path, Path]:
    """A narrated fixture with an origin, packed in several volumes under `tag`."""
    root = with_origin(released_corpus(tmp_path))
    out = tmp_path / "release"
    made = pack(root, out, part_bytes=2048)
    write_scripts(root, tag)
    write_release_record(root, (out / SUMS).read_text(encoding="utf-8"), made.clip_sums)
    write_signal(root)
    return root, out


@pytest.mark.parametrize(
    "url",
    [
        f"https://github.com/{REPO}.git",
        f"https://github.com/{REPO}",
        f"{SSH_USER}@github.com:{REPO}.git",
        f"ssh://{SSH_USER}@github.com/{REPO}.git",
    ],
)
def test_the_repository_is_read_from_origin_in_every_spelling(tmp_path, url):
    assert repository_of(with_origin(tmp_path / "corpus", url)) == REPO


@pytest.mark.parametrize("url", [None, "https://example.invalid/some/repo.git", "/srv/repo.git"])
def test_a_checkout_with_no_github_origin_is_refused(tmp_path, url):
    root = init_repository(tmp_path / "corpus")
    if url is not None:
        run([git(), "remote", "add", "origin", url], cwd=root)
    with pytest.raises(PublishRefused, match="no origin remote on GitHub"):
        repository_of(root)


def test_the_dry_run_lists_every_volume_and_the_one_command(tmp_path):
    root, out = packed(tmp_path)

    publish = plan_publish(root, out, TAG)
    lines = publish.lines()

    volumes = sorted(path for path in out.iterdir() if path.name != SUMS)
    assert len(volumes) > 1
    for path in volumes:
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        assert f"asset   {path.name}  {path.stat().st_size} byte(s)  sha256 {digest}" in lines
    assert f"publish repository {REPO} (read from the checkout's origin)" in lines
    command = shlex.split(lines[-1].removeprefix("command "))
    assert command == publish.argv
    assert command[:4] == ["gh", "release", "create", TAG]
    assert command[4:-6] == [str(out / path.name) for path in volumes] + [str(out / SUMS)]
    assert command[-6:] == ["--repo", REPO, "--title", TITLE, "--notes", NOTES]


def test_the_dry_run_names_the_release_directory_as_it_was_typed(tmp_path, monkeypatch):
    root, _ = packed(tmp_path)
    monkeypatch.chdir(tmp_path)

    publish = plan_publish(root, "release", TAG)

    assert "release/narration.zip.000" in publish.lines()[-1]
    assert str(tmp_path) not in "\n".join(publish.lines())


def test_a_volume_that_no_longer_matches_its_sum_is_refused(tmp_path):
    root, out = packed(tmp_path)
    volume = out / "narration.zip.001"
    volume.write_bytes(volume.read_bytes()[:-1] + b"\x00")

    with pytest.raises(PublishRefused, match="narration.zip.001 does not match"):
        plan_publish(root, out, TAG)


def test_a_missing_volume_is_refused(tmp_path):
    root, out = packed(tmp_path)
    (out / "narration.zip.000").unlink()

    with pytest.raises(PublishRefused, match="lacks it"):
        plan_publish(root, out, TAG)


def test_restore_scripts_written_for_another_tag_are_refused(tmp_path):
    root, out = packed(tmp_path, tag="narration-0.9.0")

    with pytest.raises(PublishRefused, match=f"not written for tag {TAG}"):
        plan_publish(root, out, TAG)


@pytest.mark.parametrize("state", [PRESENT, ABSENT, None])
def test_a_clip_signal_that_does_not_say_released_is_refused(tmp_path, state):
    # ⛔ A committed `present` would tell every fresh checkout its clips are there.
    root, out = packed(tmp_path)
    if state is None:
        (root / SIGNAL).unlink()
    else:
        write_signal(root, state)

    with pytest.raises(PublishRefused, match="does not say released"):
        plan_publish(root, out, TAG)


def test_a_corpus_whose_policy_now_commits_its_clips_is_refused(tmp_path):
    # ⛔ Packed under `never`, then the policy moved: its checkouts carry the
    # clips again, and a release would tell their pages to hide them.
    root, out = packed(tmp_path)
    manifest = root / "corpus.json"
    manifest.write_text(
        manifest.read_text(encoding="utf-8").replace('"never"', '"always"'), encoding="utf-8"
    )

    with pytest.raises(PublishRefused, match="commits its clips"):
        plan_publish(root, out, TAG)


def test_the_dry_run_says_a_tag_is_published_once_and_how_to_go_on(tmp_path):
    # ⭐ `gh release create` fails on a tag whose release exists; the dry run
    # names a new tag, and the clobbering upload that replaces the assets.
    root, out = packed(tmp_path)

    lines = plan_publish(root, out, TAG).lines()

    said = [line for line in lines if line.startswith("again ")]
    assert any(f"a release under {TAG} that already exists" in line for line in said), lines
    assert any("--tag <new tag>" in line for line in said), lines
    upload = shlex.split(said[-1].removeprefix("again"))
    assert upload[:4] == ["gh", "release", "upload", TAG] and upload[-1] == "--clobber"
    assert f"--repo {REPO}" in said[-1]
    assert lines.index(said[-1]) < len(lines) - 1 and lines[-1].startswith(
        "command gh release create"
    )


def test_a_script_the_framework_now_renders_differently_is_named_as_an_upgrade(
    tmp_path, monkeypatch
):
    # ⭐ Packed under this tag by an earlier framework: the tag agrees and the
    # template moved, so the refusal names the upgrade and not the tag.
    root, out = packed(tmp_path)
    upgraded = tmp_path / "upgraded"
    shutil.copytree(scripts.SCRIPT_DIR, upgraded)
    (upgraded / "restore.sh").write_text(
        (upgraded / "restore.sh").read_text(encoding="utf-8") + "# a newer template\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(scripts, "SCRIPT_DIR", upgraded)

    with pytest.raises(PublishRefused, match="framework was upgraded since the pack"):
        plan_publish(root, out, TAG)


def test_a_script_packed_under_another_tag_is_named_by_the_tag(tmp_path):
    root, out = packed(tmp_path, tag="narration-0.9.0")

    with pytest.raises(PublishRefused) as refused:
        plan_publish(root, out, TAG)

    assert f"not written for tag {TAG}" in str(refused.value)
    assert "upgraded" not in str(refused.value)


def test_a_hand_edited_restore_script_is_refused(tmp_path):
    root, out = packed(tmp_path)
    script = root / ".studyforge/narration-release/restore.sh"
    script.write_text(script.read_text(encoding="utf-8") + "# edited\n", encoding="utf-8")

    with pytest.raises(PublishRefused, match="restore.sh"):
        plan_publish(root, out, TAG)


def test_planning_a_publish_starts_no_process(tmp_path, monkeypatch):
    root, out = packed(tmp_path)

    def refuse(*_args, **_kwargs):
        raise AssertionError("planning a publish started a process")

    monkeypatch.setattr(subprocess, "Popen", refuse)
    monkeypatch.setattr(subprocess, "run", refuse)

    assert plan_publish(root, out, TAG).repository == REPO


def test_a_worktree_is_followed_to_the_origin_of_its_common_repository(tmp_path):
    main = with_origin(tmp_path / "main")
    # ⛔ A placeholder identity, passed for this one commit: a worktree needs a commit.
    made = run(
        [
            git(), "-c", "user.name=Example", "-c", "user.email=example@example.invalid",
            "commit", "-q", "--allow-empty", "-m", "start",
        ],
        cwd=main,
    )  # fmt: skip
    assert made.returncode == 0, made.stderr
    added = run([git(), "worktree", "add", "-q", str(tmp_path / "wt")], cwd=main)
    assert added.returncode == 0, added.stderr

    assert (tmp_path / "wt" / ".git").is_file()
    assert repository_of(tmp_path / "wt") == REPO


def test_a_corpus_in_a_subdirectory_reads_the_checkout_above_it(tmp_path):
    main = with_origin(tmp_path / "main")
    (main / "course").mkdir()
    assert repository_of(main / "course") == REPO


def test_a_release_whose_sums_are_not_the_committed_ones_is_refused(tmp_path):
    # ⛔ Every restore trusts only the committed digests, so it would refuse this release.
    root, out = packed(tmp_path)
    (root / VOLUME_SUMS).write_text(f"{'0' * 64}  narration.zip.000\n", encoding="utf-8")

    with pytest.raises(PublishRefused, match="is not this release's SHA256SUMS"):
        plan_publish(root, out, TAG)


def test_a_committed_clip_list_the_record_no_longer_matches_is_refused(tmp_path):
    root, out = packed(tmp_path)
    listed = root / CLIP_SUMS
    listed.write_text("".join(listed.read_text(encoding="utf-8").splitlines(True)[1:]), "utf-8")

    with pytest.raises(PublishRefused, match="does not name the clips"):
        plan_publish(root, out, TAG)
