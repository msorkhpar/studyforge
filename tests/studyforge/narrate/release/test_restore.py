"""The generated `restore.sh`, run: pack → restore round-trips every clip through a stand-in host.

Not a mirror (the script is not a Python module); `test_scripts.py` is the
renderer's. Every reading runs the script a pack wrote into a fixture corpus
whose clips were then deleted, against `stand_in.StandIn` on loopback, in an
environment `restoring.environment` closes. ⛔ No request leaves this machine.

- ⭐ **Public**: the download address alone restores every clip byte for byte,
  at the place the record names, and leaves no download behind.
- ⭐ **Private**: with a token, the API is read by asset id, the token is sent
  as a header and never appears in a URL, the output, or any file.
- ⭐ **`gh`**: with no token, a logged-in `gh` is asked for each asset, for the
  repository the checkout's `origin` names.
- ⭐ **Local**: volumes already on disk are read in place and never deleted.
- ⭐ **Idempotent**: a second run gives the same tree.
- ⛔ **A corrupt volume is refused** before anything is extracted, and a run
  after the release is repaired fetches only what it refused.
- ⭐ **A restore writes clips and nothing else**: no run, whole, refused or
  failed, writes the retired clip signal; a page asks its first clip itself.

- ⛔ **Only the clips the corpus committed are ever written**: a volume whose
  members are not exactly `clips.sha256`'s paths, a release whose volumes are not
  the committed ones, and clips whose bytes are not the committed ones are each
  refused, with the corpus byte-identical and no clip signal written.

Plants: `plant_a_corrupt_volume` flips one byte of one served volume, and
`restoring.forge_release` stands in for a wrong or replaced release.
"""

from __future__ import annotations

import os
import shutil
import stat
from pathlib import Path

import pytest

from studyforge.narrate.release import VOLUME_SUMS
from tests.studyforge.narrate.release.restoring import (
    DOWNLOADS,
    environment,
    files_of,
    forge_release,
    prepared,
    restore,
    restored,
    signal,
)
from tests.studyforge.narrate.release.stand_in import OWNER_REPO, TAG, TOKEN, StandIn
from tests.studyforge.narrate.release.test_publish import SSH_USER
from tests.support import git, init_repository, run, tool_on_path


def needs(*tools: str) -> None:
    """Skip, naming the tool, when this environment lacks one the script needs here."""
    for tool in tools:
        if tool_on_path(tool) is None:
            pytest.skip(f"no {tool} in this environment (the pinned dev image carries none)")


def plant_a_corrupt_volume(release: Path, name: str = "narration.zip.001") -> bytes:
    """Flip one byte of one volume; return its good bytes so the release can be repaired."""
    volume = release / name
    good = volume.read_bytes()
    volume.write_bytes(bytes([good[0] ^ 0xFF]) + good[1:])
    return good


def everything_under(root: Path) -> dict[str, bytes]:
    """Every file under `root`, relative path to bytes."""
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def test_a_public_release_restores_every_clip_byte_for_byte_and_leaves_no_download(tmp_path):
    needs("curl")
    corpus = prepared(tmp_path)
    assert set(restored(corpus).values()) == {None}, "the clips were not removed"

    with StandIn(corpus.release) as host:
        done = restore(corpus, environment(corpus, NARRATION_BASE_URL=host.base_url()))

    assert done.returncode == 0, done.stderr
    assert restored(corpus) == corpus.clips
    assert len(corpus.clips) > 1
    assert not (corpus.root / DOWNLOADS).exists()
    assert "checksums ok" in done.stdout
    assert all(path.startswith(f"/{OWNER_REPO}/releases/download/") for _, path, _ in host.requests)
    assert signal(corpus) is None


def test_a_private_release_is_read_by_asset_id_and_the_token_goes_nowhere_but_a_header(
    tmp_path,
):
    needs("curl")
    corpus = prepared(tmp_path)

    with StandIn(corpus.release, private=True) as host:
        env = environment(
            corpus, NARRATION_REPO=OWNER_REPO, NARRATION_API_URL=host.api, GITHUB_TOKEN=TOKEN
        )
        done = restore(corpus, env)

    assert done.returncode == 0, done.stderr
    assert restored(corpus) == corpus.clips
    paths = [path for _, path, _ in host.requests]
    assert paths[0] == f"/repos/{OWNER_REPO}/releases/tags/{TAG}"
    assert any(path.startswith(f"/repos/{OWNER_REPO}/releases/assets/") for path in paths)
    assert all(TOKEN not in path for path in paths)
    assert TOKEN not in done.stdout + done.stderr
    files = everything_under(corpus.root).items()
    assert [where for where, body in files if TOKEN.encode() in body] == []


def test_a_private_release_without_a_token_is_refused_by_name(tmp_path):
    needs("curl")
    corpus = prepared(tmp_path)

    with StandIn(corpus.release, private=True) as host:
        done = restore(corpus, environment(corpus, NARRATION_BASE_URL=host.base_url()))

    assert done.returncode != 0
    assert "GITHUB_TOKEN" in done.stderr
    assert set(restored(corpus).values()) == {None}
    assert not (corpus.root / DOWNLOADS).exists()


def test_gh_is_asked_for_the_repository_the_checkouts_origin_names(tmp_path):
    needs("git")
    corpus = prepared(tmp_path)
    init_repository(corpus.root)
    origin = f"{SSH_USER}@github.com:{OWNER_REPO}.git"
    added = run([git(), "remote", "add", "origin", origin], cwd=corpus.root)
    assert added.returncode == 0, added.stderr
    tools = tmp_path / "bin"
    tools.mkdir()
    log = tmp_path / "gh.log"
    fake = tools / "gh"
    # A stand-in for `gh release download <tag> --repo <r> --pattern <name> --dir <d>`.
    fake.write_text(
        f'#!/bin/sh\nprintf "%s\\n" "$*" >> "{log}"\ncp "{corpus.release}/$7" "$9/$7"\n',
        encoding="utf-8",
    )
    fake.chmod(fake.stat().st_mode | stat.S_IXUSR)

    done = restore(corpus, environment(corpus, path=f"{tools}:{os.environ.get('PATH', '')}"))

    assert done.returncode == 0, done.stderr
    assert restored(corpus) == corpus.clips
    asked = log.read_text(encoding="utf-8").splitlines()
    first = f"release download {TAG} --repo {OWNER_REPO} --pattern narration.zip.000"
    assert asked[0].startswith(first)
    assert len(asked) == len(list(corpus.release.glob("narration.zip.*")))


def test_volumes_on_this_disk_are_read_in_place_and_never_deleted(tmp_path):
    corpus = prepared(tmp_path)
    before = everything_under(corpus.release)

    done = restore(corpus, environment(corpus, NARRATION_LOCAL_DIR=str(corpus.release)))

    assert done.returncode == 0, done.stderr
    assert restored(corpus) == corpus.clips
    assert everything_under(corpus.release) == before
    assert not (corpus.root / DOWNLOADS).exists()
    assert signal(corpus) is None


def test_a_second_restore_gives_the_same_tree(tmp_path):
    needs("curl")
    corpus = prepared(tmp_path)

    with StandIn(corpus.release) as host:
        env = environment(corpus, NARRATION_BASE_URL=host.base_url())
        first = restore(corpus, env)
        tree = everything_under(corpus.root)
        second = restore(corpus, env)

    assert (first.returncode, second.returncode) == (0, 0), first.stderr + second.stderr
    assert everything_under(corpus.root) == tree
    assert restored(corpus) == corpus.clips


def test_a_corrupt_volume_is_refused_before_anything_is_extracted(tmp_path):
    needs("curl")
    corpus = prepared(tmp_path)
    good = plant_a_corrupt_volume(corpus.release)

    with StandIn(corpus.release) as host:
        env = environment(corpus, NARRATION_BASE_URL=host.base_url())
        refused = restore(corpus, env)
        downloaded = sorted(path.name for path in (corpus.root / DOWNLOADS).iterdir())
        after_refusal = restored(corpus)
        told_after_refusal = signal(corpus)
        (corpus.release / "narration.zip.001").write_bytes(good)
        host.requests.clear()
        repaired = restore(corpus, env)

    assert refused.returncode != 0
    assert "checksum mismatch on narration.zip.001" in refused.stderr
    assert set(after_refusal.values()) == {None}, "a refused run extracted clips"
    assert told_after_refusal is None, "a refused run wrote a clip signal"
    assert "narration.zip.001" not in downloaded, "the refused volume was kept to be reused"
    assert "narration.zip" not in downloaded, "the volumes were joined before they were checked"
    assert repaired.returncode == 0, repaired.stderr
    assert restored(corpus) == corpus.clips
    fetched = [path.rsplit("/", 1)[-1] for _, path, _ in host.requests]
    assert fetched == ["narration.zip.001"], "a repaired run fetched more than it refused"


def test_a_corrupt_volume_on_this_disk_is_refused_and_left_where_it_is(tmp_path):
    corpus = prepared(tmp_path)
    plant_a_corrupt_volume(corpus.release)
    before = everything_under(corpus.release)

    done = restore(corpus, environment(corpus, NARRATION_LOCAL_DIR=str(corpus.release)))

    assert done.returncode != 0
    assert "checksum mismatch" in done.stderr
    assert set(restored(corpus).values()) == {None}
    assert everything_under(corpus.release) == before


def test_a_restore_whose_extraction_fails_writes_no_clip_signal(tmp_path):
    # ⛔ One audio directory the restore cannot write into stops it after the
    # checks, and nothing but clips was ever going to be written.
    corpus = prepared(tmp_path)
    blocked = (corpus.root / next(iter(corpus.clips))).parent
    blocked.chmod(0o555)
    try:
        done = restore(corpus, environment(corpus, NARRATION_LOCAL_DIR=str(corpus.release)))
    finally:
        blocked.chmod(0o755)

    assert done.returncode != 0
    assert "checksums ok" in done.stdout
    assert signal(corpus) is None


@pytest.mark.parametrize("shell", ["bash", "dash"])
def test_the_script_runs_under_each_posix_shell(tmp_path, shell):
    needs(shell)
    corpus = prepared(tmp_path)

    done = restore(
        corpus, environment(corpus, NARRATION_LOCAL_DIR=str(corpus.release)), shell=shell
    )

    assert done.returncode == 0, done.stderr
    assert restored(corpus) == corpus.clips


def test_a_restore_without_unzip_extracts_with_python(tmp_path):
    corpus = prepared(tmp_path)
    tools = tmp_path / "bin"
    tools.mkdir()
    for tool in (
        "sh",
        "dirname",
        "awk",
        "sort",
        "sha256sum",
        "cut",
        "cat",
        "rm",
        "mkdir",
        "mv",
        "rmdir",
        "python3",
        "git",
    ):
        found = shutil.which(tool)
        if found is not None:
            (tools / tool).symlink_to(found)

    done = restore(
        corpus, environment(corpus, path=str(tools), NARRATION_LOCAL_DIR=str(corpus.release))
    )

    assert done.returncode == 0, done.stderr
    assert restored(corpus) == corpus.clips


# --------------------------------------------------------------------------
# ⛔ A release is checked against what THIS corpus committed, member by member
# --------------------------------------------------------------------------


def test_a_volume_carrying_the_manifest_and_an_escape_is_refused_and_the_corpus_is_untouched(
    tmp_path,
):
    # ⛔ A volume the corpus's committed digests accept,
    # whose members are `corpus.json` and `../x`, must not rewrite anything.
    corpus = prepared(tmp_path)
    forge_release(corpus, {"corpus.json": b"{}", "../ESCAPED.txt": b"out"}, committed=True)
    before = files_of(corpus.root)

    done = restore(corpus, environment(corpus, NARRATION_LOCAL_DIR=str(corpus.release)))

    assert done.returncode != 0
    assert "not this corpus's clips" in done.stderr
    assert files_of(corpus.root) == before
    assert not (tmp_path / "ESCAPED.txt").exists()
    assert signal(corpus) is None


def test_another_corpus_release_with_its_own_matching_sums_is_refused_at_the_volumes(tmp_path):
    # One volume on both sides, so the refusal is the digest's and not a missing part.
    corpus = prepared(tmp_path, part_bytes=10_000_000)
    forge_release(corpus, {path: b"another corpus" for path in corpus.clips}, committed=False)
    before = files_of(corpus.root)

    done = restore(corpus, environment(corpus, NARRATION_LOCAL_DIR=str(corpus.release)))

    assert done.returncode != 0
    assert "checksum mismatch on narration.zip.000" in done.stderr
    assert files_of(corpus.root) == before
    assert signal(corpus) is None


def test_clips_whose_bytes_are_not_the_committed_ones_are_refused_before_any_is_placed(tmp_path):
    # ⭐ The committed volume digests were made to agree, so the per-clip digests
    # checked in staging are the guard that answers.
    corpus = prepared(tmp_path)
    forge_release(corpus, {path: b"another corpus" for path in corpus.clips}, committed=True)
    before = files_of(corpus.root)

    done = restore(corpus, environment(corpus, NARRATION_LOCAL_DIR=str(corpus.release)))

    assert done.returncode != 0
    assert "is not the clip this corpus packed" in done.stderr
    assert files_of(corpus.root) == before
    assert not (corpus.root / DOWNLOADS / "staging").exists()
    assert signal(corpus) is None


def test_a_corpus_that_committed_no_release_record_fetches_nothing(tmp_path):
    corpus = prepared(tmp_path)
    (corpus.root / VOLUME_SUMS).unlink()

    done = restore(corpus, environment(corpus, NARRATION_LOCAL_DIR=str(corpus.release)))

    assert done.returncode != 0
    assert "no record of a packed release" in done.stderr
