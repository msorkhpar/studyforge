"""The trail's acceptance, asserted rather than described.

⛔ **Not a mirror of any one module** (R12 is one-way): these are the clauses
`E03-rendering.md` states for the task as a whole, and each one names the
instrument that would fail it.

| Clause | Instrument |
|---|---|
| prev/next traverses **every unit of both fixtures**, in order | `test_following_next_*` |
| …and in reverse | `test_following_previous_*` |
| …across module and section boundaries | `test_the_walk_crosses_*`, and its inhabitation row |
| breadcrumbs read *"Section › Module › Lesson"* from data | `test_the_trail_*` |
| works over `file://` | `test_every_reference_*` |
| no dangling links in the generated output | `test_no_link_in_the_generated_site_dangles` |

⛔ **The site is assembled by `sites.py`, not here** — that module is *the
directory of pages a build writes, and how to read one back*; this one is the
clauses. ⚠️ The split is R11's ceiling taken at a real seam rather than at a line
number: every helper below the seam is about pages on disk, and every assertion
above it is about one sentence of the epic.
"""

from __future__ import annotations

import re

import pytest

from studyforge.corpus.placement import ROOT_INDEX_FILENAME
from tests.studyforge.contents.corpora import fixture_contents, fixture_manifest
from tests.studyforge.render.page.sites import (
    FIXTURES,
    FRAGMENT,
    Site,
    a_planted_site,
    a_site,
    ancestors,
    boundaries,
    crossings,
    crumbs_on,
    dangling_in,
    depth_of,
    followed,
    generated,
    has_slot,
    ids_in,
    references_in,
    slot,
)


@pytest.fixture(params=sorted(FIXTURES), ids=sorted(FIXTURES))
def site(request, tmp_path) -> Site:
    """Each `FND-04` fixture, generated as a site."""
    return a_site(request.param, tmp_path)


# --------------------------------------------------------------------------
# Prev/next traverses every unit of both fixtures, in curriculum order
# --------------------------------------------------------------------------


def test_following_next_from_the_first_page_visits_every_unit_that_has_one(site):
    # ⛔ The first acceptance clause, walked rather than asserted about: start at
    # the first unit of the reading order and follow `next` until the bar stops
    # offering one. ⚠️ The walk is over GENERATED PAGES — an href arithmetic
    # error is a step that lands on no page, not a comparison that fails.
    walked = [entry for entry in site.walked() if entry.key not in site.absent]
    by_page = {entry.page.as_posix(): entry for entry in site.walked()}
    at, visited = walked[0], [walked[0].key]
    while True:
        body = site.text(site.pages[at.key])
        if not has_slot(body, "next"):
            break
        reference = slot(body, "next")
        landed = followed(at.page, reference.split(FRAGMENT)[0])
        if FRAGMENT in reference:
            # ⭐ The declared absence: the step lands on the root index's row for
            # a unit with no page, which is the end of the walk over pages.
            assert landed == ROOT_INDEX_FILENAME
            visited.append(reference.split(FRAGMENT, 1)[1])
            break
        at = by_page[landed]
        visited.append(at.key)
    assert visited == [entry.key for entry in site.walked()], (site.name, visited)


def test_following_previous_from_the_last_page_visits_them_all_in_reverse(site):
    # ⭐ The same clause from the other end, because `previous` and `next` are two
    # slots and a bar can be right in one direction and wrong in the other.
    walked = [entry for entry in site.walked() if entry.key not in site.absent]
    by_page = {entry.page.as_posix(): entry for entry in site.walked()}
    at, visited = walked[-1], [walked[-1].key]
    while has_slot(site.text(site.pages[at.key]), "prev"):
        reference = slot(site.text(site.pages[at.key]), "prev")
        assert FRAGMENT not in reference, "no earlier unit of a fixture is absent"
        at = by_page[followed(at.page, reference)]
        visited.append(at.key)
    assert visited == [entry.key for entry in reversed(walked)], (site.name, visited)


def test_the_walk_crosses_a_container_boundary_and_the_fixture_has_one_to_cross(site):
    # ⛔ **The inhabitation half, and it is the clause.** *"including across module
    # and section boundaries"* is unfalsifiable against a corpus whose units all
    # sit in one container, so the crossings are counted first and the assertion
    # is about them. ⚠️ `depth1` has one container and crosses nothing, which is
    # why this SKIPS there rather than passing there.
    crossings = boundaries(site)
    if not crossings:
        pytest.skip(f"{site.name} declares one container, so there is no boundary to cross")
    by_key = {entry.key: entry for entry in site.walked()}
    for before, after in crossings:
        if before in site.absent or after in site.absent:
            continue
        body = site.text(site.pages[before])
        assert has_slot(body, "next"), f"{site.name}: {before} offers no next at a boundary"
        assert followed(by_key[before].page, slot(body, "next")) == by_key[after].page.as_posix()


def test_the_fixtures_cross_each_kind_of_boundary_counted_apart(tmp_path):
    # ⛔ **The inhabitation row for the clause as a whole, one count per kind**
    # ⚠️ It used to be one total, `{"depth1": 0, "depth2": 1}`, and
    # that `1` was the compound crossing alone — so the module-only half was
    # absent and the total could not say so. ⭐ Measured since: `depth2`
    # changes the module inside one section once and both levels once.
    counted = {name: crossings(a_site(name, tmp_path / name)) for name in sorted(FIXTURES)}
    assert counted == {"depth1": {}, "depth2": {"module": 1, "section+module": 1}}, counted


def test_a_fixture_changes_module_without_changing_section(tmp_path):
    # ⛔ **The presence half, stated by its own name.** A renderer that handles a
    # both-levels change and mishandles a module change inside one section must
    # meet this crossing in a fixture, not only in `PLANTED_SHAPE`.
    counted = {name: crossings(a_site(name, tmp_path / name)) for name in sorted(FIXTURES)}
    assert sum(found.get("module", 0) for found in counted.values()) > 0, counted
    assert counted["depth2"].get("section+module", 0) > 0, "the compound control went missing"


def test_the_walk_crosses_a_module_boundary_inside_one_section(tmp_path):
    # ⛔ **The half of the clause neither fixture contains.** Two modules in one
    # section: the section crumb does not change, the module crumb does, and the
    # `next` link has to leave one module's directory for another's.
    planted = a_planted_site(tmp_path)
    inside = [
        (before, after)
        for before, after in boundaries(planted)
        if depth_of(planted, before)[0] == depth_of(planted, after)[0]
    ]
    assert inside, "the planted corpus was meant to hold two modules in one section"
    by_key = {entry.key: entry for entry in planted.walked()}
    for before, after in inside:
        if before in planted.absent or after in planted.absent:
            continue
        body = planted.text(planted.pages[before])
        assert has_slot(body, "next"), f"{before} offers no next at a module boundary"
        landed = followed(by_key[before].page, slot(body, "next"))
        assert landed == by_key[after].page.as_posix()
        assert ".." in slot(body, "next"), "a module boundary that stayed put proves nothing"


def test_the_planted_corpus_crosses_a_section_boundary_too_and_they_read_differently(tmp_path):
    # ⭐ The control: the same corpus also holds a crossing where BOTH levels
    # change, and the two populations must be different sets — otherwise the test
    # above is measuring the crossing the fixtures already had.
    planted = a_planted_site(tmp_path)
    inside = {
        pair
        for pair in boundaries(planted)
        if depth_of(planted, pair[0])[0] == depth_of(planted, pair[1])[0]
    }
    across = {pair for pair in boundaries(planted) if pair not in inside}
    assert inside and across, (sorted(inside), sorted(across))
    assert inside.isdisjoint(across)


def test_every_link_in_the_planted_site_resolves_too(tmp_path):
    # ⛔ The link check is not a property of the two fixtures: run it over the
    # corpus shape they do not have.
    planted = a_planted_site(tmp_path)
    assert len(generated(planted)) > 1
    assert dangling_in(planted) == []


def test_the_planted_sites_trail_distinguishes_its_two_modules(tmp_path):
    # ⭐ The breadcrumb clause at the shape that can expose a confused one: two
    # units in different modules of the SAME section must share crumb 1 and
    # differ at crumb 2.
    planted = a_planted_site(tmp_path)
    trails = {key: crumbs_on(planted.text(path)) for key, path in sorted(planted.pages.items())}
    grouped: dict[tuple[str, ...], list[list[str]]] = {}
    for key, found in trails.items():
        grouped.setdefault(depth_of(planted, key), []).append(found)
    sections = {found[1] for found in trails.values()}
    modules = {found[2] for found in trails.values()}
    assert len(sections) < len(modules), (sorted(sections), sorted(modules))
    assert len(grouped) == len(modules)


def test_a_boundary_crossing_changes_directory_and_not_only_a_filename(site):
    # ⭐ The reason the clause names boundaries at all: inside a container the
    # `sibling` profile answers with a bare filename, and across one it has to
    # compute a path. A crossing that stayed in one directory would prove nothing.
    crossings = [pair for pair in boundaries(site) if pair[0] not in site.absent]
    if not crossings:
        pytest.skip(f"{site.name} declares one container, so there is no boundary to cross")
    before, _ = crossings[0]
    assert ".." in slot(site.text(site.pages[before]), "next")


# --------------------------------------------------------------------------
# The breadcrumb reads "Section › Module › Lesson" from data
# --------------------------------------------------------------------------


def test_the_trail_names_the_corpus_every_container_above_the_unit_and_the_unit(site):
    # ⛔ The clause, at the depth the fixture has: one crumb for the corpus, one
    # per container level, one for the unit — which for a depth-2 corpus is the
    # *"Section › Module › Lesson"* shape `corpus.manifest` describes.
    for entry in site.walked():
        if entry.key in site.absent:
            continue
        found = crumbs_on(site.text(site.pages[entry.key]))
        assert len(found) == 2 + len(ancestors(site.contents, entry.key)), (entry.key, found)
        assert found[0] == site.contents.title
        assert found[-1] == entry.title


def test_every_crumb_is_labelled_with_the_corpus_own_words_for_its_depth(site):
    # ⛔ R1: the level words are `manifest.levels`, carried through
    # `contents.Group.level`. Not one of them is this framework's.
    declared = set(fixture_manifest(site.name).levels)
    assert declared, "a corpus declares at least one level"
    for entry in site.walked():
        if entry.key in site.absent:
            continue
        found = crumbs_on(site.text(site.pages[entry.key]))
        for crumb, group in zip(found[1:-1], ancestors(site.contents, entry.key), strict=True):
            assert group.level in declared
            assert crumb == f"{group.level} {group.title}"


def test_the_trail_marks_the_page_the_reader_is_on_and_does_not_link_it(site):
    for entry in site.walked():
        if entry.key in site.absent:
            continue
        body = site.text(site.pages[entry.key])
        region = re.search(r'<nav aria-label="Breadcrumb">(.*?)</nav>', body, re.DOTALL)
        assert region is not None
        last = re.findall(r"<li[^>]*>.*?</li>", region.group(1), re.DOTALL)[-1]
        assert 'aria-current="page"' in last
        assert "<a " not in last


def test_the_corpus_crumb_is_the_one_step_of_the_trail_that_is_a_link(site):
    # ⚠️ **`SF-14/3`, measured from this side.** `contents.Group` carries no
    # container page name, so a trail built from the two contents documents can
    # link the corpus and the unit's own page and NOTHING IN BETWEEN. ⭐ The
    # crumbs are still listed, which is what makes the gap visible.
    for entry in site.walked():
        if entry.key in site.absent:
            continue
        body = site.text(site.pages[entry.key])
        region = re.search(r'<nav aria-label="Breadcrumb">(.*?)</nav>', body, re.DOTALL)
        rows = re.findall(r"<li[^>]*>.*?</li>", region.group(1), re.DOTALL)
        assert sum("<a " in row for row in rows) == 1
        assert "<a " in rows[0]


# --------------------------------------------------------------------------
# `file://`, and no dangling link anywhere in the generated output
# --------------------------------------------------------------------------


def test_the_generated_site_is_inhabited_and_so_is_every_pages_reference_list(site):
    # ⛔ Inhabitation again, and this is the row that matters: a link check over a
    # site with no pages, or over pages with no hrefs, is green and means nothing.
    pages = generated(site)
    assert len(pages) > 1, f"{site.name} generated only {sorted(pages)}"
    assert site.absent, "the fixture's last unit is meant to have no page"
    for where, path in sorted(pages.items()):
        assert references_in(site.text(path)), f"{where} carries no local reference"


def test_no_link_in_the_generated_site_dangles(site):
    # ⛔ **The fourth clause, and the one the task exists to be able to state.**
    # Reading 1, live: every local reference on every generated page, followed
    # the way a browser would follow it.
    assert dangling_in(site) == [], site.name


def test_the_link_check_notices_a_fragment_no_page_offers(site):
    # ⭐ **Reading 2, planted in the form the clause did not picture**: not a
    # broken path, but a fragment that names an anchor the target page does not
    # offer. ⛔ It resolves to an existing FILE, so a path-only check reads green.
    page = sorted(site.pages.items())[0][1]
    body = site.text(page)
    reference = slot(body, "up")
    planted = body.replace(
        f'href="{reference}"', f'href="{reference}{FRAGMENT}not-a-unit-anybody-declared"', 1
    )
    assert planted != body, "the plant did not change the page"
    page.write_bytes(planted.encode("utf-8"))
    found = dangling_in(site)
    assert any("no such anchor" in row for row in found), found


def test_the_link_check_notices_a_path_that_lands_on_nothing(site):
    # ⭐ Reading 2b, the other way to dangle, planted outside the unit's own media
    # directories so the one allowance this check makes cannot absorb it.
    page = sorted(site.pages.items())[0][1]
    body = site.text(page)
    planted = body.replace('href="', 'href="nowhere-a-build-writes.html?', 1)
    page.write_bytes(planted.encode("utf-8"))
    found = dangling_in(site)
    assert any("no such file" in row for row in found), found


def test_the_link_check_is_green_over_a_subject_that_cannot_match_and_the_guard_is_not(tmp_path):
    # ⭐ **Reading 3, the subject that cannot match — and the point is that
    # `dangling_in` alone CANNOT TELL IT FROM A PASS.** A site with no reference
    # on it has nothing to dangle, so the check returns `[]` exactly as it does
    # on a correct site. ⛔ That is why the inhabitation guard is a separate
    # assertion and not a comment: the guard is what reads differently here, and
    # without it this green would be a vacuous one over an empty population.
    empty = Site(
        name="nothing",
        root=tmp_path,
        contents=fixture_contents("depth1"),
        absent=frozenset(),
        pages={},
        where={},
    )
    (tmp_path / ROOT_INDEX_FILENAME).write_text("<p>no links at all</p>", encoding="utf-8")
    assert dangling_in(empty) == []
    assert references_in(empty.text(tmp_path / ROOT_INDEX_FILENAME)) == []
    assert len(generated(empty)) == 1, "the guard's first clause fires on this subject"


def test_the_whole_site_is_byte_for_byte_identical_when_generated_twice(tmp_path):
    # ⛔ **R10 in the form §2d asks for**: the generator is run twice into two
    # directories and the trees are compared, rather than one function being
    # called twice. ⚠️ The bar and the trail are the two regions this task adds,
    # and both are built by iterating — a set or a directory listing anywhere
    # under them would show up here and nowhere else.
    for name in sorted(FIXTURES):
        first, second = tmp_path / f"a-{name}", tmp_path / f"b-{name}"
        one, two = a_site(name, first), a_site(name, second)
        assert sorted(generated(one)) == sorted(generated(two))
        for where in sorted(generated(one)):
            assert (first / where).read_bytes() == (second / where).read_bytes(), where


def test_every_reference_resolves_without_a_server_and_without_a_rooted_path(site):
    # ⛔ R8 and R7 together: a rooted reference breaks the `file://` floor and can
    # carry a home directory. Neither may appear in generated output.
    for where, path in sorted(generated(site).items()):
        for reference in references_in(site.text(path)):
            assert not reference.startswith("/"), f"{where} -> {reference}"
            assert not reference.startswith("//"), f"{where} -> {reference}"


def test_the_fallback_lands_on_the_absent_units_own_row_on_the_root_index(site):
    # ⛔ *"A neighbour with no generated page falls back to the root index anchor
    # for it rather than dangling."* ⭐ The anchor is asserted against the ids the
    # REAL root index emits, so a fallback agreeing with this module's own
    # spelling of a key would not pass.
    absent = sorted(site.absent)[0]
    before = [entry for entry in site.walked() if entry.key not in site.absent][-1]
    body = site.text(site.pages[before.key])
    assert has_slot(body, "next"), "the unit before the absent one offers no next"
    reference = slot(body, "next")
    head, _, fragment = reference.partition(FRAGMENT)
    assert followed(before.page, head) == ROOT_INDEX_FILENAME
    assert fragment == absent
    assert fragment in ids_in(site.text(site.root / ROOT_INDEX_FILENAME))
