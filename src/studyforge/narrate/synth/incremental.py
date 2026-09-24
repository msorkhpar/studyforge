r"""The pass: which clips must be made now, and the run that makes only those.

**What it does.** Sorts speech units into *already synthesised under the
conditions in force* and *not*, **before a request is built** — then submits only
the second set, places what comes back, and hands the record next door what it
learned.

⛔ **Four ways to be stale and every one is checked**, including that the file is
actually on disk: a record agreeing with itself is what reported *"0
synthesised"* over 619 clips that were not there. ⚠️ The acceptance is asserted
over the set of files written and the set of ids submitted, never over this
module's own report.

⛔ **Nothing is requested when nothing is stale.** An empty plan reaches no batch
and therefore no transport, which is the *"requests nothing"* half of the
acceptance made a property of the shape rather than a promise.

⛔ **Nothing is deleted, and nothing written goes unnamed** (R3,
R6). Every clip is recorded with the directory it was written into, and a
clip a re-wording replaces stays on disk as the entry's `superseded` until a
prune, so a prune can reach it without scanning a directory.

**Depends on.** `synth.record` — one way, never the reverse.
"""

from __future__ import annotations

from collections.abc import Iterator, Mapping, Sequence
from dataclasses import dataclass, replace
from pathlib import Path

from studyforge.corpus.placement import AUDIO_DIRNAME, UnitLocations
from studyforge.describe import describe
from studyforge.narrate.answers import Narrator, place
from studyforge.narrate.speakable.naming import clip_name
from studyforge.narrate.speakable.records import SpeechUnit
from studyforge.narrate.synth.location import Superseded, located, order, root_of, where_of
from studyforge.narrate.synth.record import (
    Clip,
    Conditions,
    State,
    StateError,
    read_state,
    write_state,
)

#: ⚠️ The service caps a request body at 4 MiB and this client does not split
#: for you. Counted in characters of speech, well under that cap once
#: the envelope and worst-case multi-byte encoding are paid for.
DEFAULT_BATCH_CHARS = 500_000

#: Why a unit is stale. ⛔ Sentences, because a person reads them (R6).
NO_RECORD = "no record of this unit"
WORDS_MOVED = "the wording or the format changed"
CONDITIONS_MOVED = "the conditions changed"
CLIP_ABSENT = "the clip is not on disk"


def audio_dir(root: Path | str, locations: UnitLocations) -> Path:
    """Return where one unit's clips go: its placement answer, rooted — ⛔ never composed here.

    ⛔ **`locations` is the ONE derivation**, the unit's
    `generate.declarations.unit_location`, which takes what `unit_stem` takes,
    the label included. `narrate`, the build's read and the page hold that one
    answer, so no stem is spelled here and no argument of it can be dropped here.

    ⭐ The *"through the placement policy"* half of synthesis: a caller that
    composed the media directory itself would be the second layout authority R4
    removes, and that mistake is invisible under one of the two profiles, whose
    media directory happens to sit where a hand-composed path would put it.
    """
    return Path(root) / Path(str(locations.media_dir(AUDIO_DIRNAME)))


def wanted_name(unit: SpeechUnit, conditions: Conditions) -> str:
    """Return the filename this unit's clip must have under `conditions`.

    ⛔ The stem comes from `speakable`'s one minter, which takes the whole unit so an
    id cannot be paired with words that are not its own.
    """
    return f"{clip_name(unit)}.{conditions.fmt}"


@dataclass(frozen=True, slots=True)
class Plan:
    """Which units owe synthesis, and why — ⛔ decided before anything is requested."""

    stale: tuple[SpeechUnit, ...]
    fresh: tuple[str, ...]
    reasons: Mapping[str, str]


def plan(
    units: Sequence[SpeechUnit],
    *,
    into: Path | str,
    state: State,
    conditions: Conditions,
) -> Plan:
    """Sort `units` into what must be synthesised and what already is."""
    directory = Path(into)
    fingerprint = conditions.fingerprint
    stale: list[SpeechUnit] = []
    fresh: list[str] = []
    reasons: dict[str, str] = {}
    for index, unit in enumerate(units):
        if not isinstance(unit, SpeechUnit):
            raise TypeError(f"segment {index} is {describe(unit)}, not a SpeechUnit")
        recorded = state.clips.get(unit.id)
        wanted = wanted_name(unit, conditions)
        if recorded is None:
            reasons[unit.id] = NO_RECORD
        elif recorded.filename != wanted:
            reasons[unit.id] = WORDS_MOVED
        elif recorded.conditions != fingerprint:
            reasons[unit.id] = CONDITIONS_MOVED
        elif not (directory / wanted).is_file():
            reasons[unit.id] = CLIP_ABSENT
        else:
            fresh.append(unit.id)
            continue
        stale.append(unit)
    return Plan(tuple(stale), tuple(fresh), reasons)


def batches(
    units: Sequence[SpeechUnit], *, budget: int = DEFAULT_BATCH_CHARS
) -> Iterator[tuple[SpeechUnit, ...]]:
    """Split `units` into bodies the service will accept, ⛔ never splitting a unit.

    A unit longer than the whole budget travels alone: the service chunks its own
    text, and cutting a speech unit in half here would change what is said.
    """
    if not isinstance(budget, int) or isinstance(budget, bool) or budget < 1:
        raise ValueError(f"a batch budget is a positive int, got {describe(budget)}")
    current: list[SpeechUnit] = []
    size = 0
    for unit in units:
        cost = len(unit.speak)
        if current and size + cost > budget:
            yield tuple(current)
            current, size = [], 0
        current.append(unit)
        size += cost
    if current:
        yield tuple(current)


@dataclass(frozen=True, slots=True)
class Synthesis:
    """What one pass did. ⛔ `written` is the set of files, not the run's own count."""

    written: tuple[Path, ...]
    fresh: tuple[str, ...]
    reasons: Mapping[str, str]
    failed: tuple[tuple[str, str], ...]
    retryable: tuple[str, ...]
    #: ⚠️ Placed under a name the plan did not ask for — the service answered in
    #: another format. Left visible rather than raised: the clip is good, and the
    #: unit will be re-submitted next run until the deployment agrees.
    unsettled: tuple[str, ...]
    recorded: bool


def synthesise(
    units: Sequence[SpeechUnit],
    *,
    client: Narrator,
    conditions: Conditions,
    into: Path | str,
    state: Path | str,
    budget: int = DEFAULT_BATCH_CHARS,
) -> Synthesis:
    """Synthesise only what is stale, place it, and record what it was made under.

    ⭐ **The record is written in a `finally`**, so a batch that fails after
    earlier batches were placed leaves those placed *and* recorded, and the next
    run asks only for the remainder. ⚠️ A write that itself fails then replaces
    the service's exception — the lesser of the two evils, and a known edge.
    """
    file = Path(state)
    known = read_state(file)
    root, here = _placing(file, into)
    recorded = _settled(dict(known.clips), units, root=root, into=Path(into), here=here)
    decided = plan(units, into=into, state=State(recorded, known.present), conditions=conditions)
    written: list[Path] = []
    failed: list[tuple[str, str]] = []
    retryable: list[str] = []
    unsettled: list[str] = []
    wanted = {unit.id: wanted_name(unit, conditions) for unit in decided.stale}
    try:
        for batch in batches(decided.stale, budget=budget):
            narration = client.narrate(batch)
            # ⛔ A batch that produced nothing places nothing, so a run that
            # synthesised no clip leaves no empty media directory behind.
            if narration.artifacts:
                written.extend(place(narration, into))
            for artifact in narration.artifacts:
                recorded[artifact.speech_id] = Clip(
                    filename=artifact.filename,
                    conditions=conditions.fingerprint,
                    engine=artifact.engine,
                    engine_model=artifact.engine_model,
                    where=here,
                    superseded=_carried(recorded.get(artifact.speech_id), artifact.filename, here),
                )
                if artifact.filename != wanted.get(artifact.speech_id):
                    unsettled.append(artifact.speech_id)
            failed.extend(narration.failed)
            retryable.extend(narration.retryable)
    finally:
        changed = write_state(file, recorded, conditions)
    return Synthesis(
        written=tuple(written),
        fresh=decided.fresh,
        reasons=decided.reasons,
        failed=tuple(failed),
        retryable=tuple(retryable),
        unsettled=tuple(unsettled),
        recorded=changed,
    )


def _placing(file: Path, into: Path | str) -> tuple[Path, str]:
    """Return the corpus root and `into` as the record spells it, refusing before any request.

    ⛔ A directory the record cannot spell relative to its root is a clip nobody
    could locate from the record, so it is refused rather than written.
    """
    try:
        root = root_of(file)
        return root, where_of(into, root)
    except ValueError:
        raise StateError(
            "the audio directory is not under the corpus root this record belongs to, "
            "so its clips could not be located from the record; nothing was requested"
        ) from None


def _settled(
    clips: dict[str, Clip], units: Sequence[SpeechUnit], *, root: Path, into: Path, here: str
) -> dict[str, Clip]:
    """Give each of these units' entries the directory its clip is actually in.

    ⭐ A version-1 entry has none, and one of a unit whose directory moved has
    the old one. ⛔ Only a clip found on disk in `into` moves an entry; one found
    nowhere keeps what it had, so nothing is dropped and nothing is guessed. An
    old copy still at the old directory becomes superseded rather than unnamed.
    """
    for unit in units:
        clip = clips.get(unit.id) if isinstance(unit, SpeechUnit) else None
        if clip is None or clip.where == here or not (into / clip.filename).is_file():
            continue
        superseded = set(clip.superseded)
        old = located(root, clip.where, clip.filename)
        if old is not None and old.is_file():
            superseded.add(Superseded(clip.filename, clip.where))
        clips[unit.id] = replace(clip, where=here, superseded=tuple(sorted(superseded, key=order)))
    return clips


def _carried(previous: Clip | None, filename: str, here: str) -> tuple[Superseded, ...]:
    """Return what an entry supersedes once `filename` in `here` replaces `previous`.

    ⛔ The replaced clip is named, never deleted (answer 2). ⭐ A clip written
    again at a superseded name and directory is current, so it leaves the list.
    """
    if previous is None:
        return ()
    kept = set(previous.superseded)
    moved = previous.filename != filename or (previous.where is not None and previous.where != here)
    if moved:
        kept.add(Superseded(previous.filename, previous.where))
    kept.discard(Superseded(filename, here))
    return tuple(sorted(kept, key=order))
