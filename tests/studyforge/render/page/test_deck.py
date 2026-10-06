"""Mirror of `render/page/deck.py` (R12): the deck of flashcards a practice draws on a page.

⭐ A deck draws its own section and links its own two files; a plain quiz and a code practice
draw what they always did and link neither; and the script keeps the promises its docstring
makes (no request, a guarded store).
"""

from __future__ import annotations

import re

from studyforge.render.page import deck
from tests.studyforge.render.page.test_practice import QUIZ, SHIPPED, document, panel, section

DECK = {
    "provenance": "generated",
    "trust": "advisory",
    "kind": "flashcards",
    "cards": [
        {"id": "c-1", "front": "What does `x` mean?", "back": "It means <this>."},
        {"id": "c-2", "front": "Second front?", "back": "First paragraph.\n\nSecond paragraph."},
    ],
}
BANK = {**QUIZ, "review": {"intervals_days": [1, 3, 7]}}


def markup(workspace) -> str:
    return panel(sections=[section(workspace=workspace)])


def test_a_deck_draws_every_card_with_both_sides_and_links_its_two_files():
    said = markup(DECK)
    assert said.count("data-deck-card=") == 2
    assert "<code>x</code>" in said and "It means &lt;this&gt;." in said
    assert "<p>First paragraph.</p><p>Second paragraph.</p>" in said
    assert 'data-deck="2"' in said and "data-practice-quiz=" in said
    assert re.search(r'<link rel="stylesheet" href="[^"]*deck\.css">', said)
    assert re.search(r'<script src="[^"]*deck\.js" defer></script>', said)
    assert "data-practice=" not in said, "a deck has no workspace"
    for dead in ("Run", "Submit", "data-practice-act"):
        assert dead not in said


def test_a_plain_quiz_and_a_code_practice_draw_neither_and_link_neither():
    for plain in (markup(QUIZ), markup(SHIPPED)):
        assert "deck.js" not in plain and "review.js" not in plain
        assert "data-deck" not in plain and "data-review" not in plain


def test_a_deck_names_its_two_files_once():
    assert sorted(deck.files()) == ["deck.css", "deck.js"]


def test_the_deck_script_makes_no_request_and_guards_the_store():
    script = deck.files()["deck.js"]
    for forbidden in ("fetch(", "XMLHttpRequest", "sendBeacon", "http://", "https://", "WebSocket"):
        assert forbidden not in script, forbidden
    assert script.count("try {") >= 2 and "localStorage" in script and "studyforge." in script


def test_a_deck_and_a_bank_have_no_status_on_their_card_and_a_plain_quiz_still_has():
    from studyforge.render.page import practices

    def card(workspace):
        unit = document(sections=[section(workspace=workspace)])
        return practices.card(
            unit["sections"][0],
            unit,
            __import__(
                "tests.studyforge.render.page.pages", fromlist=["sample_placement"]
            ).sample_placement(),
            "A unit",
        )

    assert 'data-practices-part="state"' not in card(DECK)
    assert 'data-practices-part="state"' not in card(BANK)
    assert 'data-practices-part="state"' in card(QUIZ)
    assert 'data-practice-kind="quiz"' in card(DECK)
