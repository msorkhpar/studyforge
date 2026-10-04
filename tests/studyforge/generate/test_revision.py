"""Mirror of `generate/revision.py` (R12): which corpora get a deck's and a bank's shared files."""

from __future__ import annotations

import json
from types import SimpleNamespace

from studyforge.generate.revision import has_decks, has_reviews


def corpus(tmp_path, *records):
    units = []
    for number, record in enumerate(records):
        directory = tmp_path / f"unit-{number}"
        directory.mkdir()
        document = {"kind": "practice", "exercise": record}
        (directory / "practice-1.json").write_text(json.dumps(document), encoding="utf-8")
        units.append(SimpleNamespace(directory=directory))
    return SimpleNamespace(units=tuple(units))


def test_a_flashcards_practice_wants_the_deck_files_and_not_the_bank_files(tmp_path):
    made = corpus(tmp_path, {"kind": "flashcards", "cards": []})
    assert has_decks(made) and not has_reviews(made)


def test_a_quiz_that_declares_a_schedule_wants_the_bank_files_and_not_the_deck_files(tmp_path):
    made = corpus(tmp_path, {"kind": "quiz", "review": {"intervals_days": [1, 3]}})
    assert has_reviews(made) and not has_decks(made)


def test_a_plain_quiz_or_a_code_practice_wants_neither(tmp_path):
    made = corpus(tmp_path, {"kind": "quiz"}, {"kind": "code"})
    assert not has_decks(made) and not has_reviews(made)
