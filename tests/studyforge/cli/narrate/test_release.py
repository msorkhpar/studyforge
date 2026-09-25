"""Mirror of `src/studyforge/cli/narrate/release.py` (R12): `--pack` and `--publish`, typed.

Every reading goes through `cli.main`, the callable the verb dispatches to:

- `--pack` writes the volumes outside the corpus and the restore scripts into
  it, prints each volume and the dry run to type next, and exits `0`;
- `--publish` is that dry run: it prints every asset and the one `gh` command,
  and runs nothing (a recording `gh` on `PATH` is never called);
- a refusal prints one `refused` line and exits `1`, having written nothing;
- the release requests are exclusive with narrating, pruning and each other,
  and neither builds a narration client;
- ⛔ nothing printed carries the directory the suite runs in.
"""

from __future__ import annotations

import io
import os
import stat

import pytest

from studyforge.cli.narrate import cli
from studyforge.narrate.release import (
    CLIP_SUMS,
    RESTORE_PS1,
    RESTORE_SH,
    VOLUME_SUMS,
    read_sums,
)
from tests.studyforge.cli.narrate.plant import released_corpus
from tests.support import git, init_repository, run

REPO = "example-owner/example-course"


def invoke(*argv):
    out = io.StringIO()
    return cli.main(list(argv), out=out), out.getvalue()


@pytest.fixture
def corpus(tmp_path, monkeypatch):
    """A narrated fixture checkout with a placeholder origin; the suite runs beside it."""
    root = released_corpus(tmp_path)
    init_repository(root)
    added = run([git(), "remote", "add", "origin", f"https://github.com/{REPO}.git"], cwd=root)
    assert added.returncode == 0, added.stderr
    monkeypatch.chdir(tmp_path)
    return root


@pytest.fixture
def no_client(monkeypatch):
    """Make building a narration client fail loudly: a release request must build none."""
    from studyforge.narrate import client

    def refuse(*_args, **_kwargs):
        raise AssertionError("a release request built a narration client")

    monkeypatch.setattr(client, "NarrateClient", refuse)


def test_pack_writes_the_volumes_and_the_scripts_and_says_what_to_type_next(
    corpus, tmp_path, no_client
):
    code, said = invoke("depth1", "--pack", "release", "--tag", "narration-2.0.0")

    assert code == 0, said
    volumes = read_sums(tmp_path / "release")
    for name, digest in volumes.items():
        assert f"volume  {name}" in said and digest in said
    for where in (RESTORE_SH, RESTORE_PS1):
        assert (corpus / where).is_file()
        assert f"wrote   {where}" in said
    assert "narration-2.0.0" in (corpus / RESTORE_SH).read_text(encoding="utf-8")
    assert "narration-clips" not in said
    assert f"wrote   {VOLUME_SUMS}" in said and f"wrote   {CLIP_SUMS}" in said
    assert (corpus / VOLUME_SUMS).read_bytes() == (tmp_path / "release" / "SHA256SUMS").read_bytes()
    assert not (corpus / ".studyforge" / "assets" / "narration-clips.js").exists()
    assert "publish studyforge narrate depth1 --publish release --tag narration-2.0.0" in said
    assert str(tmp_path) not in said


def test_publish_prints_every_asset_and_the_command_and_runs_nothing(
    corpus, tmp_path, monkeypatch, no_client
):
    assert invoke("depth1", "--pack", "release")[0] == 0
    tools = tmp_path / "bin"
    tools.mkdir()
    called = tmp_path / "gh-was-called"
    fake = tools / "gh"
    fake.write_text(f'#!/bin/sh\n: > "{called}"\n', encoding="utf-8")
    fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
    monkeypatch.setenv("PATH", f"{tools}:{os.environ['PATH']}")

    code, said = invoke("depth1", "--publish", "release")

    assert code == 0, said
    assert not called.exists(), "a dry run ran gh"
    assert f"publish repository {REPO}" in said
    for name in read_sums(tmp_path / "release"):
        assert f"asset   {name}" in said
    assert "command gh release create narration-1.0.0 release/narration.zip.000" in said
    assert said.rstrip().endswith("when you mean to")
    assert str(tmp_path) not in said


def test_a_pack_that_is_refused_exits_one_and_writes_nothing(corpus, tmp_path, no_client):
    code, said = invoke("depth1", "--pack", "depth1/inside")

    assert code == 1
    assert said.startswith("refused ")
    assert not (corpus / "inside").exists()
    assert not (corpus / RESTORE_SH).exists()


def test_a_tag_a_shell_would_misread_is_refused_before_anything_is_packed(corpus, tmp_path):
    code, said = invoke("depth1", "--pack", "release", "--tag", "x;y")

    assert code == 1
    assert "nothing was packed" in said
    assert not (tmp_path / "release").exists()


def test_publishing_a_directory_never_packed_is_refused(corpus, tmp_path):
    (tmp_path / "empty").mkdir()
    code, said = invoke("depth1", "--publish", "empty")

    assert code == 1
    assert said.startswith("refused ")


@pytest.mark.parametrize(
    "argv",
    [
        ["--pack", "release", "--voice", "a_voice"],
        ["--pack", "release", "--prune"],
        ["--pack", "release", "--publish", "release"],
        ["--publish", "release", "--prune"],
    ],
)
def test_the_release_requests_are_each_their_own(corpus, argv):
    with pytest.raises(SystemExit) as refused:
        invoke("depth1", *argv)
    assert refused.value.code == 2
