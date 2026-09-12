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
3. **Only what the record names.** The path is the walked unit's audio
   directory joined to the entry's filename, and that filename must parse back
   to the entry's own speech id. ⭐ A file beside the clips that no dead entry
   names is never read, let alone deleted — discrimination by PATH.
4. **R3 is the outer bound.** An entry the prune cannot place by rule 3 is
   HELD — kept in the record, its file kept on disk — and reported.

## ⚠️ Why an entry of a unit no longer declared is HELD

The record carries a filename and no directory, and a unit's audio directory
is placement's answer to its declarations — ordinal, title, origin — which an
undeclared unit no longer has. ⛔ Guessing it would compose a path (R4) inside
somebody's repository (R3), so the entry stays visible in the disclosure and
in `held`.

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
from studyforge.narrate.synth import forget, read_state, state_file

#: Why an entry is held. ⛔ Sentences a person reads, and none carries a value (R7).
NOT_ITS_CLIP = "the record names a file that is not this entry's own clip, so it is not deleted"
UNDECLARED = (
    "its unit is no longer declared, so placement cannot say which directory holds its "
    "clip; the entry and any clip are kept"
)
NOT_A_FILE = "what sits at this clip's path is not a file, so it is kept"


@dataclass(frozen=True, slots=True)
class Pruned:
    """What one prune did. ⛔ `deleted` is the set of files unlinked, not a count."""

    unwalked: tuple[str, ...] = ()
    deleted: tuple[Path, ...] = ()
    forgotten: tuple[str, ...] = ()
    held: tuple[tuple[str, str], ...] = ()

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
    deleted: list[Path] = []
    gone: list[str] = []
    held: list[tuple[str, str]] = []
    for speech_id in dead_entries(known, walk):
        clip, why = _clip_path(speech_id, known.clips[speech_id].filename, walk)
        if clip is None:
            held.append((speech_id, why))
            continue
        if clip.is_file():
            clip.unlink()
            deleted.append(clip)
        elif clip.exists() or clip.is_symlink():
            held.append((speech_id, NOT_A_FILE))
            continue
        gone.append(speech_id)
    return Pruned(deleted=tuple(deleted), forgotten=forget(record, gone), held=tuple(held))


def _clip_path(speech_id: str, filename: str, walk: Walk) -> tuple[Path | None, str]:
    """Where one entry's own clip is, or why the prune may not say."""
    if "/" in filename or "\\" in filename or filename in ("", ".", ".."):
        return None, NOT_ITS_CLIP
    try:
        named, _ = parse_clip_name(filename.rpartition(".")[0])
        key = unit_key_of(speech_id.partition(SEGMENT)[0])
    except SpeakableError:
        return None, NOT_ITS_CLIP
    if named != speech_id:
        return None, NOT_ITS_CLIP
    into = walk.audio.get(key)
    if into is None:
        return None, UNDECLARED
    return into / filename, ""
