"""Mirror of `src/studyforge/exercise/deck.py` (R12): the flashcards kind of exercise record."""

from __future__ import annotations

import pytest

from studyforge.exercise import (
    EXERCISE_KINDS,
    FLASHCARDS,
    Card,
    ExerciseError,
    Origin,
    cards_document,
    from_document,
    to_document,
)

WHERE = "here"
CARD = {"id": "fc-1", "front": "What does a greeter return?", "back": "A greeting."}


def deck(**extra):
    return {"kind": "flashcards", "cards": [CARD], **extra}


def test_flashcards_is_a_kind_beside_code_and_quiz():
    assert FLASHCARDS in EXERCISE_KINDS and EXERCISE_KINDS[:2] == ("code", "quiz")


def test_a_deck_reads_and_writes_back_with_provenance_and_trust_filled_in():
    exercise = from_document(deck(), WHERE)
    assert exercise.is_deck and not exercise.is_quiz and not exercise.graded
    assert exercise.main_path is None and exercise.test_path is None
    assert exercise.cards == (Card("fc-1", CARD["front"], CARD["back"]),)
    assert to_document(exercise) == {
        "provenance": "generated",
        "trust": "advisory",
        "kind": "flashcards",
        "cards": [CARD],
    }
    again = from_document(to_document(exercise), WHERE)
    assert to_document(again) == to_document(exercise)


def test_a_card_may_cite_the_passage_it_was_written_from():
    one = {**CARD, "origin": {"path": "notes/page.md", "section": "Taking a reading"}}
    exercise = from_document(deck(cards=[one]), WHERE)
    assert exercise.cards[0].origin == Origin("notes/page.md", "Taking a reading")
    assert cards_document(exercise.cards) == [one]


@pytest.mark.parametrize(
    "cards",
    [
        [],
        "fc-1",
        ["fc-1"],
        [{"id": "a", "front": "f"}],
        [{"id": "a", "back": "b"}],
        [{"id": "a", "front": " ", "back": "b"}],
        [{"id": "a", "front": "f", "back": ""}],
        [{"id": "a b", "front": "f", "back": "b"}],
        [{"id": "a", "front": "f", "back": "b", "extra": 1}],
        [CARD, CARD],
    ],
)
def test_a_card_without_a_front_and_a_back_and_a_repeated_id_are_refused(cards):
    with pytest.raises(ExerciseError):
        from_document(deck(cards=cards), WHERE)


def test_a_deck_is_never_authoritative_and_carries_no_workspace():
    for extra in (
        {"provenance": "bundled", "trust": "authoritative"},
        {"main_path": "a.py"},
        {"questions": []},
        {"test_command": ["true"]},
    ):
        with pytest.raises(ExerciseError):
            from_document(deck(**extra), WHERE)
    with pytest.raises(ExerciseError):
        from_document({"main_path": "a.py", "run_command": ["true"], "cards": [CARD]}, WHERE)
    with pytest.raises(ExerciseError):
        from_document({"kind": "quiz", "cards": [CARD], "questions": []}, WHERE)
