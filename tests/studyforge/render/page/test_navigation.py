"""Mirror of `src/studyforge/render/page/navigation.py` (R12)."""

from __future__ import annotations

import pytest

from studyforge.render.page import navigation
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
    assert navigation.section_anchor("practice-java") == "s-practice-java"
    assert navigation.block_anchor("practice-java", 3) == "practice-java-b3"
    assert navigation.section_anchor("java") != navigation.block_anchor("java", 0)


def test_an_anchor_is_derived_from_structure_and_not_from_a_heading():
    # ⭐ A retitled section must not move every anchor beneath it: nothing here
    # reads a word of the prose.
    assert navigation.block_anchor("java", 2) == "java-b2"


@pytest.mark.parametrize("key", ["Java", "practice java", "", None, 7, "a/b"])
def test_a_key_that_is_not_a_slug_is_refused(key):
    # ⛔ Required, never made: a DOM id is minted from this, and a link into the
    # page has to survive an edit to its prose.
    with pytest.raises(PageError):
        navigation.section_anchor(key)


def test_the_refusal_never_quotes_the_key():
    # ⚠️ R7: the key comes from a file a person edits and can be a path.
    offending = "/absolute/elsewhere/notes"
    with pytest.raises(PageError) as raised:
        navigation.section_anchor(offending)
    assert offending not in str(raised.value)


def test_a_slug_key_is_the_negative_control():
    assert navigation.section_anchor("practice-java")


@pytest.mark.parametrize("position", [-1, "0", True, None])
def test_a_block_position_that_is_not_an_ordinal_is_refused(position):
    with pytest.raises(PageError):
        navigation.block_anchor("java", position)


def test_the_outline_lists_sections_only_when_there_is_more_than_one():
    single = {"sections": [TWO_SECTIONS["sections"][1]]}
    levels = [level for level, _, _ in navigation.entries(single)]
    assert 1 not in levels


def test_the_outline_stops_at_level_three():
    # ⚠️ Level 4 and below turn a rail that can be scanned in one glance into a
    # second document.
    labels = [label for _, label, _ in navigation.entries(TWO_SECTIONS)]
    assert "Too deep" not in labels
    assert "B" in labels


def test_every_outline_entry_points_at_an_anchor_the_page_emits():
    # ⭐ Both come from the same walk, so an entry cannot point at nothing.
    assert navigation.entries(TWO_SECTIONS) == (
        (1, "Before you start", "#s-shared"),
        (1, "Your first class", "#s-java"),
        (2, "A", "#java-b0"),
        (3, "B", "#java-b3"),
    )


def test_an_outline_of_fewer_than_two_entries_is_no_outline_at_all():
    lone = {"sections": [{"key": "java", "heading": "T", "blocks": []}]}
    assert navigation.outline(lone) == ""


def test_the_outline_escapes_and_renders_its_labels():
    heading = {"type": "heading", "level": 2, "text": "`x` <y>"}
    document = {
        "sections": [
            {"key": "a", "heading": "One", "blocks": [heading]},
            {"key": "b", "heading": "Two", "blocks": []},
        ]
    }
    markup = navigation.outline(document)
    assert "<code>x</code> &lt;y&gt;" in markup


def test_no_links_is_no_bar():
    assert navigation.between_units(None) == ""
    assert navigation.between_units(navigation.Links()) == ""


def test_the_bar_emits_its_slots_in_the_stated_order():
    links = navigation.Links(
        previous=navigation.Link("../a.unit.html", "Previous"),
        next=navigation.Link("../c.unit.html", "Next"),
        index=navigation.Link("../../index.html", "Contents"),
    )
    markup = navigation.between_units(links)
    assert markup.index('rel="prev"') < markup.index('rel="up"') < markup.index('rel="next"')


def test_a_refused_scheme_drops_its_slot_rather_than_rendering_dead_text():
    links = navigation.Links(previous=navigation.Link("javascript:alert", "Nope"))
    assert navigation.between_units(links) == ""


def test_a_permitted_scheme_is_the_negative_control_for_that_drop():
    links = navigation.Links(previous=navigation.Link("../a.unit.html", "Yes"))
    assert "Yes" in navigation.between_units(links)


def test_a_label_is_escaped():
    links = navigation.Links(index=navigation.Link("../i.html", "<b>&"))
    assert "&lt;b&gt;&amp;" in navigation.between_units(links)


def test_the_slots_are_the_fields_of_links():
    fields = {field for field, _, _ in navigation.LINK_SLOTS}
    assert fields == set(navigation.Links.__dataclass_fields__)
