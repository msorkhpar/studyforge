"""Mirror of `src/studyforge/narrate/speakable/panel.py` (R12), and the ruling's acceptance.

⛔ A lesson's code-example panel is a code example,
and a code example is never narrated. The list the page draws as the panel
yields no speech unit, the page carries no audio inside it, the prose around it
keeps its ids and digests, and the heading over it falls silent with it.
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import PurePosixPath

import pytest

from studyforge.narrate.speakable import (
    by_position,
    clip_name,
    clip_names,
    panel,
    parse_clip_name,
    speakable_of,
)
from studyforge.render.page import AUDIO_ATTRIBUTE, Narration
from studyforge.render.page import render as render_page
from tests.studyforge.narrate.speakable import examples
from tests.studyforge.narrate.speakable.test_init import depth2_unit_01
from tests.studyforge.narrate.speakable.test_script import (
    SOURCE_LINE,
    TEST_LINE,
    UNIT,
    listing,
    said,
)
from tests.studyforge.render.page import pages as render_pages


def test_every_suffix_a_runtime_writes_is_a_code_file():
    assert {".java", ".py", ".ts", ".sh", ".sql"} <= set(panel.CODE_SUFFIXES)


def test_a_list_of_code_examples_yields_no_speech_unit():
    assert said([listing(SOURCE_LINE, TEST_LINE)]) == []
    assert said([listing(TEST_LINE)]) == [], "a test with no source beside it is an example too"
    ordered = {**listing(SOURCE_LINE), "ordered": True}
    assert said([ordered]) == [], "an ordered list of examples is not counted aloud"


def test_prose_examples_prose_yields_exactly_the_two_prose_units_at_their_own_positions():
    blocks = [
        {"type": "para", "text": "Before them."},
        listing(SOURCE_LINE, TEST_LINE),
        {"type": "para", "text": "After them."},
    ]
    assert said(blocks) == [
        (f"{UNIT}.shared.b1", "Before them."),
        (f"{UNIT}.shared.b3", "After them."),
    ]


def test_a_list_of_code_examples_nested_in_a_quote_yields_no_speech_unit():
    assert said([{"type": "quote", "blocks": [listing(SOURCE_LINE, TEST_LINE)]}]) == []


@pytest.mark.parametrize(
    "items",
    [
        pytest.param([SOURCE_LINE, "A line with no link."], id="a-plain-item"),
        pytest.param([f"{SOURCE_LINE} and more words than a label ever carries."], id="prose"),
        pytest.param(["See: [the notes](../../m/README.md)"], id="not-code"),
        pytest.param(["Source: [Wrapper.java](https://example.invalid/Wrapper.java)"], id="a-url"),
        pytest.param([f"{SOURCE_LINE} {TEST_LINE}"], id="two-links"),
        pytest.param([[SOURCE_LINE, {"type": "code", "lang": "java", "text": "x"}]], id="parts"),
    ],
)
def test_a_list_that_is_not_all_code_examples_is_still_spoken_item_by_item(items):
    # ⭐ The control: only a list whose EVERY item is one code link and a label
    # falls silent, so a lesson's ordinary lists are not caught by the rule.
    assert said([listing(*items)]), "an ordinary list fell silent"


# --------------------------------------------------------------------------
# ⛔ A lesson's code-example panel is never narrated
# --------------------------------------------------------------------------


def examples_positions(document: dict) -> tuple[tuple, list[tuple]]:
    """`(the Code Examples heading's position, its list items' positions)` in `document`."""
    key = examples.lesson_key(document)
    blocks = next(one for one in document["sections"] if one["key"] == key)["blocks"]
    heading = next(
        index for index, one in enumerate(blocks) if one.get("text") == examples.EXAMPLES_HEADING
    )
    items = [(key, (heading + 1,), sub) for sub in range(len(blocks[heading + 1]["items"]))]
    return (key, (heading,), None), items


def test_a_code_examples_list_and_its_heading_yield_no_speech_unit_and_the_prose_still_speaks():
    document = examples.with_code_examples(depth2_unit_01())
    heading, items = examples_positions(document)
    spoken = by_position(speakable_of(document).units)
    assert items and all(one not in spoken for one in items), "a code example is spoken"
    assert heading not in spoken, "the heading over nothing spoken is spoken"
    # ⭐ The control: the prose after the examples, and its heading, still speak.
    words = [one.speak for one in spoken.values()]
    assert examples.AFTER_HEADING in words and examples.AFTER_PROSE in words


def test_the_rendered_panel_carries_no_audio_even_where_a_record_names_its_clips():
    case = render_pages.depth2_unit_01()
    up = "../" * len(PurePosixPath(case.placement.unit.page).parent.parts)
    document = examples.with_code_examples(case.document, up)
    pairs = {examples.SOURCE: examples.SOURCE, examples.TEST: examples.SOURCE}
    placement = replace(
        case.placement,
        code=(".java",),
        pairing=lambda path: (pairs.get(path, path), examples.TEST),
    )
    heading, items = examples_positions(document)
    # ⭐ The page's narration is joined from the script, as a build joins it.
    clips = {one.position: clip_name(one) + ".mp3" for one in speakable_of(document).units}
    # ⛔ And a record narrated before the ruling still names every item's clip.
    stale = {position: f"stale-{index}.mp3" for index, position in enumerate(items)}
    narration = Narration.of(clips | stale, placement)
    page = render_page(document, placement, narration=narration).decode("utf-8")
    start = page.index("<div data-code-examples")
    panel = page[start : page.index("</details>\n</div>", start)]
    assert "<details data-code-example " in panel, "no panel was drawn; the reading is vacuous"
    assert AUDIO_ATTRIBUTE not in panel, "the code-example panel carries audio"
    assert "stale-" not in page, "a stale code-example clip reached the page"
    opening = page[:start].rsplit("<h2", 1)[1]
    assert examples.EXAMPLES_HEADING in opening and AUDIO_ATTRIBUTE not in opening
    # ⭐ The control: the prose after the panel still plays.
    after = page[page.index(examples.AFTER_PROSE) - 200 : page.index(examples.AFTER_PROSE)]
    assert AUDIO_ATTRIBUTE in after


#: ⛔ What the script minted for `depth2_unit_01` with the code examples in it
#: (`examples.with_code_examples`), read off the minter at `f1b55bc7`, the
#: commit before this ruling. The heading is `shared.b2` and the items are
#: `shared.b3.i1` and `shared.b3.i2`. It is the BEFORE of the record.
BEFORE_THE_EXAMPLES_RULING = (
    "basics--01-getting-started--unit-01.shared.b1-c396109f",
    "basics--01-getting-started--unit-01.shared.b2-216d28e4",
    "basics--01-getting-started--unit-01.shared.b3.i1-5bcd84c2",
    "basics--01-getting-started--unit-01.shared.b3.i2-0658d903",
    "basics--01-getting-started--unit-01.shared.b4-63d21ed8",
    "basics--01-getting-started--unit-01.shared.b5-4552bee1",
    "basics--01-getting-started--unit-01.java.b1-922d0d65",
    "basics--01-getting-started--unit-01.java.b2-ea4a45f5",
    "basics--01-getting-started--unit-01.java.b4.i1-9817129b",
    "basics--01-getting-started--unit-01.java.b4.i2-558a93ca",
    "basics--01-getting-started--unit-01.java.b4.i3-82973017",
    "basics--01-getting-started--unit-01.java.b5.b1-c9388ac2",
    "basics--01-getting-started--unit-01.java.b5.b2.i1-22a76015",
    "basics--01-getting-started--unit-01.java.b5.b2.i2-18f8c385",
)


def test_surviving_prose_around_the_examples_keeps_its_speech_id_and_digest():
    # ⛔ Equal clip names are equal ids AND equal words: nothing that survives
    # the ruling is re-synthesised, and what went away is exactly the panel
    # and the heading over it.
    after = clip_names(speakable_of(examples.with_code_examples(depth2_unit_01())).units)
    assert set(after) < set(BEFORE_THE_EXAMPLES_RULING)
    retired = sorted(set(BEFORE_THE_EXAMPLES_RULING) - set(after))
    assert [parse_clip_name(name)[0].partition(".")[2] for name in retired] == [
        "shared.b2",
        "shared.b3.i1",
        "shared.b3.i2",
    ]
    assert list(after) == [one for one in BEFORE_THE_EXAMPLES_RULING if one not in retired]


# --------------------------------------------------------------------------
# ⛔ a lesson's repeat of its quiz is never spoken: the page draws the quiz there
# --------------------------------------------------------------------------

import copy  # noqa: E402

from tests.studyforge.render.page import test_quizonce as quizonce_cases  # noqa: E402
from tests.studyforge.render.page.test_practice import QUIZ, UNGRADED  # noqa: E402
from tests.studyforge.render.page.test_practice import document as served  # noqa: E402
from tests.studyforge.render.page.test_practice import section as served_section  # noqa: E402


def _without_quiz(document: dict) -> dict:
    """`document` with every practice made a file nothing checks: no quiz can match, so the
    lesson is spoken exactly as it was before quizzes were skipped."""
    plain = copy.deepcopy(document)
    for one in plain["sections"]:
        if one.get("kind") == "practice":
            one["workspace"] = dict(UNGRADED)
    return plain


def _spoken(document: dict) -> dict:
    return {one.id: one.speak for one in speakable_of(document).units}


def _positions(document: dict) -> set:
    return {one.block_path[0] for one in speakable_of(document).units if one.section == "prose"}


def test_a_page_quiz_and_its_folded_key_yield_no_speech_unit_and_nothing_else_moves():
    follow = [{"type": "heading", "level": 2, "text": "Next"}, {"type": "para", "text": "More."}]
    given = quizonce_cases.unit(quizonce_cases.lesson(*follow))
    before, after = _spoken(_without_quiz(given)), _spoken(given)
    # ⭐ The control: without the fix this document speaks the questions, the key and the heading.
    assert "Answer key" in before.values() and "Quiz" in before.values()
    assert _positions(given) == {0, 1, 5, 6}, "a quiz block, its key or its heading is spoken"
    assert {key: before[key] for key in after} == after, "a surviving unit changed id or words"
    assert "Answer key" not in after.values() and "Quiz" not in after.values()
    for stem in quizonce_cases.STEMS:
        assert not any(stem in said for said in after.values()), stem
    units = speakable_of(given).units
    assert len(set(clip_names(units))) == len(units)


def test_a_module_quiz_that_repeats_a_page_quiz_is_silent_and_its_intro_prose_still_speaks():
    given, page, module = quizonce_cases.two_quiz_unit()
    # ⭐ The module quiz repeats the page quiz's questions, as a module quiz does.
    module["questions"] = [*page["questions"], *module["questions"]]
    blocks = given["sections"][0]["blocks"]
    blocks[7]["items"] = [
        [one["stem"], {"type": "list", "ordered": False, "items": ["a", "b"]}]
        for one in module["questions"]
    ]
    blocks.insert(6, {"type": "para", "text": "This quiz covers both pages of the module."})
    before, after = _spoken(_without_quiz(given)), _spoken(given)
    assert "Module quiz" in before.values() and "Answer key" in before.values()
    assert {key: before[key] for key in after} == after, "a surviving unit changed id or words"
    # The page quiz's heading falls silent; the module quiz's heading has its intro under it.
    assert _positions(given) == {0, 1, 5, 6}
    assert "This quiz covers both pages of the module." in after.values()
    assert "Answer key" not in after.values() and "Quiz" not in after.values()
    for one in module["questions"]:
        assert not any(one["stem"] in said for said in after.values()), one["stem"]
    units = speakable_of(given).units
    assert len(set(clip_names(units))) == len(units)


def test_a_quiz_heading_over_questions_no_practice_asks_is_spoken_as_before():
    other = quizonce_cases.lesson()
    other["blocks"][3] = {"type": "list", "ordered": True, "items": ["A different question?"]}
    given = quizonce_cases.unit(other)
    assert _spoken(given) == _spoken(_without_quiz(given))
    assert "Quiz" in _spoken(given).values() and "Answer key" in _spoken(given).values()


def test_a_unit_with_no_quiz_practice_speaks_exactly_what_it_did():
    given = served(sections=[quizonce_cases.lesson(), served_section(workspace=dict(UNGRADED))])
    assert speakable_of(given) == speakable_of(copy.deepcopy(given))
    assert len(speakable_of(given).units) == len(_spoken(_without_quiz(given)))
    assert QUIZ["questions"][0]["stem"] in " ".join(_spoken(given).values())
