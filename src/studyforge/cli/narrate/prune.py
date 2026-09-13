r"""`studyforge narrate <root> --prune`: delete the clips of entries the corpus no longer produces.

**What it does.** Walks the WHOLE corpus once (`stage.survey`), reads the
record, and for every entry whose speech id the walk did not produce deletes
the ONE clip file that entry names in its unit's audio directory — then
removes those entries through `narrate.synth.forget`. ⛔ It makes no request
to any service.

**How you use it.** `prune_corpus(root) -> Pruned`. `cli.main` calls it for
`--prune` and for nothing else; `report.prune_lines` and
`report.prune_exit_code` render it.

**Depends on.** `cli.narrate.stage` for the walk, `cli.narrate.disclosure` for
the predicate, `narrate.synth` for the record and its removal, and
`narrate.speakable.naming` for the one minter's inverse.

## ⛔ `E09` § W193 is this module's whole authority

1. **Its own request.** Nothing else in `src/` calls `prune_corpus`; `--prune`
   is exclusive with `--voice`, so a narration run never reaches it and a
   build never imports it.
2. **A partial walk refuses BY NAME**, before a file is looked at.
3. **Only what the record names.** The path is the directory the record
   carries for the clip (`W226`) — or, for a version-1 entry that carries none,
   the walked unit's audio directory — joined to the entry's filename, and that
   filename must parse back to the entry's own speech id. ⭐ A superseded clip
   an entry still names is reached the same way. ⭐ A file beside the clips that no dead entry
   names is never read, let alone deleted — discrimination by PATH.
4. **R3 is the outer bound.** An entry the prune cannot place by rule 3 is
   HELD — kept in the record, its file kept on disk — and reported.

## ⚠️ Why a version-1 entry of a unit no longer declared is still HELD

A version-2 entry carries the directory its clip was written into, so a
removed or renumbered unit's clips are reached (`W226`). ⛔ A version-1 entry
carries a filename and no directory, and a unit's audio directory is
placement's answer to declarations an undeclared unit no longer has. Guessing
it would compose a path (R4) inside somebody's repository (R3), so that entry
stays in the record, in the disclosure and in `held`.

## ⭐ Files first, then the record

A clip is unlinked before its entry is forgotten, and only entries whose file
is now absent are forgotten. A run stopped in between leaves entries naming
absent files, which the next prune forgets; the reverse order would leave
clips no record names, which no prune could ever reach again.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from studyforge.cli.narrate.disclosure import Walk, dead_entries
from studyforge.cli.narrate.stage import survey
from studyforge.narrate.speakable.naming import SEGMENT, parse_clip_name, unit_key_of
from studyforge.narrate.speakable.records import SpeakableError
from studyforge.narrate.synth import (
    Superseded,
    forget,
    forget_superseded,
    located,
    read_state,
    state_file,
)

#: Why an entry is held. ⛔ Sentences a person reads, and none carries a value (R7).
NOT_ITS_CLIP = "the record names a file that is not this entry's own clip, so it is not deleted"
UNDECLARED = (
    "its unit is no longer declared, so placement cannot say which directory holds its "
    "clip; the entry and any clip are kept"
)
NOT_A_FILE = "what sits at this clip's path is not a file, so it is kept"
STILL_NAMES = "a superseded clip of this entry is held, so the entry that names it is kept"


@dataclass(frozen=True, slots=True)
class Pruned:
    """What one prune did. ⛔ `deleted` is the set of files unlinked, not a count."""

    unwalked: tuple[str, ...] = ()
    deleted: tuple[Path, ...] = ()
    forgotten: tuple[str, ...] = ()
    held: tuple[tuple[str, str], ...] = ()
    #: `(speech id, superseded clip)` removed from a live entry (`W226`).
    cleared: tuple[tuple[str, Superseded], ...] = ()

    @property
    def refused(self) -> bool:
        """Report whether the walk missed a declared unit, so that nothing was touched."""
        return bool(self.unwalked)


def prune_corpus(root: Path | str) -> Pruned:
    """Delete the clips of every dead record entry and forget those entries.

    ⛔ Raises `BuildError` for a corpus it cannot read and `StateError` for a
    record it cannot read, both before any file is touched.
    """
    _, walk = survey(root)
    record = state_file(root)
    known = read_state(record)
    if not walk.whole:
        return Pruned(unwalked=walk.unwalked)
    base = Path(root)
    dead = set(dead_entries(known, walk))
    deleted: list[Path] = []
    gone: list[str] = []
    held: list[tuple[str, str]] = []
    cleared: list[tuple[str, Superseded]] = []
    for speech_id, entry in sorted(known.clips.items()):
        kept = False
        for item in entry.superseded:
            why = _remove(speech_id, item.filename, item.where, walk, base, deleted)
            if why:
                held.append((speech_id, why))
                kept = True
            else:
                cleared.append((speech_id, item))
        if speech_id not in dead:
            continue
        why = _remove(speech_id, entry.filename, entry.where, walk, base, deleted) or (
            STILL_NAMES if kept else ""
        )
        if why:
            held.append((speech_id, why))
            continue
        gone.append(speech_id)
    # ⭐ Files first, then the record: superseded clips of kept entries, then whole entries.
    live = forget_superseded(record, [pair for pair in cleared if pair[0] not in gone])
    return Pruned(
        deleted=tuple(deleted),
        forgotten=forget(record, gone),
        held=tuple(held),
        cleared=live,
    )


def _remove(
    speech_id: str, filename: str, where: str | None, walk: Walk, root: Path, deleted: list[Path]
) -> str:
    """Unlink one recorded clip if it is a file; return why it is held, or `""`."""
    clip, why = _clip_path(speech_id, filename, where, walk, root)
    if clip is None:
        return why
    if clip.is_file():
        clip.unlink()
        deleted.append(clip)
    elif clip.exists() or clip.is_symlink():
        return NOT_A_FILE
    return ""


def _clip_path(
    speech_id: str, filename: str, where: str | None, walk: Walk, root: Path
) -> tuple[Path | None, str]:
    """Where one recorded clip is, from the record when it says, or why the prune may not say."""
    if "/" in filename or "\\" in filename or filename in ("", ".", ".."):
        return None, NOT_ITS_CLIP
    try:
        named, _ = parse_clip_name(filename.rpartition(".")[0])
        key = unit_key_of(speech_id.partition(SEGMENT)[0])
    except SpeakableError:
        return None, NOT_ITS_CLIP
    if named != speech_id:
        return None, NOT_ITS_CLIP
    if where is not None:
        recorded = located(root, where, filename)
        return (recorded, "") if recorded is not None else (None, NOT_ITS_CLIP)
    into = walk.audio.get(key)
    if into is None:
        return None, UNDECLARED
    return into / filename, ""
