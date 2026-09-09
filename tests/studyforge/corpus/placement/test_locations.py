"""Mirror of `src/studyforge/corpus/placement/locations.py` (R12)."""

from __future__ import annotations

from pathlib import PurePosixPath

import pytest

from studyforge.address import Address
from studyforge.corpus.placement import (
    UNIT_MEDIA_DIRNAMES,
    PlacementError,
    profile_for,
    relative_href,
)

ADDRESS = Address.of("basics", "16-streams-api")
ORIGIN = "16-streams-api/README_4.4.1.md"


def unit(profile):
    origin = ORIGIN if profile == "sibling" else None
    return profile_for(profile).unit(ADDRESS, 7, "Introduction to the Streams API", origin=origin)


@pytest.mark.parametrize("profile", ["tree", "sibling"])
def test_every_path_is_relative_to_the_source_root(profile, tmp_path):
    # ⛔ Never absolute: an absolute path in a plan or a page carries the
    # user's home directory (R7), and a corpus that only builds at one
    # location cannot be cloned.
    where = unit(profile)
    for path in (where.page, *where.directories):
        assert not path.is_absolute()
        assert str(tmp_path) not in str(path)


@pytest.mark.parametrize("profile", ["tree", "sibling"])
def test_a_page_addresses_its_own_media_relative_to_itself(profile):
    # ⛔ R8: the page works over `file://` with no server and no rewriting.
    href = unit(profile).href("audio", "07.mp3")
    assert not href.startswith("/")
    assert href.endswith("audio/07.mp3")


def test_the_href_is_asked_for_and_never_composed():
    # ⛔ The rule a renderer must follow. `audio/<clip>.mp3` is the `tree`
    # shape; under `sibling` twenty units share a directory, so the same clip
    # is `<stem>.audio/<clip>.mp3`. The invariant that survives every profile
    # is "relative to the page", not the literal string.
    assert unit("tree").href("audio", "07.mp3") == "audio/07.mp3"
    assert unit("sibling").href("audio", "07.mp3") == (
        "unit-07-introduction-to-the-streams-api.audio/07.mp3"
    )


@pytest.mark.parametrize("kind", UNIT_MEDIA_DIRNAMES)
@pytest.mark.parametrize("profile", ["tree", "sibling"])
def test_every_kind_of_media_has_a_directory_and_an_href(profile, kind):
    where = unit(profile)
    assert where.media_dir(kind) in where.directories
    assert where.href(kind, "x.bin").endswith("x.bin")


@pytest.mark.parametrize("kind", ["sound", "", None, "AUDIO"])
def test_an_unknown_kind_of_media_is_refused_naming_the_ones_there_are(kind):
    with pytest.raises(PlacementError, match="kind of unit media"):
        unit("tree").media_dir(kind)


@pytest.mark.parametrize("filename", ["", "a/b.mp3", None, 7])
def test_a_media_href_names_one_file(filename):
    with pytest.raises(PlacementError, match="names one file"):
        unit("tree").href("audio", filename)


# --- the relative href computation itself ----------------------------------


@pytest.mark.parametrize(
    "page,target,expected",
    [
        ("a/b/page.html", "a/b/audio/x.mp3", "audio/x.mp3"),
        ("a/b/page.html", "a/assets/page.css", "../assets/page.css"),
        ("a/b/page.html", "index.html", "../../index.html"),
        ("page.html", "assets/page.css", "assets/page.css"),
        ("a/page.html", "a/other.html", "other.html"),
        ("a/b/c/page.html", "d/e.css", "../../../d/e.css"),
    ],
)
def test_a_page_addresses_a_target_relative_to_itself(page, target, expected):
    assert relative_href(PurePosixPath(page), PurePosixPath(target)) == expected


def test_an_absolute_path_is_refused_at_either_end():
    # A rooted href works under a server and breaks the moment the page is
    # opened from a file.
    with pytest.raises(PlacementError, match="relative to the source root"):
        relative_href(PurePosixPath("/a/page.html"), PurePosixPath("a/x.css"))
    with pytest.raises(PlacementError, match="relative to the source root"):
        relative_href(PurePosixPath("a/page.html"), PurePosixPath("/a/x.css"))


def test_an_href_never_says_how_the_file_arrived():
    # ⛔ Delivery is orthogonal to placement. The extraction source proved it
    # in reverse: 11.7 GiB of media left git for release assets, the layout on
    # disk did not move, and every page still addressed a clip the same way —
    # which is the only reason that was a script and not a re-render of 1,290
    # pages.
    href = unit("tree").href("audio", "07.mp3")
    for scheme in ("http", "file:", "git", "lfs", "release"):
        assert scheme not in href
