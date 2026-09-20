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
    # ⚠️ A PEER at its own level, so this heading is the section's content and
    # not the page's own title (`W407`) — the label has to reach the outline for
    # there to be anything to escape.
    peer = {"type": "heading", "level": 2, "text": "z"}
    document = {
        "sections": [
            {"key": "a", "heading": "One", "blocks": [heading, peer]},
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


# --------------------------------------------------------------------------
# W407 — the heading the page is headed by, and the two ways it says the title
# --------------------------------------------------------------------------


def titled(*blocks, title: str = "Testing", **overrides) -> dict:
    """A one-section document whose material opens with `blocks`."""
    section = {"key": "prose", "kind": "lesson", "heading": title, "blocks": list(blocks)}
    return {"title": title, "sections": [{**section, **overrides}]}


def test_an_opening_heading_that_dominates_its_material_is_the_title():
    # ⭐ **The measured case.** A unit titled `Testing` opens with
    # `10. Testing in jPOS Client Implementation` — the same statement, not the
    # same words — over sections one level below it. A rule that only compared
    # text leaves that page reading its title twice, which is what `W388/17` saw.
    block = {"type": "heading", "level": 1, "text": "10. Testing in jPOS Client"}
    document = titled(
        block,
        {"type": "heading", "level": 2, "text": "10.1 Unit"},
        {"type": "heading", "level": 2, "text": "10.2 Integration"},
    )
    assert anchors.title_heading(document) is block


def test_the_same_material_one_level_down_is_still_the_title():
    # ⛔ **This is the reading that threw out the level test.** The SAME corpus
    # writes 13 of its documents with the title at level 2 and its sections at
    # level 3; keyed on level 1, those thirteen pages kept reading their title
    # twice. What every opener has in common is that nothing else stands at its
    # level — not which level that is.
    block = {"type": "heading", "level": 2, "text": "1. Introduction to the thing"}
    document = titled(
        block,
        {"type": "heading", "level": 3, "text": "1.1 What it is"},
        {"type": "heading", "level": 3, "text": "1.2 What it is not"},
    )
    assert anchors.title_heading(document) is block


def test_the_peers_are_counted_on_the_declared_level_and_not_the_rendered_one():
    # ⛔ `heading_level` clamps to `h2..h6`, so a level-1 opener and the level-2
    # sections beneath it RENDER identically. A dominance test that asked the
    # clamp would refuse exactly the documents this rule exists for.
    block = {"type": "heading", "level": 1, "text": "A title"}
    document = titled(block, {"type": "heading", "level": 2, "text": "A section"})
    peer = document["sections"][0]["blocks"][1]
    assert anchors.heading_level(block) == anchors.heading_level(peer)
    assert anchors.title_heading(document) is block


def test_a_leading_heading_with_a_peer_is_a_section_and_stays_where_it_is():
    # ⛔ The clause that keeps the rule from deleting content: an opening heading
    # that has a sibling at its own level names a PART of the material, and the
    # page has never said it.
    block = {"type": "heading", "level": 2, "text": "Before you start"}
    document = titled(block, {"type": "heading", "level": 2, "text": "After you start"})
    assert anchors.title_heading(document) is None


def test_a_heading_with_peers_that_says_the_units_title_is_still_the_title():
    # ⭐ The second clause: a page cannot print the same sentence twice and call
    # the second one content.
    block = {"type": "heading", "level": 2, "text": "Testing"}
    document = titled(block, {"type": "heading", "level": 2, "text": "Something else"})
    assert anchors.title_heading(document) is block


def test_a_heading_that_is_not_the_first_block_is_never_the_pages_own():
    # ⛔ Positional. A second `# ...` further down is content, however it is
    # written and whatever it says.
    document = titled(
        {"type": "para", "text": "p"},
        {"type": "heading", "level": 1, "text": "Testing"},
    )
    assert anchors.title_heading(document) is None


def test_material_that_opens_with_a_paragraph_promotes_nothing():
    # ⛔ *"A source with no leading heading must not lose its first paragraph."*
    assert anchors.title_heading(titled({"type": "para", "text": "first"})) is None


def test_only_the_opening_section_is_asked():
    # ⭐ A later section's first heading sits nowhere near the page's title and is
    # that section's own name — it is what separates it from the section above.
    document = {
        "title": "Testing",
        "sections": [
            {"key": "shared", "heading": "Before", "blocks": [{"type": "para", "text": "p"}]},
            {
                "key": "prose",
                "heading": "Testing",
                "blocks": [{"type": "heading", "level": 1, "text": "Testing"}],
            },
        ],
    }
    assert anchors.title_heading(document) is None


@pytest.mark.parametrize("level", [True, "1", None, 1.0])
def test_headings_whose_levels_are_unusable_are_peers_of_each_other(level):
    # ⚠️ `heading_level` defaults an unusable level to 2 so the heading still
    # renders. Here they are compared as they were declared, so two unusable
    # levels are the same level — and an opener with such a peer is not a title.
    block = {"type": "heading", "level": level, "text": "Something else"}
    document = titled(block, {"type": "heading", "level": level, "text": "Another"})
    assert anchors.title_heading(document) is None
    assert anchors.title_heading(titled(block)) is block


@pytest.mark.parametrize("text", ["   ", "", None, 7])
def test_a_heading_with_nothing_in_it_is_never_the_pages_title(text):
    # ⛔ It dominates whatever is under it and it is still not a title: promoting
    # one would leave the page with a blank `<h1>` and the unit's own name
    # nowhere on it. It stays in the body, where it has always rendered empty.
    block = {"type": "heading", "level": 2, "text": text}
    assert anchors.title_heading(titled(block)) is None
    assert anchors.title_heading(titled(block, title="   ")) is None


def test_the_outline_does_not_list_the_heading_the_page_is_headed_by():
    # ⛔ A contents list whose first line is the title printed above it says
    # nothing, and the entry would point at the heading the reader is looking at.
    document = titled(
        {"type": "heading", "level": 1, "text": "10. Testing"},
        {"type": "heading", "level": 2, "text": "10.1 Unit"},
        {"type": "heading", "level": 3, "text": "10.1.1 Deeper"},
    )
    assert anchors.entries(document) == (
        (2, "10.1 Unit", "#prose-b1"),
        (3, "10.1.1 Deeper", "#prose-b2"),
    )


def test_the_headings_beneath_it_keep_their_own_levels():
    # ⚠️ The register asked what happens to the `<h2>`s beneath a promoted
    # heading: NOTHING. Promotion renumbers nothing, so the page's outline is the
    # document's own outline rather than a copy flattened onto one level.
    document = titled(
        {"type": "heading", "level": 1, "text": "10. Testing"},
        {"type": "heading", "level": 2, "text": "10.1 Unit"},
        {"type": "heading", "level": 3, "text": "10.1.1 Deeper"},
    )
    assert [level for level, _, _ in anchors.entries(document)] == [2, 3]


def test_an_outline_that_kept_the_promoted_heading_would_read_differently():
    # ⭐ Reading 2, planted: give the opening heading a peer at its own level and
    # it is content again — it is listed, at the level the material wrote it.
    document = titled(
        {"type": "heading", "level": 2, "text": "10. Testing"},
        {"type": "heading", "level": 2, "text": "11. Something"},
    )
    assert anchors.entries(document) == (
        (2, "10. Testing", "#prose-b0"),
        (2, "11. Something", "#prose-b1"),
    )
