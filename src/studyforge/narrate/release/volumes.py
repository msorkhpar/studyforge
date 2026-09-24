r"""A corpus's recorded clips, packed into release volumes a reader can fetch.

**What it does.** Reads the narration record, collects every clip it locates,
writes them into one STORED zip whose member paths are relative to the corpus
root, splits that zip into volumes of at most `PART_BYTES` each, and writes a
`SHA256SUMS` over the volumes. The zip is removed once it is split: the volumes
are the release, and the corpus keeps its clips where they are.

**How you use it.** `pack(root, out)` returns a `Packed`; `clips_of(root)`
returns the population without writing anything; `read_sums(out)` reads a
checksum manifest back. `studyforge narrate <root> --pack <dir>` is the command.

**Depends on.** `narrate.synth` for the record (`read_state`, `state_file`,
`located`), `checksum` for each volume's SHA-256, and the standard library
(`zipfile`). ⛔ It names no
source (R1) and composes no layout (R4): every path comes from the record.

## ⛔ The population is the record's, never a directory walk

⭐ A clip is packed when the record names it and locates it under the corpus
root, which is exactly the clip a page plays and the place `studyforge narrate`
wrote it. ⛔ A superseded clip is not packed: no page plays it. ⛔ A recorded
clip that is not on disk, or that the record cannot place, is REFUSED by name
before anything is written: a release is published, and a release missing a clip
the record promises would restore a corpus that names gaps on its pages.

## ⛔ Stored, sorted and stamped once, so a pack is byte-for-byte repeatable

⭐ Clips are already compressed audio, so compressing them again buys a few
percent for a great deal of time; the split is what matters, not the
compression. Members are written in sorted path order with one fixed timestamp,
fixed permissions and no extra attributes, so two packs of one corpus are
identical bytes (R10) and a volume says nothing about the machine that made it
(R7).

## ⛔ Each volume is at most `PART_BYTES`

⭐ 999,000,000 bytes: at most 999 MB in either unit, well inside a release
host's 2 GiB per-asset limit. The volumes are a plain split of the one zip, so
joining them in name order gives the zip back and any unzip tool reads it.
"""

from __future__ import annotations

import shutil
import zipfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from studyforge.checksum import Running, file_sha256
from studyforge.narrate.synth import located, read_state, state_file

#: The most bytes one volume holds: at most 999 MB, inside a 2 GiB asset limit.
PART_BYTES = 999_000_000

#: The zip the volumes split: `narration.zip.000`, `narration.zip.001`, and on.
VOLUME = "narration.zip"

#: The checksum manifest, one `<sha256>  <volume>` line per volume, `sha256sum -c` form.
SUMS = "SHA256SUMS"

#: Digits in a volume's suffix. ⛔ Fixed, so name order is numeric order.
DIGITS = 3

#: The one timestamp every member carries: the earliest a zip can state.
STAMP = (1980, 1, 1, 0, 0, 0)

#: A regular file, readable by everyone and writable by its owner.
MODE = 0o100644 << 16

#: Bytes read and written at a time while copying and splitting.
CHUNK = 1 << 20

#: The zip while it is being written, before it is split and removed.
WRITING = f"{VOLUME}.writing"


class PackRefused(ValueError):
    """The corpus cannot be packed as it stands; nothing was written."""


@dataclass(frozen=True, slots=True)
class Volume:
    """One volume on disk: its name, its size, and its SHA-256."""

    name: str
    size: int
    sha256: str


@dataclass(frozen=True, slots=True)
class Packed:
    """What one pack wrote: the volumes, and how many clips and bytes they carry."""

    volumes: tuple[Volume, ...]
    clips: int
    clip_bytes: int

    @property
    def assets(self) -> tuple[str, ...]:
        """Every file a release carries, volumes first and the manifest last."""
        return (*(volume.name for volume in self.volumes), SUMS)


def volume_name(index: int) -> str:
    """Return the name of the volume at `index`, counted from zero."""
    return f"{VOLUME}.{index:0{DIGITS}d}"


def is_volume(name: str) -> bool:
    """Whether `name` is a volume's name."""
    stem, _, digits = name.rpartition(".")
    return stem == VOLUME and len(digits) == DIGITS and digits.isdigit()


def clips_of(root: Path | str) -> tuple[tuple[str, Path], ...]:
    """Return `(member path, file)` for every clip the record locates, sorted by member path.

    ⛔ Raises `PackRefused` for no record, no clip, or a clip the record promises
    and cannot place or the disk does not hold, naming how many and the first few.
    """
    base = Path(root)
    state = read_state(state_file(base))
    if not state.present or not state.clips:
        raise PackRefused(
            "the corpus has no narration record, or the record names no clip, so there "
            "is nothing to pack; run `studyforge narrate` first"
        )
    found: dict[str, Path] = {}
    absent: list[str] = []
    for speech_id, clip in sorted(state.clips.items()):
        file = None
        if PurePosixPath(clip.filename).name == clip.filename:
            file = located(base, clip.where, clip.filename)
        if file is None or not file.is_file():
            absent.append(speech_id)
            continue
        found[file.relative_to(base).as_posix()] = file
    if absent:
        raise PackRefused(
            f"{len(absent)} clip(s) the narration record promises are not on disk or "
            f"cannot be placed, first {absent[:3]}; a release would restore a corpus "
            f"that names gaps. Run `studyforge narrate` for them, or prune the record"
        )
    return tuple(sorted(found.items()))


def pack(root: Path | str, out: Path | str, *, part_bytes: int = PART_BYTES) -> Packed:
    """Pack the clips of the corpus at `root` into volumes and a `SHA256SUMS` under `out`.

    ⛔ Refuses an `out` inside the corpus (the volumes would be committed or
    unclassified there) and an `out` holding anything but an earlier pack's
    files, which are replaced. The corpus itself is only read.
    """
    if part_bytes < 1:
        raise PackRefused(f"a volume holds at least one byte, got {part_bytes}")
    base, target = Path(root).resolve(), Path(out).resolve()
    if target == base or base in target.parents:
        raise PackRefused(
            "the release directory is inside the corpus, where the volumes would be "
            "committed or read as material; name a directory outside it"
        )
    clips = clips_of(base)
    _clear(target)
    zipped = target / WRITING
    try:
        _write_zip(zipped, clips)
        volumes = _split(zipped, target, part_bytes)
    finally:
        zipped.unlink(missing_ok=True)
    (target / SUMS).write_text(render_sums(volumes), encoding="utf-8", newline="\n")
    return Packed(
        volumes=volumes,
        clips=len(clips),
        clip_bytes=sum(file.stat().st_size for _, file in clips),
    )


def render_sums(volumes: tuple[Volume, ...]) -> str:
    """Return the checksum manifest for `volumes`, in name order."""
    return "".join(f"{volume.sha256}  {volume.name}\n" for volume in volumes)


def read_sums(out: Path | str) -> dict[str, str]:
    """Return `{volume: sha256}` from the manifest under `out`. ⛔ Raises `PackRefused`."""
    file = Path(out) / SUMS
    if not file.is_file():
        raise PackRefused(f"there is no {SUMS} in the release directory; pack it first")
    sums: dict[str, str] = {}
    for line in file.read_text(encoding="utf-8").splitlines():
        digest, _, name = line.partition("  ")
        if not is_volume(name) or len(digest) != 64:
            raise PackRefused(f"{SUMS} holds a line that names no volume; pack it again")
        sums[name] = digest
    if not sums:
        raise PackRefused(f"{SUMS} names no volume; pack it again")
    return sums


def sha256_of(file: Path) -> str:
    """Return the hex SHA-256 of one file. ⭐ `checksum.file_sha256`, the one spelling."""
    return file_sha256(file)


def _clear(target: Path) -> None:
    """Make `target` an empty release directory, removing only an earlier pack's files."""
    target.mkdir(parents=True, exist_ok=True)
    ours = {SUMS, WRITING}
    foreign = [
        path.name for path in target.iterdir() if path.name not in ours and not is_volume(path.name)
    ]
    if foreign:
        raise PackRefused(
            f"the release directory holds {len(foreign)} file(s) no pack wrote; "
            f"name an empty directory, or one an earlier pack wrote"
        )
    for path in target.iterdir():
        path.unlink()


def _write_zip(zipped: Path, clips: tuple[tuple[str, Path], ...]) -> None:
    """Write every clip into one stored zip, in the order given, with fixed metadata."""
    with zipfile.ZipFile(zipped, "w", compression=zipfile.ZIP_STORED) as archive:
        for member, file in clips:
            info = zipfile.ZipInfo(member, date_time=STAMP)
            info.compress_type = zipfile.ZIP_STORED
            info.create_system = 3
            info.external_attr = MODE
            info.file_size = file.stat().st_size
            with file.open("rb") as source, archive.open(info, "w") as sink:
                shutil.copyfileobj(source, sink, CHUNK)


def _split(zipped: Path, target: Path, part_bytes: int) -> tuple[Volume, ...]:
    """Split `zipped` into volumes of at most `part_bytes`, and return them in order."""
    needed = -(-zipped.stat().st_size // part_bytes)
    if needed > 10**DIGITS:
        raise PackRefused(
            f"the clips need {needed} volumes, and a release names at most "
            f"{10**DIGITS}; pack with larger volumes"
        )
    volumes: list[Volume] = []
    with zipped.open("rb") as source:
        while True:
            name = volume_name(len(volumes))
            size, digest = 0, Running()
            with (target / name).open("wb") as sink:
                while size < part_bytes:
                    block = source.read(min(CHUNK, part_bytes - size))
                    if not block:
                        break
                    sink.write(block)
                    digest.update(block)
                    size += len(block)
            if not size:
                (target / name).unlink()
                break
            volumes.append(Volume(name, size, digest.hex()))
    return tuple(volumes)
