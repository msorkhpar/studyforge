"""Mirror of `src/studyforge/render/page/anchors.py` (R12)."""

from __future__ import annotations

import pytest

from studyforge.render.page import anchors
from studyforge.render.page.errors import PageError

TWO_SECTIONS = {
    "sections": [
        {
            "key": "shared",
            "heading": "Before you start",
            "blocks": [{"type": "para", "text": "p"}],
        },
        {
            "key": "java",
            "heading": "Your first class",
            "blocks": [
                {"type": "heading", "level": 2, "text": "A"},
                {"type": "para", "text": "p"},
                {"type": "heading", "level": 4, "text": "Too deep"},
                {"type": "heading", "level": 3, "text": "B"},
            ],
        },
    ]
}


def test_a_section_anchor_is_prefixed_so_it_cannot_collide_with_a_block():
    assert anchors.section_anchor("practice-java") == "s-practice-java"
    assert anchors.block_anchor("practice-java", 3) == "practice-java-b3"
    assert anchors.section_anchor("java") != anchors.block_anchor("java", 0)


def test_an_anchor_is_derived_from_structure_and_not_from_a_heading():
    # ⭐ A retitled section must not move every anchor beneath it: nothing here
    # reads a word of the prose.
    assert anchors.block_anchor("java", 2) == "java-b2"


@pytest.mark.parametrize("key", ["Java", "practice java", "", None, 7, "a/b"])
def test_a_key_that_is_not_a_slug_is_refused(key):
    # ⛔ Required, never made: a DOM id is minted from this, and a link into the
    # page has to survive an edit to its prose.
    with pytest.raises(PageError):
        anchors.section_anchor(key)


def test_the_refusal_never_quotes_the_key():
    # ⚠️ R7: the key comes from a file a person edits and can be a path.
    offending = "/absolute/elsewhere/notes"
    with pytest.raises(PageError) as raised:
        anchors.section_anchor(offending)
    assert offending not in str(raised.value)


def test_a_slug_key_is_the_negative_control():
    assert anchors.section_anchor("practice-java")


@pytest.mark.parametrize("position", [-1, "0", True, None])
def test_a_block_position_that_is_not_an_ordinal_is_refused(position):
    with pytest.raises(PageError):
        anchors.block_anchor("java", position)


def test_the_outline_lists_sections_only_when_there_is_more_than_one():
    single = {"sections": [TWO_SECTIONS["sections"][1]]}
    levels = [level for level, _, _ in anchors.entries(single)]
    assert 1 not in levels


def test_the_outline_stops_at_level_three():
    # ⚠️ Level 4 and below turn a rail that can be scanned in one glance into a
    # second document.
    labels = [label for _, label, _ in anchors.entries(TWO_SECTIONS)]
    assert "Too deep" not in labels
    assert "B" in labels


def test_every_outline_entry_points_at_an_anchor_the_page_emits():
    # ⭐ Both come from the same walk, so an entry cannot point at nothing.
    assert anchors.entries(TWO_SECTIONS) == (
        (1, "Before you start", "#s-shared"),
        (1, "Your first class", "#s-java"),
        (2, "A", "#java-b0"),
        (3, "B", "#java-b3"),
    )


def test_an_outline_of_fewer_than_two_entries_is_no_outline_at_all():
    lone = {"sections": [{"key": "java", "heading": "T", "blocks": []}]}
    assert anchors.outline(lone) == ""


def test_the_outline_escapes_and_renders_its_labels():
    heading = {"type": "heading", "level": 2, "text": "`x` <y>"}
    document = {
        "sections": [
            {"key": "a", "heading": "One", "blocks": [heading]},
            {"key": "b", "heading": "Two", "blocks": []},
        ]
    }
    markup = anchors.outline(document)
    assert "<code>x</code> &lt;y&gt;" in markup


# --------------------------------------------------------------------------
# Ruling 187 — the outline's anchors are INJECTIVE, not merely covered
# --------------------------------------------------------------------------


def test_no_two_outline_entries_point_at_the_same_anchor():
    # ⛔ **Ruling 187.** `test_every_outline_entry_points_at_an_anchor_the_page
    # _emits` is asserted in both directions and a COLLISION satisfies both
    # halves of it: two sections keyed `java` both yield `#s-java`, every entry
    # still points at an anchor the page emits, and the rail silently sends two
    # lines to one place. Surjectivity was already asserted; this is the other
    # half.
    hrefs = [href for _, _, href in anchors.entries(TWO_SECTIONS)]
    assert len(hrefs) == len(set(hrefs))


def test_the_injectivity_check_above_would_notice_a_collision():
    # ⭐ Reading 2, planted: the same section key twice is exactly how the
    # collision arrives, and it is representable — nothing upstream of this
    # module promises a unit's section keys are distinct.
    section = dict(TWO_SECTIONS["sections"][1])
    colliding = {"sections": [section, dict(section)]}
    hrefs = [href for _, _, href in anchors.entries(colliding)]
    assert len(hrefs) != len(set(hrefs))
