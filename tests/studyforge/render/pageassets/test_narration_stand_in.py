"""Mirror of `src/studyforge/render/assets/narration-stand-in.js` (R12).

⭐ Where a narrated passage the page is not showing is shown instead. The
browser reading is `tests/visual/test_practice_workspace.py`; what a TEXT can
hold is that nothing is opened, that the two stand-ins are the ones named, and
that `narration.js` marks and scrolls to what this answers.
"""

from __future__ import annotations

import re

from studyforge.render.pageassets import SCRIPT_PARTS, text

PART = "narration-stand-in.js"


def behaviour(name: str = PART) -> str:
    """A part with its comments removed, so a claim is about the code."""
    return re.sub(r"/\*.*?\*/", "", text(name), flags=re.DOTALL)


def test_it_precedes_the_narration_that_reads_it_with_no_guard():
    order = list(SCRIPT_PARTS)
    assert order.index(PART) < order.index("narration.js")
    assert "var standIn = window.studyforge.standIn," in behaviour("narration.js")


def test_nothing_is_opened_and_nothing_is_drawn():
    # ⛔ Opening a code example loads a full editor, which only the reader's
    # own hand may start: this part only NAMES where a passage stands.
    body = behaviour()
    for word in (".open =", "setAttribute(", "removeAttribute(", "click(", "toggle", "innerHTML"):
        assert word not in body, word
    assert "window.studyforge.standIn = standIn;" in body


def test_a_closed_entry_stands_in_as_its_summary_and_a_listed_practice_as_its_card():
    body = behaviour()
    assert "var CLOSED = 'details:not([open])';" in body
    assert "closed.querySelector('summary')" in body
    assert "var PRACTICE = 'section[data-kind=\"practice\"][hidden]';" in body
    assert "document.querySelector('li[' + CARD + '=\"' + practice.id + '\"]')" in body
    # ⚠️ Bounded, so a page can never loop here.
    assert "level < LEVELS" in body


def test_narration_marks_the_stand_in_and_scrolls_to_it():
    body = behaviour("narration.js")
    lighting = body[body.index("function highlight()") : body.index("function reveal(")]
    assert "standing = at === -1 ? null : standIn(passages[at]);" in lighting
    assert "if (standing) { standing.removeAttribute(SPEAKING); }" in lighting
    assert "if (standing) { standing.setAttribute(SPEAKING, 'true'); }" in lighting
    revealing = body[body.index("function reveal(") : body.index("function load(")]
    assert "var target = passage && (standIn(passage) || passage);" in revealing
