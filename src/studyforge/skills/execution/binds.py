r"""Which of a corpus's directories the editor binds, and the ones it never may.

**What it does.** Derives the sources directory an editor binds from the
manifest's own `content.include` (spec §8.1: the sources alone), and refuses any bind
that reaches a directory holding a quiz's key.

**How you use it.** `source_root(manifest)` for the directory; `unkeyed(*binds)`
over every corpus-relative directory the editor will bind, before rendering.

**Depends on.** `corpus.placement` and `exercise.bundle.layout` for the one
spelling of each keyed directory. ⛔ No I/O and nothing source-specific (R1).

⭐ **Split out of `onboard` at this seam** (R11): both answer one
question — what the editor may see.

## ⛔ NO QUIZ BUNDLE IS BOUND INTO THE EDITOR

⛔ **A quiz's key never leaves the local server** (the user's ruling,
2026-09-23), and the editor is another process, on another origin, in which a
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

from pathlib import PurePosixPath

from studyforge.corpus.manifest import Manifest
from studyforge.corpus.placement import ARCHIVE_DIRNAME
from studyforge.exercise.bundle.layout import BUNDLES_DIRNAME

#: Characters that make a path component a pattern rather than a directory.
GLOB_CHARACTERS = "*?[]"

#: ⛔ The directories that hold a quiz's key, which no editor bind may reach.
KEYED = (BUNDLES_DIRNAME, ARCHIVE_DIRNAME)


class ExecutionRefused(ValueError):
    """A corpus this skill will not generate execution artifacts for, and why."""


def source_root(manifest: Manifest) -> str:
    """Return the directory an editor binds, from `content.include` (§8.1: the sources alone)."""
    roots = [_root_of(one) for one in manifest.content.include]
    if not roots or not all(roots):
        raise ExecutionRefused(
            "this corpus's content.include names the repository root, so §8.1 leaves "
            "no directory to mount: only the sources are mounted, never the "
            "repository. Declare material under a directory, or add a manifest key that "
            "names the one an editor binds"
        )
    shared = PurePosixPath(roots[0])
    for one in roots[1:]:
        shared = _common(shared, PurePosixPath(one))
    if not shared.parts:
        raise ExecutionRefused(
            "this corpus's content.include globs share no directory, so reaching them all "
            "would mount the repository, and §8.1 mounts only the sources. Declare them under one "
            "directory, or add a manifest key that names the one an editor binds"
        )
    return shared.as_posix()


def unkeyed(*binds: str) -> None:
    """Refuse any editor bind that is, holds or sits inside a directory holding a key."""
    for bind in binds:
        mine = PurePosixPath(bind)
        for keyed in KEYED:
            other = PurePosixPath(keyed)
            if mine.is_relative_to(other) or other.is_relative_to(mine):
                raise ExecutionRefused(
                    f"the editor would bind `{bind}`, which reaches `{keyed}/`, where a "
                    "quiz's key is kept; the key never leaves the local server, so this "
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
