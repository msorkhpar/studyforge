"""Clause 4 — the page is run with JavaScript disabled, and still reads.

⛔ **`SF-14`'s acceptance, made runnable before `SF-14` needs it.** The reading
floor is a page opened from a file with no server; a reader who has scripts off,
or whose browser blocked a `file://` script, must still get the words. What they
may lose is decoration — the copy button, the syntax colours — and the point of
this module is that the line between the two is asserted rather than assumed.
"""

from __future__ import annotations

import pytest

from tests.visual import site
from tests.visual.page import OpenPage

#: Sentences the fixture units carry in their prose. ⛔ Taken from the material,
#: not from the renderer, so a renderer that dropped its body would fail here
#: rather than agree with itself.
PROSE = {
    "depth2-unit-01": "A class is a name plus the state and behaviour filed under it.",
    "depth1-unit-02": None,
}

#: The page's own text, with what a *script* added taken back out.
#: ⚠️ `copy-code.js` inserts a button reading "Copy" into every code figure, so
#: a raw `innerText` comparison between the two runs fails on the decoration
#: rather than on the words — which is a true difference and the wrong one.
#: ⛔ Removing it from the scripted side, and nothing else, keeps the comparison
#: about the material.
TEXT_WITHOUT_DECORATION = (
    "(() => { const copy = document.cloneNode(true);"
    " copy.querySelectorAll('.copy').forEach(node => node.remove());"
    " return copy.getElementById('content').innerText.replace(/\\s+/g, ' ').trim(); })()"
)


@pytest.mark.parametrize("case", site.cases())
def test_the_words_survive_with_scripts_disabled(
    open_page: OpenPage, built_site: site.Site, case: str
) -> None:
    """Every visible character of the page's own text is there without a script."""
    open_page.open(built_site.url(case), scripts=True)
    with_scripts = open_page.evaluate(TEXT_WITHOUT_DECORATION)
    open_page.open(built_site.url(case), scripts=False)
    without = open_page.evaluate(TEXT_WITHOUT_DECORATION)
    assert without, "with scripts off the page has no text at all"
    assert without == with_scripts, (
        "the text of the page differs with scripts disabled — the reading floor depends on a script"
    )
    expected = PROSE[case]
    if expected:
        assert expected in str(without)


def test_the_page_still_navigates_itself_with_scripts_disabled(
    open_page: OpenPage, built_site: site.Site
) -> None:
    """⭐ Navigation is `<a href="#…">` and headings, so it must not need a script.

    ⚠️ The check is that every outline link still resolves to an element that
    exists — an in-page link to an anchor no script has minted is a link that
    goes nowhere, and it looks identical in the markup.
    """
    open_page.open(built_site.url("depth2-unit-01"), scripts=False)
    dangling = open_page.evaluate(
        "Array.from(document.querySelectorAll('nav[aria-label] a'))"
        ".map(a => a.getAttribute('href'))"
        ".filter(h => !document.querySelector(h))"
    )
    assert dangling == [], f"outline links resolving to nothing without a script: {dangling}"


def test_only_decoration_is_lost_when_scripts_are_off(
    open_page: OpenPage, built_site: site.Site
) -> None:
    """What a scriptless reader gives up, named rather than discovered later.

    ⛔ Asserted in both directions. The copy button and the syntax colours are
    *expected* to be absent — so this fails if they are absent **with** scripts
    too, which would mean the check above was passing for the wrong reason.
    """
    url = built_site.url("depth2-unit-01")
    probe = (
        "[document.querySelectorAll('.copy').length, document.querySelectorAll('.token').length]"
    )
    open_page.open(url, scripts=True)
    with_scripts = list(open_page.evaluate(probe))  # type: ignore[arg-type]
    open_page.open(url, scripts=False)
    without = list(open_page.evaluate(probe))  # type: ignore[arg-type]
    assert with_scripts[0] > 0 and with_scripts[1] > 0, (
        f"with scripts ON the page has {with_scripts} copy buttons and tokens — "
        "the control for this check did not hold"
    )
    assert without == [0, 0], f"with scripts OFF the page still reports {without}"


def test_a_page_whose_prose_is_written_by_a_script_is_caught(
    open_page: OpenPage, damaged_sites: dict[str, site.Site]
) -> None:
    """⛔ Negative control: the `noscript` tree must fail the first check.

    ⚠️ It is the exact failure this clause exists to catch, and it is invisible
    to every other test in this repository: the page carries every word, the
    bytes are stable, the goldens match — and a reader with scripts off sees an
    empty column.
    """
    broken = damaged_sites["noscript"]
    open_page.open(broken.url("depth2-unit-01"), scripts=True)
    with_scripts = open_page.evaluate(TEXT_WITHOUT_DECORATION)
    open_page.open(broken.url("depth2-unit-01"), scripts=False)
    without = open_page.evaluate(TEXT_WITHOUT_DECORATION)
    assert with_scripts, "the control page is empty even with scripts on, so it proves nothing"
    assert without != with_scripts, (
        "a page whose prose is injected by a script read identically with scripts "
        "disabled — this harness cannot see the failure SF-14 is judged on"
    )
