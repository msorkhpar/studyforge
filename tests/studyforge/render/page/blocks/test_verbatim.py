"""Mirror of `src/studyforge/render/page/blocks/verbatim.py` (R12).

⛔ **This is the seam whose failure is silent**, and these are the three tests
`SF-12`'s acceptance names. ⚠️ The first two go through **`markdown.parse`** and
never a hand-built block dict: the promise spans two tasks, and a test that built
`{"type": "para", …}` by hand would assert `SF-12` against `SF-12`'s own belief
about what `SF-07` emits — and the belief is the thing that can be wrong.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from studyforge.archive.blocks import BLOCK_TYPES
from studyforge.archive.markdown import parse
from studyforge.render.page import blocks
from studyforge.render.page.blocks import verbatim

#: ⚠️ Off CommonMark's type-6 list on purpose. A tag that IS on that list — a
#: `<div>` on its own line — is correctly an `html` block, and a test using one
#: would prove nothing about the promise.
UNKNOWN_TAG = "<blink>hello</blink>"


def render(markdown: str) -> str:
    """Parse real Markdown and render it, so both halves of the promise are live."""
    return blocks.render_all(parse(markdown), section="shared")


def test_a_para_whose_text_is_tag_shaped_renders_as_visible_text():
    # ⛔ The clause `SF-07` declined CommonMark's type-7 raw-HTML rule to keep:
    # an unknown tag on its own line stays prose, because a lesson TEACHING HTML
    # must keep it. `SF-12` is the half that gets it onto the page.
    parsed = parse(UNKNOWN_TAG + "\n")
    assert [block["type"] for block in parsed] == ["para"], (
        "the reader no longer keeps a tag-shaped line as prose; this test is "
        "asserting the wrong half of the promise"
    )
    page = render(UNKNOWN_TAG + "\n")
    assert "&lt;blink&gt;hello&lt;/blink&gt;" in page
    assert "<blink>" not in page


def test_an_html_block_reaches_the_page_verbatim():
    # ⭐ The converse, so a fix to the test above that escapes everything is
    # caught here rather than by a reader looking at a lesson's own markup as
    # literal text.
    parsed = parse("<div>\nreal markup\n</div>\n")
    assert [block["type"] for block in parsed] == ["html"]
    page = render("<div>\nreal markup\n</div>\n")
    assert "<div>\nreal markup\n</div>" in page
    assert "&lt;div&gt;" not in page


def test_exactly_one_block_type_is_emitted_without_escaping():
    # ⛔ The one that survives the vocabulary changing. The two tests above are
    # pinned to two fixture strings and a twelfth block type would pass both
    # while quietly acquiring a raw path.
    assert blocks.RAW_TYPES == frozenset({"html"})
    assert set(verbatim.RENDERS) == blocks.RAW_TYPES
    assert blocks.RAW_TYPES < set(BLOCK_TYPES)
    assert len(BLOCK_TYPES) - len(blocks.RAW_TYPES) == 10


@pytest.mark.parametrize("block_type", sorted(set(BLOCK_TYPES) - {"html"}))
def test_every_other_block_type_escapes_a_tag_in_its_text(block_type):
    # ⭐ The set is derived, so a twelfth block type is covered on the day it is
    # added rather than on the day somebody remembers.
    assert block_type not in blocks.RAW_TYPES


def test_the_decision_is_the_declared_type_and_never_the_text():
    # ⚠️ The specific way this goes wrong: deciding from the text. Two blocks
    # with byte-identical `text` and different `type` must render differently.
    payload = "<blink>x</blink>"
    as_prose = blocks.render_all([{"type": "para", "text": payload}], section="shared")
    as_markup = blocks.render_all([{"type": "html", "text": payload}], section="shared")
    assert as_prose != as_markup
    assert "&lt;blink&gt;" in as_prose
    assert payload in as_markup


def test_verbatim_imports_nothing_but_the_future():
    # ⭐ The module's own claim, asserted with `ast` rather than by grepping for
    # a word its docstring uses: its whole content is that it does not escape,
    # and importing the escaper would put the thing it refuses to do one
    # keystroke away.
    tree = ast.parse(Path(verbatim.__file__).read_text(encoding="utf-8"))
    imported = [node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)] + [
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    ]
    assert imported == ["__future__"]


def test_a_missing_text_field_renders_as_nothing_rather_than_as_none():
    assert verbatim.render({"type": "html"}, 0) == ""
