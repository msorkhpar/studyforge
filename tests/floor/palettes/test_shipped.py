"""Mirror of `tests/floor/palettes/shipped.py` (R12).

⛔ **A theme is a LOOK, and the three readings that make that true are asserted
here**: a block inside an `@media` is read, a block that redeclares what the base
already says is read ONCE, and two stops in two gradients are two groups rather
than one pool.

⭐ **The live population is asserted inhabited**: a reader that found
no theme and no gradient would make every verdict above it a green over nothing.
"""

from __future__ import annotations

import tests.floor.palettes.shipped as shipped_module
from tests.floor.palettes.colours import colour
from tests.floor.palettes.shipped import blocks, gradients, stylesheets, themes
from tests.floor.palettes.support import ACCEPTED, tree
from tests.support import assert_package_contract, repository_root


def test_states_its_contract():
    assert_package_contract(shipped_module, "tests.floor.palettes.shipped")


# --- what a block is -----------------------------------------------------------


def test_the_INNERMOST_block_is_read_and_its_line_is_where_it_opens():
    text = "/* a\n   comment */\n:root { --bg: #fff; }\n@media (x) {\n  .a { color: red; }\n}\n"
    read = blocks(text)
    assert [(selector, line) for selector, _body, line in read] == [(":root", 3), (".a", 5)]


def test_a_comment_is_not_read_and_does_not_move_a_line():
    text = "/* --bg: #000; */\n:root { --bg: #fff; }\n"
    (block,) = blocks(text)
    assert block[2] == 2
    assert "--bg: #fff" in block[1]


# --- what a theme is -----------------------------------------------------------


def test_both_themes_of_a_two_theme_stylesheet_are_read(tmp_path):
    read = themes(tree(tmp_path, ACCEPTED))
    assert [theme.label for theme in read] == [":root", ':root[data-theme="dark"]']
    assert read[1].tokens["bg"] == colour("#0f172a")
    # ⭐ The dark block redefines four tokens and INHERITS the rest from the base.
    assert read[1].tokens["surface"] == colour("#f8fafc")


def test_a_block_that_redeclares_the_SAME_look_is_read_ONCE(tmp_path):
    stylesheet = (
        ":root { --bg: #f1f5f9; }\n"
        "@media (prefers-color-scheme: dark) {\n  :root { --bg: #f1f5f9; }\n}\n"
    )
    assert len(themes(tree(tmp_path, stylesheet))) == 1


def test_a_block_inside_an_at_media_is_a_theme_of_its_own(tmp_path):
    stylesheet = (
        ":root { --bg: #f1f5f9; }\n"
        "@media (prefers-color-scheme: dark) {\n  :root:not([x]) { --bg: #0f172a; }\n}\n"
    )
    read = themes(tree(tmp_path, stylesheet))
    assert [theme.label for theme in read] == [":root", ":root:not([x])"]


def test_a_block_that_declares_no_colour_token_is_not_a_theme(tmp_path):
    stylesheet = ":root { --bg: #f1f5f9; }\n.card { color: var(--bg); border-radius: 4px; }\n"
    assert [theme.label for theme in themes(tree(tmp_path, stylesheet))] == [":root"]


# --- gradients are groups ------------------------------------------------------


def test_each_gradient_is_its_OWN_group():
    read = gradients("a { background: linear-gradient(#7b2ff7, #2b6cf7); }\n.b { x: none; }", {})
    assert len(read) == 1
    assert len(read[0]) == 2
    two = gradients("linear-gradient(#7b2ff7, #7b2ff7) radial-gradient(#2b6cf7, #2b6cf7)", {})
    assert [len(group) for group in two] == [2, 2]


def test_a_stop_written_as_a_TOKEN_is_resolved_against_the_theme_it_is_read_in():
    tokens = {"one": colour("#7b2ff7")}
    ((only,),) = gradients("linear-gradient(var(--one), var(--missing))", tokens)
    assert only == tokens["one"]


def test_a_gradient_no_token_of_this_theme_paints_is_no_group():
    assert gradients("linear-gradient(var(--absent), var(--gone))", {}) == ()


def test_a_PAINTING_stylesheets_gradient_belongs_to_every_theme(tmp_path):
    root = tree(tmp_path, ACCEPTED)
    painting = root / "src/studyforge/render/assets/lists.css"
    painting.write_text(".x { background: linear-gradient(var(--bg), var(--fg)); }\n", "utf-8")
    read = themes(root)
    assert len(read) == 2
    assert all(theme.gradients for theme in read)
    # ⭐ Resolved per theme: the same gradient reads two different pairs.
    assert read[0].gradients != read[1].gradients


# --- the live population -------------------------------------------------------


def test_the_LIVE_tree_ships_themes_and_gradients():
    root = repository_root()
    read = themes(root)
    assert stylesheets(root)
    assert read, "no shipped theme was read"
    assert any(theme.gradients for theme in read), "no gradient was read"


def test_a_tree_with_no_stylesheet_reads_NOTHING(tmp_path):
    assert themes(tmp_path) == []
    assert stylesheets(tmp_path) == []
