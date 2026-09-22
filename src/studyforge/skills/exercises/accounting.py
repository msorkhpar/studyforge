r"""How every ledger entry ends: as the basis of an exercise, or with a written reason.

**What it does.** Answers spec §7 §3's only question of each entry the ledger
recorded — *is it the basis of at least one exercise, named by that exercise's
`origin`, or is it carried with a written reason it is not?* — and ⛔ **refuses
an entry with neither** (R6). It also writes the ledger document the authoring
skill commits.

**How you use it.**

    from studyforge.skills.exercises.accounting import account, ledger_document

    accounted = account(ledger, origins, reasons, where="the ledger")
    ledger_document(ledger, accounted)     # the decoded object the skill writes

`origins` maps an exercise's name to its `Origin`; `reasons` maps
`ledger.key_of(entry)` to the one sentence saying why nothing was built from it.

**Depends on.** `ledger` for what it is accounting for, `studyforge.exercise`
for `Origin`, `studyforge.exercise.gates` for the token rule a name written
into a record obeys, and `studyforge.describe` for R7. Standard library only.
⛔ The seam runs ONE WAY: this module reads `ledger` and `ledger` reads nothing
back.

## ⛔ TWO ENDINGS, NEVER BOTH AND NEVER NEITHER

⭐ **A silent drop is how *nothing is lost* stops being checkable**, so the
only refusal that matters here is the entry nobody said anything about.
⚠️ **Both is refused too**, and that is not pedantry: a reason SAYS no exercise
was built from this entry, so a reason beside an exercise is a sentence
contradicting the row it sits on.

## ⛔ AN ORIGIN NAMES A FILE OR A REGION, AND A REGION IS `SF-36`'s

⭐ **An entry carries the whole chain of headings that encloses it**, so an
origin naming any ancestor section accounts for it — Ruling 92's region ("this
heading, and everything under it until a heading of the same or shallower
depth") read from the inside. ⛔ **A section the file does not carry is refused,
and so is one it carries twice**, the two faults `validate.source` already
keeps apart as `origin-section-missing` and `origin-section-ambiguous`: zero and
two are both loud.

## ⚠️ AN ORIGIN THAT ACCOUNTS FOR NO ENTRY IS NOT A FAULT

⛔ **A quiz question cites a PASSAGE, and a passage of prose holds no fence**
(spec §7 §7). So an origin is required to resolve to a *file the ledger read*
and to a section that file carries — never to an entry. ⭐ Requiring an entry
would refuse every quiz built from the material the quiz shape exists for,
which is the corpus this milestone has to serve.

## ⭐ THE DOCUMENT IS BYTE-STABLE FOR AN UNCHANGED CORPUS (R10)

⛔ **Nothing here reads a clock, a path outside the corpus, or the order the
caller happened to hand a mapping in.** The entries come out of the ledger in
its order and every exercise list is sorted, so re-running on an unchanged
corpus writes the same bytes.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from studyforge.describe import describe
from studyforge.exercise import ExerciseError, Origin
from studyforge.exercise.gates import require_role
from studyforge.skills.exercises.ledger import Entry, Ledger, LedgerError, Source, key_of

#: The version of the document this module writes. ⛔ Bumped when a reader of
#: the old shape would be *wrong* rather than merely incomplete, which is the
#: archive document's own rule and `bundle_api`'s. Nothing of this shape is on
#: disk anywhere yet, so this is version 1.
LEDGER_API = 1

#: The keys the accounting adds to an entry. ⛔ Both written always, so a reader
#: never has to tell *accounted by nothing* from *the key was forgotten*.
ACCOUNTED_KEYS = ("exercises", "reason")

#: The keys of the ledger document itself, in write order (R10).
LEDGER_KEYS = ("ledger_api", "sources", "entries")

#: Said in a refusal instead of the value (R7): the message tells the author
#: what to write, and the value came out of a file somebody else wrote.
REASON_DESCRIBED = "one sentence saying why no exercise was built from this entry"


@dataclass(frozen=True, slots=True)
class Accounted:
    """One entry, and how it is accounted for: by exercises, or by a written reason."""

    entry: Entry
    exercises: tuple[str, ...]
    reason: str | None


def accounts_for(entry: Entry, origin: Origin) -> bool:
    """Answer whether an exercise built from `origin` accounts for this entry.

    ⭐ A whole-file origin accounts for every entry in that file; a region
    accounts for every entry any of whose enclosing headings it names, which is
    Ruling 92's region read from the inside.
    """
    if origin.path != entry.path:
        return False
    return origin.section is None or origin.section in entry.sections


def account(
    ledger: Ledger,
    origins: Mapping[str, Origin],
    reasons: Mapping[str, str],
    where: str,
) -> tuple[Accounted, ...]:
    """Account for every entry, refusing one with neither an exercise nor a reason.

    ⛔ **Four refusals, one rule each.** An origin naming a file the ledger
    never read is material nothing accounts for; an origin naming a section
    that file does not carry exactly once cannot be resolved; a reason filed
    under no entry is a reason for something that is not there; and an entry
    with neither ending is the silent drop this whole module exists to prevent.
    """
    carried = {source.path: source for source in ledger.sources}
    for name, origin in sorted(origins.items(), key=lambda pair: str(pair[0])):
        _require_origin(_name(name, where), origin, carried, where)
    _require_reasons_land(reasons, {key_of(entry) for entry in ledger.entries}, where)
    accounted = tuple(_row(entry, origins, reasons, where) for entry in ledger.entries)
    for row in accounted:
        _require_one_ending(row, where)
    return accounted


def ledger_document(ledger: Ledger, accounted: tuple[Accounted, ...]) -> dict:
    """Return the decoded object the authoring skill writes, in one fixed order (R10)."""
    return {
        "ledger_api": LEDGER_API,
        "sources": [_source_document(source) for source in ledger.sources],
        "entries": [_entry_document(row) for row in accounted],
    }


def _row(
    entry: Entry, origins: Mapping[str, Origin], reasons: Mapping[str, str], where: str
) -> Accounted:
    """One entry with both of its possible endings read."""
    key = key_of(entry)
    return Accounted(
        entry=entry,
        exercises=tuple(
            sorted(name for name, origin in origins.items() if accounts_for(entry, origin))
        ),
        reason=_reason(reasons.get(key), key, where),
    )


def _source_document(source: Source) -> dict:
    """One file the ledger read, in `SOURCE_KEYS` order."""
    return {"path": source.path, "digest": source.digest, "sections": list(source.sections)}


def _entry_document(row: Accounted) -> dict:
    """One accounted entry, in `ENTRY_KEYS + ACCOUNTED_KEYS` order."""
    return {
        "kind": row.entry.kind,
        "path": row.entry.path,
        "ordinal": row.entry.ordinal,
        "sections": list(row.entry.sections),
        "language": row.entry.language,
        "digest": row.entry.digest,
        "exercises": list(row.exercises),
        "reason": row.reason,
    }


def _name(value: object, where: str) -> str:
    """Return an exercise's name, checked with the gate record's own role rule.

    ⛔ **Re-raised, not re-worded**, exactly as `exercise.cases.origin_in` does
    with `fields.optional_origin`: the sentence that states the shape belongs to
    the module that owns the rule, and the type changes so a caller of this
    package catches one family. ⭐ Both values are tokens written into a record
    and printed in a refusal, so a second spelling of the rule would be the
    duplication this tree keeps refusing.
    """
    try:
        return require_role(value, where)
    except ExerciseError as error:
        raise LedgerError(str(error)) from None


def _require_origin(name: str, origin: Origin, carried: Mapping[str, Source], where: str) -> None:
    """⛔ Refuse an origin naming material the ledger never read, or a region it cannot find."""
    source = carried.get(origin.path)
    if source is None:
        raise LedgerError(
            f"{where}: the exercise {name!r} cites '{origin.path}', which the ledger "
            f"has no entry for, so it is built from material the ledger does not "
            f"account for. Declare the file, or build the exercise from one that is."
        )
    if origin.section is None:
        return
    occurrences = source.sections.count(origin.section)
    if occurrences != 1:
        raise LedgerError(
            f"{where}: the exercise {name!r} cites a section of '{origin.path}' that "
            f"the file carries {occurrences} times, and a region is bounded by a "
            f"heading (Ruling 92). The section is not reproduced here (R7)."
        )


def _reason(value: object, key: str, where: str) -> str | None:
    """Read one written reason, refusing anything a reader could not act on."""
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise LedgerError(
            f"{where}: the reason filed under '{key}' must be {REASON_DESCRIBED}. "
            f"The value is {describe(value)}."
        )
    return value


def _require_reasons_land(reasons: Mapping[str, str], keys: set[str], where: str) -> None:
    """⛔ Refuse a reason filed under no entry — a typo here is a silent drop."""
    stray = sorted(key for key in reasons if key not in keys)
    if stray:
        raise LedgerError(
            f"{where}: {len(stray)} written reason is filed under an entry the ledger "
            f"does not carry, starting at '{stray[0]}'. A reason nothing is keyed to "
            f"excuses nothing, and the entry it was meant for is still unaccounted for."
        )


def _require_one_ending(row: Accounted, where: str) -> None:
    """⛔ Every entry ends one of two ways, and never both or neither (spec §7 §3)."""
    key = key_of(row.entry)
    if row.exercises and row.reason is not None:
        raise LedgerError(
            f"{where}: '{key}' is the basis of {len(row.exercises)} exercise and also "
            f"carries a written reason none was built from it. A reason says no "
            f"exercise was built from this entry, so the two cannot both be true."
        )
    if not row.exercises and row.reason is None:
        raise LedgerError(
            f"{where}: '{key}' is the basis of no exercise and carries no written "
            f"reason it is not. Every fenced example and every test file is one or "
            f"the other (spec §7 §3), because a silent drop is how 'nothing is lost' "
            f"stops being checkable."
        )
