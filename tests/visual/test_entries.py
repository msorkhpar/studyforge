"""An entry with nothing for the chosen mode stays in the index and the rail, greyed, in a browser.

⭐ **Every clause drives the real page.** A corpus with a unit in each language only, a unit
with both and a module whose every unit is of one language is built twice, once with
`outside_mode: locked` and once with `open`, and read in the headless browser from a served
origin: the greyed rows and their labels, a locked row that is not a link, the between-units bar
that passes over it, the counters that count the mode's pages only, the note a direct link shows,
and a link into a section the mode hides.

⛔ **Each clause is read both ways (R12).** A locked row has no `href` and no tab stop and an open
one keeps both; a mode that reads the row gives the link back; the bar shows a neighbour in one
mode and not in the other.

## What this module does NOT read

The tabbed examples and the practice list of a mode are other rows' clauses.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest

from tests.studyforge.generate.entries_corpus import MODULES, PAGES, build, modes
from tests.visual import served, site
from tests.visual.page import NARROW, WIDE, OpenPage

INDEX = "index.html"
SWITCH = '[data-section="mode"]'
ROWS = """
Array.from(document.querySelectorAll('<scope> li[<key>]')).map(li => {
  const link = li.querySelector('a');
  const label = li.querySelector('[data-entry-label]');
  return {
    id: li.getAttribute('<key>'), lang: li.getAttribute('data-entry-lang'),
    readable: li.getAttribute('data-readable'), shown: li.offsetHeight > 0,
    linkShown: link ? link.offsetHeight > 0 : null,
    href: link ? link.getAttribute('href') : null,
    disabled: link ? link.getAttribute('aria-disabled') : null,
    tabindex: link ? link.tabIndex : null,
    grey: getComputedStyle(li).color,
    label: label ? [getComputedStyle(label).display !== 'none', label.textContent] : null
  };
})
"""
INDEX_ROWS = ROWS.replace("<scope>", 'nav[aria-label="Contents"]').replace("<key>", "id")
RAIL_ROWS = ROWS.replace("<scope>", 'nav[aria-label="Containers"]').replace("<key>", "data-unit")
PAGER = """
Array.from(document.querySelectorAll('nav[aria-label="Between units"] a'))
  .filter(a => getComputedStyle(a).display !== 'none')
  .map(a => [a.getAttribute('rel'), a.lastChild.textContent.trim()])
"""
TALLY = """
Array.from(document.querySelectorAll('nav[aria-label="Contents"] summary > small'))
  .map(t => [t.hidden, t.textContent.trim()])
"""
LINE = """
(() => { const r = document.querySelector('section[aria-label="Progress"] p');
  return r && !r.parentNode.hidden ? r.textContent.replace(/\\s+/g, ' ').trim() : null; })()
"""
NOTE = """
(() => { const n = document.querySelector('aside[data-section="mode-outside"]');
  if (!n) return null;
  const main = document.querySelector('main');
  return {
    shown: getComputedStyle(n).display !== 'none', text: n.textContent.replace(/\\s+/g, ' ').trim(),
    main: getComputedStyle(main).display !== 'none',
    rail: Array.from(document.querySelectorAll('body > nav')).some(
      e => getComputedStyle(e).display !== 'none'),
    switch: getComputedStyle(document.querySelector('<s>')).display !== 'none'
  }; })()
""".replace("<s>", SWITCH)
CLEAR = "(() => { try { localStorage.clear(); sessionStorage.clear(); } catch (e) {} })()"


@pytest.fixture(scope="module")
def sites(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Path]:
    root = tmp_path_factory.mktemp("entries")
    return {name: build(root, name, modes(name)) for name in ("locked", "open")}


@pytest.fixture(scope="module", params=["locked", "open"])
def both(
    request: pytest.FixtureRequest, sites: dict[str, Path]
) -> Iterator[tuple[served.Served, str]]:
    """Each setting of `outside_mode`, served, with its name."""
    built = sites[request.param]
    with served.serving(site.Site(built.parent), corpus=built.name) as running:
        yield running, request.param


@pytest.fixture(scope="module")
def locked(sites: dict[str, Path]) -> Iterator[served.Served]:
    with served.serving(site.Site(sites["locked"].parent), corpus=sites["locked"].name) as run:
        yield run


@pytest.fixture(scope="module")
def opened(sites: dict[str, Path]) -> Iterator[served.Served]:
    with served.serving(site.Site(sites["open"].parent), corpus=sites["open"].name) as run:
        yield run


def read(page: OpenPage, origin: served.Served, where: str, mode: str, *, width=WIDE) -> None:
    """Open `where` with `mode` already chosen and stored, as a returning reader has."""
    page.resize(*width)
    page.open(f"{origin.origin}/{INDEX}")
    page.evaluate(CLEAR)
    page.evaluate(
        "localStorage.setItem('studyforge.display.v1', JSON.stringify("
        f"{{version: 1, display: {{mode: '{mode}'}}}}))"
    )
    page.open(f"{origin.origin}/{where}")


def row(page: OpenPage, ident: str) -> dict:
    """One row of the index, by its key."""
    return by_id(page.evaluate(INDEX_ROWS))[ident]  # type: ignore[arg-type]


def by_id(rows: list[dict]) -> dict[str, dict]:
    return {row["id"]: row for row in rows}


def test_a_row_with_nothing_for_the_mode_is_greyed_and_labelled_in_the_index_and_the_rail(
    open_page: OpenPage, both: tuple[served.Served, str]
) -> None:
    origin, _ = both
    read(open_page, origin, INDEX, "only-aa")
    for rows in (by_id(open_page.evaluate(INDEX_ROWS)),):  # type: ignore[arg-type]
        common, aa, bb, both = (rows[f"demo/unit-0{n}"] for n in (1, 2, 3, 4))
        assert common["lang"] is None and common["label"] is None
        assert common["grey"] == aa["grey"] == both["grey"]
        assert bb["lang"] == "bb" and bb["label"] == [True, "Bb"]
        assert bb["grey"] != common["grey"], "greyed"
        assert bb["shown"] and bb["linkShown"], "and not hidden"
        assert rows["other/unit-01"]["shown"], "a module's rows stay too"
        assert aa["label"][0] is False and both["label"][0] is False
        assert rows["other/unit-01"]["label"] == [True, "Bb"]
    module = open_page.evaluate("""(() => {
      const li = document.querySelector(
        'nav[aria-label="Contents"] li[data-entry-lang="bb"]:has(> details)');
      return [li.querySelector('details').id, getComputedStyle(li.querySelector('summary')).color,
        getComputedStyle(li.querySelector('summary [data-entry-label]')).display]; })()""")
    assert module[0] == "other" and module[2] != "none", "a module of one language is labelled"
    rail = by_id(open_page.evaluate(RAIL_ROWS))  # type: ignore[arg-type]
    assert rail["demo/unit-03"]["label"] == [True, "Bb"]
    assert rail["demo/unit-03"]["grey"] != rail["demo/unit-01"]["grey"]
    assert rail["demo/unit-01"]["lang"] is None


def test_the_mode_that_reads_a_row_shows_it_plainly_and_the_other_greys_the_first(
    open_page: OpenPage, both: tuple[served.Served, str]
) -> None:
    origin, outside = both
    read(open_page, origin, INDEX, "only-bb")
    rows = by_id(open_page.evaluate(INDEX_ROWS))  # type: ignore[arg-type]
    assert rows["demo/unit-03"]["label"][0] is False
    assert rows["demo/unit-02"]["label"] == [True, "Aa"]
    assert rows["other/unit-01"]["label"][0] is False


def test_under_locked_a_row_outside_the_mode_is_not_a_link_and_open_keeps_it_one(
    open_page: OpenPage, both: tuple[served.Served, str]
) -> None:
    origin, outside = both
    for mode, closed, kept in (
        ("only-aa", "demo/unit-03", "demo/unit-02"),
        ("only-bb", "demo/unit-02", "demo/unit-03"),
    ):
        read(open_page, origin, INDEX, mode)
        for rows in (
            by_id(open_page.evaluate(INDEX_ROWS)),  # type: ignore[arg-type]
            by_id(open_page.evaluate(RAIL_ROWS)),  # type: ignore[arg-type]
        ):
            if outside == "locked":
                assert rows[closed]["href"] is None and rows[closed]["disabled"] == "true"
                assert rows[closed]["tabindex"] == -1 and rows[closed]["readable"] == "false"
            else:
                assert rows[closed]["href"] and rows[closed]["disabled"] is None
                assert rows[closed]["readable"] == "true"
            assert rows[kept]["href"] and rows[kept]["disabled"] is None


def test_clicking_a_locked_row_goes_nowhere_and_it_takes_no_tab_stop(
    open_page: OpenPage, locked: served.Served
) -> None:
    read(open_page, locked, INDEX, "only-aa")
    before = open_page.evaluate("location.href")
    open_page.evaluate("""document.getElementById('demo/unit-03').querySelector('a').click()""")
    assert open_page.evaluate("location.href") == before
    stops = open_page.trail(80)
    assert not [s for s in stops if "bb-only" in s["label"] or "Bb only" in s["label"]]
    assert [s for s in stops if "aa-only" in s["label"]], "an open row is still a tab stop"
    # ⭐ The pointer cannot reach it either.
    assert (
        open_page.evaluate(
            "getComputedStyle(document.getElementById('demo/unit-03').querySelector('a'))"
            ".pointerEvents"
        )
        == "none"
    )


def test_a_closed_row_opens_again_when_a_mode_that_reads_it_is_chosen(
    open_page: OpenPage, locked: served.Served
) -> None:
    read(open_page, locked, INDEX, "only-aa")
    assert row(open_page, "demo/unit-03")["href"] is None
    open_page.evaluate(f"document.querySelector('{SWITCH} [data-mode-choice=\"only-bb\"]').click()")
    rows = by_id(open_page.evaluate(INDEX_ROWS))  # type: ignore[arg-type]
    assert rows["demo/unit-03"]["href"] and rows["demo/unit-03"]["tabindex"] == 0
    assert rows["demo/unit-02"]["href"] is None, "and the other closes"


def test_the_bar_passes_over_a_closed_neighbour_under_locked_and_walks_through_it_under_open(
    open_page: OpenPage, locked: served.Served, opened: served.Served
) -> None:
    both = PAGES["Both languages"]
    read(open_page, locked, both, "only-aa")
    assert open_page.evaluate(PAGER) == [["prev", "Aa only unit 2"], ["up", "Demo"]]
    open_page.evaluate(f"document.querySelector('{SWITCH} [data-mode-choice=\"only-bb\"]').click()")
    assert open_page.evaluate(PAGER) == [
        ["prev", "Bb only unit 3"],
        ["up", "Demo"],
        ["next", "Bb extra one 1"],
    ]
    read(open_page, opened, both, "only-aa")
    assert open_page.evaluate(PAGER) == [
        ["prev", "Bb only unit 3"],
        ["up", "Demo"],
        ["next", "Bb extra one 1"],
    ]


def test_the_bar_without_scripts_is_the_default_mode_s_and_skips_what_it_cannot_open(
    open_page: OpenPage, locked: served.Served
) -> None:
    open_page.resize(*WIDE)
    open_page.open(f"{locked.origin}/{PAGES['Both languages']}", scripts=False)
    assert open_page.evaluate(PAGER) == [["prev", "Aa only unit 2"], ["up", "Demo"]]


def test_a_direct_link_to_a_closed_page_shows_a_note_and_a_way_to_switch_and_nothing_else(
    open_page: OpenPage, locked: served.Served
) -> None:
    read(open_page, locked, PAGES["Bb only unit"], "only-aa")
    note = open_page.evaluate(NOTE)
    assert note["shown"] and note["main"] is False and note["rail"] is False
    assert note["switch"] is True
    assert "outside the reading mode you chose" in note["text"] and "Bb" in note["text"]
    assert open_page.evaluate("document.querySelectorAll('aside [data-mode-choice]').length") == 1
    open_page.evaluate("document.querySelector('aside [data-mode-choice]').click()")
    after = open_page.evaluate(NOTE)
    assert after["shown"] is False and after["main"] is True, "choosing the mode opens the page"


def test_a_page_the_mode_reads_has_no_note(open_page: OpenPage, locked: served.Served) -> None:
    read(open_page, locked, PAGES["Aa only unit"], "only-aa")
    assert open_page.evaluate(NOTE)["shown"] is False
    read(open_page, locked, PAGES["Shared ideas"], "only-bb")
    assert open_page.evaluate(NOTE) is None


def test_under_open_a_page_outside_the_mode_reads_with_a_one_line_note(
    open_page: OpenPage, opened: served.Served
) -> None:
    read(open_page, opened, PAGES["Bb only unit"], "only-aa")
    note = open_page.evaluate(NOTE)
    assert note["shown"] and note["main"] is True
    assert "reads in its own language" in note["text"] and "Bb" in note["text"]
    assert open_page.evaluate("document.querySelectorAll('aside [data-mode-choice]').length") == 0
    assert open_page.evaluate("document.body.innerText.includes('BB WORDS')") is True


def test_a_module_whose_every_unit_is_of_one_language_is_closed_as_a_page_too(
    open_page: OpenPage, locked: served.Served
) -> None:
    read(open_page, locked, MODULES["other"], "only-aa")
    assert open_page.evaluate(NOTE)["main"] is False
    read(open_page, locked, MODULES["other"], "only-bb")
    assert open_page.evaluate(NOTE)["shown"] is False


def test_the_counters_count_only_the_pages_of_the_mode_in_both_settings(
    open_page: OpenPage, both: tuple[served.Served, str]
) -> None:
    origin, outside = both
    read(open_page, origin, INDEX, "only-aa")
    assert open_page.evaluate(TALLY) == [[False, "0 of 3 read"], [True, "0 of 0 read"]]
    assert open_page.evaluate(LINE).startswith("0 of 3 units read")
    open_page.evaluate(f"document.querySelector('{SWITCH} [data-mode-choice=\"only-bb\"]').click()")
    assert open_page.evaluate(TALLY) == [[False, "0 of 3 read"], [False, "0 of 2 read"]]
    assert open_page.evaluate(LINE).startswith("0 of 5 units read")
    assert open_page.evaluate(LINE).endswith("5 to go")


def test_the_unit_up_next_is_the_first_the_mode_reads_and_has_not_been_read(
    open_page: OpenPage, both: tuple[served.Served, str]
) -> None:
    origin, outside = both
    read(open_page, origin, INDEX, "only-bb")
    open_page.evaluate("""(() => { const p = window.studyforge.progress;
      p.mark('demo/unit-01'); })()""")
    open_page.open(f"{origin.origin}/{INDEX}")
    slip = "document.querySelector('nav[aria-label=\"Up next\"] a').textContent.trim()"
    assert "Aa only unit" not in open_page.evaluate(slip)
    assert "Bb only unit 3" in open_page.evaluate(slip)
    open_page.evaluate(f"document.querySelector('{SWITCH} [data-mode-choice=\"only-aa\"]').click()")
    assert "Aa only unit 2" in open_page.evaluate(slip)
    open_page.evaluate(CLEAR)


def test_a_module_page_counts_the_units_of_the_mode(
    open_page: OpenPage, both: tuple[served.Served, str]
) -> None:
    origin, outside = both
    read(open_page, origin, MODULES["demo"], "only-aa")
    meta = "document.querySelector('body > header p:not([role])').textContent.trim()"
    heads = open_page.evaluate(
        "Array.from(document.querySelectorAll('body > header p')).map(p => p.textContent.trim())"
    )
    assert any(text.startswith("3 units") for text in heads), heads
    assert meta


def test_a_link_into_a_section_the_mode_hides_shows_that_section_and_lands_on_it(
    open_page: OpenPage, locked: served.Served
) -> None:
    where = PAGES["Both languages"]
    read(open_page, locked, where, "only-aa")
    visible = (
        "Array.from(document.querySelectorAll('main section[data-lang]'))"
        ".filter(s => getComputedStyle(s).display !== 'none').map(s => s.getAttribute('data-lang'))"
    )
    assert open_page.evaluate(visible) == ["aa"]
    open_page.evaluate("location.hash = '#s-prose-2'")
    assert open_page.evaluate(visible) == ["aa", "bb"], "the target is shown, not nowhere"
    top = open_page.evaluate(
        "Math.round(document.getElementById('s-prose-2').getBoundingClientRect().top)"
    )
    assert 0 <= top < 700
    open_page.evaluate("location.hash = '#s-prose'")
    assert open_page.evaluate(visible) == ["aa"], "another target takes the extra section away"
    open_page.open(f"{locked.origin}/{INDEX}")
    open_page.open(f"{locked.origin}/{where}#s-prose-2")
    assert open_page.evaluate(visible) == ["aa", "bb"], "a fresh load on the link lands too"


def test_the_index_fits_a_phone_with_its_labels_and_code_still_has_no_ligature(
    open_page: OpenPage, locked: served.Served
) -> None:
    read(open_page, locked, INDEX, "only-aa", width=(360, 740))
    assert open_page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
    assert row(open_page, "demo/unit-03")["label"][0] is True
    open_page.open(f"{locked.origin}/{PAGES['Aa only unit']}")
    assert open_page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
    reading = open_page.evaluate(
        "(() => { const s = getComputedStyle(document.querySelector('pre'));"
        " return [s.fontVariantLigatures, s.fontFeatureSettings]; })()"
    )
    assert reading[0] == "none" and '"liga" 0' in reading[1]
    read(open_page, locked, PAGES["Bb only unit"], "only-aa", width=(360, 740))
    assert open_page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
    assert open_page.evaluate(NOTE)["shown"] is True
    _ = NARROW
