"""The contents package's acceptance, asserted rather than described.

⛔ **Not a mirror of any one module** (R12 is one-way): these are the clauses
the package meets as a whole, and each one names the instrument that would fail
it.

| Clause | Instrument |
|---|---|
| both fixture corpora build, at both depths, from one builder | `test_both_fnd04_fixtures_*` |
| reproducible byte for byte | `test_*_bytes_*` |
| a mismatched pair is detected, not silently joined | `test_status.py`'s `join` tests |
| a neighbour yields `Links`, and the page carries the bar | `test_a_unit_with_a_neighbour_*` |
| a mixed-form contents document parses to the FULL count | `test_a_mixed_form_*` |
"""

from __future__ import annotations

import re
from pathlib import Path, PurePosixPath

import pytest

from studyforge.contents import (
    ContentsError,
    build,
    digest,
    links,
    order,
    parse,
    render,
)
from studyforge.corpus.placement import ROOT_INDEX_FILENAME
from studyforge.render.markup import safe_href
from studyforge.render.page import Link, Links
from studyforge.render.page import compose as compose_page
from studyforge.skills.reconnaissance import record
from tests.studyforge.contents.corpora import (
    fixture_containers,
    fixture_contents,
    fixture_manifest,
)
from tests.studyforge.render.page.pages import depth1_unit_02, depth2_unit_01
from tests.support import repository_root

#: The mixed-form fixture, as material rather than as a description of material.
MIXED_FORM = repository_root() / "tests" / "fixtures" / "contents" / "mixed-form"

#: What the donation records: 38 entries, 2 of them written as headings.
MIXED_FORM_ENTRIES = 38
MIXED_FORM_AS_HEADINGS = 2

#: ⛔ The naive reader the fixture exists to catch, in one line. It is the
#: majority form and nothing else — `record.LIST_MARKER` is the very pattern a
#: parser written for that form would reach for.
LIST_ONLY = re.compile(rf"{record.LIST_MARKER.pattern}.*{record.LINK.pattern}")


# --------------------------------------------------------------------------
# Both fixture corpora, at both depths, from one builder
# --------------------------------------------------------------------------


@pytest.mark.parametrize("name", ["depth1", "depth2"])
def test_both_fnd04_fixtures_build_valid_contents(name):
    built = fixture_contents(name)
    assert built.corpus == fixture_manifest(name).source
    assert built.levels == fixture_manifest(name).levels
    assert order(built) != ()


@pytest.mark.parametrize("name", ["depth1", "depth2"])
def test_both_fnd04_fixtures_survive_the_round_trip(name):
    built = fixture_contents(name)
    assert parse(render(built)) == built
    assert digest(parse(render(built))) == digest(built)


@pytest.mark.parametrize("name", ["depth1", "depth2"])
def test_the_bytes_do_not_move_between_two_builds_of_one_fixture(name):
    # ⛔ R10. Two independent reads of the same committed inputs.
    first = build(fixture_manifest(name), fixture_containers(name))
    second = build(fixture_manifest(name), fixture_containers(name))
    assert render(first) == render(second)


def test_the_two_fixtures_are_not_the_same_document():
    # ⭐ Both directions: a reproducibility check that compared a thing with
    # itself would pass whatever the builder did.
    assert render(fixture_contents("depth1")) != render(fixture_contents("depth2"))


def test_every_declared_unit_of_both_fixtures_reaches_the_contents():
    for name, expected in (("depth1", 3), ("depth2", 6)):
        declared = sum(len(container.units) for container in fixture_containers(name))
        assert declared == expected
        assert len(order(fixture_contents(name))) == declared


# --------------------------------------------------------------------------
# The between-units bar, built from contents data and nothing else
# --------------------------------------------------------------------------


def a_bar(built, key) -> Links:
    """The renderer's `Links`, built from contents data and nothing else.

    ⚠️ **This mapping is the seam, and it is one line.** `contents` returns
    plain strings so it need not import `render`; the renderer's caller turns
    them into its own type. ⛔ Which caller does it is the renderer's side.
    """
    return Links(**{field: Link(**slot) for field, slot in links(built, key).items()})


def test_the_contents_agree_with_the_placement_the_renderer_was_given():
    # ⭐ The cross-check that makes the bar meaningful: the page `contents`
    # recorded for this unit is the page the renderer is rendering.
    case = depth2_unit_01()
    entry = next(
        entry
        for entry in order(fixture_contents("depth2"))
        if entry.key == "basics/01-getting-started/unit-01"
    )
    assert entry.page == case.placement.unit.page


def test_a_unit_with_a_neighbour_renders_the_between_units_bar():
    # ⛔ The between-units clause. Without a reading order `between_units`
    # returns `''` for every caller in `src/`, and the symptom is neither
    # legible nor illegible — it is absent.
    case = depth1_unit_02()
    built = fixture_contents("depth1")
    page = compose_page(case.document, case.placement, a_bar(built, "depth-one/unit-02"))
    assert '<nav aria-label="Between units">' in page
    assert 'rel="prev"' in page and 'rel="next"' in page and 'rel="up"' in page


def test_the_bar_names_the_units_either_side_and_the_corpus_above():
    case = depth1_unit_02()
    built = fixture_contents("depth1")
    page = compose_page(case.document, case.placement, a_bar(built, "depth-one/unit-02"))
    assert "What a triple is" in page
    assert "Asking the first question" in page
    assert "Depth One Demo" in page


def followed(page: PurePosixPath, href: str) -> str:
    """Where a browser lands, following `href` from the page that carries it.

    ⛔ No filesystem: this is URL arithmetic, and resolving against the process's
    working directory would make the answer a property of where the tests ran.
    """
    parts = list(page.parent.parts)
    for part in href.split("/"):
        if part == "..":
            parts.pop()
        elif part not in ("", "."):
            parts.append(part)
    return "/".join(parts)


@pytest.mark.parametrize("name", ["depth1", "depth2"])
def test_every_bar_link_lands_on_a_page_the_contents_declare(name):
    # ⛔ R8: the bar has to work over `file://`, so each href is followed the
    # way a browser would and must land on a page this corpus declares.
    built = fixture_contents(name)
    pages = {entry.page.as_posix() for entry in order(built)}
    for entry in order(built):
        found = links(built, entry.key)
        for field in ("previous", "next"):
            if field in found:
                assert followed(entry.page, found[field]["href"]) in pages
        assert followed(entry.page, found["index"]["href"]) == ROOT_INDEX_FILENAME


def test_the_same_page_without_a_reading_order_carries_no_bar():
    # ⛔ The negative control: without a reading order the bar is absent, not
    # merely illegible.
    case = depth1_unit_02()
    assert '<nav aria-label="Between units">' not in compose_page(case.document, case.placement)


def test_the_first_unit_of_the_reading_order_has_no_previous_link_in_its_bar():
    case = depth2_unit_01()
    built = fixture_contents("depth2")
    page = compose_page(
        case.document, case.placement, a_bar(built, "advanced/02-going-further/unit-01")
    )
    assert '<nav aria-label="Between units">' in page
    assert 'rel="prev"' not in page


def test_a_same_directory_neighbour_survives_in_the_data_and_now_survives_on_the_page():
    # ⛔ Under `sibling` placement two units of one container share a
    # directory, so `relative_href` answers with a bare filename, and the set
    # of safe hrefs must admit one, or `navigation._link` drops the slot with
    # nothing raised.
    case = depth2_unit_01()
    built = fixture_contents("depth2")
    key = "basics/01-getting-started/unit-01"
    slots = links(built, key)
    assert slots["next"]["href"] == (
        "basics.01-getting-started.unit-02-fields-and-constructors.unit.html"
    )
    assert safe_href(slots["next"]["href"]) == slots["next"]["href"]
    page = compose_page(case.document, case.placement, a_bar(built, key))
    assert '<nav aria-label="Between units">' in page
    assert 'rel="prev"' in page and 'rel="up"' in page and 'rel="next"' in page


#: How the rendered bar spells each slot `contents.links` can return.
BAR_RELATIONS = {"previous": 'rel="prev"', "index": 'rel="up"', "next": 'rel="next"'}


@pytest.mark.parametrize(
    ("corpus", "case"), (("depth1", depth1_unit_02), ("depth2", depth2_unit_01))
)
def test_every_slot_the_contents_compute_reaches_the_page_under_both_profiles(corpus, case):
    # ⛔ Under both profiles, because `depth2` computes more slots than
    # `depth1` and a hole under `sibling` would sit beside a pass under `tree`.
    #
    # ⭐ The population is reported, never reduced to a scalar that agrees
    # with itself (R6): the failure names the page and the slot.
    rendered = case()
    built = fixture_contents(corpus)
    computed, present = 0, 0
    for entry in order(built):
        slots = links(built, entry.key)
        page = compose_page(rendered.document, rendered.placement, a_bar(built, entry.key))
        for field, spelling in BAR_RELATIONS.items():
            if field not in slots:
                continue
            computed += 1
            if spelling in page:
                present += 1
            else:
                pytest.fail(f"{corpus} {entry.key}: {field} -> {slots[field]['href']} was dropped")
    assert computed and computed == present, (corpus, computed, present)


def test_a_corpus_of_one_unit_still_points_at_its_index():
    built = fixture_contents("depth1")
    assert "index" in links(built, order(built)[0].key)


# --------------------------------------------------------------------------
# The mixed-form contents fixture
# --------------------------------------------------------------------------


def mixed_form_targets() -> set[str]:
    """The material the donated index points at, as the inventory would name it."""
    return {path.name for path in sorted(MIXED_FORM.glob("unit-*.md"))}


def test_the_fixture_is_mixed_form_and_the_minority_is_the_heading_form():
    # ⚠️ Asserted, because a fixture that quietly became uniform would stop
    # being able to fail the reader it was donated to catch.
    read = record.read(MIXED_FORM / "README.md", MIXED_FORM, mixed_form_targets())
    assert sum(read.forms.values()) == MIXED_FORM_ENTRIES
    assert len(read.forms) > 1
    assert min(read.forms.values()) == MIXED_FORM_AS_HEADINGS


def test_a_mixed_form_contents_document_parses_to_the_full_count():
    # ⛔ 36 of 38 are list items; a reader that saw only the
    # list form would read 36, emit 36, and raise nothing.
    read = record.read(MIXED_FORM / "README.md", MIXED_FORM, mixed_form_targets())
    assert len(read.entries) == MIXED_FORM_ENTRIES
    assert len(read.order) == len(set(read.order)) == MIXED_FORM_ENTRIES


def test_the_fixture_fails_a_reader_that_sees_only_the_list_form():
    # ⭐ The negative control run negatively: the fixture is only worth
    # committing if it can actually fail the parser it exists to catch.
    lines = (MIXED_FORM / "README.md").read_text(encoding="utf-8").splitlines()
    short = [line for line in lines if LIST_ONLY.search(line)]
    assert len(short) == MIXED_FORM_ENTRIES - MIXED_FORM_AS_HEADINGS
    assert len(short) < MIXED_FORM_ENTRIES


def test_every_entry_the_index_names_is_a_file_that_exists():
    # ⛔ A short *index* and a short *directory* are different defects, and a
    # fixture that confused them would not isolate either.
    read = record.read(MIXED_FORM / "README.md", MIXED_FORM, mixed_form_targets())
    assert all((MIXED_FORM / target).is_file() for target in read.order)


def test_the_reading_order_the_document_states_is_the_order_it_writes_them_in():
    read = record.read(MIXED_FORM / "README.md", MIXED_FORM, mixed_form_targets())
    assert read.order == [f"unit-{n:02d}.md" for n in range(1, MIXED_FORM_ENTRIES + 1)]


def test_a_contents_document_short_by_two_is_what_this_guards_against():
    # ⭐ A short contents read, stated in this package's own terms, and refused here
    # for a different reason: `build` counts what the corpus DECLARES, so a
    # short read upstream is short in the container map, where the declared
    # count is a thing somebody can compare against.
    manifest = fixture_manifest("depth1")
    containers = fixture_containers("depth1")
    full = len(order(build(manifest, containers)))
    assert full == sum(len(container.units) for container in containers)
    with pytest.raises((ContentsError, ValueError)):
        build(manifest, (*containers, *containers))


def test_the_fixture_directory_is_where_this_task_put_it():
    assert Path(MIXED_FORM).is_dir()
    assert (MIXED_FORM / "README.md").is_file()
    assert len(mixed_form_targets()) == MIXED_FORM_ENTRIES
