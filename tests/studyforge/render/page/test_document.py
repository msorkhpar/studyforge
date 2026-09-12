"""Mirror of `src/studyforge/render/page/document.py` (R12)."""

from __future__ import annotations

import pytest

from studyforge.corpus.placement import identity as identity_block
from studyforge.render import templates
from studyforge.render.page import document as document_module
from studyforge.render.page.assets import AUDIO_ATTRIBUTE
from studyforge.render.page.errors import PageError
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


def test_the_masthead_names_where_the_unit_sits():
    assert "<p>depth-one · prose</p>" in compose()


def test_a_document_with_no_title_is_refused():
    with pytest.raises(PageError):
        compose(title="   ")


def test_a_document_with_no_sections_is_refused():
    # ⛔ A title and nothing else is indistinguishable from a unit with nothing
    # to say.
    with pytest.raises(PageError):
        compose(sections=[])


def test_a_complete_unit_shows_no_pending_panel():
    assert "More to come" not in compose()


def test_a_short_unit_says_so_with_both_counts():
    markup = document_module.pending(a_document(practices={"declared": 3, "archived": 1}))
    assert "1 of 3 archived" in markup
    assert "2 to come" in markup


def test_a_unit_nothing_declared_a_count_for_is_also_outstanding():
    # ⚠️ `declared is None` is not the same as zero and must not render as it.
    markup = document_module.pending(a_document(practices={"declared": None, "archived": 0}))
    assert "cannot be called finished" in markup


def test_a_unit_with_no_practices_block_shows_no_panel():
    assert document_module.pending(a_document(practices=None)) == ""


def test_the_player_is_absent_when_the_body_carries_no_audio():
    # ⛔ At M1 `SF-12` mints no speech id and writes no audio attribute, so the
    # gate is never open and a page carries no transport for nothing.
    assert document_module.player("<p>no audio here</p>") == ""
    assert '<footer id="player"' not in compose()


def test_the_player_appears_the_moment_the_body_carries_audio():
    # ⭐ The negative control run negatively, and the M3 behaviour asserted now:
    # when `SF-18` writes the attribute the transport arrives with it.
    body = f'<p {AUDIO_ATTRIBUTE}="audio/a-1.mp3">spoken</p>'
    markup = document_module.player(body)
    # ⛔ `hidden` is part of the opening tag and is `SF-18`'s: the transport ships
    # hidden and `narration.js` unhides it once there is something behind it, the
    # way `read-mark.html` ships its control hidden. With scripting off a reader
    # is shown nothing rather than a Play button that cannot play, which is the
    # row's own "no dead control".
    assert markup.startswith('<footer id="player" hidden>')
    assert '<audio id="narrator"' in markup


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
            "identity",
            "stylesheet",
            "script",
            "meta",
            "breadcrumb",
            "outline",
            "body",
            "pending",
            "mark",
            "player",
            "nav",
        }
    )
