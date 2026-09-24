r"""One component's `consuming.json`, read — and nothing else of that component.

**What it does.** Decodes a sibling component's machine-readable consuming
contract, checks the two versions R9 puts on it, and resolves a key path out of
it or refuses by naming the path it wanted.

**How you use it.** `read(text, component=…, api=…, promise=…)` for the
document, `require(document, *path)` for a key this renderer cannot work
without, `optional(document, *path, default=…)` for one it can.

**Depends on.** `archive.scrub` for R7's gate — what this decodes, it gates —
`describe` for refusals, and `skills.buildserve.narration` for the one promise
this framework has already recorded. ⛔ Nothing else, and no I/O: the caller
opens the file, so a test never needs a sibling on disk.

## ⛔ ONE FILE, AND THE THREE THIS NEVER READS (R18)

`consuming.json`. ⛔ **Never the component's `Dockerfile`**: a consumer that
renders a compose file by reading one has forked the component, and the fork is
silent — the next image moves a path the consumer copied, nothing refuses, and
the two drift until a reader's build cannot write its own cache. ⛔ **Never its
README**, which is prose for a person. ⛔ **Never its own renderer**, which is a
second implementation of the thing this one is supposed to be a reader of.

## ⭐ A MISSING KEY IS A FINDING, NEVER A VALUE TYPED IN HERE (R19)

`require` raises and names the key path it wanted. ⛔ **That refusal is the
finding's evidence, and answering it by writing the value into this package is
the exact defect R19 forbids** — the component's contract would have stopped
being sufficient and nothing would say so. ⭐ Spec §8.1 says
`consuming.json` is sufficient to generate a working compose file with no other
input; this package is where that is demonstrated rather than asserted, and a
`require` that fires is the demonstration failing out loud.

## ⛔ THE ONLY ACCOUNT NAME A CONTRACT MAY CARRY IS ITS OWN CONTAINER USER'S

⚠️ **Measured, and it is why this module does not hand the raw document to the
gate.** A component's contract legitimately states the paths inside its own
image — a workspace root, a cache directory, a settings directory — and those
hang off the home of the account that image declares it runs as. ⛔ R7's gate
cannot tell that home from the host user's, and refuses it: both the runtime
gate and this repository's own sweep read one as a leak.

⭐ **So the home of an account the contract DECLARES as its own is masked
before the gate reads the document, and every other home shape still refuses.**
⛔ **That is narrow on purpose and it is not an off switch**: the name masked
is read out of the document's own `runs_as.user`, so a contract carrying
somebody else's home path is refused exactly as before, and a contract that
declares no user masks nothing. ⚠️ A contract naming an account it never
declared is the shape this would otherwise hide, and it is the shape a test
plants.

## ⛔ THE PROMISE IS RECORDED, THE SHAPE IS REFUSED (R9)

⭐ **`provides` is the component's promise and `consuming_api` is the file's
shape**, and they move for different reasons — so they are checked differently:

- **`provides` below what this renderer was written against is refused**: keys
  it reads may not exist yet, and guessing at their absence is migration.
- **`provides` above it is read.** The component's own contract says adding
  keys for a consumer moves `provides` and leaves what is there alone, so
  refusing a newer component would make every release break every consumer.
- ⛔ **A `consuming_api` this renderer does not know is refused outright.** That
  field versions the *shape* of what is already there, and a shape nobody has
  read is not a shape to guess at. ⚠️ Nothing is ever migrated, which is the
  half of R9 that is about all of them.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence

from studyforge.archive.scrub import assert_clean, scrub
from studyforge.describe import describe
from studyforge.skills.buildserve import narration

#: The one file a component publishes for its consumers, at its root beside its
#: pins. ⭐ One spelling for every component: `narrate-service` puts its there
#: and so does `code-server-toolchain`, and this framework's existing reader
#: already names it by that path.
CONSUMING = "consuming.json"

#: The component whose editor image this skill renders a compose file for.
#: ⭐ A component of this framework, never a source (R1) — `workspace.json`
#: pins it as a sibling checkout, exactly as it pins the narration service.
EDITOR_COMPONENT = "code-server-toolchain"

#: ⛔ The `consuming_api` this renderer knows the shape of.
EDITOR_API = 1

#: ⛔ The `provides` promise this renderer was written against. ⚠️ A **record**,
#: not a constraint this skill imposes: the component asks every consumer to
#: record the number it built against, and
#: `tests/studyforge/skills/execution/test_contract.py` re-reads it wherever
#: the sibling is on disk.
EDITOR_PROMISE = 2

#: The component that synthesises narration, and the promise this framework
#: already recorded for it. ⛔ Imported, never respelled: a second copy of a
#: promise is a copy that goes stale in silence, and `buildserve.narration` is
#: where this framework keeps that one.
NARRATION_COMPONENT = narration.COMPONENT

#: ⛔ The narration contract's shape, beside the promise `narration` records.
NARRATION_API = 1

#: ⛔ The narration component's promise, **imported and never respelled**. ⭐ A
#: second copy of a promise is a copy that goes stale in silence, and
#: `buildserve.narration` is where this framework already keeps that one.
NARRATION_PROMISE = narration.PROMISE


#: What a declared container home is replaced by before the gate reads the
#: document. ⛔ **Not `scrub`'s placeholder, deliberately**: that one is what
#: this framework writes into its OWN output, and this is a mask over a copy
#: that nothing is written from. ⚠️ It must carry no shape of its own, which is
#: why it is a phrase and not a path.
MASK = "<container home>"

#: The two path roots a home directory hangs off. ⛔ **Not a second copy of
#: R7's rule** — the gate is still the thing that refuses. This is only the
#: pair whose *declared* occupant this reader masks before handing a component's
#: contract to it.
HOME_ROOTS = ("home", "Users")


class ContractRefused(ValueError):
    """A component contract this renderer will not render against, and why."""


def read(
    text: str,
    *,
    component: str,
    api: int,
    promise: int,
    where: str = CONSUMING,
) -> Mapping[str, object]:
    """Decode one `consuming.json`, gated and version-checked.

    ⛔ Raises `ContractRefused` for anything that is not this component's
    contract at a shape and a promise this renderer has read.
    """
    try:
        document = json.loads(text)
    except (TypeError, ValueError) as exc:
        raise ContractRefused(f"{scrub(where)} is not valid JSON: {scrub(str(exc))}") from None
    if not isinstance(document, dict):
        raise ContractRefused(f"{scrub(where)} must be a JSON object, got {describe(document)}")
    assert_clean(_masked(document, _homes(document)), where)
    named = document.get("component")
    if named != component:
        raise ContractRefused(
            f"{scrub(where)} declares component {scrub(str(named))}, and this renderer "
            f"reads {scrub(component)}'s contract; the wrong sibling is pinned"
        )
    _version(document, "consuming_api", api, where, exact=True)
    _version(document, "provides", promise, where, exact=False)
    return document


def container_users(document: Mapping[str, object]) -> tuple[str, ...]:
    """Every account name this contract declares one of its own containers runs as."""
    found: set[str] = set()
    _users(document, found)
    return tuple(sorted(found))


def require(document: Mapping[str, object], *path: str) -> object:
    """Return the value at `path`, or refuse by naming the key path it wanted.

    ⭐ **The refusal is a finding against the component's contract** (R19), and
    the only legal answer to it is a key added there — never a value added here.
    """
    found = optional(document, *path, default=_MISSING)
    if found is _MISSING:
        raise ContractRefused(
            f"the contract carries no {scrub('.'.join(path))}. ⛔ This renderer needs it "
            f"and will not invent it: that key is a finding against the component "
            f"that publishes {CONSUMING}, not a value to write into this skill (R19)"
        )
    return found


def optional(document: Mapping[str, object], *path: str, default: object = None) -> object:
    """Return the value at `path`, or `default` where any step of it is absent."""
    found: object = document
    for key in path:
        if not isinstance(found, Mapping) or key not in found:
            return default
        found = found[key]
    return found


def words(document: Mapping[str, object], *path: str) -> tuple[str, ...]:
    """Return a required list of strings at `path`, refusing anything else."""
    found = require(document, *path)
    if not isinstance(found, Sequence) or isinstance(found, str):
        raise ContractRefused(
            f"the contract's {scrub('.'.join(path))} must be a list, got {describe(found)}"
        )
    for entry in found:
        if not isinstance(entry, str):
            raise ContractRefused(
                f"every entry of the contract's {scrub('.'.join(path))} must be a string, "
                f"and one is {describe(entry)}"
            )
    return tuple(found)


def blocks(document: Mapping[str, object], *path: str) -> tuple[Mapping[str, object], ...]:
    """Return a required list of objects at `path`, refusing anything else."""
    found = require(document, *path)
    if not isinstance(found, Sequence) or isinstance(found, str):
        raise ContractRefused(
            f"the contract's {scrub('.'.join(path))} must be a list, got {describe(found)}"
        )
    for entry in found:
        if not isinstance(entry, Mapping):
            raise ContractRefused(
                f"every entry of the contract's {scrub('.'.join(path))} must be an object, "
                f"and one is {describe(entry)}"
            )
    return tuple(found)


#: ⭐ A sentinel, so `optional` can tell *absent* from a declared `null`. ⛔ A
#: contract that declares `null` has said something; `None` as the absence
#: marker would read the two as one answer.
_MISSING = object()


def _users(value: object, found: set[str]) -> None:
    """Collect every `runs_as.user` anywhere in the document."""
    if isinstance(value, Mapping):
        declared = value.get("runs_as")
        if isinstance(declared, Mapping) and isinstance(declared.get("user"), str):
            found.add(str(declared["user"]))
        for item in value.values():
            _users(item, found)
    elif isinstance(value, Sequence) and not isinstance(value, str):
        for item in value:
            _users(item, found)


def _homes(document: Mapping[str, object]) -> tuple[str, ...]:
    """Return the home prefixes this contract declares as its own containers'."""
    return tuple(f"/{root}/{user}" for user in container_users(document) for root in HOME_ROOTS)


def _masked(value: object, homes: Sequence[str]) -> object:
    """Copy `value`, replacing each declared container home with the mask."""
    if isinstance(value, Mapping):
        return {key: _masked(item, homes) for key, item in value.items()}
    if isinstance(value, Sequence) and not isinstance(value, str):
        return [_masked(item, homes) for item in value]
    if isinstance(value, str):
        for home in homes:
            value = value.replace(home, MASK)
        return value
    return value


def _version(
    document: Mapping[str, object], field: str, held: int, where: str, *, exact: bool
) -> None:
    """Check one R9 field of a component's contract, and never migrate it."""
    found = document.get(field)
    if not isinstance(found, int) or isinstance(found, bool):
        raise ContractRefused(
            f"{scrub(where)}'s {field} must be a whole number, got {describe(found)}"
        )
    if found < held or (exact and found != held):
        raise ContractRefused(
            f"{scrub(where)} declares {field} {found} and this renderer was written "
            f"against {held}. ⛔ Nothing is migrated (R9): re-pin the component, or "
            f"read its contract and move the recorded number in one commit"
        )
