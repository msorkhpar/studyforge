"""Import: one archive file into a corpus root, new or existing, merging instead of clobbering.

**What it does.** Reads the whole archive and checks it before it writes anything:
- the manifest's version (R9);
- every member against the manifest;
- every digest;
- every path;
- every name and UTF-8 text, and for a sharing archive every file that is not text (R7);
- that the corpus is the same one;
- the progress record, through the store's own reader.

It then writes the material that is absent. It leaves identical files alone, keeps
every file that differs, and merges progress through `record`. Every file and
practice it touched is reported.

**How you use it.** `import_archive(archive, root, stream=None) -> int`. `unpack(archive,
store)` returns the checked contents without writing anything.

**Depends on.** `corpus.manifest` for `parse`, `load` and the depth, this package's
`layout` and `record`, and `zipfile`.

## ⛔ Never overwrite

A material file is opened with exclusive creation, so a file that appeared since the
check is kept rather than replaced. Progress is merged by the rule in `SKILL.md`, never
replaced.
"""

from __future__ import annotations

import zipfile
from dataclasses import dataclass
from pathlib import Path

from studyforge.corpus.manifest import MANIFEST_FILENAME, RAISES, load, parse
from studyforge.skills.personalarchive import record
from studyforge.skills.personalarchive.layout import (
    MANIFEST_MEMBER,
    MATERIAL_PREFIX,
    PROGRESS_MEMBER,
    SHARING,
    ArchiveError,
    Material,
    digest,
    gate,
    gate_name,
    judge_bytes,
    read_manifest,
    refused_path,
    speaker,
)


@dataclass(frozen=True)
class Unpacked:
    """An archive's checked contents: its manifest, its material, its progress text if any."""

    manifest: dict
    files: tuple[Material, ...]
    progress: str | None


def import_archive(archive: Path | str, root: Path | str, *, stream=None) -> int:
    """Import one archive file into a corpus root and return the exit code."""
    say = speaker(stream)
    try:
        refused = _import(Path(archive), Path(root), say)
    except record.REFUSALS as refusal:
        say(f"refused {refusal}")
        say("import exit 1")
        return 1
    code = 1 if refused else 0
    say(f"import exit {code}")
    return code


def unpack(archive: Path, store: str) -> Unpacked:
    """Return an archive's contents once every member has been checked. Nothing is written."""
    try:
        bundle = zipfile.ZipFile(archive)
    except zipfile.BadZipFile:
        raise ArchiveError("the archive file is not a zip archive") from None
    except OSError as fault:
        raise ArchiveError(f"the archive file cannot be read: {fault.strerror}") from None
    with bundle:
        names = bundle.namelist()
        manifest = read_manifest(_text(bundle, MANIFEST_MEMBER, names))
        declared = {MATERIAL_PREFIX + entry["path"]: entry for entry in manifest["material"]}
        expected = {MANIFEST_MEMBER, *declared, *([PROGRESS_MEMBER] * manifest["progress"])}
        if len(set(names)) != len(names) or set(names) != expected:
            raise ArchiveError("the archive's members are not exactly what its manifest declares")
        sharing = manifest["kind"] == SHARING
        files = tuple(
            _checked(bundle, member, entry, store, sharing=sharing)
            for member, entry in declared.items()
        )
        progress = _text(bundle, PROGRESS_MEMBER, names) if manifest["progress"] else None
    return Unpacked(manifest, files, progress)


def _import(archive: Path, root: Path, say) -> int:
    """Check everything, then write material and merge progress; return the refused count."""
    if not root.is_dir():
        raise ArchiveError("the corpus root must be an existing directory")
    unpacked = unpack(archive, record.store_path(root))
    depth = _same_corpus(root, unpacked)
    practices = {}
    if unpacked.progress is not None:
        practices = record.staged(unpacked.progress, depth)["practices"]
    _material(root, unpacked.files, say)
    return record.merge_into(root, depth, practices, say)


def _checked(
    bundle: zipfile.ZipFile, member: str, entry: dict, store: str, *, sharing: bool
) -> Material:
    """Return one declared material file once its path, size, digest and text are checked."""
    path = entry["path"]
    reason = refused_path(path, store)
    if reason is not None:
        raise ArchiveError(f"a material file {reason}")
    gate_name(path)
    if bundle.getinfo(member).file_size != entry["bytes"]:
        raise ArchiveError(f"'{path}' is not the size its manifest records")
    data = _read(bundle, member)
    if digest(data) != entry["sha256"]:
        raise ArchiveError(f"'{path}' does not match its recorded digest")
    if not gate(path, data) and sharing:
        judge_bytes(path, data)
    return Material(path, data, entry["executable"])


def _same_corpus(root: Path, unpacked: Unpacked) -> int:
    """Refuse an archive of another corpus than the root holds; return the depth to merge at."""
    carried = {material.path: material for material in unpacked.files}
    if MANIFEST_FILENAME not in carried:
        raise ArchiveError(f"the archive carries no {MANIFEST_FILENAME}")
    try:
        theirs = parse(carried[MANIFEST_FILENAME].data.decode("utf-8"))
    except UnicodeDecodeError:
        raise ArchiveError(f"the archive's {MANIFEST_FILENAME} is not UTF-8 text") from None
    except RAISES:
        # ⛔ The manifest's own refusal is reported as it is, never wrapped.
        raise
    if theirs.source != unpacked.manifest["source"]:
        raise ArchiveError(f"the archive's {MANIFEST_FILENAME} is not the corpus it declares")
    here = root / MANIFEST_FILENAME
    ours = load(here) if here.exists() else theirs
    if ours.source != theirs.source:
        raise ArchiveError("the corpus root holds a different corpus from the archive")
    for material in unpacked.files:
        if any(parent.is_symlink() for parent in _within(root, material.path)):
            raise ArchiveError(f"'{material.path}' would be written through a symbolic link")
    return ours.depth


def _material(root: Path, files: tuple[Material, ...], say) -> None:
    """Write each absent file, leave each identical one, keep each that differs; report."""
    added, same, kept = 0, 0, []
    for material in files:
        target = root / material.path
        if target.is_file() and target.read_bytes() == material.data:
            same += 1
        elif _write_new(root, target, material):
            added += 1
        else:
            kept.append(material.path)
    say(f"material added {added}")
    say(f"material same {same}")
    for path in kept:
        say(f"material kept {path}")


def _write_new(root: Path, target: Path, material: Material) -> bool:
    """Create `target` with the material's bytes; return False when something is in the way."""
    if any(parent.exists() and not parent.is_dir() for parent in _within(root, material.path)[:-1]):
        return False
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(target, "xb") as handle:
            handle.write(material.data)
    except FileExistsError, IsADirectoryError:
        return False
    if material.executable:
        target.chmod(target.stat().st_mode | 0o111)
    return True


def _within(root: Path, relative: str) -> list[Path]:
    """Return every path from the root's first child down to `relative`, in order."""
    parts = Path(relative).parts
    return [root.joinpath(*parts[: index + 1]) for index in range(len(parts))]


def _text(bundle: zipfile.ZipFile, member: str, names: list[str]) -> str:
    """Return one member as UTF-8 text, refusing an absent or unreadable one."""
    if member not in names:
        raise ArchiveError(f"the archive has no {member}")
    try:
        return _read(bundle, member).decode("utf-8")
    except UnicodeDecodeError:
        raise ArchiveError(f"the archive's {member} is not UTF-8 text") from None


def _read(bundle: zipfile.ZipFile, member: str) -> bytes:
    """Return one member's bytes, refusing a damaged one."""
    try:
        return bundle.read(member)
    except zipfile.BadZipFile, ValueError, OSError:
        raise ArchiveError(f"the archive's member for '{member}' is damaged") from None
