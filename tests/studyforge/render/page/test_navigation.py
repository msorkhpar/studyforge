"""Mirror of `src/studyforge/render/page/navigation.py` (R12)."""

from __future__ import annotations

import pytest

from studyforge.render import templates
from studyforge.render.page import navigation
from studyforge.render.page.errors import PageError
from studyforge.render.pageassets import SURFACE_HOOKS
from tests.support import repository_root

#: This module's subject, as source, for the two R13 sweeps below.
SOURCE = (repository_root() / "src" / "studyforge" / "render" / "page" / "navigation.py").read_text(
    encoding="utf-8"
)

#: Every glyph this module's regions put in front of a reader that is not a
#: letter, a digit or punctuation a keyboard types. ⛔ The population is the
#: FINDING `SF-34` handed over, written down: the bar's two arrows, and the
#: trail's separator, which would have been the third instance.
PRODUCT_GLYPHS = ("\u2190", "\u2192", "\u203a", "\u2014", "\u00b7")

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
    fields = {field for field, _ in navigation.LINK_SLOTS}
    assert fields == set(navigation.Links.__dataclass_fields__)


def test_every_slot_of_the_bar_is_authored_in_a_template_that_wants_exactly_two_values():
    # ⛔ `SF-34`'s handed finding, at the mechanism: the row is a FILE now, so the
    # `rel` and the arrow are not in Python to be got wrong. ⚠️ `placeholders`
    # rather than a substring, because `fill` is exact in both directions and a
    # template that wanted a third value would fail at run time, not here.
    for _, row in navigation.LINK_SLOTS:
        assert row in templates.names(), row
        assert templates.placeholders(row) == frozenset({"href", "label"}), row


# --------------------------------------------------------------------------
# R13 — no glyph and no markup of the bar's or the trail's in Python
# --------------------------------------------------------------------------


@pytest.mark.parametrize("glyph", PRODUCT_GLYPHS)
def test_no_product_glyph_is_typed_in_this_module(glyph):
    # ⛔ R13, and the population is `SF-34`'s finding rather than this test's
    # guess. ⚠️ The docstring QUOTES the two arrows it removed, which is the
    # shape that would make a naive `glyph in SOURCE` read red on a green tree —
    # so the sweep reads the code and not the prose.
    assert glyph not in code_of(SOURCE), glyph


def test_the_glyph_sweep_reads_the_code_and_not_the_docstrings():
    # ⭐ Reading 3, the subject that cannot match: strip the code and the two
    # arrows the docstrings quote must still be THERE, or the sweep above is
    # passing because it is looking at nothing.
    prose = SOURCE.replace(code_of(SOURCE), "")
    assert "\u2190" in prose and "\u2192" in prose


def test_the_glyph_sweep_would_catch_a_glyph_put_back():
    # ⭐ Reading 2, planted in a form the clause did not picture: not the arrow
    # the finding named, but the separator, in an f-string, in a loop body.
    planted = code_of(SOURCE) + '\nROW = f"<li>\u203a {x}</li>"\n'
    assert any(glyph in planted for glyph in PRODUCT_GLYPHS)


def test_no_rel_value_of_the_bar_is_typed_in_this_module():
    # ⛔ The other half of the same finding: `rel="prev"` was `("previous",
    # "prev", "\u2190 ")` and is markup. It lives in `link-previous.html` now.
    assert 'rel="' not in code_of(SOURCE)
    assert 'rel="prev"' in templates.template("link-previous.html").template


def code_of(source: str) -> str:
    """`source` with every string literal and comment removed — the code, only.

    ⛔ Built with `ast` and `tokenize` rather than a regex, because the thing
    being searched for is a character that also appears in this module's own
    prose, and a sweep that cannot tell the two apart reads the wrong one.
    """
    import io
    import tokenize

    kept = []
    for token in tokenize.generate_tokens(io.StringIO(source).readline):
        if token.type in (tokenize.COMMENT, tokenize.STRING):
            continue
        kept.append(token.string)
    return "\n".join(kept)


# --------------------------------------------------------------------------
# A neighbour with no generated page falls back to the root index's anchor
# --------------------------------------------------------------------------

#: The index slot every fallback hangs its fragment on.
AN_INDEX = navigation.Link("../../index.html", "Depth Two Demo")

#: A unit key, exactly as `Address.unit_key` mints one.
A_KEY = "basics/01-getting-started/unit-03"


def test_a_neighbour_with_no_page_points_at_its_own_row_on_the_root_index():
    # ⛔ The clause: *falls back to the root index anchor for it rather than
    # dangling*. The href is None — a DECLARED absence — and the key is the
    # anchor `render.index.disclosure` gives that unit's row.
    links = navigation.Links(next=navigation.Link(None, "Fields", A_KEY), index=AN_INDEX)
    markup = navigation.between_units(links)
    assert f'href="../../index.html#{A_KEY}"' in markup
    assert 'rel="next"' in markup


def test_a_neighbour_that_has_a_page_is_the_negative_control_for_that_fallback():
    # ⭐ Run negatively: the same slot with an href must NOT acquire a fragment.
    links = navigation.Links(next=navigation.Link("../x/y.unit.html", "Fields", A_KEY))
    markup = navigation.between_units(links)
    assert 'href="../x/y.unit.html"' in markup
    assert "#" not in markup


def test_a_neighbour_with_no_page_and_no_key_drops_rather_than_guessing():
    # ⛔ Ruling 164: this is chrome, and there is nothing useful to point at.
    links = navigation.Links(next=navigation.Link(None, "Fields"), index=AN_INDEX)
    assert 'rel="next"' not in navigation.between_units(links)
    assert 'rel="up"' in navigation.between_units(links)


def test_a_fallback_with_no_index_to_hang_it_on_drops_too():
    links = navigation.Links(next=navigation.Link(None, "Fields", A_KEY))
    assert navigation.between_units(links) == ""


def test_the_composed_fallback_is_gated_as_one_string():
    # ⛔ A key is a corpus's own text. Gating only the index's half would let a
    # key no href can be spelled with reach the page.
    links = navigation.Links(
        next=navigation.Link(None, "Fields", 'x" onclick="alert(1)'), index=AN_INDEX
    )
    assert 'rel="next"' not in navigation.between_units(links)


def test_the_index_slot_itself_has_no_fallback_because_it_is_the_fallback():
    index = navigation.Link(None, "Demo", A_KEY)
    assert navigation.between_units(navigation.Links(index=index)) == ""


# --------------------------------------------------------------------------
# The breadcrumb — "Section \u203a Module \u203a Lesson", from data
# --------------------------------------------------------------------------

#: A depth-2 trail, labelled the way `contents` labels one: the corpus's own
#: word for each depth, then the title the corpus gave that container.
A_TRAIL = (
    navigation.Crumb("section", "Basics", "../../index.html"),
    navigation.Crumb("module", "Getting Started", "../01-getting-started.section.html"),
    navigation.Crumb("", "Your first class"),
)


def test_the_trail_reads_from_data_in_hierarchy_order():
    markup = navigation.breadcrumb(A_TRAIL)
    assert '<nav aria-label="Breadcrumb">' in markup
    assert (
        markup.index("Basics") < markup.index("Getting Started") < markup.index("Your first class")
    )


def test_every_word_of_the_trail_came_out_of_the_trail():
    # ⛔ R1: not one sentence of this framework's own is on the trail. The only
    # words it emits are the ones the caller handed it, plus markup.
    import re

    markup = navigation.breadcrumb(A_TRAIL)
    given = {word for crumb in A_TRAIL for word in f"{crumb.level} {crumb.title}".split()}
    shown = set(re.sub(r"<[^>]*>", " ", markup).split()) - {"\u203a"}
    assert shown, "the trail put no words on the page at all"
    assert shown <= given, shown - given


def test_the_level_word_is_wrapped_in_the_published_hooks_and_not_a_new_spelling():
    # ⛔ `SF-14/1`: two renderers had each invented their own spelling for this.
    markup = navigation.breadcrumb(A_TRAIL)
    attribute, value = SURFACE_HOOKS["kind"], SURFACE_HOOKS["level"]
    assert f'<span {attribute}="{value}">section</span> Basics' in markup
    assert f'<span {attribute}="{value}">module</span> Getting Started' in markup


def test_a_corpus_that_names_a_level_with_nothing_loses_the_space_with_the_word():
    # ⚠️ A conditional separator left in the caller is a page that differs from
    # its golden by one character on every such corpus.
    trail = (navigation.Crumb("", "Basics", "../i.html"), navigation.Crumb("", "Here"))
    assert "<li><a" in navigation.breadcrumb(trail)
    assert "> Basics" not in navigation.breadcrumb(trail)


def test_the_separator_stands_between_crumbs_and_never_before_the_first():
    markup = navigation.breadcrumb(A_TRAIL)
    separator = templates.fill(navigation.SEPARATOR_TEMPLATE)
    assert markup.count(separator) == len(A_TRAIL) - 1
    assert f"<ol><li>{separator}" not in markup


def test_the_last_crumb_is_the_page_and_is_never_a_link():
    # ⛔ A page that links to itself is a way to get nowhere.
    trail = (*A_TRAIL[:2], navigation.Crumb("", "Your first class", "./itself.unit.html"))
    markup = navigation.breadcrumb(trail)
    assert '<li aria-current="page">' in markup
    assert "itself.unit.html" not in markup


def test_a_crumb_with_no_page_keeps_its_words_and_loses_only_its_link():
    # ⛔ Ruling 164 read at the element: dropping the crumb would renumber the
    # hierarchy on the page, which is worse than an unlinked word.
    trail = (navigation.Crumb("section", "Basics"), *A_TRAIL[1:])
    markup = navigation.breadcrumb(trail)
    assert "Basics" in markup
    assert markup.count("<li") == len(trail)


def test_a_crumb_whose_href_is_refused_keeps_its_words_too():
    trail = (navigation.Crumb("section", "Basics", "javascript:alert"), *A_TRAIL[1:])
    markup = navigation.breadcrumb(trail)
    assert "Basics" in markup
    assert "javascript" not in markup


def test_a_permitted_href_is_the_negative_control_for_both_of_those_drops():
    markup = navigation.breadcrumb(A_TRAIL)
    assert 'href="../../index.html"' in markup


def test_a_crumbs_title_is_escaped_and_rendered():
    trail = (navigation.Crumb("<b>", "`x` & <y>", "../i.html"), navigation.Crumb("", "Here"))
    markup = navigation.breadcrumb(trail)
    assert "<code>x</code> &amp; &lt;y&gt;" in markup
    assert "&lt;b&gt;" in markup


@pytest.mark.parametrize("trail", [None, (), (navigation.Crumb("section", "Only"),)])
def test_a_trail_of_fewer_than_two_crumbs_is_no_trail_at_all(trail):
    # ⛔ One crumb is a list of one: chrome that says nothing, which is the same
    # argument `outline` makes about a single entry.
    assert navigation.breadcrumb(trail) == ""


def test_the_trail_is_byte_for_byte_stable_across_calls():
    # ⛔ R10, at the region that reads a template file once per crumb.
    assert navigation.breadcrumb(A_TRAIL) == navigation.breadcrumb(A_TRAIL)


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
    hrefs = [href for _, _, href in navigation.entries(TWO_SECTIONS)]
    assert len(hrefs) == len(set(hrefs))


def test_the_injectivity_check_above_would_notice_a_collision():
    # ⭐ Reading 2, planted: the same section key twice is exactly how the
    # collision arrives, and it is representable — nothing upstream of this
    # module promises a unit's section keys are distinct.
    section = dict(TWO_SECTIONS["sections"][1])
    colliding = {"sections": [section, dict(section)]}
    hrefs = [href for _, _, href in navigation.entries(colliding)]
    assert len(hrefs) != len(set(hrefs))
