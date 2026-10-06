"""Mirror of `render/page/scope.py` (R12): the sentence naming where a deck or a bank came from."""

from __future__ import annotations

from studyforge.exercise import Card, Exercise, Origin
from studyforge.render.page import scope


def deck(*paths: str | None) -> Exercise:
    cards = tuple(
        Card(f"c-{n}", "Front?", "Back.", None if path is None else Origin(path, "S"))
        for n, path in enumerate(paths)
    )
    return Exercise(None, None, None, None, "generated", "advisory", kind="flashcards", cards=cards)


def test_cards_citing_one_page_or_none_keep_the_sentence_they_always_had():
    assert scope.deck_template(deck("a.md", "a.md")) == scope.DECK_PAGE
    assert scope.deck_template(deck(None, None)) == scope.DECK_PAGE


def test_cards_citing_several_pages_are_said_to_come_from_several_pages():
    assert scope.deck_template(deck("a.md", "b.md")) == scope.DECK_SEVERAL


def test_a_bank_is_judged_by_its_questions_citations_the_same_way():
    from tests.studyforge.skills.exercises.authoring import gauge_questions

    one = Exercise(None, None, None, None, "generated", "advisory", kind="quiz",
                   questions=gauge_questions())
    assert scope.review_template(one) == scope.REVIEW_PAGE
    from dataclasses import replace

    first, *rest = gauge_questions()
    spread = (replace(first, origin=Origin("other/page.md", "S")), *rest)
    many = replace(one, questions=spread)
    assert scope.review_template(many) == scope.REVIEW_SEVERAL
