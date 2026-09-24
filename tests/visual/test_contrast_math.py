"""The arithmetic and the ledger — the part of this harness that needs no browser.

⭐ **Everything here is standard library and a file read**, so these assertions
run and carry the same weight on any machine, with or without a browser.
"""

from __future__ import annotations

import pytest

from tests.visual import contrast, palette

#: The spec's own worked values. ⛔ Black on white is exactly 21, and white on
#: white exactly 1 — two numbers that need no library to check, which is the
#: point of writing them down.
BLACK = (0.0, 0.0, 0.0, 1.0)
WHITE = (255.0, 255.0, 255.0, 1.0)


def test_the_extremes_are_the_specifications_numbers() -> None:
    assert contrast.ratio(BLACK, WHITE) == pytest.approx(21.0, abs=1e-9)
    assert contrast.ratio(WHITE, WHITE) == pytest.approx(1.0, abs=1e-9)
    assert contrast.ratio(BLACK, WHITE) == contrast.ratio(WHITE, BLACK)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("rgb(1, 2, 3)", (1.0, 2.0, 3.0, 1.0)),
        ("rgba(1, 2, 3, 0.5)", (1.0, 2.0, 3.0, 0.5)),
        ("rgb(1 2 3 / 50%)", (1.0, 2.0, 3.0, 0.5)),
    ],
)
def test_the_colour_shapes_a_browser_actually_returns_are_read(value, expected) -> None:
    assert contrast.parse(value) == expected


@pytest.mark.parametrize("value", ["transparent", "", "currentColor", "none"])
def test_a_colour_that_does_not_resolve_raises_rather_than_defaulting(value) -> None:
    """⛔ The control for the check above, and the one that matters.

    A parser that returned black for an unresolved token would turn *"this
    token is not defined in this theme"* — the failure `palette.css`'s own
    docstring calls invisible — into a comfortable pass against a dark colour.
    """
    with pytest.raises(contrast.ColourError):
        contrast.parse(value)


def test_a_translucent_foreground_is_composited_before_the_ratio_is_taken() -> None:
    """`--hl-code` is `rgba`; a ratio that ignored alpha would be a number about nothing."""
    half_black = (0.0, 0.0, 0.0, 0.5)
    assert contrast.ratio(half_black, WHITE) < contrast.ratio(BLACK, WHITE)
    assert contrast.ratio(half_black, WHITE) > contrast.ratio(WHITE, WHITE)


@pytest.mark.parametrize(
    ("size", "weight", "expected"),
    [
        (16.0, 400, contrast.AA_NORMAL),
        (24.0, 400, contrast.AA_LARGE),
        (19.0, 700, contrast.AA_LARGE),
    ],
)
def test_large_text_clears_a_lower_bar_exactly_where_the_specification_says(
    size, weight, expected
) -> None:
    assert contrast.threshold(size, weight) == expected


# --- the ledger ------------------------------------------------------------


def test_the_ledger_is_total_over_the_stylesheet_in_both_directions() -> None:
    """Every colour token has a row, and every row names a real token.

    ⛔ This is what stops *"contrast for every palette token"* becoming
    *"contrast for the tokens somebody remembered"*. A token added to
    `palette.css` fails here, on the tree, before it reaches a theme nobody
    looked at.
    """
    tokens = set(palette.colour_tokens())
    rows = set(palette.LEDGER)
    assert tokens - rows == set(), (
        f"colour tokens with no coverage decided: {sorted(tokens - rows)}"
    )
    assert rows - tokens == set(), f"ledger rows naming no token: {sorted(rows - tokens)}"


def test_every_ledger_row_names_one_of_the_four_coverages_and_says_why() -> None:
    kinds = {palette.MEASURED, palette.SURFACE, palette.STRUCTURAL, palette.UNPAINTED}
    for token, (kind, ground, why) in palette.LEDGER.items():
        assert kind in kinds, f"{token}: unknown coverage {kind!r}"
        assert len(why) > 20, f"{token}: a reason this short is a label, not a reason"
        if kind == palette.MEASURED:
            assert ground in palette.LEDGER, f"{token}: names no ground its ratio is taken against"
            assert palette.LEDGER[ground][0] in (palette.SURFACE,), (
                f"{token}: its ground {ground} is not classified as a surface"
            )
        else:
            assert ground is None, f"{token}: only a measured token has a ground"


def test_the_unpainted_rows_are_derived_from_the_stylesheets_not_believed() -> None:
    """⛔ The ledger's excuses are checked against the CSS, in both directions.

    ⚠️ This is the row that would otherwise rot. A token classified `UNPAINTED`
    and then given a use in a stylesheet is a contrast question nobody asked;
    a token painted all along and classified `UNPAINTED` is a check quietly
    skipped. Both fail here.
    """
    derived = set(palette.unpainted())
    declared = {name for name, (kind, _, _) in palette.LEDGER.items() if kind == palette.UNPAINTED}
    assert derived == declared, (
        f"stylesheets paint {sorted(declared - derived)} which the ledger calls unpainted; "
        f"nothing paints {sorted(derived - declared)} which the ledger does not"
    )


def test_every_colour_token_is_declared_in_both_themes() -> None:
    """`palette.css` claims it; this is the claim checked rather than inherited.

    ⚠️ A token declared once is not an error the cascade reports — it silently
    keeps its light value in the dark theme, which is exactly the *"wrong in one
    of them, invisible to whoever authored it"* failure the stylesheet warns
    about.
    """
    once = [token for token, count in palette.defined_in_both().items() if count < 2]
    assert not once, f"colour tokens declared in one theme only: {once}"


def test_a_token_defined_in_one_theme_is_caught() -> None:
    """⛔ The negative control for the check above."""
    broken = ":root { --bg: #fff; --fg: #000; }\n@media (prefers-color-scheme: dark) {\n"
    broken += ":root { --bg: #000; }\n}\n"
    assert palette.defined_in_both(broken) == {"--bg": 2, "--fg": 1}


def test_a_measure_is_not_mistaken_for_a_colour() -> None:
    """⛔ Decided from the value, so `--font-mono` cannot join the contrast walk.

    ⚠️ Not hypothetical: resolved through `getComputedStyle`, a font stack comes
    back as the *inherited text colour*, so a token walk that trusted names
    would have reported a plausible ratio for a font.
    """
    text = ":root { --font-ui: Arial, sans-serif; --measure: 80ch; --fg: #1b1a17; }"
    assert palette.colour_tokens(text) == ("--fg",)
