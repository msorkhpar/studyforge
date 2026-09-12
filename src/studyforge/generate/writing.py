r"""The one place a build puts bytes on disk, and the one place it refuses to.

**What it does.** Holds `Written` — what a pass put on disk and what it left
alone — and the three calls every pass writes through: `place` for bytes a pass
rendered, `copy` for a file it brings in from the archive, and `mint` for a
directory the plan declares.

**How you use it.** `place(out, at, body, written, refused, replaced,
footprint=…)`; `copy(out, at, source, written, refused, replaced,
footprint=…)`; `mint(out, at, refused)`; add the records two passes return
with `+`.

**Depends on.** `generate.footprint` for the line between the build's own
output and everybody else's, and the standard library.

## ⛔ R3 BY REFUSING, NOT BY REMEMBERING

**No path that already exists is written unless the plan declares it as this
build's own.** Every other target on disk is named in `Written.refused` and left
byte-for-byte alone; nothing is moved, renamed or deleted, and the only
directories minted are the ones a target needs.

## ⛔ THE REBUILD POLICY, AND WHY IT IS A FOOTPRINT RATHER THAN A MEMORY

⭐ **R3 distinguishes the build's own prior output from the user's material.** A
file the build wrote last time is not somebody's material; it is the build's own
previous answer, and replacing it is what *rebuilding after editing a lesson*
means. ⛔ Everything else stays protected absolutely and is refused **by name**.

⛔ **The line between the two is `generate.footprint.Footprint`, derived from
`studyforge plan`** — the enumeration that already exists, is goldened and is
asserted. ⚠️ **It is not a memory of what ran**: no digest is recorded, no
receipt is written into the output tree, and nothing here reads state an earlier
run left behind. A build asks *"does the plan declare this path as mine?"* and
nothing else.

## ⛔ WHAT THE FOOTPRINT CANNOT TELL, STATED HERE RATHER THAN DISCOVERED LATER

⛔ **The plan enumerates paths, not history, so a footprint cannot distinguish
this build's own prior output from ANY other file occupying the same path.** Two
cases follow and both are real:

⭐ **A generated page a person edited by hand is replaced, and that is RIGHT.**
R19 rules a hand-edit to a generated artifact a *finding, not a fix*, and every
placement profile already puts that page in the corpus's own ignore lines, so the
edit was never tracked either.

⛔ **Somebody's own file at a footprint path, before any build has ever run, is
replaced too — and that is WRONG.** It is the *"a foreign file is refused by
name"* half of the decision, and this mechanism cannot keep it.

⛔ **The second case is measured, not feared** — a hand-written `index.html`
placed in an empty output directory is destroyed by the FIRST build, which is
the one run where no prior output exists to be somebody's own. ⚠️ **It is named
in the report** — a `replace` line, never a silent `wrote` — but naming is not
refusing.

⭐ **Closing it needs a witness the plan cannot supply**: a receipt the build
writes and reads back, or a generator marker inside the artifact. Both are
remembering, both are outside this module, and neither was ruled. ⛔ **So the
gap is reported rather than closed by reflex here**, which is the same
discipline the paragraph this replaces used while the rebuild policy itself was
open.

⛔ **A directory where a file belongs is still a refusal, and a file where a
directory belongs still is too.** Replacing this build's own file is a write;
removing a tree, or a file the build never wrote, is a deletion, and nothing
here deletes.

⭐ **One module, so the refusal cannot be forgotten by a pass added later.** A
second pass that opened a file itself would be a second R3 policy, and the one
that skipped the check would be the one nobody noticed. ⚠️ `copy` exists rather
than `place(out, at, source.read_bytes(), …)` for one reason and it is not
style: a lesson video is megabytes, and a build that read every one of them
into memory to hand them straight back out would be sized by the corpus.

## ⚠️ `missing` is a RECORD, not a policy

⭐ A pass may find that a corpus declares a file it never fetched —
`media_skipped` is exactly that state, and it is legal. ⛔ **So `Written.missing`
names it and the build carries on.** Whether a build should *stop* on one, or
drain them into a report, is a decision this module does not take: it is the
same shape as `refused`, which has named rather than raised since the first
pass existed.

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

import shutil
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from studyforge.generate.declarations import BuildError
from studyforge.generate.footprint import Footprint


@dataclass(frozen=True, slots=True)
class Written:
    """What one run put on disk, and what it refused to touch.

    ⭐ All of them are paths **relative to the output root**, exactly as
    placement named them — so a caller can diff them against `studyforge plan`
    without knowing where the run wrote.

    ⚠️ `pages`, `assets` and `media` are separate because they answer different
    questions: the plan enumerates pages one by one and both the shared bundle
    and a unit's media as *directories*, and a single list would make the second
    unaskable.

    ⭐ `missing` is the one entry that is not about this build's own conduct: a
    file the corpus's material names and its archive does not hold. It is
    reported rather than raised — see this module's docstring.

    ⛔ **`replaced` is a CROSS-CUTTING record, exactly like `refused`, and not a
    fourth category of output.** A replaced page is still one of `pages`, so
    `paths` stays the path-for-path diff against `studyforge plan` that
    Ruling 99 asks for whether the run was a first build or a rebuild. ⭐ It is
    reported separately because *"which of my files did this run overwrite"* is
    the question the rebuild policy owes an auditable answer to, and a report
    that said `wrote` for both would not be one.
    """

    pages: tuple[PurePosixPath, ...] = ()
    assets: tuple[PurePosixPath, ...] = ()
    media: tuple[PurePosixPath, ...] = ()
    refused: tuple[PurePosixPath, ...] = ()
    missing: tuple[PurePosixPath, ...] = ()
    replaced: tuple[PurePosixPath, ...] = ()

    def __add__(self, other: Written) -> Written:
        """Two passes' records, in the order the passes ran."""
        if not isinstance(other, Written):
            return NotImplemented
        return Written(
            pages=self.pages + other.pages,
            assets=self.assets + other.assets,
            media=self.media + other.media,
            refused=self.refused + other.refused,
            missing=self.missing + other.missing,
            replaced=self.replaced + other.replaced,
        )

    @property
    def paths(self) -> tuple[PurePosixPath, ...]:
        """Every file this run actually wrote, page, bundle and media alike."""
        return self.pages + self.assets + self.media


def place(
    out: Path,
    at: PurePosixPath,
    body: bytes,
    written: list[PurePosixPath],
    refused: list[PurePosixPath],
    replaced: list[PurePosixPath],
    *,
    footprint: Footprint,
) -> None:
    """Write `body` at `at` under `out`, or name the path and leave it alone.

    ⛔ Refuses when `out` is not an existing directory — see this module's
    docstring. The refusal names neither the root nor the target (R7).

    ⛔ **`footprint` is required and keyword-only.** A pass added later cannot
    reach the write without answering *whose file is this*, and an omission is
    a `TypeError` at the call rather than a silent overwrite at a reader's.
    """
    target = _under(out, at)
    if target.exists():
        if not _mine(target, at, footprint):
            # ⛔ R3: named and left alone, never opened for writing.
            refused.append(at)
            return
        replaced.append(at)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(body)
    written.append(at)


def copy(
    out: Path,
    at: PurePosixPath,
    source: Path,
    written: list[PurePosixPath],
    refused: list[PurePosixPath],
    replaced: list[PurePosixPath],
    *,
    footprint: Footprint,
) -> None:
    """Copy `source` to `at` under `out`, or name the path and leave it alone.

    ⛔ **Content only: `copyfile` rather than `copy2`**, so the archive's
    *permissions* are not carried into the generated tree. A generated file gets
    the ordinary mode a new file gets, and in particular an archive file that
    arrived executable — a downloaded sample, a file restored from an archive
    that kept its bits — does not put an executable byte in a reader's
    repository. ⚠️ **The timestamp is NOT the reason**, and the sentence that
    said it was is wrong in the wrong direction: `copy2` would carry the
    archive's mtime, which is *more* stable across two builds than the wall
    clock `copyfile` leaves. R10 is about the bytes, and both spellings agree
    about those.
    """
    target = _under(out, at)
    if target.exists():
        if not _mine(target, at, footprint):
            # ⛔ R3, the same refusal `place` makes and for the same reason.
            refused.append(at)
            return
        replaced.append(at)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    written.append(at)


def _mine(target: Path, at: PurePosixPath, footprint: Footprint) -> bool:
    """Whether an existing `target` is this build's own prior output to replace.

    ⛔ **A directory is never this build's own file**, whatever the plan says
    about the path: replacing one would mean removing a tree, and the rebuild
    policy is *overwrite what the build wrote*, not *delete what is in the way*.
    ⚠️ Checked before the footprint rather than after, so a directory standing
    where a page belongs is refused by name under both profiles.
    """
    if target.is_dir():
        return False
    return footprint.owns(at)


def mint(out: Path, at: PurePosixPath, refused: list[PurePosixPath]) -> None:
    """Create the directory `at` under `out`, or name it and leave it alone.

    ⚠️ **A directory is not a write and is not recorded as one.** `Written`
    enumerates files, and `studyforge plan` enumerates a media directory as a
    directory — so one that is already there is simply already there, and only a
    *file* sitting where a directory belongs is a refusal (R3).
    """
    directory = _under(out, at)
    if directory.exists() and not directory.is_dir():
        refused.append(at)
        return
    directory.mkdir(parents=True, exist_ok=True)


def _under(out: Path, at: PurePosixPath) -> Path:
    """Resolve one target under the output root, refusing a root that is not one.

    ⛔ The refusal names neither the root nor the target (R7).
    """
    if not out.is_dir():
        raise BuildError(
            "the output root is not a directory that already exists; a build mints "
            "its own pages and never its own root, because a relative one would "
            "resolve against whatever the caller's working directory happens to be"
        )
    return out / at
