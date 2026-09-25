"""The authored practices: every exercise the authoring pass committed, joined into the archive.

**What it does.** Finds every exercise bundle the exercises skill committed
under `exercises/` — a code bundle (`bundle.json`) and a quiz (`tests/quiz.json`)
alike — refuses one its gates did not clear, and joins each into the archive of
the container it belongs to: its practice document's fields, and its unit's
practice count raised by one.

**How you use it.** The generated `emit.py` calls it; a person never does.

    held = authored(root)                        # every bundle, checked, once per run
    container, fields = held.joined(container, read.documents(root, container))
    held.finish()                                # a bundle no container claimed refuses

**Depends on.** `exercise.bundle` for the bundle, its places and its emission,
`exercise.gates` for the gate record, `skills.exercises` for the quiz's own
document, and `archive` for `build` and the personal-data gate. ⛔ Nothing here
authors, and nothing here writes a file.

## ⭐ THE SCAFFOLD CARRIES THE PRACTICES, SO `read.py` NEVER DOES

⚠️ **Measured on a real course:** the scaffold had no step for
practice documents, so the course's person wrote one into `read.py`. It read
code bundles only and stopped at the first ordinal with no `bundle.json`, so a
quiz would have ended the count and every exercise after it was lost. ⭐ A
committed bundle is in the same place and the same shape in every corpus, so
reading it is the framework's, and `read.documents` returns the source's own
material only.

## ⛔ A PRACTICE THE PERSON'S READER ALREADY CARRIES IS KEPT, NOT DOUBLED

⭐ An adapter written before this module carries its authored practices
itself. So a practice document `read.documents` already returns at a bundle's
ordinal, carrying that bundle's exact exercise record, is the bundle's own and
is left as it is — its unit already counts it. ⛔ A document at that ordinal
carrying ANY other record is a collision: the source's own practice and an
authored one would share a number, and the run refuses naming the bundle.

## ⛔ AUTHORED PRACTICES NUMBER AFTER THE SOURCE'S OWN, WITH NO GAP

⭐ After joining, a unit's practice documents must be numbered 1 to its count
with none missing. ⚠️ Otherwise `validate`'s practice-count check would refuse
the container map, and a gap would be a lost exercise.

## ⛔ A BUNDLE THE GATES DID NOT CLEAR IS REFUSED HERE, BEFORE ANY DOCUMENT

⭐ Every bundle's gate record must be present, must clear, and must still
digest to the files beside it, or the run refuses naming the bundle's
directory. The generated `emit.py` stages the whole archive and moves it only
at the end, so nothing half-emitted reaches it either way.
"""

from __future__ import annotations

import dataclasses
import json
from dataclasses import dataclass, field
from pathlib import Path

from studyforge.archive.document import build
from studyforge.archive.scrub import assert_clean
from studyforge.exercise.bundle import BUNDLE_FILENAME, BUNDLES_DIRNAME, Places, bundle_of, emit
from studyforge.exercise.gates import drifted, record_of
from studyforge.skills.exercises import QUIZ_DOCUMENT, QuizRefused, quiz_of

#: ⚠️ The date and source an emission is taken with. The generated `emit.py`
#: rebuilds every document with the run's own, so neither reaches the archive.
PLACEHOLDER_DATE = "1970-01-01"
PLACEHOLDER_SOURCE = "-"

#: The fields of an emitted document that `archive.document.build` takes as
#: input. ⭐ The rest (its counts, its digest, its API version) is `build`'s
#: arithmetic over these, and is recomputed.
BUILD_FIELDS = (
    "variant",
    "unit",
    "kind",
    "ordinal",
    "title",
    "blocks",
    "starting_code",
    "exercise",
)

#: ⭐ What a quiz practice shows above its questions. A quiz has no `emit`: its
#: record is the whole exercise, and these two blocks are its page text.
QUIZ_BLOCKS = (
    {"type": "heading", "level": 2, "text": "Check yourself"},
    {
        "type": "para",
        "text": "Questions on what this page has just taught. Choose one answer for each.",
    },
)


class PracticeRefused(RuntimeError):
    """A committed exercise the archive will not carry, and why.

    ⛔ Names the bundle's corpus-relative directory and the rule, never a
    machine path or a value (R7).
    """


@dataclass(frozen=True, slots=True)
class Practice:
    """One committed exercise, cleared by its gates: where it sits and its document's fields."""

    places: Places
    fields: dict

    @property
    def page(self) -> tuple[str, str, int]:
        """The page it joins: `(address key, variant, unit)`."""
        return (self.places.address.key, self.places.variant, self.places.unit)


@dataclass(slots=True)
class Authored:
    """Every committed exercise of one run, by page, and which pages a container has claimed."""

    pages: dict[tuple[str, str, int], tuple[Practice, ...]]
    claimed: set[tuple[str, str, int]] = field(default_factory=set)

    def joined(self, container, documents) -> tuple[object, list[dict]]:
        """Return `container` with its units' practice counts raised, and `documents` joined.

        ⭐ Each unit's authored practices follow its own documents, and a unit
        is refused when its practices are not then numbered 1 to its count.
        """
        found = list(documents)
        units = []
        for unit in container.units:
            page = (container.address.key, container.variant, unit.n)
            self.claimed.add(page)
            added = [one.fields for one in self.pages.get(page, ()) if _new(one, found)]
            found.extend(added)
            units.append(dataclasses.replace(unit, practices=unit.practices + len(added)))
            _require_numbered(found, container, units[-1])
        return dataclasses.replace(container, units=units), found

    def finish(self) -> None:
        """Refuse an exercise no container's units claimed: it would be dropped silently."""
        for page, practices in sorted(self.pages.items()):
            if page not in self.claimed:
                raise PracticeRefused(
                    f"'{practices[0].places.bundle}' is an exercise for unit {page[2]} of "
                    f"'{page[0]}' ({page[1]}), and no container read.containers returned "
                    f"declares that unit. An exercise joins a unit the curriculum "
                    f"records; remove the bundle or correct it."
                )


def authored(root: Path | str) -> Authored:
    """Read every committed exercise under `exercises/`, each checked before any is returned.

    ⛔ One bad bundle refuses the run rather than being skipped (R6).
    """
    base = Path(root)
    tree = base / BUNDLES_DIRNAME
    found: dict[tuple[str, str, int], list[Practice]] = {}
    for path in sorted(tree.rglob(BUNDLE_FILENAME)) if tree.is_dir() else ():
        one = _code(base, path.parent.relative_to(base).as_posix())
        found.setdefault(one.page, []).append(one)
    for path in sorted(tree.rglob(Path(QUIZ_DOCUMENT).name)) if tree.is_dir() else ():
        where = path.parent.parent.relative_to(base).as_posix()
        if path.relative_to(base).as_posix() == f"{where}/{QUIZ_DOCUMENT}":
            one = _quiz(base, path, where)
            found.setdefault(one.page, []).append(one)
    return Authored({page: tuple(sorted(one, key=_ordinal)) for page, one in found.items()})


def _ordinal(practice: Practice) -> int:
    """Sort key: a practice's ordinal on its page."""
    return practice.places.ordinal


def _code(base: Path, where: str) -> Practice:
    """Read one code bundle through the framework's emission, and keep its document's fields."""
    at = f"{where}/{BUNDLE_FILENAME}"
    bundle = bundle_of(json.loads((base / at).read_text(encoding="utf-8")), at)
    if bundle.places.bundle != where:
        raise PracticeRefused(
            f"the bundle at '{where}' declares an identity whose directory is "
            f"'{bundle.places.bundle}', so it is refused rather than emitted under an "
            f"identity nobody can find it by."
        )
    _require_cleared(base, bundle.places, where)
    document = emit(base, bundle, source=PLACEHOLDER_SOURCE, ingested=PLACEHOLDER_DATE).document
    fields = {"address": bundle.address, **{key: document[key] for key in BUILD_FIELDS}}
    if build(source=PLACEHOLDER_SOURCE, ingested=PLACEHOLDER_DATE, **fields) != document:
        raise PracticeRefused(
            f"'{where}' emits a document the archive cannot carry whole: rebuilt from "
            f"{list(BUILD_FIELDS)} it differs from the framework's emission."
        )
    return Practice(bundle.places, fields)


def _quiz(base: Path, path: Path, where: str) -> Practice:
    """Read one quiz's own document, and build its practice document's fields once."""
    try:
        quiz = quiz_of(json.loads(path.read_text(encoding="utf-8")), where)
    except QuizRefused as refused:
        raise PracticeRefused(str(refused)) from None
    _require_cleared(base, quiz.places, where)
    fields = {
        "address": quiz.places.address,
        "variant": quiz.places.variant,
        "unit": quiz.places.unit,
        "kind": "practice",
        "ordinal": quiz.places.ordinal,
        "title": quiz.title,
        "blocks": [dict(block) for block in QUIZ_BLOCKS],
        "exercise": quiz.record,
    }
    build(source=PLACEHOLDER_SOURCE, ingested=PLACEHOLDER_DATE, **fields)
    return Practice(quiz.places, fields)


def _new(practice: Practice, documents: list[dict]) -> bool:
    """Whether `practice` is not already among `documents`, refusing a collision."""
    ordinal = practice.places.ordinal
    for one in _practices_of(documents, practice.places.unit):
        if one.get("ordinal") == ordinal:
            if one.get("exercise") == practice.fields["exercise"]:
                return False
            raise PracticeRefused(
                f"'{practice.places.bundle}' is practice {ordinal} of its unit, and "
                f"read.documents already returns a different practice at that ordinal. "
                f"An authored exercise numbers after the source's own; re-run "
                f"the authoring pass so it numbers from the next free ordinal."
            )
    return True


def _practices_of(documents: list[dict], unit: int) -> list[dict]:
    """Return the practice documents of one unit among `documents`."""
    return [one for one in documents if one.get("unit") == unit and one.get("kind") == "practice"]


def _require_numbered(documents: list[dict], container, unit) -> None:
    """Refuse a unit whose practices are not numbered 1 to its count with none missing."""
    have = sorted(one.get("ordinal") for one in _practices_of(documents, unit.n))
    wanted = list(range(1, unit.practices + 1))
    if have != wanted:
        raise PracticeRefused(
            f"unit {unit.n} of '{container.address.key}' carries {unit.practices} "
            f"practice(s), so its practices must be numbered {wanted}, and they are "
            f"numbered {have}. A gap is a lost exercise, and a repeat overwrites one."
        )


def _require_cleared(base: Path, places: Places, where: str) -> None:
    """Refuse a bundle whose gate record is absent, did not clear, or no longer matches."""
    gates = base / places.gates
    if not gates.is_file():
        raise PracticeRefused(
            f"'{where}' ships no gate record. An authored exercise ships only with the "
            f"record of the gates it cleared (spec §7), so this one was never proven."
        )
    decoded = json.loads(gates.read_text(encoding="utf-8"))
    assert_clean(decoded, places.gates)
    record = record_of(decoded, places.gates)
    if not record.clears:
        raise PracticeRefused(
            f"'{where}' ships a gate record in which not every gate held. A shortfall "
            f"is reported, never emitted: re-author the exercise."
        )
    moved = drifted(base / places.bundle, record.inputs, places.bundle)
    if moved:
        raise PracticeRefused(
            f"'{where}' no longer matches the gate record beside it: {moved[0]} The "
            f"gates were run over other files, so what they proved is not this bundle."
        )
