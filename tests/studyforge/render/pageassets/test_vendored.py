"""Mirror of `src/studyforge/render/pageassets/vendored.py` (R12)."""

from __future__ import annotations

import pytest

from studyforge.render.pageassets import (
    HEADER_MARKERS,
    VENDORED,
    AssetError,
    header_of,
    is_vendored,
    licence_for,
    licence_names,
    names,
    text,
)


@pytest.mark.parametrize("bundle", sorted(VENDORED))
def test_every_vendored_bundle_is_on_disk(bundle):
    assert bundle in names()


@pytest.mark.parametrize("bundle", sorted(VENDORED))
def test_every_vendored_bundle_ships_its_licence_beside_it(bundle):
    # ⛔ In the same directory. A licence in another tree is one that goes
    # missing the first time the directory is copied.
    licence = licence_for(bundle)
    assert licence in licence_names()
    assert "MIT" in text(licence)


def test_no_licence_sits_there_covering_nothing():
    # The other direction: a licence whose bundle was removed is a claim about
    # code that is no longer shipped.
    covered = set(VENDORED.values())
    assert set(licence_names()) == covered


@pytest.mark.parametrize("bundle", sorted(VENDORED))
@pytest.mark.parametrize("marker", HEADER_MARKERS)
def test_the_header_says_what_it_is_and_how_to_reproduce_it(bundle, marker):
    # ⛔ "Unedited" is only checkable if the file says what it should be equal
    # to. Version, licence, and the exact command that re-vendors it.
    assert marker in header_of(bundle), f"{bundle}'s header does not say {marker!r}"


@pytest.mark.parametrize("bundle", sorted(VENDORED))
def test_the_header_names_the_licence_file_beside_it(bundle):
    assert licence_for(bundle) in header_of(bundle)


def test_the_header_is_read_as_characters_because_a_bundle_is_one_line():
    # ⚠️ A minified bundle is a single enormous line, so "the first five lines"
    # would be the whole file. Proved rather than remembered.
    assert "\n" not in text("plyr.js")[600:5000]


@pytest.mark.parametrize("name", ["reading.css", "palette.css", "copy-code.js"])
def test_a_file_this_project_wrote_is_not_vendored(name):
    assert not is_vendored(name)
    with pytest.raises(AssetError, match="not a vendored bundle"):
        licence_for(name)


def test_the_vendored_set_is_exactly_what_the_headers_claim():
    # ⭐ Both lists derived independently: the mapping above, and the files
    # that actually carry a vendoring header. A bundle added to the directory
    # without being registered fails here.
    claimed = {name for name in names() if "VENDORED, UNMODIFIED" in text(name)[:600]}
    assert claimed == set(VENDORED)
