r"""The build's narration pass: it READS a record and a disk, and synthesises nothing.

**What it does.** Opens a corpus's narration record once and answers, for each
unit page, which of the three states `W202` answer 4 names that page is in, as
the `render.page.Narration` the renderer takes. `write_narration(root, into)`
re-runs the unit-page pass after `studyforge narrate`, rewriting only the pages
whose bytes moved.

**How you use it.**

    from studyforge.generate import write_narration

    moved = write_narration(corpus_root, output_root)
    moved.written.pages    # pages whose narration changed, rewritten
    moved.unchanged        # this build's own pages whose bytes did not move

`recorded(root)` and `narration_for(...)` are the two halves `generate.units`
calls while it renders; a page pass never reads the record itself.

**Depends on.** `narrate.playable` for the join, `narrate.synth` for where the
record lives, how it is read and where a unit's clips were placed,
`render.page` for `Narration`, and `generate.units` for the page pass (deferred:
`units` imports this module). Not `narrate.client` and not `synthesise`
(`W202` answer 3), asserted by `tests/studyforge/generate/test_no_synthesis.py`.

## The three states are `W202` answer 4's, cited and not re-derived

No record: `SILENT`, so the page is byte-for-byte the pre-narration page. A
record: `playable_of` is asked WITH `audio=`, because without the directory a
recorded clip is taken at its word and a broken corpus renders as a working one.
The gaps are `UNKEPT` only (`handoffs/SF-38.md`, *For dependents*):
`NOT_RECORDED` is a unit nobody promised anything, never a gap.

## Where the disk is probed, and `SF-42/1`

`synth.audio_dir` is asked where `narrate` placed a unit's clips. It takes no
`label`, and the `sibling` profile names a labelled unit's audio directory from
it, so for such a unit the writer's directory and the one the page links
differ. Then the disk is probed where the PAGE looks: every href a page emits
must be answerable, and a clip placed somewhere the page cannot reach is a
promise this page does not keep. The page names the gap; nothing is guessed.

## What "does not rewrite" means here, against `SF-43`'s rebuild policy

A full build (`write_site`) replaces its whole footprint, so every page is
rewritten, byte-identical where nothing moved (R10). `write_narration` is the
pass invoked alone: a page this build owns whose rendered bytes equal what is on
disk is not opened for writing at all, and every other target goes through
`writing.place`, so refusals are unchanged. The two agree; neither weakens R3.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from studyforge.corpus.placement import AUDIO_DIRNAME, UnitLocations
from studyforge.generate.declarations import BuildError, Corpus, UnitSource, read_corpus
from studyforge.generate.writing import Written, place
from studyforge.narrate.playable import MISFILED, NOT_ON_DISK, NOT_PLACED, Playable, playable_of
from studyforge.narrate.synth import State, StateError, audio_dir, read_state, state_file
from studyforge.render.page import SILENT, Narration, Placement

#: The silent states that are a promise the disk did not keep. `NOT_RECORDED`
#: is deliberately absent: see this module's contract.
UNKEPT = frozenset({NOT_PLACED, MISFILED, NOT_ON_DISK})


@dataclass(frozen=True, slots=True)
class Renarrated:
    """What `write_narration` did: the pages it wrote, and the ones it left alone."""

    written: Written
    #: Pages this build owns whose bytes did not move, so they were not rewritten.
    unchanged: tuple[PurePosixPath, ...] = ()


def recorded(root: Path | str) -> State:
    """Read the corpus's narration record once, or stop naming it.

    An absent record is `State(present=False)`, the ordinary case. An unreadable
    one STOPS the build (`W202` answer 6): rendering it silent would make a
    broken narration identical to none, which is the defect answer 4 removes.
    The message is the record's own and carries no path (R7).
    """
    try:
        return read_state(state_file(root))
    except StateError as error:
        raise BuildError(f"the narration record cannot be read: {error}") from None


def gaps(playing: Playable) -> tuple:
    """Return the positions the record promised a clip for and cannot deliver, in order."""
    return tuple(entry.position for entry in playing.silent if entry.reason in UNKEPT)


def narration_for(
    corpus: Corpus,
    source: UnitSource,
    at: UnitLocations,
    document: dict,
    placement: Placement,
    state: State,
) -> Narration:
    """Return one unit page's narration, in whichever of the three states it is in."""
    if not state.present:
        return SILENT
    wrote = audio_dir(
        corpus.root,
        corpus.profile,
        source.container.address,
        source.ordinal,
        source.title,
        origin=source.origin,
    )
    looks = corpus.root / Path(str(at.media_dir(AUDIO_DIRNAME)))
    # `SF-42/1`: probe where the page's hrefs resolve, which is `wrote` unless a
    # label moved the page's directory and not the writer's.
    playing = playable_of(document, state, audio=wrote if wrote == looks else looks)
    return Narration.of(playing.filenames, placement, missing=gaps(playing))


def write_narration(root: Path | str, into: Path | str) -> Renarrated:
    """Re-run the unit-page pass after narration moved, rewriting only moved pages.

    `into` is required, as for every pass in this package. The import is
    deferred because `generate.units` imports this module for `narration_for`.
    """
    from studyforge.generate.units import unit_bodies

    corpus = read_corpus(root)
    out = Path(into)
    written: list[PurePosixPath] = []
    refused: list[PurePosixPath] = []
    replaced: list[PurePosixPath] = []
    unchanged: list[PurePosixPath] = []
    for at, body in unit_bodies(corpus):
        target = out / Path(str(at))
        if corpus.footprint.owns(at) and _holds(target, body):
            unchanged.append(at)
            continue
        place(out, at, body, written, refused, replaced, footprint=corpus.footprint)
    return Renarrated(
        Written(pages=tuple(written), refused=tuple(refused), replaced=tuple(replaced)),
        tuple(unchanged),
    )


def _holds(target: Path, body: bytes) -> bool:
    """Whether `target` is a regular file already holding exactly `body`."""
    return target.is_file() and not target.is_symlink() and target.read_bytes() == body
