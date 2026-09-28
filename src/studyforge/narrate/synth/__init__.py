r"""Incremental synthesis, and the record that makes *"nothing changed"* decidable.

**What it does.** Decides, for each speech unit, whether the clip on disk was
synthesised **under the conditions in force now** — and only then asks the
service for the ones that were not.

**How you use it.**

    conditions = Conditions.of(client.probe(), voice="narrator", fmt="opus")
    outcome = synthesise(
        units,
        client=client,
        conditions=conditions,
        into=audio_dir(root, locations),  # the unit's `unit_location`, label and all
        state=state_file(root),
    )

⛔ **`probe()` is the caller's, not this package's** — the service's contract
already says so, and a build probes once for a whole corpus rather than once
per unit. Handing the answer in is what lets an unchanged re-run make **zero**
requests, which is the half of the acceptance a report cannot be trusted for.

**Depends on.** `narrate.recorded` for the record and where a clip goes,
`archive.scrub`, `version`, `narrate.answers`, `narrate.speakable` and
`corpus.placement`. ⭐ The last one is the difference
from `narrate/client.py`, which is asserted **not** to import it: the client
must not know where a study site keeps its audio, and this package is the caller
that asks the policy on its behalf (R4).

⛔ **Not on `narrate.client` and not on `narrate.wire`**. A
build reads the record, and a build never synthesises: the pass takes any
`answers.Narrator`, and a fresh interpreter importing `studyforge.generate` or
`cli/plan` is asserted to load no wire.

## ⛔ WHY A FILENAME IS NOT ENOUGH, AND WHY THIS CONTRACT EXISTS

⭐ `speakable` names a clip `<speech id>-<8 hex of the words>`, so *did the wording
change* is answerable from the name alone and needs no record. ⚠️ **But the
acceptance is *"writes nothing AND REQUESTS NOTHING"*, and a name cannot carry
what a clip was made UNDER.** ⛔ A voice change, a `provides` bump or a
`chunk_chars` change at the deployment leaves every filename byte-identical
while every clip on disk is stale.

⭐ **So the record's subject is the conditions, and the fields are:**

| in the record | why it is there |
|---|---|
| `voice` | not in the name, and it is the whole sound of the clip |
| `format` | in the name's suffix, and recorded so a change is one comparison |
| `provides` | the service's promise. A bump may change what synthesis means |
| `chunk_chars` | ⛔ part of the content address and a **deployment** setting |
| `engine_model` | ⛔ part of the content address, read off `/healthz` |

⚠️ **A clip's own `engine` and `engine_model` are recorded and are NOT compared.**
They are *what made that file* — on a cache hit, the **first** synthesis's rather
than what is deployed — so they are provenance, for a person reading the
record. ⛔ **The deployment's `engine_model` is a different fact**: `/healthz`
reports it, the service's address is taken over it, and so it is a condition.

## ⛔ WHERE IT LIVES, AND WHY IT IS NOT DERIVED STATE

`.studyforge/narration.json`, versioned by `narration_api` — beside
`site.json`, outside the corpus content tree, so §8.2 and R3 both hold.

⚠️ **Unlike the discovery cache it is NOT rebuildable from the tree**, and that
is why an unreadable one **refuses** instead of being discarded: throwing it away
re-synthesises every clip in the corpus, silently, which is the exact outcome the
incremental clause exists to prevent. ⭐ It is therefore state a clone wants to
carry, for the same reason the clips themselves are carried: a clone with the
clips and no record re-synthesises all of them on its first build.

⛔ **This package holds no opinion about how any file reaches a clone** — `into`
and `state` are arguments, and what is or is not carried is a manifest policy
(`corpus.manifest`).

## ⛔ THE SEAM, AND WHY THIS IS A PACKAGE

⭐ **`record` answers *"what were these clips made under"*; `incremental`
answers *"which ones must be made now"*.** ⛔ Written as one module it read
**466 against R11's 400**, and R11's remedy is a split at a named seam rather
than a trim — the same answer `narrate/speakable/` reached one row earlier, in
this same package, for the same reason.

⚠️ The dependency runs one way: `incremental` imports `record`, never the
reverse, and both import `location`, which imports neither. The
contract must be readable by something that is not the pass — a
report, a coverage tracker, a person — without dragging a client in.

⭐ **So `record` and `location` live in `narrate.recorded`, outside this
package**, and this package re-exports them unchanged. ⛔ A build, a plan and
the study server read the record; none of them synthesises, and a learner's copy
of a course carries the server with no synthesis in it (`studyforge.release`).

## ⛔ ONE UNIT'S FAILURE DOES NOT COST ANOTHER ITS CLIP

Stale units go out in batches under a character budget, because the service caps
a body and the service does not split for you. ⭐ **Each batch's artifacts are placed
before the next is submitted, and the record is written in a `finally`** — so a
service that goes away half-way through a corpus leaves every clip it did produce
placed *and recorded*, and the next run asks only for the remainder.
"""

from studyforge.narrate.recorded.location import Superseded, audio_dir, located, root_of, where_of
from studyforge.narrate.recorded.record import (
    CLIP_KEYS,
    KNOWN_NARRATION_API,
    NARRATION_API,
    NARRATION_STATE_FILENAME,
    STATE_KEYS,
    SUPERSEDED_KEY,
    WRITING_SUFFIX,
    Clip,
    Conditions,
    State,
    StateError,
    forget,
    forget_superseded,
    read_state,
    render_state,
    state_file,
    the_one_file,
    write_state,
)
from studyforge.narrate.synth.incremental import (
    CLIP_ABSENT,
    CONDITIONS_MOVED,
    DEFAULT_BATCH_CHARS,
    NO_RECORD,
    WORDS_MOVED,
    Plan,
    Synthesis,
    batches,
    plan,
    synthesise,
    wanted_name,
)

#: ⛔ The package's whole public surface.
__all__ = [
    "CLIP_ABSENT",
    "CLIP_KEYS",
    "CONDITIONS_MOVED",
    "DEFAULT_BATCH_CHARS",
    "KNOWN_NARRATION_API",
    "NARRATION_API",
    "NARRATION_STATE_FILENAME",
    "NO_RECORD",
    "STATE_KEYS",
    "SUPERSEDED_KEY",
    "WORDS_MOVED",
    "WRITING_SUFFIX",
    "Clip",
    "Conditions",
    "Plan",
    "State",
    "Superseded",
    "StateError",
    "Synthesis",
    "audio_dir",
    "batches",
    "forget",
    "forget_superseded",
    "located",
    "plan",
    "read_state",
    "render_state",
    "root_of",
    "state_file",
    "synthesise",
    "the_one_file",
    "wanted_name",
    "where_of",
    "write_state",
]
