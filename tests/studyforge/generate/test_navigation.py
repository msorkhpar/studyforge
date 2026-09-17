"""Mirror of `src/studyforge/generate/navigation.py` (R12).

⭐ **The stand-in it replaces is imported and compared against.**
`tests/studyforge/render/page/sites.py` wrote `bar_for` and `trail_for` by hand
and says in its own docstring that it stands in for this caller — so the shipped
join is checked against an independently written one rather than against itself.
"""

from __future__ import annotations

import pytest

from studyforge.generate import ancestors, bar, index_href, page_paths, read_corpus, trail
from studyforge.render.page import Crumb, Link
from tests.studyforge.generate.corpora import BOTH, FIXTURES, with_a_unit_missing


def a_walk(name: str):
    from studyforge.contents import order

    corpus = read_corpus(FIXTURES / name)
    return corpus, [entry.key for entry in order(corpus.contents)]


# --------------------------------------------------------------------------
# ⭐ bar — the between-units slots
# --------------------------------------------------------------------------


@pytest.mark.parametrize("name", BOTH)
def test_the_first_unit_has_no_previous_and_the_last_has_no_next(name):
    corpus, walked = a_walk(name)

    first = bar(corpus.contents, walked[0])
    last = bar(corpus.contents, walked[-1])

    assert first.previous is None and first.next is not None
    assert last.next is None and last.previous is not None
    assert first.index is not None and last.index is not None


@pytest.mark.parametrize("name", BOTH)
def test_prev_and_next_traverse_every_declared_unit_in_reading_order(name):
    corpus, walked = a_walk(name)

    forward = [bar(corpus.contents, key).next for key in walked[:-1]]
    assert [link.key for link in forward] == walked[1:]
    backward = [bar(corpus.contents, key).previous for key in walked[1:]]
    assert [link.key for link in backward] == walked[:-1]


def test_a_neighbour_with_no_page_is_a_declared_absence_and_never_a_guessed_href(tmp_path):
    """⛔ The failure neither of Ruling 164's policies catches: a legal dangling href."""
    root = with_a_unit_missing(tmp_path, "depth1", "archive/depth-one/raw/prose/unit-02")
    corpus = read_corpus(root)

    slot = bar(corpus.contents, "depth-one/unit-01", corpus.absent).next

    assert isinstance(slot, Link)
    assert slot.key == "depth-one/unit-02"
    assert slot.href is None, "an href here would point at a page nobody wrote"
    assert slot.label, "the absent unit is still named"


def test_a_neighbour_that_is_present_keeps_the_href_the_contents_computed(tmp_path):
    root = with_a_unit_missing(tmp_path, "depth1", "archive/depth-one/raw/prose/unit-02")
    corpus = read_corpus(root)

    from studyforge.contents import links

    slot = bar(corpus.contents, "depth-one/unit-02", corpus.absent).next
    assert slot.href == links(corpus.contents, "depth-one/unit-02")["next"]["href"]


@pytest.mark.parametrize("name", BOTH)
def test_the_shipped_join_agrees_with_the_hand_written_stand_in(tmp_path, name):
    """⭐ `sites.py`'s `bar_for`, written by hand for the acceptance, and this one."""
    from tests.studyforge.render.page.sites import a_site

    site = a_site(name, tmp_path / name)
    corpus = read_corpus(FIXTURES / name)

    from tests.studyforge.render.page.sites import bar_for

    for entry in site.walked():
        assert bar(corpus.contents, entry.key, site.absent) == bar_for(site, entry)


# --------------------------------------------------------------------------
# ⭐ trail — the breadcrumbs
# --------------------------------------------------------------------------


@pytest.mark.parametrize("name", BOTH)
def test_the_trail_runs_corpus_then_every_container_then_the_unit(name):
    corpus, walked = a_walk(name)

    for key in walked:
        crumbs = trail(corpus.contents, key, index_href(corpus.contents, key))
        assert crumbs[0].title == corpus.contents.title
        assert crumbs[0].href.endswith("index.html")
        assert len(crumbs) == 2 + len(ancestors(corpus.contents, key))
        assert crumbs[-1].href is None, "the last crumb is the page the reader is on"


@pytest.mark.parametrize("name", BOTH)
def test_every_label_comes_out_of_the_contents_document(name):
    """⛔ R1: the word for a depth is the corpus's own, carried through `Group.level`."""
    corpus, walked = a_walk(name)

    for key in walked:
        crumbs = trail(corpus.contents, key, index_href(corpus.contents, key))
        groups = ancestors(corpus.contents, key)
        assert [crumb.level for crumb in crumbs[1:-1]] == [group.level for group in groups]
        assert [crumb.title for crumb in crumbs[1:-1]] == [group.title for group in groups]
        assert set(crumb.level for crumb in crumbs[1:-1]) <= set(corpus.manifest.levels)


def test_a_container_with_a_page_is_linked_and_one_without_is_only_listed():
    """⚠️ `SF-14/3` from the page's side, and the half of it this row closes.

    ⭐ A container map is written at the address units are declared under and
    nowhere above it, so `advanced/02-going-further` has a page and `advanced`
    has none — measured from `page_paths`, not asserted.
    """
    from studyforge.corpus.placement import relative_href

    corpus = read_corpus(FIXTURES / "depth2")
    above = page_paths(corpus)
    key = "advanced/02-going-further/unit-01"
    unit = next(source for source in corpus.units if source.key == key)

    from studyforge.generate import unit_location

    at = unit_location(corpus, unit)
    crumbs = trail(
        corpus.contents,
        key,
        index_href(corpus.contents, key),
        {name: relative_href(at.page, page) for name, page in above.items()},
    )

    assert set(above) == {
        "basics/01-getting-started",
        "advanced/02-going-further",
        "advanced/03-putting-it-together",
    }
    assert [crumb.title for crumb in crumbs[1:-1]] == ["Advanced", "Going Further"]
    assert crumbs[1].href is None, "no container map is written at 'advanced'"
    assert crumbs[2].href == "going-further.section.html"


@pytest.mark.parametrize("name", BOTH)
def test_the_trail_matches_the_stand_in_apart_from_the_hrefs_this_row_adds(tmp_path, name):
    """⭐ The stand-in gave every container crumb `href=None`; this row links them."""
    from tests.studyforge.render.page.sites import a_site, trail_for

    site = a_site(name, tmp_path / name)
    corpus = read_corpus(FIXTURES / name)

    for entry in site.walked():
        to_index = index_href(corpus.contents, entry.key)
        mine = trail(corpus.contents, entry.key, to_index)
        theirs = trail_for(corpus.contents, entry, to_index)
        assert [Crumb(c.level, c.title) for c in mine] == [Crumb(c.level, c.title) for c in theirs]
        assert all(crumb.href is None for crumb in theirs[1:])
