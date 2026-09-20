"""Clause 2 — computed contrast, for every palette token, in both themes.

⛔ **"Computed" is load-bearing.** Every colour here is what the *browser* said
the colour was after the cascade, the media query and the custom-property
resolution had all run. Nothing is read out of `palette.css` and compared to a
number typed in a test — that check exists already, in `test_palette`, and it
cannot see a token the dark block forgot or a rule that overrode one.

⭐ **Three claims, and together they are total over the palette:**

1. **Every token resolves in both themes**, and the two themes disagree — the
   *"defined once and therefore wrong in one of them"* failure the stylesheet's
   own docstring calls invisible.
2. **Every element that paints text on a real page clears WCAG AA** for its size
   and weight, against the ground it actually sits on.
3. **Every `MEASURED` token clears AA against its declared ground**, whether or
   not this corpus's fixtures happen to contain the construct that shows it —
   `--tok-number` has no numeric literal in either fixture, and a check that
   covered only what the fixtures paint would have said so in no way at all.

⚠️ `palette.UNPAINTED` tokens have no ratio because nothing paints with them.
That is `QA-03/2`, a finding about the palette, and not a hole here.
"""

from __future__ import annotations

import pytest

from tests.visual import contrast, palette, site, theme
from tests.visual.page import SCHEMES, OpenPage

#: Tokens whose ratio is asserted, taken from the ledger rather than listed.
MEASURED_TOKENS = tuple(
    token for token, (kind, _, _) in palette.LEDGER.items() if kind == palette.MEASURED
)


@pytest.fixture(scope="module")
def readings(browser, built_site: site.Site) -> dict:
    """One pass over both themes and every page kind, reused by every check below.

    ⛔ **Every page kind since `W98`, and that is what makes clause 2 total over
    `SF-34`'s chrome.** Four of the six regions — the between-units bar, the
    practice panel, a container's unit listing and the root index's disclosure
    tree — were painted by `chrome.css` and read by nothing here, because the
    harness wrote no page that carried one. ⚠️ `SF-34`'s Acceptance row 2(b) is
    the clause that was part-Blocked on it.

    ⭐ A module-scoped reading because launching a browser and laying out four
    pages to answer one question at a time turns a two-second check into a
    minute — and a slow harness is one somebody starts skipping.

    ⚠️ It opens its **own** tab rather than taking `open_page`, which is
    function-scoped: a module-scoped fixture that asks for a narrower one is a
    `ScopeMismatch`, and the shape that hides the error is to widen `open_page`
    — which would then leak one test's navigation into the next.

    ⛔ **Opening its own tab means CLOSING its own tab** (`W397`), which is what
    the `with` is for: a tab left open here outlives this module and costs the
    session a renderer process for the rest of the run.
    """
    built = built_site
    taken: dict = {}
    with OpenPage(browser) as page:
        for scheme in SCHEMES:
            resolved: dict[str, str] = {}
            elements: list[dict] = []
            for case in site.pages():
                page.open(built.url(case), scheme=scheme)
                resolved = theme.resolve(page)
                elements += [dict(each, case=case) for each in theme.text_elements(page)]
            taken[scheme] = {"resolved": resolved, "elements": elements}
    return taken


def test_every_colour_token_resolves_in_both_themes(readings: dict) -> None:
    unresolved = {
        scheme: sorted(token for token, value in taken["resolved"].items() if value is None)
        for scheme, taken in readings.items()
    }
    assert not any(unresolved.values()), f"tokens the browser could not resolve: {unresolved}"


def test_no_colour_token_is_the_same_in_both_themes(readings: dict) -> None:
    """⛔ The check `palette.css` asks for in its own docstring, taken from the browser.

    ⚠️ A token declared only in `:root` does not fail to resolve in dark — it
    resolves to its **light** value, which is exactly why the stylesheet calls
    the failure invisible to whoever authored it. Identity across the two
    themes is what that looks like from here.
    """
    light, dark = (readings[scheme]["resolved"] for scheme in SCHEMES)
    same = sorted(token for token in light if light[token] == dark[token])
    assert not same, f"identical in light and dark, so one theme is wrong: {same}"


@pytest.mark.parametrize("scheme", SCHEMES)
def test_every_element_painting_text_clears_aa_against_the_ground_it_sits_on(
    readings: dict, scheme: str
) -> None:
    """The page as rendered, element by element — the reading a unit test cannot take."""
    failures = []
    for element in readings[scheme]["elements"]:
        ratio = contrast.ratio(contrast.parse(element["colour"]), contrast.parse(element["ground"]))
        needed = contrast.threshold(element["size"], element["weight"])
        if ratio + 1e-9 < needed:
            failures.append(
                f"{element['case']} {element['tag']}.{element['cls']} "
                f"{element['colour']} on {element['ground']} = {ratio:.2f} (needs {needed}) "
                f"— {element['text']!r}"
            )
    assert not failures, f"{scheme}: {len(failures)} element(s) below AA:\n" + "\n".join(failures)


@pytest.mark.parametrize("scheme", SCHEMES)
@pytest.mark.parametrize("token", MEASURED_TOKENS)
def test_every_measured_token_clears_aa_against_its_declared_ground(
    readings: dict, scheme: str, token: str
) -> None:
    """⭐ Coverage that does not depend on the fixture containing the construct.

    ⛔ Both colours still come from the browser — this is the ledger choosing
    *which* pair to compare, never supplying either value.
    """
    resolved = readings[scheme]["resolved"]
    ground = palette.LEDGER[token][1]
    ratio = contrast.ratio(contrast.parse(resolved[token]), contrast.parse(resolved[ground]))
    assert ratio >= contrast.AA_NORMAL, (
        f"{scheme}: {token} ({resolved[token]}) on {ground} ({resolved[ground]}) "
        f"= {ratio:.2f}, below AA {contrast.AA_NORMAL}"
    )


@pytest.mark.parametrize("scheme", SCHEMES)
def test_no_text_on_the_page_is_painted_in_a_colour_the_palette_does_not_define(
    readings: dict, scheme: str
) -> None:
    """⭐ The other direction: a browser default leaking through would show up here.

    ⚠️ An unstyled link is `rgb(0, 0, 238)` and passes AA against a light
    ground, so the ratio check above would never notice it. This would.
    """
    known = theme.tokens_by_colour(readings[scheme]["resolved"])
    stray = sorted(
        {
            f"{element['tag']}.{element['cls']}: {element['colour']}"
            for element in readings[scheme]["elements"]
            if element["colour"] not in known
        }
    )
    assert not stray, f"{scheme}: text painted in colours no palette token defines: {stray}"


def test_the_contrast_check_fails_on_a_stylesheet_whose_text_matches_its_ground(
    open_page: OpenPage, damaged_sites: dict[str, site.Site]
) -> None:
    """⛔ Negative control. `--fg` set to `--bg` must be caught, in both themes.

    ⭐ This is the whole argument for the module. Every assertion above is a
    claim that a bad page would fail — and until a bad page has been shown to
    fail, that is a claim and not a measurement.
    """
    broken = damaged_sites["contrast"]
    caught = {}
    for scheme in SCHEMES:
        open_page.open(broken.url(site.cases()[0]), scheme=scheme)
        worst = min(
            contrast.ratio(contrast.parse(el["colour"]), contrast.parse(el["ground"]))
            for el in theme.text_elements(open_page)
        )
        caught[scheme] = worst
    assert all(worst < contrast.AA_NORMAL for worst in caught.values()), (
        f"a page whose text colour equals its background measured {caught} — "
        "this harness cannot see a contrast failure"
    )
