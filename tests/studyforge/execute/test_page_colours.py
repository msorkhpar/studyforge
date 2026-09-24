"""Mirror of `src/studyforge/execute/page_colours.py` (R12): the page's colours, read.

⭐ **Each reading is checked against the stylesheet's own words**, and each
refusal names what it could not read — a colour the editor cannot be given is
a refused editor, never a silently stock one.
"""

from __future__ import annotations

import pytest

from studyforge.execute import page_colours
from studyforge.execute.page_colours import (
    GROUND,
    INK,
    EditorColoursUnread,
    code_block,
    colour,
    highlight,
    palette,
    property_of,
)
from studyforge.render.pageassets import AssetError


def test_each_theme_carries_every_colour_property_of_the_other():
    themes = palette()
    assert set(themes) == {"light", "dark"}
    colours = {key for key in themes["dark"] if key.startswith(("--code", "--tok"))}
    assert colours and colours <= set(themes["light"])
    assert themes["light"]["--code-bg"] != themes["dark"]["--code-bg"]


def test_the_last_rule_naming_a_token_wins():
    # ⭐ `code-highlight.css`'s documented cascade: `annotation` is in the
    # punctuation group AND the type group, and the type group comes later.
    painted = highlight()
    assert painted["annotation"]["color"] == "var(--tok-type)"
    assert painted["keyword"]["font-weight"] == "600"
    assert painted["comment"]["font-style"] == "italic"
    # ⭐ A container that paints nothing is read as inheriting, not as a colour.
    assert painted["expression"]["color"] == "inherit"


def test_the_code_blocks_ground_and_ink_are_named_properties():
    assert code_block() == {GROUND: "--code-bg", INK: "--code-fg"}


def test_a_value_that_is_not_a_palette_property_is_refused_without_reproducing_it():
    assert property_of("var(--tok-type)") == "--tok-type"
    with pytest.raises(EditorColoursUnread, match="got a str") as refused:
        property_of("teal")
    assert "teal" not in str(refused.value)


def test_colours_are_spelled_the_workbenchs_way():
    assert colour("#ABC") == "#aabbcc"
    assert colour("#0b1120") == "#0b1120"
    assert colour("#0b1120", "40") == "#0b112040"
    # ⛔ No `#` of its own, so refused, and the value is never echoed (R7).
    for refused in ("teal", "var(--x)", "rgb(1, 2, 3)", "rgba(255, 201, 51, .12)"):
        with pytest.raises(EditorColoursUnread) as said:
            colour(refused)
        assert refused not in str(said.value)


def test_a_stylesheet_that_cannot_be_read_is_refused(monkeypatch):
    def unreadable(name):
        raise AssetError(f"cannot read the page asset {name!r}: gone")

    monkeypatch.setattr(page_colours, "text", unreadable)
    with pytest.raises(EditorColoursUnread, match="palette.css"):
        palette()
