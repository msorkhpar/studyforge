"""Mirror of `tests/floor/palettes/__init__.py` (R12).

⛔ **Asserted in BOTH directions**: every rejected identity the live table
names is PLANTED and found by name, and the ACCEPTED identity — cool slate with one loud accent —
is read CLEAN by the same
table in the same run.

⭐ **The conjunction is asserted as a conjunction**: one part of a row, the parts
split across two themes, and two gradient stops in two different gradients are
each read clean, because none of them is a palette anybody sees.
"""

from __future__ import annotations

import pytest

import tests.floor.palettes as palettes_module
from tests.floor.palettes import (
    RULE_PALETTE,
    STYLESHEET_DIR,
    UI_CONVENTION,
    check_rejected_palettes,
    palette_census,
    themes,
)
from tests.floor.palettes.support import (
    ACCEPTED,
    CREAM,
    GRADIENT,
    SATURATED,
    SLATE,
    named,
    tree,
)
from tests.support import assert_package_contract, repository_root


def test_states_its_contract():
    assert_package_contract(palettes_module, "tests.floor.palettes")


# --- a planted rejected identity, by name --------------------------------------


def test_a_planted_WARM_CREAM_AND_TERRACOTTA_theme_is_found_and_named(tmp_path):
    root = tree(tmp_path, ":root { --bg: #faf4e8; --accent: #c96b45; }\n")
    (finding,) = check_rejected_palettes(root)
    assert (finding.path, finding.line, finding.rule) == (
        f"{STYLESHEET_DIR}/palette.css",
        1,
        RULE_PALETTE,
    )
    assert CREAM in finding.message
    assert UI_CONVENTION in finding.message
    assert "ground: hue 20-70" in finding.message
    assert "never leave the two disagreeing" in finding.message


def test_the_same_slate_WITH_teal_green_and_amber_is_refused(tmp_path):
    root = tree(
        tmp_path,
        ":root { --bg: #f1f5f9; --accent: #0f9b8e; --sign: #e8a33d; --focus: #0369a1; }\n",
    )
    assert named(root) == [SLATE]


def test_a_saturated_ground_is_refused_on_its_own(tmp_path):
    root = tree(tmp_path, ":root { --bg: #0b5a3a; --accent: #f1f2ee; }\n")
    assert named(root) == [SATURATED]


def test_a_near_black_ground_with_an_acid_or_vermilion_accent_is_refused(tmp_path):
    root = tree(tmp_path, ":root { --bg: #0b0b0b; --accent: #b6ff1a; }\n")
    assert named(root) == ["Near-black ground, acid-green accent"]
    root = tree(tmp_path / "second", ":root { --bg: #111111; --accent: #e23b0b; }\n")
    assert named(root) == ["Near-black ground, vermilion accent"]


def test_a_purple_to_blue_gradient_is_refused_when_both_stops_are_in_ONE(tmp_path):
    root = tree(
        tmp_path,
        ":root { --bg: #f1f5f2; }\n.hero { background: linear-gradient(#7b2ff7, #2b6cf7); }\n",
    )
    assert named(root) == [GRADIENT]


def test_a_gradient_painted_with_TOKENS_is_resolved_in_that_theme(tmp_path):
    root = tree(
        tmp_path,
        ":root { --bg: #f1f5f2; --one: #7b2ff7; --two: #2b6cf7; }\n"
        ".hero { background: radial-gradient(var(--one), var(--two)); }\n",
    )
    assert named(root) == [GRADIENT]


# --- the conjunction, the other way --------------------------------------------


def test_the_identity_the_user_ACCEPTED_is_read_clean(tmp_path):
    # ⭐ The heart of it: cool slate is what was accepted, and the rejected row is
    # the TRIPLE. A check that refused this would have refused the remedy.
    root = tree(tmp_path, ACCEPTED)
    assert check_rejected_palettes(root) == []
    assert len(themes(root)) == 2


def test_the_SAME_ground_WITHOUT_its_accent_is_clean(tmp_path):
    root = tree(tmp_path, ":root { --bg: #faf4e8; --accent: #23449a; }\n")
    assert check_rejected_palettes(root) == []


def test_two_halves_in_two_THEMES_are_not_one_identity(tmp_path):
    root = tree(
        tmp_path,
        ':root { --bg: #faf4e8; --accent: #23449a; }\n:root[data-theme="dark"] '
        "{ --bg: #26322c; --accent: #c96b45; }\n",
    )
    assert check_rejected_palettes(root) == []


def test_the_same_two_stops_in_TWO_gradients_are_not_one(tmp_path):
    root = tree(
        tmp_path,
        ":root { --bg: #f1f5f2; }\n"
        ".a { background: linear-gradient(#7b2ff7, #7b2ff7); }\n"
        ".b { background: linear-gradient(#2b6cf7, #2b6cf7); }\n",
    )
    assert check_rejected_palettes(root) == []


def test_a_mid_dark_ground_with_character_is_not_a_near_black_one(tmp_path):
    # ⭐ §3's own counter-example: asphalt, which the brief asks FOR.
    root = tree(tmp_path, ":root { --bg: #2b2e31; --accent: #b6ff1a; }\n")
    assert check_rejected_palettes(root) == []


# --- the live tree and the empty one -------------------------------------------


def test_the_LIVE_tree_ships_none_of_them_over_an_inhabited_population():
    root = repository_root()
    assert themes(root), "no shipped theme was read"
    assert check_rejected_palettes(root) == []


def test_the_census_prints_its_denominator_and_what_it_does_NOT_read():
    (line,) = palette_census(repository_root())
    assert "rejected palettes:" in line
    assert "0 shipped" in line
    assert "COLOUR only" in line


def test_a_tree_with_no_convention_and_no_stylesheet_is_SILENT(tmp_path):
    # ⛔ The floor runs over trees that are not this repository.
    assert check_rejected_palettes(tmp_path) == []
    (line,) = palette_census(tmp_path)
    assert "0 rejected identities" in line
    assert "over 0 theme(s)" in line


def test_a_stylesheet_whose_convention_has_no_rejected_table_is_silent(tmp_path):
    header = "| Role | Read from |\n|---|---|\n| `ground` | `--bg` |\n"
    root = tree(tmp_path, ":root { --bg: #0b5a3a; }\n", document=header)
    assert check_rejected_palettes(root) == []


@pytest.mark.parametrize("selector", [":root", ':root:not([data-theme="light"])'])
def test_a_theme_is_read_wherever_its_block_is_declared(tmp_path, selector):
    stylesheet = (
        f":root {{ --accent: #c96b45; }}\n@media (prefers-color-scheme: dark) {{\n"
        f"  {selector} {{ --bg: #faf4e8; }}\n}}\n"
    )
    assert named(tree(tmp_path, stylesheet)) == [CREAM]
