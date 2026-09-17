"""Mirror of `src/studyforge/render/page/blocks/__init__.py` (R12)."""

from __future__ import annotations

import pytest

from studyforge.archive.blocks import BLOCK_TYPES, CONTAINER_TYPES
from studyforge.render.page import blocks
from studyforge.render.page.errors import PageError
from tests.studyforge.render.page.pages import sample_placement
from tests.support import assert_package_contract

#: One minimal, valid block of every type in the vocabulary. ⛔ Keyed by the
#: archive's names and checked against `BLOCK_TYPES` below, so a twelfth type
#: fails here rather than going unrendered by every test in the suite.
SAMPLES = {
    "heading": {"type": "heading", "level": 2, "text": "H"},
    "para": {"type": "para", "text": "P"},
    "code": {"type": "code", "lang": "java", "text": "x"},
    "table": {"type": "table", "headers": ["a"], "rows": [["b"]]},
    "list": {"type": "list", "ordered": False, "items": ["i"]},
    "image": {"type": "image", "src": "media/a.png", "alt": "A", "width": 10},
    "video": {"type": "video", "src": "media/a.mp4", "title": "T"},
    "rule": {"type": "rule"},
    "quote": {"type": "quote", "blocks": [{"type": "para", "text": "Q"}]},
    "html": {"type": "html", "text": "<div>x</div>"},
    "disclosure": {
        "type": "disclosure",
        "summary": "S",
        "open": False,
        "blocks": [{"type": "para", "text": "D"}],
    },
}


def test_the_package_states_its_contract():
    assert_package_contract(blocks, "studyforge.render.page.blocks")


def test_the_samples_cover_the_vocabulary_exactly():
    assert tuple(SAMPLES) == BLOCK_TYPES


def test_every_block_type_has_exactly_one_renderer():
    # ⛔ A type nobody renders is a lesson's content missing from the page with
    # no error anywhere; a type rendered twice is an answer that depends on
    # import order.
    assert tuple(blocks.RENDERERS) == BLOCK_TYPES


def test_the_mapping_is_in_vocabulary_order():
    # ⚠️ R10: nothing downstream may depend on which module was imported first.
    assert list(blocks.RENDERERS) == list(BLOCK_TYPES)


def test_no_module_claims_a_type_twice():
    claimed = [name for module in blocks.MODULES for name in module.RENDERS]
    assert sorted(claimed) == sorted(BLOCK_TYPES)


@pytest.mark.parametrize("block_type", BLOCK_TYPES)
def test_every_block_type_renders_to_something(block_type):
    markup = blocks.render_one(
        SAMPLES[block_type], 0, placement=sample_placement(), section="shared"
    )
    assert markup.strip(), f"{block_type} renders as nothing"


def test_an_unknown_block_type_is_refused_rather_than_dropped():
    # ⛔ A block silently dropped is a lesson short of a paragraph with nothing
    # to show for it (R6).
    with pytest.raises(PageError) as raised:
        blocks.render_one({"type": "carousel", "text": "x"}, 0, section="shared")
    assert "carousel" in str(raised.value)


def test_a_block_that_is_not_an_object_is_refused():
    with pytest.raises(PageError):
        blocks.render_one("not a block", 0, section="shared")


@pytest.mark.parametrize("block_type", CONTAINER_TYPES)
def test_a_container_gets_its_children_rendered(block_type):
    # ⭐ The recursion is derived from `CONTAINER_TYPES`, so a third container
    # type is walked on the day it is added.
    markup = blocks.render_one(SAMPLES[block_type], 0, section="shared")
    assert "<p>" in markup


def test_a_container_recurses_all_the_way_down():
    nested = {
        "type": "quote",
        "blocks": [
            {
                "type": "disclosure",
                "summary": "S",
                "open": True,
                "blocks": [{"type": "para", "text": "deep"}],
            }
        ],
    }
    markup = blocks.render_one(nested, 0, section="shared")
    assert "<blockquote><details" in markup
    assert "deep" in markup


def test_blocks_are_joined_by_a_newline_so_a_page_can_be_read():
    markup = blocks.render_all(
        [SAMPLES["para"], SAMPLES["rule"], SAMPLES["para"]], section="shared"
    )
    assert markup.count("\n") == 2


# --- W303: a type that is not a name is refused by name --------------------

#: Every way a block's `type` can arrive as something that is not a name.
#: ⛔ Each is valid JSON, so each can reach the dispatcher off disk: `[...]` and
#: `{...}` are the two that are *unhashable*, and those are the ones that used
#: to leave a bare `TypeError` rather than a refusal.
UNNAMEABLE_TYPES = [["para"], {"para": 1}, None, 3, True]


@pytest.mark.parametrize("block_type", UNNAMEABLE_TYPES)
def test_W303_a_type_that_is_not_a_name_is_refused_by_name(block_type):
    # ⛔ Measured reachable through a document that BOTH `archive.document.parse`
    # and `unit.served.parse` accept, so the refusal has to be the page's rather
    # than the interpreter's.
    with pytest.raises(PageError) as raised:
        blocks.render_one({"type": block_type, "text": "x"}, 2, section="shared")
    assert "block 2" in str(raised.value)


@pytest.mark.parametrize("block_type", UNNAMEABLE_TYPES)
def test_W303_the_refusal_describes_the_type_and_never_quotes_the_block(block_type):
    # ⛔ R7: a block's own fields are a corpus's material and can carry anything,
    # so the refusal names what arrived instead of reproducing it.
    with pytest.raises(PageError) as raised:
        blocks.render_one({"type": block_type, "text": "SECRET"}, 0, section="shared")
    assert "SECRET" not in str(raised.value)


def test_W303_a_well_formed_run_of_blocks_still_renders_unchanged():
    # ⭐ The other direction: the guard sits in front of the dispatch and changes
    # nothing that was already renderable.
    markup = blocks.render_all([SAMPLES["para"], SAMPLES["heading"]], section="shared")
    assert "<p>P</p>" in markup
    assert "<h2" in markup


def test_W303_no_module_declares_a_type_its_own_dispatch_cannot_answer():
    # ⛔ This is the property that keeps `_RENDERERS[block["type"]]` in `prose`
    # and `figure` unreachable with a bad key, and so keeps a guard out of both:
    # a renderer is entered only for a type `RENDERERS` already matched, so the
    # key is present by the time it is indexed. ⚠️ A module that claimed a type
    # its own mapping could not answer would put that `KeyError` back.
    unbacked = {
        module.__name__: [name for name in module.RENDERS if name not in module._RENDERERS]
        for module in blocks.MODULES
        if hasattr(module, "_RENDERERS")
    }
    assert unbacked, "no renderer module exposes an inner dispatch, so this asserts nothing"
    assert all(names == [] for names in unbacked.values()), unbacked


def test_an_empty_run_of_blocks_renders_as_nothing():
    assert blocks.render_all(None, section="shared") == ""
    assert blocks.render_all([], section="shared") == ""
