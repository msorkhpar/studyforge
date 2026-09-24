"""Export: one corpus into one archive file, for its owner or for sharing.

**What it does.** Walks the corpus root for its material and gates every file name and
every UTF-8 text file (R7). For a `sharing` archive, it also judges every file that is
not UTF-8 text by the text its bytes carry. For an `owner` archive, it also reads the progress
record through the store. It then writes the manifest, the material and, for an
owner, the progress record into a new zip file. It refuses, and leaves no file,
whenever anything fails.

**How you use it.** `export(root, archive, kind=OWNER | SHARING, stream=None) -> int`.
`material(root, store, kind=...)` returns the files an export carries.

**Depends on.** `corpus.manifest` for the corpus's `source` and depth, this package's
`layout` and `record`, and `os`, `stat` and `zipfile`.

## ⛔ Sharing carries no progress, by construction and by assertion

A `sharing` export never calls the progress reader. The store's own directory is
pruned from the material walk for both kinds. `test_export.py` asserts that no
practice key, no progress field and no planted identity reaches a sharing archive.

## ⛔ No file reaches a sharing archive unjudged

`layout.gate` answers whether it read a file as text. For a sharing archive, a `False`
sends the file to `layout.judge_bytes`, and the report counts every file judged that
way. An owner archive carries such a file unread, as it always has.
"""

from __future__ import annotations

import contextlib
import os
import stat
import zipfile
from pathlib import Path

from studyforge.corpus.manifest import MANIFEST_FILENAME, load
from studyforge.skills.personalarchive import record
from studyforge.skills.personalarchive.layout import (
    EPOCH,
    KINDS,
    MANIFEST_MEMBER,
    MATERIAL_PREFIX,
    NEVER_MATERIAL,
    OWNER,
    PROGRESS_MEMBER,
    SHARING,
    ArchiveError,
    Material,
    gate,
    gate_name,
    judge_bytes,
    manifest_document,
    render,
    speaker,
)


def export(root: Path | str, archive: Path | str, *, kind: str, stream=None) -> int:
    """Export one corpus into a new archive file and return the exit code."""
    say = speaker(stream)
    try:
        files, judged, practices = _export(Path(root), Path(archive), kind)
    except record.REFUSALS as refusal:
        say(f"refused {refusal}")
        say("export exit 1")
        return 1
    say(f"material {files} file(s)")
    if kind == SHARING:
        say(f"material judged as bytes {judged}")
    if kind == OWNER:
        say(f"progress {practices} practice(s)")
    else:
        say("progress none: a sharing archive carries no progress")
    say(f"export {kind} exit 0")
    return 0


def material(
    root: Path, store: str, *, kind: str, judged: list[str] | None = None
) -> list[Material]:
    """Return every file an archive for `kind` carries, each gated (R7), in path order.

    Every file judged by its bytes is appended to `judged`, when one is given.
    """
    found: list[Material] = []
    judged = [] if judged is None else judged
    for directory, subdirectories, names in os.walk(root):
        here = Path(directory)
        kept = []
        for name in sorted(subdirectories):
            relative = (here / name).relative_to(root).as_posix()
            if name in NEVER_MATERIAL or relative == store:
                continue
            gate_name(relative)
            if (here / name).is_symlink():
                raise ArchiveError(
                    f"'{relative}' is a symbolic link, which an archive cannot carry"
                )
            kept.append(name)
        subdirectories[:] = kept
        for name in sorted(names):
            if name in NEVER_MATERIAL:
                continue
            found.append(_carried(root, here / name, kind, judged))
    return sorted(found, key=lambda carried: carried.path)


def _export(root: Path, archive: Path, kind: str) -> tuple[int, int, int]:
    """Check, read and write one export; return the file, judged-as-bytes and practice counts."""
    if kind not in KINDS:
        raise ArchiveError(f"who the archive is for must be one of {list(KINDS)}; none is assumed")
    manifest = load(root / MANIFEST_FILENAME)
    if archive.exists() or archive.is_symlink():
        raise ArchiveError("the archive file already exists, and nothing is overwritten")
    if not archive.parent.is_dir():
        raise ArchiveError("the archive file's directory does not exist")
    if archive.parent.resolve().is_relative_to(root.resolve()):
        raise ArchiveError("the archive file is inside the corpus root, so it would carry itself")
    judged: list[str] = []
    files = material(root, record.store_path(root), kind=kind, judged=judged)
    progress = record.owned(root, manifest.depth) if kind == OWNER else None
    document = manifest_document(kind, manifest.source, files, progress=progress is not None)
    _write(archive, document, files, progress)
    return len(files), len(judged), len(progress["practices"]) if progress else 0


def _carried(root: Path, path: Path, kind: str, judged: list[str]) -> Material:
    """Return one regular file as carried material, or refuse it."""
    relative = path.relative_to(root).as_posix()
    gate_name(relative)
    if path.is_symlink() or not path.is_file():
        raise ArchiveError(f"'{relative}' is not a regular file, which an archive cannot carry")
    data = path.read_bytes()
    if not gate(relative, data) and kind == SHARING:
        judge_bytes(relative, data)
        judged.append(relative)
    return Material(relative, data, bool(path.stat().st_mode & 0o111))


def _write(archive: Path, document: dict, files: list[Material], progress: dict | None) -> None:
    """Write the archive file, created exclusively. A failure removes what was started."""
    handle = open(archive, "xb")
    try:
        with handle, zipfile.ZipFile(handle, "w") as bundle:
            _member(bundle, MANIFEST_MEMBER, render(document).encode("utf-8"), False)
            for carried in files:
                _member(bundle, MATERIAL_PREFIX + carried.path, carried.data, carried.executable)
            if progress is not None:
                _member(bundle, PROGRESS_MEMBER, render(progress).encode("utf-8"), False)
    except BaseException:
        with contextlib.suppress(OSError):
            archive.unlink()
        raise


def _member(bundle: zipfile.ZipFile, name: str, data: bytes, executable: bool) -> None:
    """Add one member with a fixed date and a plain file mode. ⛔ A zip entry has no owner name."""
    info = zipfile.ZipInfo(name, date_time=EPOCH)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = (stat.S_IFREG | (0o755 if executable else 0o644)) << 16
    bundle.writestr(info, data)
