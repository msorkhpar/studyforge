"""Mirror of `src/studyforge/narrate/release/upload.py` (R12): the owner's upload and its dry run.

- the repository is read from the checkout's `origin`, in each spelling git
  returns, and a checkout with no GitHub origin is refused;
- the dry run lists every volume with its real size and digest, then the one
  `gh release create` command, and runs nothing;
- ⛔ a volume that no longer matches `SHA256SUMS`, a missing volume, and
  restore scripts written for another tag are each refused before `gh` runs;
- a real upload runs exactly that command, and here the `gh` it runs is a
  recording stand-in on `PATH`: ⛔ nothing reaches a release host.
"""

from __future__ import annotations

import hashlib
import shlex
import stat
from pathlib import Path

import pytest

from studyforge.narrate.release import pack, write_scripts
from studyforge.narrate.release.upload import (
    NOTES,
    TITLE,
    UploadRefused,
    plan_upload,
    repository_of,
    run_upload,
)
from studyforge.narrate.release.volumes import SUMS
from tests.studyforge.cli.narrate.plant import narrated
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
    root = with_origin(narrated(tmp_path))
    out = tmp_path / "release"
    pack(root, out, part_bytes=2048)
    write_scripts(root, tag)
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
    with pytest.raises(UploadRefused, match="no origin remote on GitHub"):
        repository_of(root)


def test_the_dry_run_lists_every_volume_and_the_one_command(tmp_path):
    root, out = packed(tmp_path)

    upload = plan_upload(root, out, TAG)
    lines = upload.lines()

    volumes = sorted(path for path in out.iterdir() if path.name != SUMS)
    assert len(volumes) > 1
    for path in volumes:
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        assert f"asset   {path.name}  {path.stat().st_size} byte(s)  sha256 {digest}" in lines
    assert f"upload  repository {REPO} (read from the checkout's origin)" in lines
    command = shlex.split(lines[-1].removeprefix("command "))
    assert command == upload.argv
    assert command[:4] == ["gh", "release", "create", TAG]
    assert command[4:-6] == [str(out / path.name) for path in volumes] + [str(out / SUMS)]
    assert command[-6:] == ["--repo", REPO, "--title", TITLE, "--notes", NOTES]


def test_the_dry_run_names_the_release_directory_as_it_was_typed(tmp_path, monkeypatch):
    root, _ = packed(tmp_path)
    monkeypatch.chdir(tmp_path)

    upload = plan_upload(root, "release", TAG)

    assert "release/narration.zip.000" in upload.lines()[-1]
    assert str(tmp_path) not in "\n".join(upload.lines())


def test_a_volume_that_no_longer_matches_its_sum_is_refused(tmp_path):
    root, out = packed(tmp_path)
    volume = out / "narration.zip.001"
    volume.write_bytes(volume.read_bytes()[:-1] + b"\x00")

    with pytest.raises(UploadRefused, match="narration.zip.001 does not match"):
        plan_upload(root, out, TAG)


def test_a_missing_volume_is_refused(tmp_path):
    root, out = packed(tmp_path)
    (out / "narration.zip.000").unlink()

    with pytest.raises(UploadRefused, match="lacks it"):
        plan_upload(root, out, TAG)


def test_restore_scripts_written_for_another_tag_are_refused(tmp_path):
    root, out = packed(tmp_path, tag="narration-0.9.0")

    with pytest.raises(UploadRefused, match=f"not written for tag {TAG}"):
        plan_upload(root, out, TAG)


def test_a_hand_edited_restore_script_is_refused(tmp_path):
    root, out = packed(tmp_path)
    script = root / ".studyforge/narration-release/restore.sh"
    script.write_text(script.read_text(encoding="utf-8") + "# edited\n", encoding="utf-8")

    with pytest.raises(UploadRefused, match="restore.sh"):
        plan_upload(root, out, TAG)


def test_a_real_upload_runs_exactly_the_command_through_gh(tmp_path, monkeypatch):
    root, out = packed(tmp_path)
    tools = tmp_path / "bin"
    tools.mkdir()
    log = tmp_path / "gh.argv"
    fake = tools / "gh"
    fake.write_text(f'#!/bin/sh\nprintf "%s\\n" "$@" > "{log}"\n', encoding="utf-8")
    fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
    upload = plan_upload(root, out, TAG)
    monkeypatch.setenv("PATH", str(tools))

    assert run_upload(upload) == 0

    assert log.read_text(encoding="utf-8").splitlines() == upload.argv[1:]


def test_an_upload_with_no_gh_is_refused_and_names_what_to_publish(tmp_path, monkeypatch):
    root, out = packed(tmp_path)
    upload = plan_upload(root, out, TAG)
    monkeypatch.setenv("PATH", str(tmp_path / "nothing-here"))

    with pytest.raises(UploadRefused, match="gh is not installed"):
        run_upload(upload)
