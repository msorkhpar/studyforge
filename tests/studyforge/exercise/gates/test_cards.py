"""Mirror of `src/studyforge/exercise/gates/cards.py` (R12): `C1` and `C2`."""

from __future__ import annotations

import pytest

from studyforge.exercise import Card, Exercise, ExerciseError, Origin
from studyforge.exercise.gates import C1, C2, CARDS, Cited, GateRecord, record_of, registered
from studyforge.exercise.gates.cards import check_cards, cited_for, cited_role, require_deck
from tests.studyforge.skills.exercises.authoring import gauge_questions

WHERE = "here"
PAGE = Origin("notes/gauge.md", "Taking a reading")
LEDGER = {"notes/gauge.md": "sha256:" + "a" * 64}


def deck(*cards: Card) -> Exercise:
    return Exercise(None, None, None, None, "generated", "advisory", kind="flashcards", cards=cards)


def good(n: int = 1) -> Card:
    return Card(f"c-{n}", f"What does reading {n} say?", f"It says {n}.", PAGE)


def cited(*cards: Card, digest: str = LEDGER["notes/gauge.md"]) -> tuple[Cited, ...]:
    return tuple(
        Cited(cited_role(one.id), one.origin.path, one.origin.section, digest)
        for one in cards
        if one.origin
    )


def verdicts(*cards: Card, origins=None, ledger=LEDGER):
    made = deck(*cards)
    return check_cards(made, cited(*cards) if origins is None else origins, ledger, WHERE)


def test_the_family_declares_two_gates_and_a_record_is_complete_only_with_both():
    assert CARDS.gates == (C1, C2) and CARDS in registered()
    held = verdicts(good(1), good(2))
    assert [v.id for v in held] == [C1, C2] and all(v.held for v in held)
    record = GateRecord(inputs=(), origins=cited(good(1), good(2)), verdicts=(held[0],))
    with pytest.raises(ExerciseError):
        record_of(
            {
                "record_api": 1,
                "inputs": [],
                "origins": [],
                "verdicts": [
                    {"id": C1, "family": "cards", "held": True, "says": "ok"},
                ],
            },
            WHERE,
        )
    assert record is not None


def test_c1_refuses_a_card_that_turns_over_to_its_own_front_and_a_repeated_front():
    same = Card("c-1", "What is it?", "what is   IT?", PAGE)
    twin = Card("c-2", "What does reading 1 say?", "Something else.", PAGE)
    first, second = verdicts(good(1), same)[0], verdicts(good(1), twin)[0]
    assert not first.held and "own front" in first.says and "What is it?" in first.says
    assert not second.held and "ask what another card asks" in second.says
    assert "c-1" not in first.says, "a card is named by its front, never by its id"


def test_c1_refuses_a_back_that_is_a_lesson():
    long = Card("c-1", "What does it say?", "word " * 200, PAGE)
    assert not verdicts(long)[0].held


def test_c2_holds_while_the_passage_digests_to_the_ledger_and_not_after():
    cards = (good(1), good(2))
    assert verdicts(*cards)[1].held
    moved = {"notes/gauge.md": "sha256:" + "b" * 64}
    drifted = verdicts(*cards, ledger=moved)[1]
    assert not drifted.held and "changed in the source" in drifted.says
    missing = verdicts(*cards, ledger={})[1]
    assert not missing.held and "does not account for" in missing.says


def test_c2_refuses_a_card_that_cites_nothing_or_whose_digest_is_not_in_the_record():
    bare = Card("c-1", "What does it say?", "It says.", None)
    assert not verdicts(bare)[1].held
    assert not verdicts(good(1), origins=())[1].held


def test_cited_for_reads_the_ledger_and_refuses_a_passage_it_does_not_hold():
    (one,) = cited_for((good(1),), LEDGER, WHERE)
    assert one.digest == LEDGER["notes/gauge.md"] and one.role == "card:c-1"
    assert cited_for((Card("c-2", "f", "b"),), LEDGER, WHERE) == ()
    with pytest.raises(ExerciseError):
        cited_for((good(1),), {}, WHERE)


def test_a_deck_that_is_not_one_or_holds_nothing_or_claims_authority_is_refused_by_the_gates():
    quiz = Exercise(
        None, None, None, None, "generated", "advisory", kind="quiz", questions=gauge_questions()
    )
    bundled = Exercise(
        None, None, None, None, "bundled", "authoritative", kind="flashcards", cards=(good(1),)
    )
    for refused in (quiz, deck(), bundled):
        with pytest.raises(ExerciseError):
            require_deck(refused, WHERE)
