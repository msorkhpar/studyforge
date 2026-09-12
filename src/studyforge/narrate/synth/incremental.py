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

**Depends on.** `synth.record` — one way, never the reverse.
"""

from __future__ import annotations

from collections.abc import Iterator, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

from studyforge.corpus.placement import AUDIO_DIRNAME, Profile
from studyforge.describe import describe
from studyforge.narrate.client import NarrateClient, place
from studyforge.narrate.speakable.naming import clip_name
from studyforge.narrate.speakable.records import SpeechUnit
from studyforge.narrate.synth.record import Clip, Conditions, State, read_state, write_state

#: ⚠️ The service caps a request body at 4 MiB and this client does not split
#: for you (`NS-05`). Counted in characters of speech, well under that cap once
#: the envelope and worst-case multi-byte encoding are paid for.
DEFAULT_BATCH_CHARS = 500_000

#: Why a unit is stale. ⛔ Sentences, because a person reads them (R6).
NO_RECORD = "no record of this unit"
WORDS_MOVED = "the wording or the format changed"
CONDITIONS_MOVED = "the conditions changed"
CLIP_ABSENT = "the clip is not on disk"


def audio_dir(
    root: Path | str,
    profile: Profile,
    address: object,
    ordinal: int,
    title: str,
    *,
    origin: str | None = None,
) -> Path:
    """Ask the placement policy where one unit's clips go — ⛔ never composed here.

    ⭐ This is the *"through the placement policy"* half of this row: a caller
    that composed the media directory itself would be the second layout authority
    R4 removes, and `NS-05/2` measures why that mistake is invisible under one of
    the two profiles.
    """
    where = profile.unit(address, ordinal, title, origin=origin).media_dir(AUDIO_DIRNAME)
    return Path(root) / Path(str(where))


def wanted_name(unit: SpeechUnit, conditions: Conditions) -> str:
    """Return the filename this unit's clip must have under `conditions`.

    ⛔ The stem comes from `SF-16`'s one minter, which takes the whole unit so an
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
    client: NarrateClient,
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
    decided = plan(units, into=into, state=known, conditions=conditions)
    recorded = dict(known.clips)
    written: list[Path] = []
    failed: list[tuple[str, str]] = []
    retryable: list[str] = []
    unsettled: list[str] = []
    wanted = {unit.id: wanted_name(unit, conditions) for unit in decided.stale}
    try:
        for batch in batches(decided.stale, budget=budget):
            narration = client.narrate(batch)
            written.extend(place(narration, into))
            for artifact in narration.artifacts:
                recorded[artifact.speech_id] = Clip(
                    filename=artifact.filename,
                    conditions=conditions.fingerprint,
                    engine=artifact.engine,
                    engine_model=artifact.engine_model,
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
