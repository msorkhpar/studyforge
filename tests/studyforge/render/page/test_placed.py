"""Mirror of `render/page/placed.py` (R12): `<!-- practice N -->` draws a practice in place."""

from __future__ import annotations

import pytest

from studyforge.render.page import PageError, anchors, editions, placed, render
from studyforge.render.page import practices as practices_region
from studyforge.render.pageassets import search
from tests.studyforge.render.page.pages import sample_placement
from tests.studyforge.render.page.test_practice import QUIZ, document, section


def marker(number):
    return {"type": "html", "text": f"<!-- practice {number} -->"}


def lesson(*middle):
    """A lesson of two parts, with `middle` between them."""
    return {
        "key": "java",
        "kind": "lesson",
        "heading": "Lesson",
        "blocks": [
            {"type": "heading", "level": 2, "text": "Part one"},
            {"type": "para", "text": "The first part teaches fields."},
            *middle,
            {"type": "heading", "level": 2, "text": "Part two"},
            {"type": "para", "text": "The second part teaches bitmaps."},
        ],
        "video": None,
        "workspace": None,
        "attachments": [],
    }


def titled(one, heading):
    return {**one, "heading": heading}


def unit(*middle):
    """A lesson and three practices: two code practices and a quiz, in that order."""
    return document(
        sections=[
            lesson(*middle),
            titled(section(key="practice-java"), "Build a field"),
            titled(section(key="practice-java-2"), "Build a bitmap"),
            titled(section(key="practice-java-3", workspace=QUIZ), "Check yourself"),
        ]
    )


def page(doc) -> str:
    return render(doc, sample_placement()).decode()


def body(text: str) -> str:
    return text[text.index('<main id="content">') :]


# --- the plan ------------------------------------------------------------------------------------


def test_a_marker_names_the_nth_practice_of_the_unit_at_its_own_block():
    found = placed.plan(unit(marker(2)))
    assert found.spots == {("java", 2): ("practice-java-2",)}
    assert found.placed({"key": "practice-java-2"}) and not found.placed({"key": "practice-java"})


def test_no_marker_is_no_plan_and_any_other_comment_is_not_a_marker():
    other = {"type": "html", "text": "<!-- practice notes: keep this short -->"}
    assert placed.plan(unit()) is placed.NONE
    assert placed.plan(unit(other)) is placed.NONE
    doc = unit(other)
    assert placed.outlined(doc, placed.NONE) is doc
    assert placed.spliced(doc["sections"][0], placed.NONE, lambda keys, spot: "x") is (
        doc["sections"][0]
    )


@pytest.mark.parametrize("number", [0, 4, 12])
def test_a_marker_naming_a_practice_the_unit_does_not_have_is_refused_by_name(number):
    with pytest.raises(PageError) as raised:
        page(unit(marker(number)))
    said = str(raised.value)
    assert f"<!-- practice {number} -->" in said and "'java'" in said
    assert "this unit has 3 practices" in said


def test_a_practice_marked_twice_is_refused_by_name():
    with pytest.raises(PageError) as raised:
        page(unit(marker(1), {"type": "para", "text": "Between."}, marker(1)))
    assert "<!-- practice 1 -->" in str(raised.value) and "second time" in str(raised.value)


@pytest.mark.parametrize(
    "holder",
    [
        {"type": "quote", "blocks": [marker(1)]},
        {"type": "disclosure", "summary": "More", "open": False, "blocks": [marker(1)]},
        {"type": "list", "ordered": False, "items": [["An item", marker(1)]]},
    ],
)
def test_a_marker_inside_a_quote_a_disclosure_or_a_list_is_refused(holder):
    with pytest.raises(PageError) as raised:
        page(unit(holder))
    assert "inside a quote, a disclosure or a list" in str(raised.value)


def test_a_marker_in_a_practice_is_refused():
    doc = unit()
    doc["sections"][1] = {**doc["sections"][1], "blocks": [marker(2)]}
    with pytest.raises(PageError) as raised:
        page(doc)
    said = str(raised.value)
    assert "<!-- practice 2 -->" in said and "stands in a practice" in said


# --- the page ------------------------------------------------------------------------------------


def test_a_placed_practice_stands_after_the_part_it_tests_and_is_not_drawn_again():
    text = body(page(unit(marker(1))))
    first, second = text.index("The first part teaches"), text.index("Part two")
    card = text.index('id="card-practice-java"')
    statement = text.index('id="s-practice-java"')
    panel = text.index('data-practice="basics/unit-03/practice-java"')
    assert first < card < statement < panel < second
    key = "basics/unit-03/practice-java"
    for drawn in ('id="card-practice-java"', 'id="s-practice-java"', f'data-practice="{key}"'):
        assert text.count(drawn) == 1, drawn
    # ⭐ The list after the lesson counts and lists only what is still there, in order.
    listed = text[text.index('<section id="practices"') :]
    assert "Practice (2)" in listed and 'id="card-practice-java"' not in listed
    assert listed.index('id="card-practice-java-2"') < listed.index('id="card-practice-java-3"')
    assert text.count("<div data-workspace ") == 1


def test_the_placed_card_list_carries_the_markers_own_anchor():
    text = body(page(unit(marker(2))))
    spot = anchors.block_anchor("java", 2)
    assert f'<section id="{spot}" data-practices data-practices-placed' in text


def test_a_quiz_placed_by_a_marker_is_a_quiz_card_and_its_questions_stand_there():
    text = body(page(unit(marker(3))))
    card = text.index('id="card-practice-java-3"')
    quiz = text.index('data-practice-quiz="basics/unit-03/practice-java-3"')
    assert card < quiz < text.index("Part two")
    assert 'data-practice-kind="quiz"' in text[card : card + 400]
    assert text.count('data-practice-quiz="basics/unit-03/practice-java-3"') == 1


def test_every_practice_placed_leaves_no_list_and_keeps_the_workspace():
    text = body(page(unit(marker(1), marker(2), marker(3))))
    assert '<section id="practices"' not in text
    assert text.count("data-practices-placed") == 3
    assert text.count("<div data-workspace ") == 1


def test_a_quiz_the_lesson_repeats_stays_where_quizonce_drew_it_and_its_marker_draws_nothing():
    stem = QUIZ["questions"][0]["stem"]
    repeat = {"type": "list", "ordered": True, "items": [[stem]]}
    text = body(page(unit(marker(3), repeat)))
    assert text.count('data-practice-quiz="basics/unit-03/practice-java-3"') == 1
    assert "<!-- practice 3 -->" in text
    assert 'id="card-practice-java-3"' not in text


def test_the_same_document_renders_the_same_bytes():
    doc = unit(marker(2))
    assert render(doc, sample_placement()) == render(doc, sample_placement())


def test_the_regions_are_unchanged_by_an_empty_plan():
    doc = unit()
    shown = sample_placement()
    assert practices_region.region(doc, shown, placed.NONE) == practices_region.region(doc, shown)
    found = anchors.entries(placed.outlined(editions.collapsed(doc), placed.NONE))
    assert found == anchors.entries(doc)


# --- the outline and the search index ------------------------------------------------------------


def test_the_outline_lists_a_placed_practice_where_it_stands_under_the_heading_above():
    doc = unit(marker(2))
    found = anchors.entries(placed.outlined(doc, placed.plan(doc)))
    assert [(level, label) for level, label, _ in found] == [
        (1, "Lesson"),
        (2, "Part one"),
        (3, "Build a bitmap"),
        (2, "Part two"),
        (1, "Practice (2)"),
        (2, "Build a field"),
        (2, "Check yourself"),
    ]
    assert found[2][2] == "#" + anchors.block_anchor("java", 2)


def test_search_keeps_the_lesson_around_a_placed_practice_and_none_of_the_practice():
    found = search.read(page(unit(marker(1))))
    text = " ".join(part for _, _, part in found["sections"])
    assert "The first part teaches fields." in text and "The second part teaches bitmaps." in text
    assert "Do the thing." not in text
    headings = [heading for heading, _, _ in found["sections"]]
    assert "Part two" in headings and "Build a field" not in headings


def test_a_practice_with_language_editions_is_placed_as_its_one_card_and_every_edition():
    from tests.studyforge.render.page.test_editions import four

    editions_of = four()
    doc = document(sections=[lesson(marker(1)), *editions_of])
    text = body(page(doc))
    end = text.index("Part two")
    assert text.count("data-practice-card=") == 1 and text.index("data-practice-card=") < end
    for one in editions_of:
        assert text.index(f'id="s-{one["key"]}"') < end
    assert '<section id="practices"' not in text
