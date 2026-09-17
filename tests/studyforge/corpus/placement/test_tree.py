"""Mirror of `src/studyforge/corpus/placement/tree.py` (R12)."""

from __future__ import annotations

from pathlib import PurePosixPath

import pytest

from studyforge.address import Address
from studyforge.corpus.placement import GENERATED_ROOT, profile_for
from studyforge.corpus.placement.tree import TreeProfile

TREE = profile_for("tree")

#: The extraction source's shape below the container, measured 2026-09-09 from
#: a real unit directory: `audio/`, `video/` and the unit document beside
#: `index.html`, under `units/unit-NN/`.
SOURCE_SHAPE = ("units", "unit-07")


def test_the_address_becomes_directories_under_one_generated_root():
    where = TREE.unit(Address.of("basics", "16-streams-api"), 7, "Streams")
    assert where.page.parts[:4] == (GENERATED_ROOT, "basics", "16-streams-api", "units")


def test_the_shape_below_the_container_is_the_extraction_sources_own():
    # ⭐ Segment for segment, so a later migration moves a tree rather than
    # re-deriving one, and every href a page holds to its own media is
    # unchanged.
    where = TREE.unit(Address.of("basics", "16-streams-api"), 7, "Streams")
    assert where.page.parts[-3:-1] == SOURCE_SHAPE
    assert where.audio.parts[-3:] == (*SOURCE_SHAPE, "audio")
    assert where.images.parts[-3:] == (*SOURCE_SHAPE, "images")
    assert where.video.parts[-3:] == (*SOURCE_SHAPE, "video")


def test_the_page_filename_is_the_one_thing_that_is_not_the_same():
    # ⛔ Measured 2026-09-09: the extraction source's `study/` tree holds 1,290
    # unit pages named `index.html` and 0 named `*.unit.html`. §5 rules that
    # every generated page carries a real name, because a scan reads names.
    # So one file per unit is renamed by a migration and nothing else moves —
    # and the task document's "byte-identically" is true of the directories
    # and false of that one filename.
    where = TREE.unit(Address.of("basics", "16-streams-api"), 7, "Streams")
    assert where.page.name != "index.html"
    assert where.page.name.endswith(".unit.html")


def test_the_media_href_is_the_plain_one_the_extraction_source_writes():
    # ⚠️ `audio/<clip>.mp3` — which is what made moving 11.7 GiB out of git a
    # script rather than a re-render of 1,290 pages.
    where = TREE.unit(Address.of("basics", "16-streams-api"), 7, "Streams")
    assert where.href("audio", "07.mp3") == "audio/07.mp3"


@pytest.mark.parametrize(
    "segments", [("depth-one",), ("basics", "01-x"), ("a", "b", "c"), ("a", "b", "c", "d")]
)
def test_every_depth_places_correctly(segments):
    # ⭐ Depth 1 is the common case — two of the four designed shapes — and it
    # is not a reduced depth 2.
    address = Address.of(*segments)
    where = TREE.unit(address, 1, "A unit")
    assert where.page.parts[1 : 1 + len(segments)] == segments


def test_a_container_page_sits_in_the_directory_that_spells_its_address():
    page = TREE.container(Address.of("basics", "16-streams-api"), ("Basics", "Streams API")).page
    assert page == PurePosixPath(
        GENERATED_ROOT, "basics", "16-streams-api", "streams-api.section.html"
    )


def test_the_profile_needs_no_origin():
    # ⚠️ Which is what makes it the profile for material with no source layout
    # worth preserving. An origin is accepted and ignored.
    address = Address.of("depth-one")
    assert TREE.unit(address, 1, "A") == TREE.unit(address, 1, "A", origin="depth-one/01.md")
    assert TREE.container(address, ("D",)) == TREE.container(address, ("D",), origin="x/y.md")


def test_placing_the_same_unit_twice_gives_the_same_paths():
    # ⛔ R10.
    address = Address.of("basics", "01-x")
    assert TREE.unit(address, 3, "A unit") == TREE.unit(address, 3, "A unit")


def test_the_profile_declares_its_name_and_what_it_does():
    assert TreeProfile.name == "tree"
    assert "one generated root" in TreeProfile.describes


def test_the_media_globs_are_scoped_under_the_generated_root_by_where_they_live():
    # ⛔ Every media kind's directory name — `audio` first — is a word a real
    # repository uses for its own material; an unanchored `audio/` in the root
    # ignore file would tell git to ignore its own recordings. ⭐ W242: the lines
    # live in `.studyforge/.gitignore`, so git applies them below it and nowhere
    # else — the file's place is the anchor.
    lines = TREE.media_ignore_lines()
    assert lines
    assert all(not line.startswith("/") and line.endswith("/") for line in lines)
    assert TREE.ignore_home().parts == (GENERATED_ROOT, ".gitignore")


def test_there_is_one_media_glob_per_media_kind():
    from studyforge.corpus.placement import UNIT_MEDIA_DIRNAMES

    lines = TREE.media_ignore_lines()
    assert len(lines) == len(UNIT_MEDIA_DIRNAMES)
    for kind in UNIT_MEDIA_DIRNAMES:
        assert any(f"/{kind}/" in line for line in lines)
