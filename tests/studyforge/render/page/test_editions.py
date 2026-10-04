"""Mirror of `src/studyforge/render/page/editions.py` (R12).

⭐ A practice that differs only by language is ONE practice: a four-language practice is one card
with one status and the sentence naming its editions, every edition's panel carries the switch at
the top, and the outline lists it once. ⛔ Every clause is read both ways: a practice with no
`edition`, an edition that stands alone, and a quiz that names one are ordinary practices.
"""

from __future__ import annotations

import dataclasses
import json
import re

from studyforge.render import modes
from studyforge.render.page import anchors, editions, practices, render
from tests.studyforge.render.page.pages import sample_placement
from tests.studyforge.render.page.test_practice import QUIZ, SHIPPED, document, section

LANGS = ("python", "typescript", "java", "kotlin")
LABELS = {"python": "Python", "typescript": "TypeScript", "java": "Java", "kotlin": "Kotlin"}


def edition(lang: str, *, name: str = "conversation", key: str | None = None, title=None) -> dict:
    """One language edition of a practice, as the unit builder writes it."""
    made = section(key=key or f"practice-{name}-{lang}")
    made["heading"] = title or f"Keep a conversation ({LABELS[lang]})"
    made["workspace"] = {**SHIPPED, "main_path": f"practice/{name}/{lang}/main"}
    made["lang"] = lang
    made["edition"] = name
    return made


def four() -> list[dict]:
    return [edition(lang) for lang in LANGS]


def offer() -> modes.Offer:
    choices = tuple(
        modes.Choice(
            lang, f"Read in {LABELS[lang]}", "summary", lang, tuple(LANGS), (lang,)
        )
        for lang in LANGS
    )
    return modes.Offer(
        choices=choices,
        default="python",
        languages=tuple((lang, LABELS[lang]) for lang in LANGS),
        grey=True,
    )


def page(sections, *, with_offer: bool = False) -> str:
    placement = sample_placement()
    if with_offer:
        placement = dataclasses.replace(placement, offer=offer())
    return render(document(sections=list(sections)), placement).decode("utf-8")


def cards(markup: str) -> list[str]:
    listed = markup[markup.index('<ol data-practices-part="cards">') :]
    listed = listed[: listed.index("</ol>")]
    return ['<li id="card-' + one for one in listed.split('<li id="card-')[1:]]


def test_four_language_editions_are_one_card_with_one_status_and_the_languages_named():
    markup = page(four(), with_offer=True)
    found = cards(markup)
    assert len(found) == 1
    card = found[0]
    assert ">Keep a conversation</a>" in card, "the title carries no language"
    assert card.count('data-practices-part="state"') == 1
    assert "Available in: " in card
    for lang in LANGS:
        section = f"s-practice-conversation-{lang}"
        assert f'data-edition="{lang}" data-edition-section="{section}"' in card
    assert "of 4 languages" in card
    assert anchors.practices_title(1) in markup
    assert "Practice (1)" in markup


def test_every_edition_panel_and_statement_is_on_the_page_with_the_switch_at_the_top():
    markup = page(four(), with_offer=True)
    panels = re.findall(r'<section data-practice="[^"]+"[^>]*>', markup)
    assert len(panels) == 4
    assert [re.search(r'data-edition="([^"]+)"', p).group(1) for p in panels] == list(LANGS)
    for at in re.finditer(r'<section data-practice="[^"]+"[^>]*>(.{0,500})', markup, re.S):
        row = at.group(1)
        assert row.startswith('<p data-practice-part="editions" role="group"'), row[:120]
        assert row.split(">")[0].endswith(" hidden"), "the switch ships hidden until scripted"
        buttons = re.findall(r'data-edition-switch="([^"]+)"', row.split("</p>")[0])
        assert buttons == list(LANGS)
    statements = re.findall(r'<section id="s-practice-conversation-[a-z]+"[^>]*>', markup)
    assert len(statements) == 4
    assert all("data-lang=" not in one for one in statements), "no reading mode may hide an edition"
    assert [re.search(r'data-edition="([^"]+)"', one).group(1) for one in statements] == list(LANGS)


def test_the_outline_lists_the_practice_once_by_its_language_free_title():
    found = anchors.entries(document(sections=four()), offer())
    assert found == (
        (1, "Practice (1)", "#practices"),
        (2, "Keep a conversation", "#card-practice-conversation-python"),
    )


def test_the_workspace_says_which_language_each_mode_opens_a_practice_in():
    mine = page(four(), with_offer=True)
    attribute = re.search(r"data-edition-modes='([^']+)'", mine)
    assert attribute
    said = json.loads(attribute.group(1))
    assert said["attribute"] == modes.MODE_ATTRIBUTE
    table = said["modes"]
    assert set(table) == set(LANGS)
    assert table["java"][0] == "java" and table["java"][1:] == ["python", "typescript", "kotlin"]
    assert "data-edition-modes" not in page(four(), with_offer=False)


def test_a_practice_with_no_edition_is_unchanged_by_the_key_existing():
    plain = [section(key="practice-a"), section(key="practice-b")]
    markup = page(plain)
    assert len(cards(markup)) == 2
    for word in ("data-edition", "data-practice-editions", "data-practice-part=\"editions\""):
        assert word not in markup


def test_an_edition_standing_alone_and_a_quiz_that_names_one_are_ordinary_practices():
    alone = page([edition("python")])
    assert len(cards(alone)) == 1
    assert "data-edition" not in alone
    quiz = section(key="practice-q", workspace=QUIZ)
    quiz["edition"], quiz["lang"] = "conversation", "python"
    assert editions.edition_of(quiz) is None


def test_editions_of_different_practices_are_different_cards_in_the_order_they_first_appear():
    sections = [
        edition("python", name="first"),
        edition("python", name="second"),
        edition("java", name="first"),
        edition("java", name="second"),
    ]
    markup = page(sections)
    found = cards(markup)
    assert len(found) == 2
    assert [re.search(r'data-practice-card="([^"]+)"', one).group(1) for one in found] == [
        "s-practice-first-python",
        "s-practice-second-python",
    ]


def test_a_title_that_names_no_language_in_parentheses_is_kept_as_it_is():
    same = [edition(lang, title="Keep a conversation") for lang in LANGS]
    assert ">Keep a conversation</a>" in cards(page(same))[0]
    odd = [edition(lang, title=f"Keep a conversation ({lang} edition)") for lang in LANGS]
    assert "Keep a conversation (python edition)" in cards(page(odd))[0]


def test_the_cards_of_a_page_without_editions_are_the_bytes_they_were():
    ungraded = practices.card(section(), document(), sample_placement(), "A unit")
    assert "data-practice-editions" not in ungraded
    assert ungraded.startswith('<li id="card-practice-java" data-practice-card="s-practice-java"')
