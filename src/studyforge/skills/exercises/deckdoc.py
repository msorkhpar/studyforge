"""A deck's own document, read back: the one versioned reader of `tests/deck.json`.

**What it does.** Reads the document `gating.gate_deck` writes into a deck's bundle and returns the
deck it describes: where it sits, its title and its exercise record. ⛔ It refuses a document at a
`deck_api` this build does not speak, one whose keys are not the written ones in the written order,
an identity that does not name the directory the document sits in, and a record that is not a deck.

**How you use it.** An adapter reads each committed deck through it, then builds the deck's practice
document from what it returns, exactly as it does a quiz (`quizdoc.quiz_of`):

    text = (root / where / DECK_DOCUMENT).read_text(encoding="utf-8")
    deck = deck_of(json.loads(text), where)
    deck.places, deck.title, deck.record    # the record goes under `exercise`

**Depends on.** `studyforge.version` for R9's one guard, `exercise` for the record and
`exercise.bundle.Places` for where a deck sits. Standard library only. ⛔ No I/O: the caller reads
the file.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from studyforge.address import Address
from studyforge.exercise import Exercise, from_document
from studyforge.exercise.bundle import Places
from studyforge.version import check

#: ⭐ Where a deck's own document sits inside its bundle: `tests/`, because `bundle.layout` closes
#: a bundle's file set and no other name would pass `studyforge validate`'s contents check.
DECK_DOCUMENT = "tests/deck.json"

#: The deck document's version, and its key order (R10).
DECK_API = 1
DECK_KEYS = ("deck_api", "address", "variant", "unit", "ordinal", "title", "exercise")


class DeckRefused(ValueError):
    """A deck document this build cannot read, and why."""


@dataclass(frozen=True, slots=True)
class Deck:
    """One committed deck: where it sits, its title, its record and that record read."""

    places: Places
    title: str
    #: The record as the document holds it, which is what an archive carries.
    record: Mapping[str, object]
    exercise: Exercise


def deck_of(document: object, where: str) -> Deck:
    """Read one deck's own document, found in the bundle directory `where`."""
    at = f"{where}/{DECK_DOCUMENT}"
    if not isinstance(document, dict):
        raise DeckRefused(f"{at} is not a JSON object, so it is not a deck's document")
    check("deck_api", document.get("deck_api"), (DECK_API,), where=at, error=DeckRefused)
    if tuple(document) != DECK_KEYS:
        raise DeckRefused(
            f"{at} does not carry {list(DECK_KEYS)} in that order, so it is not the document the "
            f"authoring pass writes; re-run the pass rather than editing it"
        )
    places = _places(document, at)
    try:
        bundle = places.bundle
    except ValueError:
        raise DeckRefused(f"{at} carries an identity that names no bundle directory") from None
    if bundle != where:
        raise DeckRefused(
            f"{at} declares an identity whose directory is '{bundle}', so it is refused rather "
            f"than emitted under an identity nobody can find it by"
        )
    title = document["title"]
    if not isinstance(title, str) or not title.strip():
        raise DeckRefused(f"{at} carries no title")
    exercise = from_document(document["exercise"], at)
    if not exercise.is_deck:
        raise DeckRefused(f"{at} carries an exercise record that is not a deck")
    return Deck(places, title, document["exercise"], exercise)


def _places(document: Mapping[str, object], at: str) -> Places:
    """Return where the document says its deck sits, refusing a malformed identity."""
    segments, variant = document["address"], document["variant"]
    unit, ordinal = document["unit"], document["ordinal"]
    if (
        not isinstance(segments, list)
        or not all(isinstance(one, str) for one in segments)
        or not isinstance(variant, str)
        or not all(isinstance(one, int) and not isinstance(one, bool) for one in (unit, ordinal))
    ):
        raise DeckRefused(
            f"{at} carries an identity that is not an address of segments, a variant, a unit and "
            f"an ordinal"
        )
    try:
        return Places(Address.of(*segments), variant, unit, ordinal)
    except ValueError:
        raise DeckRefused(f"{at} carries an address that does not read") from None
