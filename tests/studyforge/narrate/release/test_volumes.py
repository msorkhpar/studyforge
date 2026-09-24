"""Mirror of `src/studyforge/narrate/release/volumes.py` (R12): the pack, read off the disk.

⭐ Every clause is read from the files a pack wrote and the zip they join into,
never from `Packed`'s own account alone:

- the population is the record's clips, each at its recorded place, and a
  file in an audio directory that the record does not name is not packed;
- two packs of one corpus are the same bytes, and joining the volumes gives a
  stored zip every clip reads back from unchanged;
- every volume is at most the bound, and the default bound is at most 999 MB;
- `SHA256SUMS` names every volume with its real digest;
- a missing clip, no record, a release directory inside the corpus and one
  holding foreign files are each refused before anything is written.
"""

from __future__ import annotations

import hashlib
import io
import zipfile
from pathlib import Path

import pytest

from studyforge.narrate.release import volumes
from studyforge.narrate.release.volumes import (
    PART_BYTES,
    SUMS,
    PackRefused,
    clips_of,
    is_volume,
    pack,
    read_sums,
    volume_name,
)
from studyforge.narrate.synth import read_state, state_file
from tests.studyforge.cli.narrate.plant import narrated
from tests.studyforge.generate.corpora import BOTH


def joined(out: Path) -> bytes:
    """The volumes under `out`, joined in name order: the zip a restore extracts."""
    names = sorted(path.name for path in out.iterdir() if is_volume(path.name))
    return b"".join((out / name).read_bytes() for name in names)


def on_disk(out: Path) -> dict[str, bytes]:
    """Every file under `out`, by name."""
    return {path.name: path.read_bytes() for path in sorted(out.iterdir())}


@pytest.mark.parametrize("name", BOTH)
def test_the_population_is_every_clip_the_record_locates_at_its_recorded_place(tmp_path, name):
    root = narrated(tmp_path, name)
    state = read_state(state_file(root))
    expected = sorted(f"{clip.where}/{clip.filename}" for clip in state.clips.values())

    members = [member for member, _ in clips_of(root)]

    assert members == expected
    assert len(members) == len(state.clips) > 1, "the reading is vacuous"


def test_a_file_the_record_does_not_name_is_not_packed(tmp_path):
    root = narrated(tmp_path)
    member, file = clips_of(root)[0]
    stray = file.parent / "stray.mp3"
    stray.write_bytes(b"not a recorded clip")

    assert stray.relative_to(root).as_posix() not in dict(clips_of(root))
    out = tmp_path / "release"
    pack(root, out)
    with zipfile.ZipFile(io.BytesIO(joined(out))) as archive:
        assert "stray.mp3" not in " ".join(archive.namelist())
        assert member in archive.namelist()


@pytest.mark.parametrize("name", BOTH)
def test_joined_volumes_are_a_stored_zip_holding_every_clip_byte_for_byte(tmp_path, name):
    root = narrated(tmp_path, name)
    out = tmp_path / "release"

    packed = pack(root, out, part_bytes=1500)

    with zipfile.ZipFile(io.BytesIO(joined(out))) as archive:
        assert archive.testzip() is None
        infos = archive.infolist()
        assert [info.filename for info in infos] == [member for member, _ in clips_of(root)]
        for info in infos:
            assert info.compress_type == zipfile.ZIP_STORED
            assert info.date_time == volumes.STAMP
            assert info.extra == b"", "a member carries attributes of the machine that packed it"
            assert archive.read(info) == (root / info.filename).read_bytes()
    assert packed.clips == len(infos)
    assert len(packed.volumes) > 1, "the split was not exercised"


@pytest.mark.parametrize("bound", [7, 97, 1500, 10_000_000])
def test_every_volume_is_at_most_the_bound_and_only_the_last_is_short(tmp_path, bound):
    root = narrated(tmp_path)
    out = tmp_path / "release"

    packed = pack(root, out, part_bytes=bound)

    sizes = [(out / volume.name).stat().st_size for volume in packed.volumes]
    assert sizes == [volume.size for volume in packed.volumes]
    assert all(0 < size <= bound for size in sizes)
    assert all(size == bound for size in sizes[:-1])
    assert [volume.name for volume in packed.volumes] == [
        volume_name(index) for index in range(len(sizes))
    ]


def test_more_volumes_than_a_release_names_is_refused_and_leaves_no_zip(tmp_path):
    root = narrated(tmp_path)
    out = tmp_path / "release"

    with pytest.raises(PackRefused, match="at most 1000"):
        pack(root, out, part_bytes=1)

    assert list(out.iterdir()) == []


def test_the_default_bound_is_at_most_999_mb_and_inside_a_2_gib_asset():
    assert PART_BYTES <= 999 * 1000 * 1000
    assert PART_BYTES < 2 * 1024**3


def test_a_bound_below_one_byte_is_refused(tmp_path):
    root = narrated(tmp_path)
    with pytest.raises(PackRefused):
        pack(root, tmp_path / "release", part_bytes=0)
    assert not (tmp_path / "release").exists()


@pytest.mark.parametrize("name", BOTH)
def test_two_packs_of_one_corpus_are_the_same_bytes(tmp_path, name):
    root = narrated(tmp_path, name)

    pack(root, tmp_path / "one", part_bytes=2048)
    pack(root, tmp_path / "two", part_bytes=2048)

    assert on_disk(tmp_path / "one") == on_disk(tmp_path / "two")


def test_the_manifest_names_every_volume_with_its_real_digest(tmp_path):
    root = narrated(tmp_path)
    out = tmp_path / "release"
    packed = pack(root, out, part_bytes=2048)

    sums = read_sums(out)

    assert sums == {
        volume.name: hashlib.sha256((out / volume.name).read_bytes()).hexdigest()
        for volume in packed.volumes
    }
    assert packed.assets == (*sums, SUMS)
    assert sorted(path.name for path in out.iterdir()) == sorted(packed.assets)


def test_a_repack_replaces_an_earlier_pack_and_leaves_no_stale_volume(tmp_path):
    root = narrated(tmp_path)
    out = tmp_path / "release"
    pack(root, out, part_bytes=100)
    assert len(read_sums(out)) > 2

    packed = pack(root, out)

    assert sorted(path.name for path in out.iterdir()) == sorted(packed.assets)
    assert len(packed.volumes) == 1


def test_a_clip_the_record_promises_and_the_disk_lacks_is_refused_before_anything_is_written(
    tmp_path,
):
    root = narrated(tmp_path)
    _, file = clips_of(root)[0]
    file.unlink()

    with pytest.raises(PackRefused) as refusal:
        pack(root, tmp_path / "release")

    assert "1 clip(s)" in str(refusal.value)
    assert not (tmp_path / "release").exists()


def test_a_corpus_with_no_record_is_refused(tmp_path):
    root = narrated(tmp_path)
    state_file(root).unlink()

    with pytest.raises(PackRefused, match="no narration record"):
        pack(root, tmp_path / "release")


@pytest.mark.parametrize("inside", [".", "release", ".studyforge/release"])
def test_a_release_directory_inside_the_corpus_is_refused(tmp_path, inside):
    root = narrated(tmp_path)
    before = sorted(path for path in root.rglob("*"))

    with pytest.raises(PackRefused, match="inside the corpus"):
        pack(root, root / inside)

    assert sorted(path for path in root.rglob("*")) == before


def test_a_release_directory_holding_a_file_no_pack_wrote_is_refused_and_kept(tmp_path):
    root = narrated(tmp_path)
    out = tmp_path / "release"
    out.mkdir()
    (out / "notes.txt").write_text("the owner's own", encoding="utf-8")

    with pytest.raises(PackRefused, match="no pack wrote"):
        pack(root, out)

    assert on_disk(out) == {"notes.txt": b"the owner's own"}


def test_a_manifest_line_that_names_no_volume_is_refused(tmp_path):
    out = tmp_path / "release"
    out.mkdir()
    (out / SUMS).write_text(f"{'0' * 64}  ../escape\n", encoding="utf-8")

    with pytest.raises(PackRefused, match="names no volume"):
        read_sums(out)


def test_the_pack_writes_nothing_into_the_corpus(tmp_path):
    root = narrated(tmp_path)
    before = {path: path.read_bytes() for path in root.rglob("*") if path.is_file()}

    pack(root, tmp_path / "release")

    assert {path: path.read_bytes() for path in root.rglob("*") if path.is_file()} == before
