"""Mirror of `src/studyforge/render/page/practices.py` (R12).

⭐ The register ruling, read in the markup a page ships: a lesson's practices are
one **Practice (n)** list of titled cards, each saying what it practises and
carrying a slot for its status, and one workspace follows them. ⛔ Every
clause is read both ways — present where it is owed, absent where it is not.
"""

from __future__ import annotations

import re

from studyforge.render import templates
from studyforge.render.page import anchors, practices, render
from tests.studyforge.render.page.pages import sample_placement
from tests.studyforge.render.page.test_practice import QUIZ, SHIPPED, UNGRADED, document, section


def page(*sections) -> str:
    """The whole page for a unit carrying these sections."""
    return render(document(sections=list(sections)), sample_placement()).decode("utf-8")


def cards(markup: str) -> list[str]:
    """Each card's markup, in the order the list carries them."""
    listed = markup[markup.index('<ol data-practices-part="cards">') :]
    listed = listed[: listed.index("</ol>")]
    return ['<li id="card-' + one for one in listed.split('<li id="card-')[1:]]


def lesson(key="lesson-java"):
    """A lesson section, which is never a card."""
    return section(kind="lesson", workspace=None, key=key)


def test_a_lessons_practices_are_one_list_titled_by_their_count():
    three = page(
        section(key="practice-a"),
        section(key="practice-b", workspace=UNGRADED),
        section(key="practice-c", workspace=QUIZ),
    )
    listed = three[three.index('<section id="practices"') :]
    listed = listed[: listed.index("</section>")]
    assert f">{anchors.practices_title(3)}</h2>" in listed
    assert anchors.practices_title(3) == "Practice (3)"
    found = cards(listed)
    assert [re.search(r'data-practice-card="([^"]+)"', one).group(1) for one in found] == [
        "s-practice-a",
        "s-practice-b",
        "s-practice-c",
    ]


def test_a_unit_with_no_practice_has_no_list_and_no_workspace():
    plain = page(lesson())
    assert "data-practices" not in plain
    assert "data-workspace" not in plain
    # ⭐ The negative control: the same page with a practice carries both.
    assert "data-practices" in page(lesson(), section())
    assert "data-workspace" in page(lesson(), section())


def test_a_card_is_titled_by_its_practice_and_opens_that_practice():
    # ⛔ The card names its practice by the key the panel's runs are recorded
    # under — the one the status is read back by — never a second spelling.
    markup = page(section())
    one = cards(markup)[0]
    key = re.search(r'<section data-practice="([^"]+)"', markup).group(1)
    assert key == "basics/unit-03/practice-java"
    assert f'data-practice-key="{key}"' in one
    assert 'href="#s-practice-java"' in one
    assert f'data-corpus="{sample_placement().corpus}"' in one
    assert ">Practice</a></h3>" in one


def test_a_card_lists_what_its_record_says_it_practises_and_nothing_where_it_says_nothing():
    said = cards(page(section(workspace={**SHIPPED, "concepts": ["Records", "a < b"]})))[0]
    assert 'data-practices-part="concepts"' in said
    assert "<li>Records</li>" in said
    # ⛔ A concept is the corpus's text, escaped like every other.
    assert "<li>a &lt; b</li>" in said
    silent = cards(page(section()))[0]
    assert 'data-practices-part="concepts"' not in silent


def test_a_graded_practice_and_a_quiz_carry_a_status_slot_that_ships_saying_nothing():
    # ⛔ The status is the reader's own record: the slot ships HIDDEN, with both
    # words, so a built page says nothing about any reader (R10). ⭐ A card says
    # which record it is read from: a quiz's from the reader's browser store,
    # a code practice's from the server.
    graded, ungraded, quiz = cards(
        page(
            section(key="practice-a"),
            section(key="practice-b", workspace=UNGRADED),
            section(key="practice-c", workspace=QUIZ),
        )
    )
    for card in (graded, quiz):
        assert templates.fill(practices.STATE_TEMPLATE) in card
        assert '<p data-practices-part="state" hidden>' in card
    assert 'data-practice-kind="code"' in graded and 'data-practice-kind="code"' in ungraded
    assert 'data-practice-kind="quiz"' in quiz
    # ⚠️ An ungraded practice is completed by nothing, so the record could only
    # ever say *not started* — it carries no slot at all.
    assert 'data-practices-part="state"' not in ungraded


def test_no_card_carries_a_quiz_answer():
    # ⛔ A quiz's key lives only in its own section's key block (register
    # ruling, 2026-09-25) — and a card is a new place the page could leak one.
    quiz = cards(page(section(workspace=QUIZ)))[0]
    for word in ("correct", "The page says so.", "A type"):
        assert word not in quiz, word


def test_the_list_stands_before_the_first_practice_and_the_workspace_after_the_last():
    # ⛔ The document's own order is kept: a lesson before the practices stays
    # before the list, and the practices' material follows it for a reader with
    # no script (R8).
    markup = page(lesson(), section(key="practice-a"), section(key="practice-b"))
    at = markup.index
    assert at('id="s-lesson-java"') < at('<section id="practices"')
    assert at('<section id="practices"') < at('id="s-practice-a"') < at('id="s-practice-b"')
    assert at('id="s-practice-b"') < at("<div data-workspace ") < at("</main>")
    assert markup.count("<div data-workspace ") == 1


def test_the_workspace_ships_hidden_with_its_title_and_three_acts():
    shell = practices.workspace(document())
    assert shell.startswith('<div data-workspace role="dialog"')
    assert " hidden>" in shell.splitlines()[0]
    acts = re.findall(r'data-workspace-act="(\w+)"', shell)
    assert acts == ["previous", "next", "close"]
    assert 'data-workspace-part="title"' in shell
    # ⛔ Not an editor: the workspace ships no frame. One is added only when a
    # practice is opened (`practice-editor.js`).
    assert "<iframe" not in shell
    # ⛔ And a unit with no practice has none, asked of the part itself.
    assert practices.workspace(document(sections=[lesson()])) == ""
