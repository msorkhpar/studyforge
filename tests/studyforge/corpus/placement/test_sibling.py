"""Mirror of `src/studyforge/corpus/placement/sibling.py` (R12)."""

from __future__ import annotations

from pathlib import PurePosixPath

import pytest

from studyforge.address import Address
from studyforge.corpus.placement import (
    ROOT_INDEX_FILENAME,
    STUDY_DIRNAME,
    UNIT_MEDIA_DIRNAMES,
    PlacementError,
    profile_for,
    unit_stem,
)
from studyforge.corpus.placement.names import contained_stem
from studyforge.corpus.placement.sibling import SiblingProfile

SIBLING = profile_for("sibling")
ADDRESS = Address.of("basics", "16-streams-api")
ORIGIN = "16-streams-api/README_4.4.1.md"
TITLE = "Introduction to the Streams API"


def outside_the_declaration(paths):
    """Every path that is not inside a `study/` directory, named (`W323`, clause 5).

    ⭐ **The instrument both ways.** A corpus placed under this profile has no
    such path; a plant that writes beside the material has one per artifact,
    and the assertion names them rather than counting them.
    """
    return sorted(str(path) for path in paths if STUDY_DIRNAME not in PurePosixPath(path).parts)


def every_path(where):
    """One unit's page and every directory it may claim."""
    return (where.page, *where.directories)


def test_a_unit_page_lands_in_the_declared_subdirectory_beside_its_source_file():
    # ⭐ SF-03's acceptance, and R3's whole point: the material's own directory
    # gains a page, and the README beside it is untouched. ⛔ `W323`, clause 1:
    # the page is in that directory's `study/`, not loose in it.
    page = SIBLING.unit(ADDRESS, 7, TITLE, origin=ORIGIN).page
    assert page.parent == PurePosixPath(ORIGIN).parent / STUDY_DIRNAME
    assert page.name.endswith(".unit.html")


def test_the_source_directory_gains_one_entry_and_not_one_per_artifact():
    # ⛔ `W323`'s measured defect: a source directory held its sources, one page
    # per source and one media directory per source, in one listing. ⭐ Whatever
    # this profile writes from a source file, the directory holding that file
    # gains exactly one name.
    beside = PurePosixPath(ORIGIN).parent
    where = SIBLING.unit(ADDRESS, 7, TITLE, origin=ORIGIN)
    container = SIBLING.container(ADDRESS, ("Basics", "Streams API"), origin=ORIGIN)
    gained = {path.parts[len(beside.parts)] for path in (*every_path(where), container.page)}
    assert gained == {STUDY_DIRNAME}


def test_a_source_file_at_the_corpus_root_puts_no_generated_file_at_the_root():
    # ⛔ `W323`, clause 3: the only generated file at the corpus ROOT is the
    # root index. A source at the root is exactly the case that broke it — the
    # rule was "beside the source file", so its page and its media landed there.
    where = SIBLING.unit(ADDRESS, 7, TITLE, origin="README.md")
    container = SIBLING.container(ADDRESS, ("Basics", "Streams API"), origin="README.md")
    at_the_root = [
        str(path) for path in (*every_path(where), container.page) if len(path.parts) == 1
    ]
    assert at_the_root == []
    # ⭐ The control: there IS one generated name at the root, and it is the one
    # this framework mints for it.
    assert SIBLING.corpus().root_index == PurePosixPath(ROOT_INDEX_FILENAME)


def test_the_page_is_beside_the_source_and_not_under_the_address():
    # ⚠️ Measured 2026-09-09: the Java corpus's module directories are FLAT —
    # `16-streams-api/` sits at the repository root — while its address is two
    # levels. So the address is identity and the directory comes from
    # `origin`; a profile that used the address for both would create
    # `basics/16-streams-api/` beside the material and restructure nothing
    # into it.
    page = SIBLING.unit(ADDRESS, 7, TITLE, origin=ORIGIN).page
    assert "basics" not in page.parts


def test_every_artifact_of_one_unit_is_named_from_that_units_stem():
    # ⚠️ `W323` moved the media one level down, so a directory's NAME is now the
    # stem exactly rather than the stem plus a suffix; what has not changed is
    # that a unit's artifacts are all named from its own identity.
    where = SIBLING.unit(ADDRESS, 7, TITLE, origin=ORIGIN)
    stem = contained_stem(ADDRESS, 7, TITLE)
    assert where.page.name.startswith(stem)
    for directory in where.directories:
        assert directory.name == stem
        assert directory.parent.parent == where.page.parent


def test_the_media_sits_under_one_directory_per_kind_and_one_per_unit_inside_it():
    # ⛔ `W323`, clause 2: generated audio is under a declared subdirectory,
    # not one directory per unit interleaved with the material. ⚠️ Many units
    # share one `study/`, so the stem still has to discriminate — one level
    # lower, inside the kind's own directory, where it collides with nothing.
    where = SIBLING.unit(ADDRESS, 7, TITLE, origin=ORIGIN)
    assert where.audio.parent.name == "audio"
    assert where.audio.parent.parent.name == STUDY_DIRNAME
    other = SIBLING.unit(ADDRESS, 8, "Collectors", origin="16-streams-api/README_4.4.2.md")
    assert where.audio != other.audio
    # ⭐ One `audio/` for the whole source directory, however many units it has.
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


def test_a_container_page_lands_in_the_declared_subdirectory_beside_its_source_file():
    page = SIBLING.container(ADDRESS, ("Basics", "Streams API"), origin="16-streams-api/README.md")
    assert page.page == PurePosixPath("16-streams-api/study/streams-api.section.html")


def test_the_worked_example_from_the_spec_is_reproduced_exactly():
    # ⭐ §5's own listing, once the corpus records its numbering as data. This
    # is the answer the deferred placement golden was waiting on: the label is the
    # seam, and with it the shape matches the spec character for character.
    where = SIBLING.unit(ADDRESS, 7, TITLE, origin=ORIGIN, label="4.4.1")
    stem = "basics.16-streams-api.4.4.1-introduction-to-the-streams-api"
    assert str(where.page) == f"16-streams-api/study/{stem}.unit.html"
    assert str(where.audio) == f"16-streams-api/study/audio/{stem}"
    assert str(where.practice) == f"16-streams-api/study/practice/{stem}"


def test_placing_the_same_unit_twice_gives_the_same_paths():
    a = SIBLING.unit(ADDRESS, 7, TITLE, origin=ORIGIN)
    assert a == SIBLING.unit(ADDRESS, 7, TITLE, origin=ORIGIN)


def test_the_profile_declares_its_name_and_what_it_does():
    assert SiblingProfile.name == "sibling"
    assert "beside the source file" in SiblingProfile.describes


def test_the_media_globs_match_the_directories_this_profile_actually_mints():
    # ⭐ Ruling 91's cheapest half: under this profile the generated names are
    # the unit's own stem, so a corpus cannot enumerate them — one measured
    # build wrote 79 artifacts, 67 of them content-hash-named.
    where = SIBLING.unit(ADDRESS, 7, TITLE, origin=ORIGIN)
    lines = SIBLING.media_ignore_lines()
    for line in lines:
        assert line.startswith(f"{STUDY_DIRNAME}/") and line.endswith("/")
    kinds = [line.split("/")[1] for line in lines]
    assert kinds == list(UNIT_MEDIA_DIRNAMES)
    for kind in kinds:
        # ⛔ The rule matches the directory that actually holds the clips: the
        # kind's own directory under `study/`, whose children are the stems.
        assert where.media_dir(kind).parent.parts[-2:] == (STUDY_DIRNAME, kind)


def test_the_media_globs_no_longer_match_a_repositorys_own_directory_by_suffix():
    # ⚠️ The rule was `*.audio/`, a bare stem suffix: a repository keeping its
    # own `lecture.audio/` had one git would ignore. ⭐ `W323` put this
    # profile's declared segment in front of every line.
    assert not [line for line in SIBLING.media_ignore_lines() if line.startswith("*.")]


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
            beside = PurePosixPath(unit.origin).parent / STUDY_DIRNAME
            assert where.page == beside / f"{stem}.unit.html"
            # ⛔ The kinds are placement's own tuple, never retyped here: a
            # fifth kind must not leave this control quietly checking four.
            assert where.directories == tuple(beside / kind / stem for kind in UNIT_MEDIA_DIRNAMES)
            checked += 1
    assert checked > 0


# --------------------------------------------------------------------------
# ⛔ `W323`: everything this profile writes is under the declared subdirectory
# --------------------------------------------------------------------------


@pytest.mark.parametrize("fixture", ["depth2", "shared-origin"])
def test_a_whole_corpus_lands_under_the_declared_subdirectory_and_nowhere_else(fixture):
    # ⛔ `W323`, clause 5, the affirming half: placed over a real corpus rather
    # than over one call, because "and nowhere else" is a property of the set.
    from studyforge.corpus.container import parse
    from studyforge.corpus.manifest import parse as parse_manifest
    from tests.support import repository_root

    root = repository_root() / "tests" / "fixtures" / fixture
    manifest = parse_manifest((root / "corpus.json").read_text("utf-8"), "corpus.json")
    paths = []
    for path in sorted((root / "archive").rglob("container.json")):
        held = parse(path.read_text("utf-8"), path.relative_to(root).as_posix(), manifest)
        paths.append(SIBLING.container(held.address, held.titles, origin=held.origin).page)
        for unit in held.units:
            paths += every_path(
                SIBLING.unit(held.address, unit.n, unit.title, origin=unit.origin, label=unit.label)
            )
    assert paths, f"{fixture} placed nothing"
    assert outside_the_declaration(paths) == []


def test_a_plant_that_writes_beside_the_material_is_caught_by_name():
    # ⛔ `W323`, clause 5, the refuting half — and the plant is not invented:
    # it is this profile's own arithmetic from before the row, which is what
    # the instrument has to catch if it is worth running.
    class Loose(SiblingProfile):
        name = "loose"

        def study_dir(self, origin, address, what="artifact"):
            return super().study_dir(origin, address, what).parent

    planted = every_path(Loose().unit(ADDRESS, 7, TITLE, origin=ORIGIN))
    named = outside_the_declaration(planted)
    assert len(named) == len(planted)
    assert all(str(path) in named for path in planted)
    # ⭐ The control, in one assertion: the shipped profile places the same unit
    # and the same instrument says nothing.
    assert outside_the_declaration(every_path(SIBLING.unit(ADDRESS, 7, TITLE, origin=ORIGIN))) == []


def test_a_unit_with_no_address_is_refused_rather_than_named_without_one():
    with pytest.raises(PlacementError):
        SIBLING.unit(None, 1, TITLE, origin=ORIGIN)
