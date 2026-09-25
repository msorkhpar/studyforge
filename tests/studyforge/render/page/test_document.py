"""Mirror of `src/studyforge/render/page/document.py` (R12)."""

from __future__ import annotations

import pytest

from studyforge.corpus.placement import identity as identity_block
from studyforge.render import templates
from studyforge.render.page import document as document_module
from studyforge.render.page.assets import AUDIO_ATTRIBUTE
from studyforge.render.page.errors import PageError
from studyforge.render.page.narration import SILENT, Narration
from tests.studyforge.render.page.pages import depth1_unit_02, sample_placement


def a_document(**overrides) -> dict:
    """A served unit document, minimal but shaped exactly as the builder writes one."""
    base = {
        "api": 1,
        "source": "demo",
        "address": ["depth-one"],
        "variant": "prose",
        "unit": 1,
        "title": "A Unit",
        "practices": {"declared": 0, "archived": 0},
        "sections": [
            {
                "key": "prose",
                "kind": "lesson",
                "heading": "A Unit",
                "blocks": [{"type": "para", "text": "p"}],
                "video": None,
                "workspace": None,
            }
        ],
        "built_from": [],
    }
    return {**base, **overrides}


def compose(**overrides) -> str:
    return document_module.compose(a_document(**overrides), sample_placement())


def test_a_page_ends_in_exactly_one_newline():
    page = compose()
    assert page.endswith("</html>\n")
    assert not page.endswith("\n\n")


def test_the_identity_block_is_on_the_page_and_reads_back():
    # ⛔ R4: discovery reads this block and never the path.
    page = compose()
    read = identity_block.parse(page, depth=1)
    assert read.corpus == "demo"
    assert read.unit == 1
    assert read.variant == "prose"
    assert list(read.address.segments) == ["depth-one"]


def test_a_document_that_cannot_identify_itself_is_refused_as_a_page_error():
    with pytest.raises(PageError):
        compose(variant="Not A Slug")


def test_the_masthead_prints_no_bare_kind_label_and_no_builder_slug():
    # ⛔ The address slugs joined by middle dots are builder words, and the
    # variant alone under the title is a bare kind word; the masthead is the trail and the title,
    # and nothing else.
    page = compose()
    masthead = page.split("<header>", 1)[1].split("</header>", 1)[0]
    assert "<p>" not in masthead
    assert "prose" not in masthead
    assert "·" not in page
    assert "depth-one ·" not in page


def test_the_variant_is_still_the_page_s_own_in_its_identity_block():
    # ⭐ The other way: the variant is not lost, only no longer printed alone.
    page = compose()
    head = page.split("<body>", 1)[0]
    assert "prose" in head


def test_a_document_with_no_title_is_refused():
    with pytest.raises(PageError):
        compose(title="   ")


def test_a_document_with_no_sections_is_refused():
    # ⛔ A title and nothing else is indistinguishable from a unit with nothing
    # to say.
    with pytest.raises(PageError):
        compose(sections=[])


def test_a_complete_unit_shows_no_pending_panel():
    assert "Practices still to come" not in compose()


def test_a_short_unit_says_so_with_both_counts():
    markup = document_module.pending(a_document(practices={"declared": 3, "archived": 1}))
    assert "1 practice is here, 2 still to come." in markup
    # ⛔ No builder word and no middle dot in what the reader reads.
    assert "archived" not in markup
    assert "·" not in markup


def test_the_count_agrees_with_its_number():
    markup = document_module.pending(a_document(practices={"declared": 4, "archived": 2}))
    assert "2 practices are here, 2 still to come." in markup


def test_a_unit_nothing_declared_a_count_for_is_also_outstanding():
    # ⚠️ `declared is None` is not the same as zero and must not render as it.
    markup = document_module.pending(a_document(practices={"declared": None, "archived": 0}))
    assert "cannot be called finished" in markup


def test_a_unit_with_no_practices_block_shows_no_panel():
    assert document_module.pending(a_document(practices=None)) == ""


def test_the_player_is_absent_when_the_body_carries_no_audio():
    # ⛔ The page renderer mints no speech id and writes no audio attribute, so
    # a page without narration carries no transport for nothing.
    assert document_module.player("<p>no audio here</p>") == ""
    assert '<footer id="player"' not in compose()


def test_the_player_appears_the_moment_the_body_carries_audio():
    # ⭐ The negative control run negatively: when narration writes the attribute the transport
    # arrives with it.
    body = f'<p {AUDIO_ATTRIBUTE}="audio/a-1.mp3">spoken</p>'
    markup = document_module.player(body)
    # ⛔ `hidden` is part of the opening tag and is the player's: the transport ships
    # hidden and `narration.js` unhides it once there is something behind it, the
    # way `read-mark.html` ships its control hidden. With scripting off a reader
    # is shown nothing rather than a Play button that cannot play, which is the
    # row's own "no dead control".
    assert markup.startswith('<footer id="player" hidden>')
    assert '<audio id="narrator"' in markup


def test_a_narrated_page_links_no_script_that_says_whether_its_clips_are_here():
    # ⛔ The page asks its first clip itself (`narration-probe.js`): nothing
    # written beside the pages says whether the clips arrived, so nothing stale
    # can hide them.
    where = sample_placement()
    narration = Narration.of({("prose", (0,), None): "a-11111111.mp3"}, where)
    page = document_module.compose(a_document(), where, narration=narration)
    assert AUDIO_ATTRIBUTE in page, "⛔ born vacuous: the page must carry a narrated passage"
    assert page.count("<script src=") == 1, "a narrated page links one script: the bundle"
    assert "narration-clips" not in page


def test_a_page_that_was_promised_nothing_carries_no_gap_panel():
    # ⛔ No permanent notice: a corpus without narration is COMPLETE, not short.
    assert document_module.narration_gap(SILENT) == ""
    assert "narration-gap" not in compose()


def test_the_gap_panel_names_both_counts_and_not_only_the_shortfall():
    # ⚠️ A bare "2 passages are silent" leaves the reader unable to tell a mostly
    # working unit from a wholly broken one, which is the same conflation one
    # layer along.
    narration = Narration.of(
        {("s", (0,), None): "a-11111111.mp3"},
        sample_placement(),
        missing=[("s", (1,), None), ("s", (2,), None)],
    )
    markup = document_module.narration_gap(narration)
    assert "2 of 3 narrated passages" in markup
    assert markup.startswith('<section data-section="narration-gap">')


def test_the_gap_notice_rides_inside_the_players_own_region():
    # ⭐ So a page can never say "some narration is missing" with no transport to
    # say it about — and so no eighth skeleton slot had to be minted for it.
    narration = Narration.of({}, sample_placement(), missing=[("s", (0,), None)])
    body = f'<p {AUDIO_ATTRIBUTE}="">spoken, and not on disk</p>'
    markup = document_module.player(body, narration)
    assert markup.index("narration-gap") < markup.index('<footer id="player"')


def test_a_body_with_no_audio_at_all_takes_neither_the_player_nor_the_notice():
    # ⛔ The negative control run negatively: the gate is still derived from the
    # body, so a caller naming gaps for a page that emitted no attribute gets
    # neither half rather than a notice about a transport that is not there.
    narration = Narration.of({}, sample_placement(), missing=[("s", (0,), None)])
    assert document_module.player("<p>no audio here</p>", narration) == ""


def test_the_panel_tells_the_reader_which_of_the_two_states_this_is():
    # ⛔ **PLANT `P13` SURVIVED TWELVE RED AND THIS IS THE TEST IT ASKED FOR.**
    # Deleting the panel's last sentence — the one that says the audio WENT
    # MISSING rather than was NEVER MADE — broke nothing, and that sentence is
    # the entire narration promise as a reader experiences it. ⭐ The
    # counts are machinery; this is what makes the two states distinguishable to
    # a person, so it is a CONTRACT, exactly as `player.html`'s keyboard sentence
    # is one.
    markup = templates.template(document_module.NARRATION_GAP_TEMPLATE).template
    assert "never been narrated" in markup, "the panel does not name the state it is NOT"
    assert "went missing" in markup, "the panel does not name the state it IS"


def test_the_gap_markup_is_a_template_file_and_not_a_python_string():
    # ⛔ R13: the count is composed in Python and every word a reader sees is a
    # file, which is `pending`'s split exactly.
    assert document_module.NARRATION_GAP_TEMPLATE in templates.names()
    assert "\n" in templates.template(document_module.NARRATION_GAP_TEMPLATE).template


def test_the_player_markup_is_a_template_file_and_not_a_python_string():
    # ⛔ R13's one live piece of work in the ported module: the triple-quoted
    # `PLAYER` literal becomes a file during the port, not after it.
    assert document_module.PLAYER_TEMPLATE in templates.names()
    assert "\n" in templates.template(document_module.PLAYER_TEMPLATE).template


def test_an_optional_region_is_empty_or_its_markup_and_one_newline():
    assert document_module._region("") == ""
    assert document_module._region("<x>") == "<x>\n"


def test_the_page_is_byte_for_byte_stable_across_runs():
    # ⛔ R10: no clock, no directory enumeration, no set iteration.
    case = depth1_unit_02()
    first = document_module.compose(case.document, case.placement)
    second = document_module.compose(case.document, case.placement)
    assert first == second


def test_every_slot_the_skeleton_declares_is_filled_by_the_composer():
    # ⭐ Strict substitution already refuses a mismatch at run time; this says so
    # at the level a reviewer reads, and names the slots.
    assert templates.placeholders(document_module.SKELETON) == frozenset(
        {
            "title",
            "heading",
            "headingattributes",
            "identity",
            "stylesheet",
            "script",
            "meta",
            "breadcrumb",
            "rail",
            "outline",
            "body",
            "pending",
            "mark",
            "player",
            "nav",
        }
    )


# --------------------------------------------------------------------------
# A unit page states its title once
# --------------------------------------------------------------------------


def heading_of(page: str) -> str:
    """The page's `<h1>`, tag and all."""
    start = page.index("<h1")
    return page[start : page.index("</h1>", start) + len("</h1>")]


def with_material(*blocks, title: str = "Testing") -> dict:
    """A served document whose one section opens with `blocks`."""
    return a_document(
        title=title,
        sections=[
            {
                "key": "prose",
                "kind": "lesson",
                "heading": title,
                "blocks": list(blocks),
                "video": None,
                "workspace": None,
            }
        ],
    )


def test_a_page_whose_material_restates_the_title_in_other_words_says_it_once():
    # ⭐ **As a real corpus carries it**: the unit is titled `Testing`
    # and its material opens with `10. Testing in jPOS Client Implementation`.
    document = with_material(
        {"type": "heading", "level": 1, "text": "10. Testing in jPOS Client"},
        {"type": "para", "text": "p"},
    )
    page = document_module.compose(document, sample_placement())
    assert page.count("10. Testing in jPOS Client") == 1
    assert "<h1" in heading_of(page) and "10. Testing in jPOS Client" in heading_of(page)


def test_a_page_whose_material_restates_the_title_in_its_own_words_says_it_once():
    # ⭐ **The same defect as this repository's `depth1` fixture carries it**: the
    # heading is at level 2 and says exactly the unit's title.
    document = with_material(
        {"type": "heading", "level": 2, "text": "Testing"},
        {"type": "para", "text": "p"},
    )
    page = document_module.compose(document, sample_placement())
    assert page.count(">Testing</h") == 1
    assert heading_of(page).endswith(">Testing</h1>")


def test_a_page_whose_material_states_no_title_is_headed_by_the_units():
    # ⛔ The common case for an authored corpus, and it is unchanged: nothing was
    # promoted, so nothing is withheld and the `<h1>` is the unit's own name.
    document = with_material({"type": "para", "text": "first"})
    page = document_module.compose(document, sample_placement())
    assert heading_of(page) == "<h1>Testing</h1>"
    assert ">first</p>" in page


def test_a_leading_heading_that_says_something_else_is_not_taken_off_the_page():
    # ⛔ *"A source whose opening heading differs from the unit title carries real
    # content that must not vanish."* ⚠️ It has a PEER at its own level, so it
    # names a part of the material rather than the whole of it.
    document = with_material(
        {"type": "heading", "level": 2, "text": "Before you start"},
        {"type": "para", "text": "p"},
        {"type": "heading", "level": 2, "text": "After you start"},
    )
    page = document_module.compose(document, sample_placement())
    assert heading_of(page) == "<h1>Testing</h1>"
    assert ">Before you start</h2>" in page


def test_the_promoted_heading_keeps_its_anchor():
    # ⭐ What makes this a MOVE rather than a deletion: a link or a bookmark into
    # the page lands where it always did.
    document = with_material({"type": "heading", "level": 1, "text": "10. Testing"})
    page = document_module.compose(document, sample_placement())
    assert '<h1 id="prose-b0"' in page


def test_the_promoted_heading_keeps_its_clip_and_brings_the_transport():
    # ⛔ Every clip the walker mints reaches exactly one element — so a heading
    # the page moved must carry the audio it carried in the body, or the corpus
    # has a file on disk that nothing can ever play.
    document = with_material({"type": "heading", "level": 1, "text": "10. Testing"})
    narration = Narration.of({("prose", (0,), None): "a-11111111.mp3"}, sample_placement())
    page = document_module.compose(document, sample_placement(), narration=narration)
    assert AUDIO_ATTRIBUTE in heading_of(page)
    assert '<footer id="player"' in page, "the page's only passage is its heading"


def test_a_page_with_no_promoted_heading_carries_no_heading_attributes():
    assert document_module.heading_attributes(with_material({"type": "para", "text": "p"})) == ""


def test_the_tab_and_the_identity_still_name_the_unit_and_not_the_material():
    # ⛔ The `<h1>` names the PAGE; the title names the UNIT, and the contents,
    # the trail and the bar between units all use the latter.
    document = with_material({"type": "heading", "level": 1, "text": "10. Testing"})
    page = document_module.compose(document, sample_placement())
    assert "<title>Testing</title>" in page
    assert 'data-label="Testing"' in page
    assert "10. Testing" not in page[: page.index("<body>")]


def test_the_promoted_heading_is_inline_prose_and_is_escaped():
    # ⚠️ It is material and carries the archive's inline markers, exactly as the
    # same block would have carried them in the body.
    document = with_material({"type": "heading", "level": 1, "text": "`x` <y>"})
    page = document_module.compose(document, sample_placement())
    assert "<code>x</code> &lt;y&gt;" in heading_of(page)
