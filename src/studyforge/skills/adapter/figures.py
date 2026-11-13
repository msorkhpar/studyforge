"""A lesson's figures: each local image its blocks name, carried into the unit as an asset.

**What it does.** Reads the `image` blocks of one lesson (`![alt](path)` or a
lone `<img>` line, which `archive.markdown` already reads), finds each local
file beside the lesson's source, and answers the blocks with each `src`
rewritten to the unit's own copy, the `assets` entries that declare those
copies, and the files to copy. ⛔ It refuses a figure it cannot carry honestly
rather than dropping it.

**How you use it.** The generated `emit.py` calls it; a person never does.

    lifted = lift(root, unit.origin, fields["blocks"])
    fields = {**fields, "blocks": lifted.blocks, "assets": [*assets, *lifted.assets]}
    lifted.place(staging.unit_files(address, unit))

**Depends on.** `archive.blocks` for the block types that hold blocks, and
`sourcepath` for what a path inside the source may be. ⛔ Nothing here renders
or places a page's copy: the archive, the media pass and the renderer already
carry an image from an `assets` entry to the page.

## ⭐ THE ARCHIVE ALREADY HOLDS A FIGURE; THE ADAPTER NEVER PUT ONE THERE

⚠️ **Measured on a real course:** a lesson that drew a feasible region could
not show it. The block was read, but nothing copied the file into the unit's
own directory or declared it, so the page would reach for a file no build
placed. ⭐ Every Markdown corpus has the same gap in the same place, so closing
it is the framework's.

## ⛔ FOUR REFUSALS, EACH A FIGURE THAT WOULD REACH A READER BROKEN

| what the block names | the answer |
|---|---|
| no alternative text | ⛔ **refused**: a figure a screen reader cannot say, and narration skips |
| a path outside the corpus, or no file | ⛔ **refused**: the page would show a broken glyph |
| a file that is not a picture a browser shows | ⛔ **refused**, naming the types it takes |
| a file over `MAX_FIGURE_BYTES` | ⛔ **refused**: a page opens with every figure it holds |

⭐ A remote `src` (`https://…`) is left as written and declares nothing: the
page offers it as a link (R8), and nothing is on disk to carry. ⚠️ Two
different files with one name are refused too, because only the name survives
placement and one would be shown for both. ⛔ No refusal quotes a path: the
lesson is named by its source path and the figure by its place in the lesson.
"""

from __future__ import annotations

import hashlib
import posixpath
import shutil
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from studyforge.archive.blocks import CONTAINER_TYPES
from studyforge.sourcepath import source_path_fault

#: Where a unit's figures sit inside its own directory, as an asset's `local` names them.
FIGURES_DIR = "media"

#: ⛔ Closed: the picture types a browser shows, by suffix, and the content type each declares.
FIGURE_TYPES = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".svg": "image/svg+xml",
    ".webp": "image/webp",
}

#: The largest figure carried, in bytes. ⚠️ A plot saved at a sensible resolution is
#: tens of kilobytes; one over two megabytes is a photograph or a mistake, and the page
#: downloads it the moment it opens.
MAX_FIGURE_BYTES = 2 * 1024 * 1024

#: What marks a `src` as off this machine.
REMOTE_MARK = "://"


class FigureRefused(ValueError):
    """A figure this adapter will not carry, and why. ⛔ Never quotes a path."""


@dataclass(frozen=True, slots=True)
class Lifted:
    """One lesson's blocks with their figures carried, and what carrying them takes."""

    blocks: list
    assets: list[dict]
    #: `(local, source file)` per figure, each `local` once.
    files: tuple[tuple[str, Path], ...]

    def place(self, unit_files: Path) -> list[Path]:
        """Copy each figure into the unit's own directory and return where each landed."""
        placed = []
        for local, origin in self.files:
            target = unit_files / PurePosixPath(local)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(origin, target)
            placed.append(target)
        return placed


def lift(root: Path, origin: str, blocks: list, declared: list | tuple = ()) -> Lifted:
    """Carry every local figure `blocks` names, read from the lesson at `origin` under `root`.

    ⭐ A figure whose `src` is already the `local` of an entry in `declared` (the
    document's own `assets`) was carried by the adapter's reader, and is left as it is.
    """
    kept = {entry.get("local") for entry in declared if isinstance(entry, dict)}
    held: dict[str, Path] = {}
    assets: list[dict] = []
    counter = [0]

    def carried(block: object) -> object:
        if not isinstance(block, dict):
            return block
        if block.get("type") in CONTAINER_TYPES and isinstance(block.get("blocks"), list):
            return {**block, "blocks": [carried(inner) for inner in block["blocks"]]}
        if block.get("type") != "image":
            return block
        counter[0] += 1
        src = block.get("src")
        if not isinstance(src, str) or REMOTE_MARK in src or src in kept:
            return block
        found = _figure(Path(root), origin, src, block.get("alt"), counter[0])
        local = f"{FIGURES_DIR}/{found.name}"
        if held.setdefault(local, found) != found:
            raise FigureRefused(
                f"{origin}: figure {counter[0]} has the same file name as an earlier figure "
                f"of this lesson and is a different file; only the name survives placement, "
                f"so one would be shown for both. Rename one of them."
            )
        if not any(entry["local"] == local for entry in assets):
            assets.append(_asset(local, found))
        return {**block, "src": local}

    lifted = [carried(block) for block in blocks]
    return Lifted(blocks=lifted, assets=assets, files=tuple(held.items()))


def _figure(root: Path, origin: str, src: str, alt: object, number: int) -> Path:
    """Return the file one figure names, refusing one a reader would see broken."""
    if not isinstance(alt, str) or not alt.strip():
        raise FigureRefused(
            f"{origin}: figure {number} has no alternative text. Write what the figure "
            f"shows inside the brackets, ![like this](file.png): a reader who cannot see "
            f"it is told nothing, and narration says nothing for it."
        )
    named = posixpath.normpath(posixpath.join(posixpath.dirname(origin), src))
    fault = source_path_fault(named)
    resolved = (root / named).resolve()
    if fault is not None or not resolved.is_relative_to(root.resolve()) or not resolved.is_file():
        raise FigureRefused(
            f"{origin}: figure {number} names no file inside the corpus, read beside the "
            f"lesson's source. Give the path relative to the lesson's own file."
        )
    content_type = FIGURE_TYPES.get(resolved.suffix.lower())
    if content_type is None:
        raise FigureRefused(
            f"{origin}: figure {number} is not a picture a browser shows. The types "
            f"carried are {sorted(FIGURE_TYPES)}."
        )
    size = resolved.stat().st_size
    if size > MAX_FIGURE_BYTES:
        raise FigureRefused(
            f"{origin}: figure {number} is {size} bytes, over the {MAX_FIGURE_BYTES} a "
            f"figure may be. Save it smaller: a plot needs tens of kilobytes."
        )
    return resolved


def _asset(local: str, found: Path) -> dict:
    """The `assets` entry for one carried figure, in `MEDIA_ENTRY_KEYS` order."""
    data = found.read_bytes()
    return {
        "remote": None,
        "local": local,
        "sha256": hashlib.sha256(data).hexdigest(),
        "bytes": len(data),
        "content_type": FIGURE_TYPES[found.suffix.lower()],
        "kind": "image",
    }
