"""An entry with nothing for a mode is tagged on every page that lists it, and only then.

⭐ The row's markup claims, end to end through `write_site`: the language of an entry is a data
attribute of its row in the index, the rail and a module's list; a closed row under
`outside_mode: locked` has no `href`, `aria-disabled` and no tab stop and keeps its address in
`data-href`; the bar of a unit page holds the neighbours the default mode cannot open as hidden
alternates; a page that belongs to some languages only carries the note. A corpus with no modes,
or whose entries all have something common to every mode, carries none of it.
"""

from __future__ import annotations

import re

from tests.studyforge.generate.entries_corpus import MODULES, PAGES, build, modes
from tests.studyforge.generate.test_modes_site import files
from tests.studyforge.validate.test_languages import READING

ENTRY = re.compile(r'<li id="([^"]+)"( data-entry-lang="([^"]+)")?[^>]*>(<a[^>]*>)?')
TOKENS = (b"data-entry-lang", b"data-entry-label", b"data-pager", b"data-outside", b"mode-outside")


def text(out, where):
    return (out / where).read_text(encoding="utf-8")


def test_the_index_the_rail_and_a_modules_list_carry_each_entrys_languages(tmp_path):
    out = build(tmp_path, "c", modes("open"))
    for where in ("index.html", MODULES["demo"]):
        rows = {m.group(1): m.group(3) for m in ENTRY.finditer(text(out, where))}
        assert rows["demo/unit-01"] is None and rows["demo/unit-02"] == "aa"
        assert rows["demo/unit-03"] == "bb" and rows["demo/unit-04"] == "aa bb"
    rail = text(out, PAGES["Shared ideas"])
    assert '<li data-unit="demo/unit-02" data-entry-lang="aa"' in rail
    assert '<li data-unit="demo/unit-01" data-readable' in text(out, PAGES["Aa only unit"])
    assert '<li data-entry-lang="bb" data-readable="true"><details>' in rail, "the module"
    assert "data-entry-label>Aa, Bb</span>" in text(out, "index.html")


def test_under_open_every_link_stays_a_link_and_the_root_names_no_lock(tmp_path):
    out = build(tmp_path, "c", modes("open"))
    page = text(out, PAGES["Both languages"])
    assert "data-outside" not in page and "data-pager" not in page
    assert "aria-disabled" not in text(out, "index.html")
    assert re.search(r'<a rel="prev" href="[^"]*unit-03', page), "the bar walks through it"


def test_under_locked_a_closed_row_is_not_a_link_and_keeps_its_address(tmp_path):
    out = build(tmp_path, "c", modes("locked"))
    for where in ("index.html", MODULES["demo"], PAGES["Aa only unit"]):
        row = re.search(r'<li [^>]*"demo/unit-03"[^>]*>.*?</li>', text(out, where), re.S)
        closed = row.group(0)
        assert 'data-readable="false"' in closed, where
        assert '<a aria-disabled="true" tabindex="-1" data-href="' in closed, where
        assert " href=" not in closed, where
    open_row = re.search(r'<li [^>]*"demo/unit-02"[^>]*>.*?</li>', text(out, "index.html"), re.S)
    assert '<a href="' in open_row.group(0) and "aria-disabled" not in open_row.group(0)
    assert '<html lang="en" data-mode="only-aa" data-outside="locked">' in text(out, "index.html")


def test_under_locked_the_bar_holds_the_neighbours_and_shows_the_first_the_default_can_open(
    tmp_path,
):
    page = text(build(tmp_path, "c", modes("locked")), PAGES["Both languages"])
    bar = page[page.index('aria-label="Between units"') :]
    previous = re.findall(r'<a data-pager="previous"([^>]*)>', bar)
    # Nearest first, up to the first unit every mode reads: 3 is closed to the default mode, 2 is
    # the one shown, and 1 is the end of the walk.
    assert [("rel=" in a, "hidden" in a) for a in previous] == [
        (False, True),
        (True, False),
        (False, True),
    ]
    assert "unit-03" in previous[0] and "unit-02" in previous[1] and "unit-01" in previous[2]
    assert 'data-pager-lang="aa"' in previous[1] and "data-pager-lang" not in previous[2]
    following = re.findall(r'<a data-pager="next"([^>]*)>', bar)
    assert len(following) == 2 and all("hidden" in a for a in following)
    assert 'data-pager-lang="bb"' in following[0], "the default mode can open neither"
    assert 'rel="next"' not in bar


def test_a_page_that_belongs_to_some_languages_only_carries_the_note_and_its_languages(tmp_path):
    for outside in ("open", "locked"):
        out = build(tmp_path, outside, modes(outside))
        page = text(out, PAGES["Bb only unit"])
        assert 'data-entry-lang="bb"' in page.split(">", 2)[1] + page.split(">", 2)[0]
        assert "<aside" in page and "It is read in: Bb." in page
        assert ("Switch to Bb" in page) == (outside == "locked")
        assert "<aside" not in text(out, PAGES["Shared ideas"])
        assert "mode-outside" not in text(out, PAGES["Shared ideas"])
    module = text(out, MODULES["other"])
    assert 'data-entry-lang="bb"' in module and "Switch to Bb" in module


def test_the_stylesheet_greys_a_row_per_mode_and_hides_everything_else_only_under_locked(tmp_path):
    for outside in ("open", "locked"):
        css = text(build(tmp_path, outside, modes(outside)), ".studyforge/assets/modes.css")
        assert 'html[data-mode="only-aa"] li[data-entry-lang]:not([data-entry-lang~="aa"])' in css
        assert 'html[data-mode="only-bb"] li[data-entry-lang]:not([data-entry-lang~="bb"])' in css
        hides = "body > :not(header):not(script) { display: none; }" in css
        assert hides == (outside == "locked")
        assert "section[data-lang][data-linked]" in css


def test_a_modes_corpus_whose_every_unit_is_common_has_none_of_it(tmp_path):
    from tests.studyforge.generate.test_modes_site import DOCUMENTS
    from tests.studyforge.generate.test_section_language import build as plain_build

    out = plain_build(tmp_path, "plain", DOCUMENTS[:1], READING)
    body = b"".join(path.read_bytes() for path in sorted(out.rglob("*.html")))
    assert not [word for word in TOKENS if word in body]


def test_a_second_build_changes_nothing(tmp_path):
    assert files(build(tmp_path, "one", modes("locked"))) == files(
        build(tmp_path, "two", modes("locked"))
    )
