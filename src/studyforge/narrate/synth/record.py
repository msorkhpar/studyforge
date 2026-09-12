r"""`.studyforge/narration.json` — what a clip was synthesised UNDER (R9).

| | |
|---|---|
| **File** | `.studyforge/narration.json` — ⭐ located by Ruling 351 |
| **Version key** | `narration_api` — ⭐ **minted here**, and registered in `version.CONTRACT_FIELDS` in the same commit |
| **Written by** | `SF-17` — ⛔ **the one writer** (Ruling 330, unchanged) |

⛔ **Ruling 351 deliberately left the FIELDS to this office** (Ruling 344): the
property it fixed is *for each speech unit, whether the clip on disk was
synthesised under the conditions in force now*. The argument for which facts are
conditions and which are provenance is in the package docstring next door.

## ⛔ `check`, NOT `is_supported` — the opposite of `site_api`, from its argument

⭐ The discovery cache may be discarded on an unknown version because the tree
rebuilds it. ⛔ **This record is rebuildable only by re-synthesising every clip
in the corpus** — hours, a service, and no message — so R9's refusal is spent by
**stopping**. That is the whole difference between derived state and a record of
what happened.

## ⛔ NOTHING HERE KNOWS WHERE A CORPUS KEEPS ITS AUDIO

`state_file(root)` composes the record's own name against the placement
package's `GENERATED_ROOT`, and nothing else. The directory is the policy's;
only the filename is this contract's (R4).
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from studyforge.archive.scrub import assert_clean
from studyforge.corpus.placement import GENERATED_ROOT
from studyforge.describe import describe
from studyforge.narrate.client import Health, NarrationError
from studyforge.version import check

ENCODING = "utf-8"

#: R9's key for this contract. ⭐ Minted by `SF-17` (Ruling 351) and registered
#: in `version.CONTRACT_FIELDS` in the same commit, per that tuple's convention.
NARRATION_API = 1
KNOWN_NARRATION_API = frozenset({NARRATION_API})

#: The record's own name. ⚠️ Its **directory** is the placement policy's
#: `GENERATED_ROOT` and is never spelled here — one authority on layout (R4).
NARRATION_STATE_FILENAME = "narration.json"

#: Fixed rather than sorted, so an unchanged corpus renders identical bytes (R10).
STATE_KEYS = ("narration_api", "conditions", "clips")
CLIP_KEYS = ("filename", "conditions", "engine", "engine_model")

#: How much of the conditions' hash is kept. Long enough that two condition sets
#: colliding is not a thing that happens; short enough to read.
FINGERPRINT_LENGTH = 16

#: Appended while the record is being written. A torn `*.writing` file reads as
#: absent; a record half-overwritten in place reads as *present and wrong*.
WRITING_SUFFIX = ".writing"


class StateError(NarrationError):
    """The regeneration record cannot be read, so nothing may be decided from it.

    ⛔ Deliberately a refusal and not a rebuild: discarding this record
    re-synthesises a whole corpus without saying so.
    """


@dataclass(frozen=True, slots=True)
class Conditions:
    """What a clip is synthesised **under** — everything its filename cannot carry.

    ⛔ `voice` and `fmt` are required and non-empty. A build that leaves them to
    the service's default cannot say what its clips were made under, and the
    record would be a claim rather than a fact.
    """

    voice: str
    fmt: str
    provides: int | None = None
    chunk_chars: int | None = None

    def __post_init__(self) -> None:
        """Refuse an unstated voice or format, naming which one is missing."""
        for label, value in (("voice", self.voice), ("format", self.fmt)):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(
                    f"a {label} for the record is a non-empty str, got {describe(value)}; "
                    f"state it rather than letting the service choose, or the record "
                    f"cannot say what a clip was made under"
                )

    @classmethod
    def of(cls, health: Health, *, voice: str, fmt: str) -> Conditions:
        """Read the deployment's half off a `probe()` and pair it with the asked-for half."""
        if not isinstance(health, Health):
            raise TypeError(f"conditions are read from a Health, got {describe(health)}")
        return cls(voice, fmt, health.provides, health.chunk_chars)

    def document(self) -> dict[str, object]:
        """Return the conditions as the object the record carries."""
        return {
            "voice": self.voice,
            "format": self.fmt,
            "provides": self.provides,
            "chunk_chars": self.chunk_chars,
        }

    @property
    def fingerprint(self) -> str:
        """Return the one string a recorded clip is compared against.

        ⛔ Over `sort_keys=True` bytes, so the fingerprint is a property of the
        conditions and not of the order this module happens to write them in.
        """
        canonical = json.dumps(self.document(), sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(canonical.encode(ENCODING)).hexdigest()[:FINGERPRINT_LENGTH]


@dataclass(frozen=True, slots=True)
class Clip:
    """One recorded clip: what it is called, what it was made under, and by what."""

    filename: str
    conditions: str
    engine: str = ""
    engine_model: str = ""

    def document(self) -> dict[str, object]:
        """Return this clip's entry, in `CLIP_KEYS` order."""
        written = {
            "filename": self.filename,
            "conditions": self.conditions,
            "engine": self.engine,
            "engine_model": self.engine_model,
        }
        return {key: written[key] for key in CLIP_KEYS}


@dataclass(frozen=True, slots=True)
class State:
    """The record as this build reads it. ⛔ Absent is a state, not a failure."""

    clips: Mapping[str, Clip]
    present: bool = True


def state_file(root: Path | str) -> Path:
    """Return where the record lives under `root`. ⛔ The directory is the policy's."""
    return Path(root) / GENERATED_ROOT / NARRATION_STATE_FILENAME


def read_state(path: Path | str) -> State:
    """Read the record, or report it absent. ⛔ An unreadable one raises (R9).

    ⚠️ **`check`, not `is_supported`** — see the module docstring. An unknown
    `narration_api` stops rather than quietly re-synthesising a corpus.
    """
    where = NARRATION_STATE_FILENAME
    file = Path(path)
    if not file.is_file():
        return State(clips={}, present=False)
    try:
        payload = json.loads(file.read_text(encoding=ENCODING))
    except (ValueError, UnicodeDecodeError):
        raise StateError(f"{where} is not readable as JSON") from None
    if not isinstance(payload, dict):
        raise StateError(f"{where} holds {describe(payload)}, not an object")
    check(
        "narration_api",
        payload.get("narration_api"),
        KNOWN_NARRATION_API,
        where=where,
        error=StateError,
    )
    return State(clips=_clips_of(payload.get("clips"), where))


def _clips_of(entries: object, where: str) -> dict[str, Clip]:
    """Return the recorded clips, refusing a shape this build cannot decide from."""
    if not isinstance(entries, dict):
        raise StateError(f"{where} holds clips that are {describe(entries)}, not an object")
    clips: dict[str, Clip] = {}
    for speech_id, entry in entries.items():
        if not isinstance(entry, dict):
            raise StateError(f"{where} records {describe(entry)} for a clip, not an object")
        filename, fingerprint = entry.get("filename"), entry.get("conditions")
        if not isinstance(filename, str) or not isinstance(fingerprint, str):
            raise StateError(f"{where} records a clip with no filename or no conditions")
        clips[str(speech_id)] = Clip(
            filename=filename,
            conditions=fingerprint,
            engine=str(entry.get("engine", "")),
            engine_model=str(entry.get("engine_model", "")),
        )
    return clips


def render_state(clips: Mapping[str, Clip], conditions: Conditions) -> str:
    """Return the record's bytes — identical for an unchanged corpus (R10).

    ⚠️ **There is no clock in this document and there is deliberately no room for
    one.** *How stale is this?* is answered by the fingerprints against the
    conditions in force, which is a better answer than a timestamp and needs no
    exemption from R10.

    ⚠️ **The top-level `conditions` are the ones in force at the last write, and
    a clip's own are authoritative.** After a partial failure the two disagree on
    purpose: that is what says which clips still owe a re-synthesis.
    """
    written = {
        "narration_api": NARRATION_API,
        "conditions": conditions.document(),
        "clips": {key: clips[key].document() for key in sorted(clips)},
    }
    document = {key: written[key] for key in STATE_KEYS}
    assert_clean(document, NARRATION_STATE_FILENAME)
    return json.dumps(document, indent=2, ensure_ascii=False, sort_keys=False) + "\n"


def write_state(path: Path | str, clips: Mapping[str, Clip], conditions: Conditions) -> bool:
    """Write the record if its bytes moved, and report whether they did.

    ⛔ **Identical bytes are not rewritten**, so *"re-running with no content
    change writes nothing"* is true of the record as well as of the clips.
    Staged beside the target and moved into place.
    """
    file = Path(path)
    rendered = render_state(clips, conditions).encode(ENCODING)
    if file.is_file() and file.read_bytes() == rendered:
        return False
    file.parent.mkdir(parents=True, exist_ok=True)
    staged = file.with_name(file.name + WRITING_SUFFIX)
    try:
        staged.write_bytes(rendered)
        staged.replace(file)
    finally:
        staged.unlink(missing_ok=True)
    return True
