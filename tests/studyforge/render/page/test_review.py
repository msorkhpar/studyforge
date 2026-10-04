"""Mirror of `render/page/review.py` (R12): the spaced-review bank a quiz with a schedule draws."""

from __future__ import annotations

import re

from studyforge.render.page import review
from tests.studyforge.render.page.test_practice import QUIZ, SHIPPED, document, panel, section

BANK = {**QUIZ, "review": {"intervals_days": [1, 3, 7]}}


def markup(workspace) -> str:
    return panel(sections=[section(workspace=workspace)])


def test_a_review_bank_draws_its_questions_its_key_and_its_plan_and_links_its_two_files():
    said = markup(BANK)
    assert said.count("data-practice-question=") == len(QUIZ["questions"])
    assert 'data-review="3"' in said
    assert '"intervals_days":[1,3,7]' in said
    assert re.search(r'<script src="[^"]*review\.js" defer></script>', said)
    assert 'data-review-part="key"' in said and 'data-practice-part="key"' not in said
    assert '"correct"' not in said, "the key block lists the keyed id, never a correct flag"


def test_a_plain_quiz_and_a_code_practice_link_no_review_files():
    for plain in (markup(QUIZ), markup(SHIPPED)):
        assert "review.js" not in plain and "data-review" not in plain


def test_a_bank_names_its_two_files_once():
    assert sorted(review.files()) == ["review.css", "review.js"]


def test_the_review_script_makes_no_request_and_guards_the_store():
    script = review.files()["review.js"]
    for forbidden in ("fetch(", "XMLHttpRequest", "sendBeacon", "http://", "https://", "WebSocket"):
        assert forbidden not in script, forbidden
    assert script.count("try {") >= 2 and "localStorage" in script and "studyforge." in script
