r"""The one place a build puts bytes on disk, and the one place it refuses to.

**What it does.** Holds `Written` — what a pass put on disk and what it left
alone — and `place`, the single call every pass writes through.

**How you use it.** `place(out, at, body, written, refused)`; add the records
two passes return with `+`.

**Depends on.** Nothing but the standard library.

## ⛔ R3 BY REFUSING, NOT BY REMEMBERING

**No path that already exists is written.** A target on disk is named in
`Written.refused` and left byte-for-byte alone; nothing is moved, renamed or
overwritten, and the only directories minted are the ones a target needs.

⚠️ **That is R3's floor and it is NOT a rebuild policy.** What a *second* build
should do to a file the first build wrote — overwrite it, skip it, compare a
digest — is a decision left open on purpose. ⛔ Deciding it here by reflex is
exactly how a generator ends up rewriting material somebody else owns, and the
safe direction while it is open is to write nothing over anything.

⭐ **One call, so the refusal cannot be forgotten by a pass added later.** A
second pass that opened a file itself would be a second R3 policy, and the one
that skipped the check would be the one nobody noticed.

## ⛔ A build mints its own pages and never its own output ROOT

⚠️ **Measured, and this guard exists because of it**: `tests/emission` calls
every public callable in `src/` with filler arguments, so it called this one
with the relative path `alpha` — and a writer that minted its own root created
`alpha/alpha` **in the repository**, silently, on every full test run. ⭐ A
relative output root resolves against whatever the process's working directory
happens to be, which is the one thing a build must never let decide where its
output lands. ⛔ So the root is the caller's to create and this refuses without
it.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from studyforge.generate.declarations import BuildError


@dataclass(frozen=True, slots=True)
class Written:
    """What one run put on disk, and what it refused to touch.

    ⭐ All three are paths **relative to the output root**, exactly as placement
    named them — so a caller can diff them against `studyforge plan` without
    knowing where the run wrote.

    ⚠️ `pages` and `assets` are separate because they answer different
    questions: the plan enumerates pages one by one and the shared bundle as a
    directory, and a single list would make the second unaskable.
    """

    pages: tuple[PurePosixPath, ...] = ()
    assets: tuple[PurePosixPath, ...] = ()
    refused: tuple[PurePosixPath, ...] = ()

    def __add__(self, other: Written) -> Written:
        """Two passes' records, in the order the passes ran."""
        if not isinstance(other, Written):
            return NotImplemented
        return Written(
            pages=self.pages + other.pages,
            assets=self.assets + other.assets,
            refused=self.refused + other.refused,
        )

    @property
    def paths(self) -> tuple[PurePosixPath, ...]:
        """Every file this run actually wrote, pages and bundle alike."""
        return self.pages + self.assets


def place(
    out: Path,
    at: PurePosixPath,
    body: bytes,
    written: list[PurePosixPath],
    refused: list[PurePosixPath],
) -> None:
    """Write `body` at `at` under `out`, or name the path and leave it alone.

    ⛔ Refuses when `out` is not an existing directory — see this module's
    docstring. The refusal names neither the root nor the target (R7).
    """
    if not out.is_dir():
        raise BuildError(
            "the output root is not a directory that already exists; a build mints "
            "its own pages and never its own root, because a relative one would "
            "resolve against whatever the caller's working directory happens to be"
        )
    target = out / at
    if target.exists():
        # ⛔ R3: named and left alone, never opened for writing.
        refused.append(at)
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(body)
    written.append(at)
