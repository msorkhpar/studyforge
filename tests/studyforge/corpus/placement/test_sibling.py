"""Mirror of `src/studyforge/corpus/placement/sibling.py` (R12)."""

from __future__ import annotations

from pathlib import PurePosixPath

import pytest

from studyforge.address import Address
from studyforge.corpus.placement import PlacementError, profile_for, unit_stem
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
    stem = unit_stem(7, TITLE)
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


def test_two_containers_sharing_a_directory_would_collide_and_that_is_findable():
    # ⚠️ The one real collision risk, stated rather than hoped away: two
    # CONTAINERS whose units land in one directory with the same ordinal. The
    # Java corpus does not do this — one module directory per container — but
    # nothing in this profile prevents it, so SF-25 owns the check and this
    # pins the shape of what it must find.
    here = SIBLING.unit(ADDRESS, 7, "Streams", origin="shared/README_a.md")
    there = SIBLING.unit(Address.of("advanced", "17-x"), 7, "Streams", origin="shared/README_b.md")
    assert here.page == there.page


@pytest.mark.parametrize("origin", [None, "", 7])
def test_a_unit_with_no_origin_is_refused(origin):
    with pytest.raises(PlacementError, match="records no usable 'origin'"):
        SIBLING.unit(ADDRESS, 7, TITLE, origin=origin)


def test_a_container_page_lands_beside_the_containers_own_source_file():
    page = SIBLING.container(ADDRESS, ("Basics", "Streams API"), origin="16-streams-api/README.md")
    assert page.page == PurePosixPath("16-streams-api/streams-api.section.html")


def test_the_worked_example_from_the_spec_is_reproduced_exactly():
    # ⭐ §5's own listing, once the corpus records its numbering as data. This
    # is the answer SF-31's deferred golden was waiting on: the label is the
    # seam, and with it the shape matches the spec character for character.
    where = SIBLING.unit(ADDRESS, 7, TITLE, origin=ORIGIN, label="4.4.1")
    assert str(where.page) == "16-streams-api/4.4.1-introduction-to-the-streams-api.unit.html"
    assert str(where.audio) == "16-streams-api/4.4.1-introduction-to-the-streams-api.audio"
    assert str(where.practice) == "16-streams-api/4.4.1-introduction-to-the-streams-api.practice"


def test_placing_the_same_unit_twice_gives_the_same_paths():
    a = SIBLING.unit(ADDRESS, 7, TITLE, origin=ORIGIN)
    assert a == SIBLING.unit(ADDRESS, 7, TITLE, origin=ORIGIN)


def test_the_profile_declares_its_name_and_what_it_does():
    assert SiblingProfile.name == "sibling"
    assert "beside the source file" in SiblingProfile.describes
