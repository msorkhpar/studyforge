"""One poisoned field in an otherwise valid document, for every field there is.

**What it does.** Takes a reader and a document it accepts, poisons **one leaf
at a time**, and reports every field whose refusal reproduces what it refused.

**How you use it.** `document_census(readers)` where each reader is a
`Reader(name, call, document)`. `leaves(document)` is the walk on its own.

**Depends on.** `copy`, `dataclasses`, this package's `probe` for the poison
values and its `containment` for the directory each reader runs in. Nothing
from `studyforge` — the readers are handed in.

## ⛔ Why the per-callable probe could not reach these

`tests/emission/probe.py` calls a public function with one poisoned argument.
That reaches a refusal raised **at the boundary** and nothing deeper: every
refusal inside a document reader fires only when the *rest* of the document is
valid, so a probe that poisons the whole argument gets refused at the first
gate and never arrives.

⚠️ **Measured: the per-callable probe reports zero echoes on a tree that has
48 of them.** ⛔ That is not the probe being wrong — it is the probe's stated
coverage limit, recorded in `tests/emission/__init__.py` and now closed from
the other side. ⭐ **A check that knows what it cannot see is what let this be
built at all;** the finding was in W1's handoff before the code was.

## ⛔ Two poisons, because one of them is protected by luck

**`POISON`** is a home path, and most readers now gate it: `assert_clean` runs
over the whole document first, refuses it, and the field's own message never
runs. ⚠️ **That is protection by shape list, not by construction** — Ruling 17
measured exactly this, 4 of 10 poison shapes coming back clean *because the
gate's list happened to name them*.

**`ESCAPING`** is an absolute path with nothing personal in it — a build
directory on a shared machine. ⛔ The gate does not refuse it, so it reaches
the field validation underneath, which is where the branches that fire
*because a value is absolute* live. ⭐ Those are the worst sites in the tree:
`manifest/content.py` and `manifest/edits.py` refuse a path for **starting
with a slash** and then quote it.

⚠️ Both are reported separately. A field that leaks only `ESCAPING` is a field
whose safety depends on a list somebody keeps current, and saying so is the
point.
"""

from __future__ import annotations

import copy
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field

from tests.emission.containment import Tally, contained
from tests.emission.probe import POISON, POISON_ROOT

#: An absolute path carrying no personal data at all. ⛔ Assembled, like every
#: poison here, so the repository's own R7 sweep is not asked for an exception.
ESCAPING = "/" + "srv/build-artifacts/material"

#: `(name, value)` for each poison, in report order.
POISONS = (("home path", POISON), ("escaping path", ESCAPING))


@dataclass(frozen=True)
class Reader:
    """One document reader, and a document it accepts."""

    name: str
    call: Callable[[object], object]
    document: object


@dataclass(frozen=True, order=True)
class Leak:
    """One field whose refusal reproduced the value it refused."""

    reader: str
    where: str
    poison: str
    message: str

    def __str__(self) -> str:
        """Name the field and show the message with the poison masked."""
        masked = self.message
        for name, value in POISONS:
            masked = masked.replace(value, f"<the poisoned {name}>")
        return f"{self.reader}: {self.where} ({self.poison})\n      -> {masked}"


@dataclass
class DocumentCensus:
    """What the walk found, and how much of each document it reached."""

    probed: int = 0
    fields: int = 0
    leaks: list[Leak] = field(default_factory=list)
    accepted: int = 0

    #: ⛔ What the containment saw while the readers ran. A reader
    #: is a parser and is expected to write nothing — ⭐ which is a claim, and
    #: this is the instrument that makes it one instead of an assumption.
    contained: Tally = field(default_factory=Tally)

    def report(self) -> str:
        """A one-screen summary, printed into any failure this causes."""
        lines = [
            f"poisoned {self.fields} field(s) across {self.probed} probe(s)",
            f"{len(self.leaks)} refusal(s) reproduce the value they refused",
            f"{self.accepted} probe(s) were accepted — that field refuses nothing",
            f"{self.contained.landed} write(s) landed in directories the harness minted; "
            f"{self.contained.refused} refused inside the poison's namespace; "
            f"{self.contained.spawns} process start(s) refused",
            f"{len(self.contained.escapes)} write(s) aimed outside anything the harness owns",
        ]
        lines += [f"  - {escape}" for escape in sorted(self.contained.escapes)]
        lines += [f"  - {leak}" for leak in sorted(self.leaks)]
        return "\n".join(lines)


def leaves(value: object, where: str = "") -> Iterator[tuple[str, object]]:
    """`(path, value)` for every string a document reaches, keys included.

    ⛔ **Keys as well as values.** A document keyed by a filesystem path is as
    much a leak as one valued by it, and `archive.scrub._walk` already says so
    — this is the same walk asked for a different purpose.
    """
    if isinstance(value, str):
        yield where, value
    elif isinstance(value, dict):
        for key, item in value.items():
            if isinstance(key, str):
                yield f"{where}.<key {key}>", key
            yield from leaves(item, f"{where}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            yield from leaves(item, f"{where}[{index}]")


def replaced(document: object, where: str, poison: str) -> object:
    """`document` with the one leaf at `where` replaced by `poison`."""
    copied = copy.deepcopy(document)
    _put(copied, where.split(".")[1:], poison)
    return copied


def _put(node: object, steps: list[str], poison: str) -> None:
    """Walk `steps` into `node` and overwrite the leaf, in place."""
    step = steps[0]
    if step.startswith("<key "):
        key = step[len("<key ") : -1]
        node[poison] = node.pop(key)  # type: ignore[index]
        return
    key, index = _split(step)
    target = node[key] if key is not None else node  # type: ignore[index]
    if index is not None:
        if len(steps) == 1:
            target[index] = poison  # type: ignore[index]
            return
        _put(target[index], steps[1:], poison)  # type: ignore[index]
        return
    if len(steps) == 1:
        node[key] = poison  # type: ignore[index]
        return
    _put(target, steps[1:], poison)


def _split(step: str) -> tuple[str | None, int | None]:
    """`"units[2]"` → `("units", 2)`; `"[2]"` → `(None, 2)`; `"title"` → `("title", None)`."""
    if "[" not in step:
        return step, None
    name, _, rest = step.partition("[")
    return (name or None), int(rest.rstrip("]"))


def document_census(readers: list[Reader]) -> DocumentCensus:
    """Poison every field of every reader's document, one at a time.

    ⛔ **Every reader runs inside the containment**: a directory the
    harness mints, with every write aimed anywhere else refused and counted.
    ⚠️ Once per reader rather than once per probe — the containment is what the
    call may touch, and that does not change between two fields of one document.
    """
    found = DocumentCensus()
    for reader in readers:
        sites = list(leaves(reader.document, ""))
        found.fields += len(sites)
        with contained(found.contained, reader.name, POISON_ROOT):
            for where, _original in sites:
                for name, poison in POISONS:
                    found.probed += 1
                    raised = _refusal(reader, where, poison)
                    if raised is None:
                        found.accepted += 1
                    elif poison in str(raised):
                        found.leaks.append(Leak(reader.name, where, name, str(raised)))
    return found


def _refusal(reader: Reader, where: str, poison: str) -> BaseException | None:
    try:
        poisoned = replaced(reader.document, where, poison)
    except KeyError, IndexError, TypeError:  # pragma: no cover - a walk the put cannot follow
        return None
    try:
        reader.call(poisoned)
    except BaseException as raised:  # noqa: BLE001 — the message is the subject
        return raised
    return None
