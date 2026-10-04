"""Mirror of `skills/exercises/deckdoc.py` (R12): the one reader of a deck's own document."""

from __future__ import annotations

import json

import pytest

from studyforge.skills.exercises import DECK_DOCUMENT, DeckDraft, deck_of, gate_deck
from tests.studyforge.skills.exercises.test_deckgating import _brief, cards


def _document(tmp_path):
    brief, ledger = _brief(tmp_path)
    gated = gate_deck(DeckDraft("Gauge cards", cards()), brief, ledger, where="w")
    return brief, json.loads(dict(gated.files)[brief.places.in_bundle(DECK_DOCUMENT)])


def test_a_deck_document_reads_back_through_its_one_reader(tmp_path):
    brief, document = _document(tmp_path)
    deck = deck_of(document, brief.places.bundle)
    assert deck.title == "Gauge cards" and deck.exercise.is_deck and len(deck.exercise.cards) == 2
    origin = {"path": "notes/gauge.md", "section": "Taking a reading"}
    assert origin in deck.record["cards"][0].values()


def test_a_document_that_is_not_a_deck_s_own_is_refused(tmp_path):
    brief, document = _document(tmp_path)
    where = brief.places.bundle
    with pytest.raises(Exception, match="not a JSON object"):
        deck_of([], where)
    with pytest.raises(Exception, match="in that order"):
        deck_of(dict(reversed(list(document.items()))), where)
    with pytest.raises(Exception, match="identity"):
        deck_of(document, where + "-other")
    with pytest.raises(Exception, match="no title"):
        deck_of({**document, "title": " "}, where)
