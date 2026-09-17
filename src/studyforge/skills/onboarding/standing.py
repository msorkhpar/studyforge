r"""Where a corpus stands, read the way a build reads it, for the reader's document.

**What it does.** Reads one corpus root through the build's own readers and
returns a `Standing`: how many units the container maps declare, how many have
material, how many a page would narrate, how many are reading-only, and whether
any unit needs a container — or that nothing has been ingested, or why the
corpus could not be read.

**How you use it.** `standing_of(root)`, then hand the answer to
`artifacts.reader_document(..., standing=...)`. `onboard(..., root=...)` does
both. ⛔ Nothing raises for a corpus the build refuses: the refusal is the answer.

**Depends on.** `generate` for the declarations (`read_corpus`,
`unit_location`), `narrate.synth` for the narration record (`read_state`) and
where a unit's clips are probed (`audio_dir`), `narrate.playable` for the join
a page plays through, and `unit.builder` for the document that join walks —
the calls `generate.narration.heard` and `recorded` make, asked of surfaces.
⛔ **No second reader**: every file is opened by the module a build opens it with.

## ⛔ Each count is the build's own answer, never a re-derivation

- **units** — the units the container maps declare, and separately those with
  material, which are the ones a build renders (`read_corpus` skips the rest).
- **narrated** — a unit whose page plays at least one clip: `playable_of`,
  asked with the page's own audio directory, is truthy — the question a build's
  page pass asks. ⛔ An unreadable record is a refusal, as it stops a build.
- **reading-only** — a unit whose declared practice count, as
  `generate.declared_practices` reads it, is zero.
- **container** — needed exactly when some unit declares a practice, because
  a graded practice runs in the pinned toolchain and a reading page never does.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from studyforge.archive.errors import ArchiveError
from studyforge.corpus.manifest import MANIFEST_FILENAME
from studyforge.generate import RAISES, UnitSource, read_corpus, unit_location
from studyforge.narrate.playable import playable_of
from studyforge.narrate.synth import StateError, audio_dir, read_state, state_file
from studyforge.unit.builder import build_unit
from studyforge.unit.errors import ContentError

#: What a build lets out for a corpus it will not read, plus the unit builder's own.
REFUSED = (*RAISES, ContentError, ArchiveError)


@dataclass(frozen=True, slots=True)
class Standing:
    """One corpus's state, or the reason it has none yet.

    ⭐ `read` is False before anything is ingested; `refused` carries a build's
    refusal, whose message names the record and never a path (R7).
    """

    read: bool = False
    refused: str = ""
    declared: int = 0
    units: int = 0
    narrated: int = 0
    reading_only: int = 0
    #: Whether the corpus holds a narration record at all.
    recorded: bool = False

    @property
    def container(self) -> bool:
        """Whether any unit needs a container: some unit declares a graded practice."""
        return self.units > self.reading_only


def standing_of(root: Path | str | None) -> Standing:
    """Read where the corpus at `root` stands. `None` is a root nobody named: nothing read."""
    if root is None or not (Path(root) / MANIFEST_FILENAME).is_file():
        return Standing()
    try:
        corpus = read_corpus(root)
        if not corpus.maps:
            return Standing()
        state = read_state(state_file(root))
        narrated = 0
        for source in corpus.units:
            probed = audio_dir(root, unit_location(corpus, source))
            narrated += bool(playable_of(_document(source), state, audio=probed))
    except StateError as error:
        # ⭐ The build's own sentence for it (`generate.narration.recorded`).
        return Standing(refused=f"the narration record cannot be read: {error}")
    except REFUSED as refusal:
        return Standing(refused=str(refusal))
    return Standing(
        read=True,
        declared=sum(len(container.units) for _, container in corpus.maps),
        units=len(corpus.units),
        narrated=narrated,
        reading_only=sum(1 for source in corpus.units if not source.declared_practices),
        recorded=state.present,
    )


def _document(source: UnitSource) -> dict:
    """Build one unit's served document exactly as the page pass does."""
    return build_unit(source.directory, declared_practices=source.declared_practices)
