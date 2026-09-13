"""Mirror of `src/studyforge/corpus/placement/bound.py` (R12, `INT09-5`)."""

from __future__ import annotations

import pytest

from studyforge.corpus.container import from_document, parse
from studyforge.corpus.manifest import from_document as manifest_from_document
from studyforge.corpus.manifest import parse as parse_manifest
from studyforge.corpus.placement import (
    PlacementError,
    bind,
    profile_for,
    registered,
    unit_stem,
)
from tests.studyforge.validate import corpora
from tests.support import repository_root

SIBLING = profile_for("sibling")

#: Every committed fixture corpus. ⛔ None of them collides, so each is a control.
FIXTURES = ("depth1", "depth2", "shared-origin")


def series(address, letter, *, title="Shared", deepest=None, origins=True):
    """One container of two units whose ordinals and titles another series can mirror.

    Every origin is in `src/`, so two series built here share one directory.
    """
    depth = len(address)
    manifest = manifest_from_document(
        {**corpora.MANIFEST, "placement": "sibling", "levels": ["group", "course"][-depth:]},
        "corpus.json",
    )
    units = [
        corpora.unit_entry(n, origin=f"src/{letter}{n}.md" if origins else None, title=title)
        for n in (1, 2)
    ]
    titles = [f"Group {letter}"] * (depth - 1) + [deepest or f"Series {letter}"]
    document = corpora.container(
        units, address=address, origin=f"src/{letter.upper()}.md", titles=titles
    )
    return from_document(document, "container.json", manifest)


def placed(profile, held):
    """Every declared unit's page under `profile`, in declared order."""
    return [
        profile.unit(c.address, u.n, u.title, origin=u.origin, label=u.label).page.as_posix()
        for c in held
        for u in c.units
    ]


# --------------------------------------------------------------------------
# a mirrored series is placeable
# --------------------------------------------------------------------------


def test_mirrored_series_in_one_directory_get_one_page_per_unit_named_by_container():
    held = (series(("first",), "a"), series(("second",), "b"))
    bound = bind(SIBLING, held)
    assert placed(bound, held) == [
        "src/first-unit-01-shared-1.unit.html",
        "src/first-unit-02-shared-2.unit.html",
        "src/second-unit-01-shared-1.unit.html",
        "src/second-unit-02-shared-2.unit.html",
    ]
    assert bound.collisions == ()


def test_and_the_unbound_profile_places_the_same_series_on_one_page_per_pair():
    # ⚠️ The defect, kept as the control: four units, two paths.
    held = (series(("first",), "a"), series(("second",), "b"))
    assert len(set(placed(SIBLING, held))) == 2


def test_only_the_colliding_units_are_qualified():
    held = (
        series(("first",), "a"),
        series(("second",), "b"),
        series(("third",), "c", title="Distinct"),
    )
    bound = bind(SIBLING, held)
    assert set(bound.qualifiers) == {("first", 1), ("first", 2), ("second", 1), ("second", 2)}
    assert placed(bound, held[2:]) == placed(SIBLING, held[2:])


@pytest.mark.parametrize("fixture", FIXTURES)
def test_a_collision_free_fixture_binds_to_exactly_the_profiles_own_answer(fixture):
    # ⭐ Byte-identity for a corpus with no collision: no unit is qualified, so
    # every location is the profile's own.
    root = repository_root() / "tests" / "fixtures" / fixture
    manifest = parse_manifest((root / "corpus.json").read_text("utf-8"), "corpus.json")
    maps = sorted((root / "archive").rglob("container.json"))
    held = [parse(p.read_text("utf-8"), p.relative_to(root).as_posix(), manifest) for p in maps]
    assert held, fixture
    profile = profile_for(manifest.placement)
    bound = bind(profile, held)
    assert (bound.qualifiers, bound.collisions) == ({}, ())
    for container in held:
        for unit in container.units:
            asked = (container.address, unit.n, unit.title)
            where = {"origin": unit.origin, "label": unit.label}
            assert bound.unit(*asked, **where) == profile.unit(*asked, **where)


# --------------------------------------------------------------------------
# what the container cannot separate is a collision, by name
# --------------------------------------------------------------------------


def test_what_the_container_cannot_separate_is_a_collision_naming_both_and_the_path():
    held = (series(("one", "x"), "a"), series(("two", "x"), "b"))
    bound = bind(SIBLING, held)
    # Two units per series, each a page and four media directories.
    assert len(bound.collisions) == 10
    message = bound.collisions[0].message
    assert "two/x unit 1's page" in message
    assert "one/x unit 1's page" in message
    assert "'src/x-unit-01-shared-1.unit.html'" in message


def test_two_container_pages_on_one_path_collide_and_are_never_qualified():
    held = (
        series(("first",), "a", title="One", deepest="Same"),
        series(("second",), "b", title="Two", deepest="Same"),
    )
    bound = bind(SIBLING, held)
    assert [(c.first.describe(), c.second.describe()) for c in bound.collisions] == [
        ("container first's page", "container second's page")
    ]
    assert bound.qualifiers == {}


def test_binding_a_bound_profile_binds_the_profile_itself():
    held = (series(("first",), "a"), series(("second",), "b"))
    once = bind(SIBLING, held)
    twice = bind(once, held)
    assert twice.profile is SIBLING
    assert twice.qualifiers == once.qualifiers


@pytest.mark.parametrize("name", sorted(registered()))
def test_every_question_but_unit_is_the_profiles_own(name):
    profile = profile_for(name)
    bound = bind(profile, ())
    assert (bound.name, bound.describes, repr(bound), bound.corpus()) == (
        profile.name,
        profile.describes,
        repr(profile),
        profile.corpus(),
    )
    assert (bound.ignore_home(), bound.media_ignore_lines()) == (
        profile.ignore_home(),
        profile.media_ignore_lines(),
    )


def test_a_unit_that_cannot_be_placed_is_left_to_the_callers_own_call():
    held = (series(("first",), "a", origins=False),)
    bound = bind(SIBLING, held)
    unit = held[0].units[0]
    with pytest.raises(PlacementError):
        bound.unit(held[0].address, unit.n, unit.title, origin=unit.origin)


def test_a_qualifier_is_a_filename_component_and_a_refusal_does_not_echo_it():
    assert unit_stem(1, "Title", qualifier="first") == "first-unit-01-title"
    with pytest.raises(PlacementError) as caught:
        unit_stem(1, "Title", qualifier="../private")
    assert "../private" not in str(caught.value)
