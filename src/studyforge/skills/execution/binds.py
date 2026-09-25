r"""Which of a corpus's directories the editor binds, and the ones it never may.

**What it does.** Derives the sources directory an editor binds from the
manifest's own `content.include` (spec §8.1: the sources alone), adds the copy
of the corpus's code a lesson's code links open, and refuses any bind that
reaches a directory holding a quiz's key.

**How you use it.** `source_root(manifest)` for the directory; `code_bind(block,
sources)` for the copy's bind beside it; `unkeyed(*binds)` over every
corpus-relative directory the editor will bind, before rendering.

**Depends on.** `corpus.placement` and `exercise.bundle.layout` for the one
spelling of each keyed directory, `execute.codetree` for where the copy is, and
`contract` for where the editor keeps its workspace. ⛔ No I/O and nothing
source-specific (R1).

## ⭐ MATERIAL AT THE ROOT BINDS THE COPY, NEVER THE REPOSITORY

⚠️ §8.1 mounts the sources and never the repository, so a corpus whose material
sits at its root — a course whose lessons are `*/README_*.md` beside their
modules — has no directory of its own to bind. ⭐ **It binds the copy of its
code** (`execute.codetree`), which is exactly its code, lives in its own
bookkeeping and is the one tree a run may write into.

⭐ **Split out of `onboard` at this seam** (R11): both answer one
question — what the editor may see.

## ⛔ NO QUIZ BUNDLE IS BOUND INTO THE EDITOR

⛔ **A quiz's key lives only in the page it grades** (the user's ruling,
2026-09-25), and the editor is another process, on another origin, in which a
reader can open any file it binds. ⭐ So every directory the editor binds is
checked against the two that hold a key — the bundles (`BUNDLES_DIRNAME`,
whose `tests/quiz.json` is the key) and the archive (`ARCHIVE_DIRNAME`, whose
`practice-M.json` carries it) — and a bind that IS one, HOLDS one or sits
INSIDE one is refused rather than rendered. ⭐ It reads the paths, not the
disk, so it holds for a bundle authored after the file was generated.

⚠️ **What it does not cover** is a key copied by hand into the sources or a
practice workspace; the served site's own gate (`serve.withheld`) is where a
copy is refused, and the run route's output is gated the same way.
"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import PurePosixPath

from studyforge.corpus.manifest import Manifest
from studyforge.corpus.placement import ARCHIVE_DIRNAME, PRACTICE_DIRNAME
from studyforge.execute.codetree import CODE_COPY
from studyforge.exercise.bundle.layout import BUNDLES_DIRNAME
from studyforge.skills.execution.contract import blocks, require

#: Characters that make a path component a pattern rather than a directory.
GLOB_CHARACTERS = "*?[]"

#: ⛔ The directories that hold a quiz's key, which no editor bind may reach.
KEYED = (BUNDLES_DIRNAME, ARCHIVE_DIRNAME)


class ExecutionRefused(ValueError):
    """A corpus this skill will not generate execution artifacts for, and why."""


def source_root(manifest: Manifest) -> str:
    """Return the directory an editor binds, from `content.include` (§8.1: the sources alone).

    ⭐ **A corpus whose material sits at the repository root binds the COPY of
    its code** (`execute.CODE_COPY`): no directory of its own is the sources
    without being the repository, and the copy is the corpus's code and nothing
    else, in its own bookkeeping.
    """
    roots = [_root_of(one) for one in manifest.content.include]
    if not roots or not all(roots):
        return CODE_COPY
    shared = PurePosixPath(roots[0])
    for one in roots[1:]:
        shared = _common(shared, PurePosixPath(one))
    return shared.as_posix() if shared.parts else CODE_COPY


def code_bind(block: Mapping[str, object], sources: str) -> tuple[str, str] | None:
    """Return `(corpus-relative dir, container path)` for the copy of the code, or `None`.

    ⭐ **The editor opens a lesson's code from the copy**, so it binds the copy
    beside the sources, at the contract's workspace root under the copy's own
    last name. `None` when the sources already are, or hold, the copy.
    """
    if PurePosixPath(CODE_COPY).is_relative_to(PurePosixPath(sources)):
        return None
    root = require(block, "workspace", "container_path")
    inside = f"{str(root).rstrip('/')}/{PurePosixPath(CODE_COPY).name}"
    if inside in {str(entry.get("container_path")) for entry in blocks(block, "mounts")}:
        raise ExecutionRefused(
            "the contract already mounts something where the copy of the code would go, "
            "and this skill will not shadow it"
        )
    return CODE_COPY, inside


def unkeyed(*binds: str) -> None:
    """Refuse any editor bind that is, holds or sits inside a directory holding a key."""
    for bind in binds:
        mine = PurePosixPath(bind)
        for keyed in KEYED:
            other = PurePosixPath(keyed)
            if mine.is_relative_to(other) or other.is_relative_to(mine):
                raise ExecutionRefused(
                    f"the editor would bind `{bind}`, which reaches `{keyed}/`, where a "
                    "quiz's key is kept; the key lives only in the page it grades, so this "
                    "skill binds no directory that reaches one. Keep the material outside it"
                )


def _root_of(pattern: str) -> str:
    """Return one include glob's directory prefix, up to its first pattern part.

    ⚠️ A glob with no pattern part names a FILE, so its directory is what is
    taken — a corpus that includes one file by name has still said where its
    material lives.
    """
    kept: list[str] = []
    for part in PurePosixPath(pattern).parts:
        if any(one in part for one in GLOB_CHARACTERS):
            return "/".join(kept)
        kept.append(part)
    return "/".join(kept[:-1])


def _common(first: PurePosixPath, second: PurePosixPath) -> PurePosixPath:
    """Return the longest directory both paths share."""
    shared = []
    for one, other in zip(first.parts, second.parts, strict=False):
        if one != other:
            break
        shared.append(one)
    return PurePosixPath(*shared)


def workspaces_bind(block: Mapping[str, object], sources: str) -> tuple[str, str] | None:
    """Return `(corpus-relative dir, container path)` for the practice workspaces, or `None`.

    ⭐ **Read FROM where `emit` places them** — `PRACTICE_DIRNAME`, the one
    spelling `exercise.bundle.Places.workspace` and the adapter's own practices
    share — ⛔ never a second spelling of it. It sits inside the
    contract's workspace root, beside the sources, under its own name.
    ⭐ `None` when the sources already hold it: a second bind of what the first
    shows is two windows onto one directory.
    """
    if PurePosixPath(PRACTICE_DIRNAME).is_relative_to(PurePosixPath(sources)):
        return None
    root = require(block, "workspace", "container_path")
    inside = f"{str(root).rstrip('/')}/{PRACTICE_DIRNAME}"
    taken = {str(entry.get("container_path")) for entry in blocks(block, "mounts")}
    if inside in taken:
        raise ExecutionRefused(
            "the contract already mounts something where the practice workspaces would go, "
            "and this skill will not shadow it"
        )
    return PRACTICE_DIRNAME, inside
