"""Mirror of `skills/exercises/deckgating.py` (R12): a deck is gated by `C1` and `C2` alone."""

from __future__ import annotations

from studyforge.exercise import Card, Origin
from studyforge.exercise.bundle import Places
from studyforge.exercise.gates import C1, C2
from studyforge.skills.exercises import (
    DECK_DOCUMENT,
    Brief,
    DeckDraft,
    gate_deck,
    source_case,
    take,
)
from tests.studyforge.skills.exercises.authoring import write_corpus

GAUGE = 3


def _brief(tmp_path):
    material, graders, pages = write_corpus(tmp_path)
    ledger = take(tmp_path, material, graders, "the ledger")
    page = pages[GAUGE]
    places = Places(page.address, page.variant, page.unit, 1)
    return Brief(page, source_case(page, ledger), 1, places, 1, ()), ledger


def cards() -> tuple[Card, ...]:
    return (
        Card("c-hour", "When is the gauge read?", "At the same hour every day.",
             Origin("notes/gauge.md", "Taking a reading")),
        Card("c-book", "When is a reading copied into the book?", "On the same day.",
             Origin("notes/gauge.md", "Writing it down")),
    )


def test_a_deck_clears_c1_and_c2_with_no_runner_and_no_judge(tmp_path):
    brief, ledger = _brief(tmp_path)
    gated = gate_deck(DeckDraft("Gauge cards", cards()), brief, ledger, where="w")
    assert gated.clears, [v.says for v in gated.refused]
    assert [v.id for v in gated.record.verdicts] == [C1, C2]
    assert len(gated.record.origins) == 2 and gated.output == ""
    names = {path for path, _ in gated.files}
    assert brief.places.in_bundle(DECK_DOCUMENT) in names and brief.places.gates in names


def test_a_deck_with_a_card_that_cites_nothing_does_not_clear(tmp_path):
    brief, ledger = _brief(tmp_path)
    bare = (*cards(), Card("c-bare", "What is bare?", "A card with no passage."))
    gated = gate_deck(DeckDraft("Gauge cards", bare), brief, ledger, where="w")
    assert [v.id for v in gated.refused] == [C2]
