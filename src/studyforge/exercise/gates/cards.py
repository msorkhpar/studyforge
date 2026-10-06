"""The `cards` family, `C1` and `C2`: the gates a deck of flashcards clears before it ships.

**What it does.** Answers the two gates of a deck, and registers the family so a record naming it is
complete only with both. `C1` holds when every card is a sound card: a front and a back that are
not one text, a back short enough to be a card, and no two fronts that ask the same thing. `C2`
holds when every card cites the passage it was written from and that passage still digests to what
the ledger has.

**How you use it.**

    verdicts = check_cards(exercise, origins, ledger, where)
    cited = cited_for(exercise.cards, ledger, where)      # at authoring time

**Depends on.** `gates.families` for the registry, `gates.digests` for `Cited`, `gates.record` for
`Verdict`, `exercise.deck` for the cards and `exercise.quiz` for the one normal form two texts are
compared in. Standard library otherwise.

## ⛔ BOTH ARE MECHANICAL, AND `validate` CAN RE-TAKE BOTH

⭐ Unlike a quiz's `Q1` to `Q3`, no judgement is taken once and shipped: a card's rule is its shape,
and its passage is a digest. ⛔ A card is named by its front, never by its id (R7: an id is a value
a record has no reason to copy into a sentence).
"""

from __future__ import annotations

from collections.abc import Mapping

from studyforge.describe import describe
from studyforge.exercise.deck import DECK_PROVENANCE, DECK_TRUST, Card
from studyforge.exercise.errors import ExerciseError
from studyforge.exercise.gates.digests import Cited
from studyforge.exercise.gates.families import Family, register
from studyforge.exercise.gates.record import Verdict
from studyforge.exercise.quiz import normalised
from studyforge.exercise.record import Exercise

#: The two gates a deck clears.
C1, C2 = "C1", "C2"

#: ⭐ Registered at import: a record naming this family is complete only with both.
CARDS = register(Family("cards", (C1, C2)))

#: A back of more characters than this is a lesson and not a card.
MOST_BACK = 800

#: How a cited passage names the card it was written from: `card:<id>`.
CARD_ROLE = "card"


def cited_role(card: str) -> str:
    """Return the `origins` role that carries this card's passage."""
    return f"{CARD_ROLE}:{card}"


def check_cards(
    exercise: Exercise,
    origins: tuple[Cited, ...],
    ledger: Mapping[str, str],
    where: str,
) -> tuple[Verdict, ...]:
    """Answer `C1` and `C2` — ⛔ always both, in order."""
    cards = require_deck(exercise, where)
    return (_c1(cards), _c2(cards, origins, ledger))


def require_deck(exercise: Exercise, where: str) -> tuple[Card, ...]:
    """Return the cards to gate, refusing anything this family has no business reading."""
    if not isinstance(exercise, Exercise) or not exercise.is_deck:
        raise ExerciseError(
            f"{where}: the cards gates read a 'flashcards' exercise. A quiz is gated by its "
            f"own five and a code exercise by running it."
        )
    if (exercise.provenance, exercise.trust) != (DECK_PROVENANCE, DECK_TRUST):
        raise ExerciseError(
            f"{where}: a deck is {DECK_PROVENANCE!r} and {DECK_TRUST!r}, and no deck may claim "
            f"to be the source's own grader."
        )
    if not exercise.cards:
        raise ExerciseError(f"{where}: this deck holds no card, so there is nothing to gate.")
    return exercise.cards


def cited_for(cards: tuple[Card, ...], ledger: Mapping[str, str], where: str) -> tuple[Cited, ...]:
    """Return one cited passage per card that names one, read from the ledger at authoring time.

    ⛔ Refuses a card whose passage the ledger does not account for: nothing the source has is
    lost, and nothing a card cites is missing from it. A card with no origin cites nothing, and
    `C2` says so.
    """
    built: list[Cited] = []
    for card in cards:
        if card.origin is None:
            continue
        digest = ledger.get(card.origin.path)
        if digest is None:
            raise ExerciseError(
                f"{where}: the source ledger has no entry for '{card.origin.path}', so a card "
                f"cites material the ledger does not account for."
            )
        if not isinstance(digest, str):
            raise ExerciseError(
                f"{where}: the source ledger answers with something that is not a digest for "
                f"'{card.origin.path}'. The value is {describe(digest)}."
            )
        built.append(
            Cited(
                role=cited_role(card.id),
                path=card.origin.path,
                section=card.origin.section,
                digest=digest,
            )
        )
    return tuple(built)


def _c1(cards: tuple[Card, ...]) -> Verdict:
    """Every card is sound: two different texts, a short back, and a front nobody else has."""
    findings: list[str] = []
    seen: dict[str, int] = {}
    for card in cards:
        named = f"the card {card.front!r}"
        front, back = normalised(card.front), normalised(card.back)
        if front == back:
            findings.append(f"{named} turns over to its own front, so it says nothing new")
        if len(card.back) > MOST_BACK:
            findings.append(
                f"{named} has a back of {len(card.back)} characters, and a card's back is at "
                f"most {MOST_BACK}: more than that is a lesson"
            )
        seen[front] = seen.get(front, 0) + 1
    repeated = sum(count - 1 for count in seen.values() if count > 1)
    if repeated:
        findings.append(
            f"{repeated} card(s) ask what another card asks, so the reader is shown one question "
            f"twice"
        )
    if findings:
        return _verdict(
            C1,
            False,
            f"{len(findings)} finding(s) in this deck's {len(cards)} cards: " + "; ".join(findings),
        )
    return _verdict(
        C1,
        True,
        f"each of the {len(cards)} cards has a front and a different back of a card's length, "
        f"and no two fronts ask the same thing",
    )


def _c2(cards: tuple[Card, ...], origins: tuple[Cited, ...], ledger: Mapping[str, str]) -> Verdict:
    """Every card cites its passage, and each passage still digests to the ledger's value."""
    cited = {entry.role: entry for entry in origins}
    findings: list[str] = []
    for card in cards:
        named = f"the card {card.front!r}"
        if card.origin is None:
            findings.append(f"{named} cites no passage, so nothing says what it was written from")
            continue
        entry = cited.get(cited_role(card.id))
        if entry is None:
            findings.append(f"{named} cites a passage the record carries no digest for")
        elif entry.path != card.origin.path or entry.section != card.origin.section:
            findings.append(f"{named} cites a passage other than the one its digest belongs to")
        elif ledger.get(card.origin.path) is None:
            findings.append(f"{named} cites material the source ledger does not account for")
        elif ledger[card.origin.path] != entry.digest:
            findings.append(
                f"{named} cites material that has changed in the source since the card was written"
            )
    if findings:
        return _verdict(
            C2,
            False,
            f"{len(findings)} of this deck's {len(cards)} cards no longer resolve to the passage "
            f"they were written from: " + "; ".join(findings),
        )
    return _verdict(
        C2,
        True,
        f"each of the {len(cards)} cards cites a passage the ledger still digests to the value "
        f"the deck was built from",
    )


def _verdict(gate: str, held: bool, says: str) -> Verdict:
    """Return one of this family's verdicts."""
    return Verdict(id=gate, family=CARDS.name, held=held, says=says)
