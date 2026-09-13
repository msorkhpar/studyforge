"""Mirror of `src/studyforge/render/page/blocks/prose.py` (R12)."""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

from studyforge.render.page.blocks import prose
from studyforge.render.pageassets import SURFACE_CLASSES, SURFACE_HOOKS


def render(block: dict, position: int = 0, section: str = "shared") -> str:
    """One prose block, with the arguments the dispatcher supplies."""
    return prose.render(block, position, section=section)


def test_the_declared_types_are_exactly_the_branches():
    assert sorted(prose.RENDERS) == sorted(prose._RENDERERS)


def test_a_heading_carries_the_anchor_the_outline_points_at():
    assert render({"type": "heading", "level": 2, "text": "Hi"}, 3, "java") == (
        '<h2 id="java-b3">Hi</h2>'
    )


@pytest.mark.parametrize(
    ("level", "expected"), [(1, 2), (2, 2), (3, 3), (6, 6), (7, 6), (None, 2), ("x", 2)]
)
def test_a_heading_is_clamped_to_h2_through_h6(level, expected):
    # ⛔ Never h1: the page's single h1 is the unit's title.
    markup = render({"type": "heading", "level": level, "text": "T"})
    assert markup.startswith(f"<h{expected} ")


def test_a_paragraph_escapes_and_renders_its_markers():
    assert render({"type": "para", "text": "a `b` & <c>"}) == (
        "<p>a <code>b</code> &amp; &lt;c&gt;</p>"
    )


def test_a_rule_is_the_element_and_nothing_else():
    assert render({"type": "rule"}) == "<hr>"


def test_a_list_takes_the_published_class_and_its_own_tag():
    ordered = render({"type": "list", "ordered": True, "items": ["a"]})
    unordered = render({"type": "list", "ordered": False, "items": ["a"]})
    assert ordered == f'<ol class="{SURFACE_CLASSES["list"]}"><li>a</li></ol>'
    assert unordered.startswith(f'<ul class="{SURFACE_CLASSES["list"]}">')


def test_a_list_item_is_inline_prose():
    markup = render({"type": "list", "ordered": False, "items": ["**b** <x>"]})
    assert "<strong>b</strong> &lt;x&gt;" in markup


def test_a_nested_list_renders_as_a_list_inside_its_parent_item():
    # ⛔ W258: never its parent's text, and its parts stay in reading order.
    klass = SURFACE_CLASSES["list"]
    nested = {"type": "list", "ordered": True, "items": ["x", "<y>"]}
    block = {"type": "list", "ordered": False, "items": [["a", nested, "b"], "c"]}
    assert render(block) == (
        f'<ul class="{klass}"><li>a<ol class="{klass}"><li>x</li><li>&lt;y&gt;</li></ol>b</li>'
        f"<li>c</li></ul>"
    )


def test_a_table_scrolls_inside_its_own_box():
    # ⛔ Without the wrapper the page scrolls sideways and every paragraph with it.
    markup = render({"type": "table", "headers": ["H"], "rows": [["a", "<b>"]]})
    assert markup.startswith(f'<div class="{SURFACE_HOOKS["table_scroll"]}"><table>')
    assert "<thead><tr><th>H</th></tr></thead>" in markup
    assert "<td>&lt;b&gt;</td>" in markup
    assert markup.endswith("</tbody></table></div>")


def test_a_table_with_no_headers_emits_no_thead():
    markup = render({"type": "table", "headers": [], "rows": [["a"]]})
    assert "<thead>" not in markup


def test_a_quote_holds_whatever_it_holds():
    markup = prose.render({"type": "quote"}, 0, children="<p>x</p>")
    assert markup == "<blockquote><p>x</p></blockquote>"


def test_a_disclosure_is_closed_unless_the_archive_says_open():
    shut = {"type": "disclosure", "summary": "S", "open": False}
    ajar = {"type": "disclosure", "summary": "S", "open": True}
    closed = prose.render(shut, 0, children="<p>a</p>")
    opened = prose.render(ajar, 0, children="<p>a</p>")
    assert " open>" not in closed
    assert "<details class=" in closed and " open>" in opened


def test_a_disclosure_escapes_its_summary():
    markup = prose.render({"type": "disclosure", "summary": "<b>"}, 0, children="")
    assert "<summary>&lt;b&gt;</summary>" in markup


def test_a_disclosure_takes_the_published_class():
    markup = prose.render({"type": "disclosure", "summary": "S"}, 0, children="")
    assert f'class="{SURFACE_CLASSES["disclosure"]}"' in markup


def test_not_one_class_name_is_typed_in_this_module():
    # ⛔ `W9`, made structural. Every class this module emits comes from the
    # published surface, so it cannot invent a name the stylesheet does not
    # target — which is the failure that renders a complete, unstyled page with
    # no error anywhere.
    source = Path(prose.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    literals = [
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    ]
    typed = [value for value in literals if re.search(r'class="[a-z]', value)]
    assert typed == [], f"a class name is typed here rather than published: {typed}"
