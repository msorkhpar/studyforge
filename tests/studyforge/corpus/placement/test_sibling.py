"""Mirror of `src/studyforge/corpus/placement/sibling.py` (R12)."""

from __future__ import annotations

from pathlib import PurePosixPath

import pytest

from studyforge.address import Address
from studyforge.corpus.placement import PlacementError, profile_for, unit_stem
from studyforge.corpus.placement.names import contained_stem
from studyforge.corpus.placement.sibling import SiblingProfile

SIBLING = profile_for("sibling")
ADDRESS = Address.of("basics", "16-streams-api")
ORIGIN = "16-streams-api/README_4.4.1.md"
TITLE = "Introduction to the Streams API"


def test_a_unit_page_lands_beside_its_source_file():
    # ⭐ SF-03's acceptance, and R3's whole point: the material's own directory
    # gains a page, and the README beside it is untouched.
    page = SIBLING.unit(ADDRESS, 7, TITLE, origin=ORIGIN).page
    assert page.parent == PurePosixPath(ORIGIN).parent
    assert page.name.endswith(".unit.html")


def test_the_page_is_beside_the_source_and_not_under_the_address():
    # ⚠️ Measured 2026-09-09: the Java corpus's module directories are FLAT —
    # `16-streams-api/` sits at the repository root — while its address is two
    # levels. So the address is identity and the directory comes from
    # `origin`; a profile that used the address for both would create
    # `basics/16-streams-api/` beside the material and restructure nothing
    # into it.
    page = SIBLING.unit(ADDRESS, 7, TITLE, origin=ORIGIN).page
    assert "basics" not in page.parts


def test_every_artifact_of_one_unit_sorts_together_beside_its_page():
    where = SIBLING.unit(ADDRESS, 7, TITLE, origin=ORIGIN)
    stem = contained_stem(ADDRESS, 7, TITLE)
    assert where.page.name.startswith(stem)
    for directory in where.directories:
        assert directory.name.startswith(stem + ".")
        assert directory.parent == where.page.parent


def test_the_media_directories_are_dot_suffixed_and_not_shared_subfolders():
    # ⛔ Many units share one directory here, so `audio/` as a subdirectory
    # would collide twenty ways and no clip could be told from another.
    where = SIBLING.unit(ADDRESS, 7, TITLE, origin=ORIGIN)
    assert where.audio.name.endswith(".audio")
    other = SIBLING.unit(ADDRESS, 8, "Collectors", origin="16-streams-api/README_4.4.2.md")
    assert where.audio != other.audio
    assert where.audio.parent == other.audio.parent


def test_two_units_in_one_directory_never_produce_the_same_name():
    # ⭐ The acceptance clause, proved by construction rather than by survey:
    # the ordinal is in the stem, so two units of one container cannot collide
    # however alike their titles are.
    first = SIBLING.unit(ADDRESS, 7, "Streams", origin=ORIGIN)
    second = SIBLING.unit(ADDRESS, 8, "Streams", origin="16-streams-api/README_4.4.2.md")
    assert first.page != second.page
    assert set(first.directories).isdisjoint(second.directories)


def test_two_containers_sharing_a_directory_are_named_apart_by_their_address():
    # ⛔ `W254`. This test once pinned the collision: two CONTAINERS whose units
    # land in one directory with one ordinal and title. A real corpus did it (a
    # mirrored series), so every `sibling` name now carries its container's address.
    here = SIBLING.unit(ADDRESS, 7, "Streams", origin="shared/README_a.md")
    there = SIBLING.unit(Address.of("advanced", "17-x"), 7, "Streams", origin="shared/README_b.md")
    assert here.page.parent == there.page.parent
    assert set((here.page, *here.directories)).isdisjoint((there.page, *there.directories))


@pytest.mark.parametrize("origin", [None, "", 7])
def test_a_unit_with_no_origin_is_refused(origin):
    with pytest.raises(PlacementError, match="the unit at .* records no usable 'origin'"):
        SIBLING.unit(ADDRESS, 7, TITLE, origin=origin)


@pytest.mark.parametrize("origin", [None, "", 7])
def test_a_container_with_no_origin_is_refused_and_is_not_called_a_unit(origin):
    # ⚠️ The two records that carry an `origin` are different records, and an
    # integrator sent to the wrong one looks in the wrong place.
    with pytest.raises(PlacementError) as raised:
        SIBLING.container(ADDRESS, ("Basics", "Streams API"), origin=origin)
    assert "container" in str(raised.value)
    assert "unit" not in str(raised.value)


def test_a_container_page_lands_beside_the_containers_own_source_file():
    page = SIBLING.container(ADDRESS, ("Basics", "Streams API"), origin="16-streams-api/README.md")
    assert page.page == PurePosixPath("16-streams-api/streams-api.section.html")


def test_the_worked_example_from_the_spec_is_reproduced_exactly():
    # ⭐ §5's own listing, once the corpus records its numbering as data. This
    # is the answer SF-31's deferred golden was waiting on: the label is the
    # seam, and with it the shape matches the spec character for character.
    where = SIBLING.unit(ADDRESS, 7, TITLE, origin=ORIGIN, label="4.4.1")
    stem = "16-streams-api/basics.16-streams-api.4.4.1-introduction-to-the-streams-api"
    assert str(where.page) == f"{stem}.unit.html"
    assert str(where.audio) == f"{stem}.audio"
    assert str(where.practice) == f"{stem}.practice"


def test_placing_the_same_unit_twice_gives_the_same_paths():
    a = SIBLING.unit(ADDRESS, 7, TITLE, origin=ORIGIN)
    assert a == SIBLING.unit(ADDRESS, 7, TITLE, origin=ORIGIN)


def test_the_profile_declares_its_name_and_what_it_does():
    assert SiblingProfile.name == "sibling"
    assert "beside the source file" in SiblingProfile.describes


def test_the_media_globs_match_the_stems_this_profile_actually_mints():
    # ⭐ Ruling 91's cheapest half: under this profile the generated names are
    # the unit's own stem, so a corpus cannot enumerate them — one measured
    # build wrote 79 artifacts, 67 of them content-hash-named.
    where = SIBLING.unit(ADDRESS, 7, TITLE, origin=ORIGIN)
    stem = contained_stem(ADDRESS, 7, TITLE)
    for line in SIBLING.media_ignore_lines():
        assert line.startswith("*.") and line.endswith("/")
    kinds = [line[2:-1] for line in SIBLING.media_ignore_lines()]
    assert [where.media_dir(kind).name for kind in kinds] == [f"{stem}.{k}" for k in kinds]


def test_the_media_globs_are_unanchored_because_the_material_is():
    assert not [line for line in SIBLING.media_ignore_lines() if line.startswith("/")]


# --------------------------------------------------------------------------
# ⛔ `W254`: every name carries the container's address
# --------------------------------------------------------------------------


def test_containers_whose_deepest_segments_match_are_still_named_apart():
    # ⭐ The whole address, not its last segment: `a/x` and `b/x` share one name
    # otherwise, which is not "by construction".
    first = SIBLING.unit(Address.of("a", "x"), 1, "Shared", origin="src/a1.md")
    second = SIBLING.unit(Address.of("b", "x"), 1, "Shared", origin="src/b1.md")
    assert first.page != second.page


@pytest.mark.parametrize("fixture", ["depth2", "shared-origin"])
def test_a_name_differs_from_the_unit_stem_only_by_the_address_in_front(fixture):
    # ⛔ The control for `W254`'s cost: every `sibling` name moves by exactly
    # the address prefix, and nothing else about it changes.
    from studyforge.corpus.container import parse
    from studyforge.corpus.manifest import parse as parse_manifest
    from tests.support import repository_root

    root = repository_root() / "tests" / "fixtures" / fixture
    manifest = parse_manifest((root / "corpus.json").read_text("utf-8"), "corpus.json")
    assert manifest.placement == "sibling"
    checked = 0
    for path in sorted((root / "archive").rglob("container.json")):
        held = parse(path.read_text("utf-8"), path.relative_to(root).as_posix(), manifest)
        prefix = ".".join(held.address.segments) + "."
        for unit in held.units:
            where = SIBLING.unit(
                held.address, unit.n, unit.title, origin=unit.origin, label=unit.label
            )
            stem = prefix + unit_stem(unit.n, unit.title, unit.label)
            beside = PurePosixPath(unit.origin).parent
            assert where.page == beside / f"{stem}.unit.html"
            assert where.directories == tuple(
                beside / f"{stem}.{kind}" for kind in ("audio", "images", "video", "practice")
            )
            checked += 1
    assert checked > 0


def test_a_unit_with_no_address_is_refused_rather_than_named_without_one():
    with pytest.raises(PlacementError):
        SIBLING.unit(None, 1, TITLE, origin=ORIGIN)
