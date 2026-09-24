r"""The stage itself: one corpus root in, its clips placed and recorded.

**What it does.** Reads the corpus's declarations, derives every unit's speech
units, probes the narration service **once**, and hands each unit's units to
`narrate.synth.synthesise` with the one `Conditions` that probe produced and
the directory `corpus.placement` names for that unit's audio.

**How you use it.** `narrate_corpus(root, client, voice=…, fmt=…)` returns a
`Narrated`. ⭐ `client` is an argument so a test can hand in a recording
transport; `cli.main` builds the real one.

**Depends on.** `generate.declarations` for the corpus walk and `unit_location`,
the one derivation of where a unit's artifacts go, which the page also asks;
`unit.builder` for each unit's served document, `narrate.speakable`
for its speech units, `narrate.synth` for the pass, `narrate.answers`
for the client's shape, and `cli.narrate.disclosure` for the dead-entry count.
⛔ Not `narrate.client` or `narrate.wire`: the dispatcher imports this module
for every verb, so the client is `cli.main`'s to import when it runs.
⛔ It names no source (R1) and composes no path (R4).

## ⛔ `probe()` is called HERE, exactly once, and never per unit

⭐ The narration service and `narrate.synth` both leave the probe to the caller:
a corpus probes once and every unit is synthesised under the one answer. ⛔ An
unchanged re-run therefore sends that one `GET /healthz` and nothing else — the
probe is how the pass learns whether the deployment's conditions moved, so it
cannot be skipped.

## ⛔ The order is what makes a refusal cost nothing

1. The corpus is read and every unit's speech is derived — a corpus defect is
   reported before the network is touched.
2. The record is read — an unreadable one stops before a single request (R9).
3. The service is probed. ⭐ **Absent is an answer, not an error** (R6, R8):
   `Narrated.health.reachable` is `False`, nothing is requested, nothing written.
4. Units are synthesised in declared order. A service that goes away part-way
   stops the stage with every earlier clip placed and recorded.

## ⛔ `narrate` DELETES NOTHING, and says what it would have to (R3, R6)

⭐ **The dead-entry disclosure is `Narrated.dead`**: the record entries whose speech
id this walk did not produce, counted before the probe so an absent service
still reports it. ⛔ **Nothing on this path removes a file or an entry** —
`synthesise` merges into the record (answer 2), and the prune is
`prune.prune_corpus`, reached only by `--prune`. `survey` is the ONE walk both
share, so the count and the prune cannot disagree about what was produced.

⚠️ **The report is not the truth; the disk and the record are.** A unit whose
synthesis raised has its placed clips recorded by `synthesise`'s own `finally`
but no `Synthesis` here — the next run finds them fresh.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from studyforge.cli.narrate.disclosure import Walk, dead_entries, superseded_clips
from studyforge.generate.declarations import Corpus, UnitSource, read_corpus, unit_location
from studyforge.narrate.answers import Health, NarrationError, Narrator
from studyforge.narrate.speakable import SpeechUnit, speakable_of
from studyforge.narrate.synth import (
    Conditions,
    StateError,
    Synthesis,
    audio_dir,
    read_state,
    state_file,
    synthesise,
)
from studyforge.unit.builder import build_unit


@dataclass(frozen=True, slots=True)
class Narrated:
    """What one run of the stage did, unit by unit.

    ⛔ `health` is the ONE probe's answer. `units` pairs a unit key with its
    `Synthesis`; `stopped` is the sentence a mid-run failure raised, if any.
    """

    health: Health
    units: tuple[tuple[str, Synthesis], ...] = ()
    stopped: str | None = None
    #: ⭐ The dead-entry disclosure: record entries the walk did not produce, sorted.
    dead: tuple[str, ...] = ()
    #: Declared units the walk had no material for — ⛔ non-empty means partial.
    unwalked: tuple[str, ...] = ()
    #: ⭐ Clips the record names as superseded, counted when the run returns.
    superseded: tuple[tuple[str, object], ...] = ()

    @property
    def written(self) -> tuple[Path, ...]:
        """Every clip this run placed, in declared unit order."""
        return tuple(path for _, done in self.units for path in done.written)

    @property
    def fresh(self) -> int:
        """How many speech units were already synthesised under these conditions."""
        return sum(len(done.fresh) for _, done in self.units)

    @property
    def failed(self) -> tuple[tuple[str, str], ...]:
        """`(speech id, reason)` for every unit the service could not synthesise."""
        return tuple(item for _, done in self.units for item in done.failed)

    @property
    def retryable(self) -> tuple[str, ...]:
        """Speech ids a job stopped early on; resubmitting asks only for these."""
        return tuple(item for _, done in self.units for item in done.retryable)

    @property
    def unsettled(self) -> tuple[str, ...]:
        """Speech ids placed under a format the run did not ask for."""
        return tuple(item for _, done in self.units for item in done.unsettled)


@dataclass(frozen=True, slots=True)
class UnitWork:
    """One unit's speech and where its clips go — ⛔ both derived before any request."""

    key: str
    speech: tuple[SpeechUnit, ...]
    into: Path


def unit_work(root: Path | str, source: UnitSource, corpus: Corpus) -> UnitWork:
    """Derive one declared unit's speech units and the audio directory its own page links."""
    document = build_unit(source.directory, declared_practices=source.declared_practices)
    at = unit_location(corpus, source)
    return UnitWork(source.key, speakable_of(document).units, audio_dir(root, at))


def survey(root: Path | str) -> tuple[tuple[UnitWork, ...], Walk]:
    """Read the corpus and derive every walked unit's speech and audio directory.

    ⛔ The ONE walk `narrate` and `prune` share. No request and no write.
    """
    corpus = read_corpus(root)
    work = tuple(unit_work(root, source, corpus) for source in corpus.units)
    walk = Walk(
        produced=frozenset(unit.id for item in work for unit in item.speech),
        audio={item.key: item.into for item in work},
        unwalked=tuple(sorted(corpus.absent)),
    )
    return work, walk


def narrate_corpus(
    root: Path | str,
    client: Narrator,
    *,
    voice: str,
    fmt: str,
) -> Narrated:
    """Narrate every declared unit of the corpus at `root`, probing the service once.

    ⛔ Raises `BuildError` for a corpus it cannot read and `StateError` for a
    record it cannot read, both before any request. `PersonalDataLeak` travels
    through untouched.
    """
    work, walk = survey(root)
    record = state_file(root)

    def disclosed() -> dict:
        """Read the disclosure off the record as it stands when the run returns."""
        state = read_state(record)
        return {
            "dead": dead_entries(state, walk),
            "unwalked": walk.unwalked,
            "superseded": superseded_clips(state),
        }

    disclosed()
    # ⛔ An unstated voice or format is refused here, before the probe is sent.
    Conditions(voice, fmt)
    health = client.probe()
    if not health.reachable:
        return Narrated(health=health, **disclosed())
    conditions = Conditions.of(health, voice=voice, fmt=fmt)
    done: list[tuple[str, Synthesis]] = []
    for unit in work:
        if not unit.speech:
            continue
        try:
            synthesis = synthesise(
                unit.speech, client=client, conditions=conditions, into=unit.into, state=record
            )
        except StateError:
            raise
        except NarrationError as failure:
            return Narrated(health=health, units=tuple(done), stopped=str(failure), **disclosed())
        done.append((unit.key, synthesis))
    return Narrated(health=health, units=tuple(done), **disclosed())
