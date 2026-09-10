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


def test_an_empty_run_of_blocks_renders_as_nothing():
    assert blocks.render_all(None, section="shared") == ""
    assert blocks.render_all([], section="shared") == ""
