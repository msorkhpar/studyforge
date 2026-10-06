"""One deck of flashcards, gated: `C1` and `C2` over a `DeckDraft`, and the files it would commit.

**What it does.** Answers the two card gates over one deck draft, writes the deck's document into
a staging root (never the corpus), takes the inputs a gate record names, and returns the same
`Gated` a code or a quiz draft returns. ⭐ It needs no runner and no judge: both gates are
mechanical.

**How you use it.**

    gated = gate_deck(draft, brief, ledger, where=where)
    gated.clears                        # did C1 and C2 hold

⛔ It shares the staging helpers of `gating`, which owns them; this module only draws the deck.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from studyforge.exercise import DECK_PROVENANCE, DECK_TRUST, FLASHCARDS, Exercise, to_document
from studyforge.exercise.gates import GateRecord, check_cards, cited_card_role, taken_over
from studyforge.skills.exercises.deckdoc import DECK_API, DECK_DOCUMENT, deck_of
from studyforge.skills.exercises.drafts import Brief, DeckDraft
from studyforge.skills.exercises.gating import Gated
from studyforge.skills.exercises.ledger import Ledger, digests
from studyforge.skills.exercises.staging import cited, json_bytes, lay_down, record_bytes


def gate_deck(draft: DeckDraft, brief: Brief, ledger: Ledger, *, where: str) -> Gated:
    """Answer `C1` and `C2` over one deck draft.

    ⭐ Needs no runner and no judge: both are mechanical.
    """
    places = brief.places
    exercise = Exercise(
        None,
        None,
        None,
        None,
        DECK_PROVENANCE,
        DECK_TRUST,
        kind=FLASHCARDS,
        cards=draft.cards,
    )
    origins = cited(
        tuple((cited_card_role(card.id), card.origin) for card in draft.cards if card.origin),
        ledger,
    )
    verdicts = check_cards(exercise, origins, digests(ledger), where)
    document = {
        "deck_api": DECK_API,
        "address": list(places.address.segments),
        "variant": places.variant,
        "unit": places.unit,
        "ordinal": places.ordinal,
        "title": draft.title,
        "exercise": to_document(exercise),
    }
    with tempfile.TemporaryDirectory(prefix="studyforge-stage-") as staged:
        stage = Path(staged)
        lay_down(stage, {places.in_bundle(DECK_DOCUMENT): json_bytes(document)})
        inputs = taken_over(stage / places.bundle, (("tests", DECK_DOCUMENT),), where)
    record = GateRecord(inputs=inputs, origins=origins, verdicts=verdicts)
    if record.clears:
        # ⛔ A deck that cleared is re-read through the one reader an adapter reads it by.
        deck_of(document, places.bundle)
    files = (
        (places.in_bundle(DECK_DOCUMENT), json_bytes(document)),
        (places.gates, record_bytes(record, where)),
    )
    accounts = tuple(
        (f"{places.bundle}:{card.id}", card.origin) for card in draft.cards if card.origin
    )
    return Gated(places, record, files, accounts, "")
