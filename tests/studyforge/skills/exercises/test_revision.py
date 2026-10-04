"""Revision aids through the authoring pass: a deck and a review bank, committed and read back.

⭐ What it asserts: a review bank clears `Q1` to `Q5` and `S1`; a deck and a bank are committed as
the documents an adapter reads, and the adapter builds the same practice documents from them.
`gate_deck` and `deck_of` have their own modules' tests.
"""

from __future__ import annotations

import json
from dataclasses import replace

import pytest

from studyforge.exercise import Card, Origin
from studyforge.exercise.bundle import Places
from studyforge.exercise.gates import C1, C2
from studyforge.exercise.gates.quiz import Q5, S1
from studyforge.exercise.quiz import Review
from studyforge.skills.adapter.practices import PracticeRefused, authored
from studyforge.skills.exercises import (
    DECK_DOCUMENT,
    Brief,
    DeckDraft,
    QuizDraft,
    deck_of,
    gate_deck,
    gate_quiz,
    source_case,
    take,
)
from tests.studyforge.skills.exercises.authoring import Judging, gauge_questions, write_corpus

GAUGE = 3


def _brief(tmp_path, ordinal: int = 1):
    material, graders, pages = write_corpus(tmp_path)
    ledger = take(tmp_path, material, graders, "the ledger")
    page = pages[GAUGE]
    places = Places(page.address, page.variant, page.unit, ordinal)
    return Brief(page, source_case(page, ledger), 1, places, 1, ()), ledger, material, graders


def cards() -> tuple[Card, ...]:
    return (
        Card("c-hour", "When is the gauge read?", "At the same hour every day.",
             Origin("notes/gauge.md", "Taking a reading")),
        Card("c-book", "When is a reading copied into the book?", "On the same day.",
             Origin("notes/gauge.md", "Writing it down")),
    )


def _commit(gated, root):
    for path, data in gated.files:
        target = root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)


def test_a_review_bank_clears_the_quiz_gates_and_r1_together(tmp_path):
    brief, ledger, *_ = _brief(tmp_path)
    draft = QuizDraft("Gauge review", gauge_questions(), review=Review((1, 3)))
    gated = gate_quiz(draft, brief, ledger, Judging(), where="w")
    assert gated.clears, [v.says for v in gated.refused]
    ids = [v.id for v in gated.record.verdicts]
    assert S1 in ids and Q5 in ids and len(ids) == 6
    document = json.loads(dict(gated.files)[brief.places.in_bundle("tests/quiz.json")])
    assert document["exercise"]["review"] == {"intervals_days": [1, 3]}


def test_a_bank_with_fewer_questions_than_steps_is_refused_by_r1_alone(tmp_path):
    brief, ledger, *_ = _brief(tmp_path)
    draft = QuizDraft("Gauge review", gauge_questions(), review=Review((1, 3, 7)))
    gated = gate_quiz(draft, brief, ledger, Judging(), where="w")
    assert [v.id for v in gated.refused] == [S1]


def test_a_quiz_without_a_schedule_has_no_r1_and_is_the_record_it_was(tmp_path):
    brief, ledger, *_ = _brief(tmp_path)
    gated = gate_quiz(QuizDraft("Gauge", gauge_questions()), brief, ledger, Judging(), where="w")
    assert [v.id for v in gated.record.verdicts][-1] == Q5 and S1 not in [
        v.id for v in gated.record.verdicts
    ]
    assert "review" not in json.loads(
        dict(gated.files)[brief.places.in_bundle("tests/quiz.json")]
    )["exercise"]


def test_the_adapter_reads_a_committed_deck_and_a_committed_bank_into_practice_documents(tmp_path):
    brief, ledger, *_ = _brief(tmp_path)
    root = tmp_path / "corpus"
    _commit(gate_deck(DeckDraft("Gauge cards", cards()), brief, ledger, where="w"), root)
    second = replace(brief, places=Places(brief.places.address, brief.places.variant,
                                          brief.places.unit, 2))
    _commit(gate_quiz(QuizDraft("Gauge review", gauge_questions(), review=Review((1, 3))),
                      second, ledger, Judging(), where="w"), root)
    found = authored(root)
    (one, two) = next(iter(found.pages.values()))
    assert one.fields["exercise"]["kind"] == "flashcards" and one.fields["title"] == "Gauge cards"
    assert two.fields["exercise"]["kind"] == "quiz" and two.fields["exercise"]["review"]
    assert one.fields["blocks"][0]["text"] == "Revise"


def test_a_deck_whose_cards_were_edited_after_the_gates_is_refused_by_the_adapter(tmp_path):
    brief, ledger, *_ = _brief(tmp_path)
    root = tmp_path / "corpus"
    _commit(gate_deck(DeckDraft("Gauge cards", cards()), brief, ledger, where="w"), root)
    path = root / brief.places.in_bundle(DECK_DOCUMENT)
    text = path.read_text(encoding="utf-8").replace("same hour", "same time")
    path.write_text(text, encoding="utf-8")
    with pytest.raises(PracticeRefused):
        authored(root)
