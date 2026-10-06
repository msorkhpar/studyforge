"""A flashcard deck: cards the reader turns over, with a front and a back.

**What it does.** Defines the `flashcards` kind of exercise record: a `cards` list, each card a
`front`, a `back` and, optionally, the `origin` passage it was written from. The reader flips each
card and marks it known or to see again; what they marked is kept in their own browser. No card is
graded: a deck completes nothing and has no run.

**How you use it.** `cards_of(value, where)` reads the key, `cards_document(cards)` writes it, and
`record.from_document` calls `require_deck_shape` for a record of kind `flashcards`.

**Depends on.** `exercise.errors`, `exercise.cases` for `Origin`, `exercise.quiz.options` for the id
rule and `unit.trust` for R5's narrowing. Nothing that could reach a file, a process or a socket.

## ⛔ A DECK IS `generated` AND `advisory`, ALWAYS

A card is judged by nobody who can be asked again, so no deck may claim to be the source's own
grader: the same pair a quiz is, for the same reason, and refused the same way.

## ⛔ FRONT AND BACK ARE THE WHOLE OF A CARD

A card is `id`, `front`, `back`, and optionally `origin`, in that order. A front and a back are
sentences (non-blank text); the ids are plain tokens and distinct. Whether two fronts ask the same
thing, or a back gives itself away by repeating its front, is the family's gate `C1`.
"""

from __future__ import annotations

from dataclasses import dataclass

from studyforge.describe import describe, describe_keys
from studyforge.exercise.cases import Origin, origin_document, origin_in
from studyforge.exercise.errors import ExerciseError
from studyforge.exercise.quiz import read_id, read_text, require_distinct

#: The key a flashcard record carries in place of a workspace.
CARDS = "cards"

#: One card's keys in the order they are written (R10); `origin` only where a card has one.
CARD_KEYS = ("id", "front", "back", "origin")
REQUIRED_CARD_KEYS = ("id", "front", "back")

#: ⛔ Every key a flashcard record may carry, in `record.EXERCISE_KEYS` order.
DECK_KEYS = ("provenance", "trust", "kind", "origin", CARDS, "concepts")
DECK_REQUIRED_KEYS = (CARDS,)

#: What a deck is, fixed as a quiz's are.
DECK_PROVENANCE = "generated"
DECK_TRUST = "advisory"


@dataclass(frozen=True, slots=True)
class Card:
    """One card: what is asked, what it turns over to, and the passage it was written from."""

    id: str
    front: str
    back: str
    origin: Origin | None = None


def cards_of(value: object, where: str) -> tuple[Card, ...]:
    """Read the `cards` a deck holds, in the order they were written."""
    if isinstance(value, str) or not isinstance(value, (list, tuple)):
        raise ExerciseError(
            f"{where}: 'cards' must be an array of card objects, each {list(CARD_KEYS)}. "
            f"The value is {describe(value)}."
        )
    if not value:
        raise ExerciseError(
            f"{where}: 'cards' is empty. A deck is its cards, and a deck with none shows the "
            f"reader nothing to turn over."
        )
    cards = tuple(_card(entry, where) for entry in value)
    require_distinct([card.id for card in cards], where, "card id")
    return cards


def cards_document(cards: tuple[Card, ...]) -> list[dict]:
    """Return the cards as decoded objects, each in `CARD_KEYS` order (R10)."""
    written = []
    for card in cards:
        one = {"id": card.id, "front": card.front, "back": card.back}
        if card.origin is not None:
            one |= {"origin": origin_document(card.origin)}
        written.append(one)
    return written


def cards_in(record: dict, where: str) -> tuple[Card, ...] | None:
    """Return the cards a record carries, or `None` where it carries none."""
    return cards_of(record[CARDS], where) if CARDS in record else None


def require_deck_shape(record: dict, where: str) -> tuple[str, str]:
    """Refuse every way a flashcard record can be wrong, and return its `(provenance, trust)`."""
    from studyforge.unit.errors import ContentError
    from studyforge.unit.trust import check_test_record

    unknown = [key for key in record if key not in DECK_KEYS]
    if unknown:
        raise ExerciseError(
            f"{where}: a deck carries {list(DECK_KEYS)} and this one also carries "
            f"{describe_keys(unknown)}. A deck turns cards over in place of a workspace: there "
            f"is no file to edit, nothing to execute and no run that could complete it."
        )
    missing = [key for key in DECK_REQUIRED_KEYS if key not in record]
    if missing:
        raise ExerciseError(f"{where}: a deck is missing {missing}. The cards are the whole of it.")
    try:
        pair = check_test_record(record.get("provenance", DECK_PROVENANCE), record.get("trust"))
    except ContentError as error:
        raise ExerciseError(f"{where}: {error}") from None
    if pair != (DECK_PROVENANCE, DECK_TRUST):
        raise ExerciseError(
            f"{where}: a deck is {DECK_PROVENANCE!r} and {DECK_TRUST!r}, and this one declares "
            f"{pair[0]!r} and {pair[1]!r}. No card was checked by anyone who can be asked again, "
            f"so no deck may claim to be the source's own grader."
        )
    return pair


def require_no_cards(record: dict, where: str) -> None:
    """⛔ Refuse `cards` on a record that is not a deck, naming the key."""
    if CARDS in record:
        raise ExerciseError(
            f"{where}: 'exercise' names {[CARDS]} on a record that is not a deck. Cards are what "
            f"a deck carries in place of a workspace or questions, so they are a key nothing "
            f"ever shows here."
        )


def _card(entry: object, where: str) -> Card:
    """Read one card, refusing a key it does not define — because a typo is one."""
    if not isinstance(entry, dict):
        raise ExerciseError(
            f"{where}: a card is an object, {list(CARD_KEYS)}. This one is {describe(entry)}."
        )
    unknown = [key for key in entry if key not in CARD_KEYS]
    missing = [key for key in REQUIRED_CARD_KEYS if key not in entry]
    if unknown or missing:
        raise ExerciseError(
            f"{where}: a card is {list(CARD_KEYS)}, with 'origin' optional. This one is missing "
            f"{missing} and carries {describe_keys(unknown)} the card does not define."
        )
    return Card(
        id=read_id(entry["id"], "a card's", where),
        front=read_text(entry["front"], "a card's 'front' is what it asks", where),
        back=read_text(entry["back"], "a card's 'back' is what it turns over to", where),
        origin=origin_in(entry, where),
    )
