"""Mirror of `src/studyforge/render/index/placement.py` (R12).

⭐ **Every href the one index page writes**, and the two shapes it may never be.
"""

from __future__ import annotations

from pathlib import PurePosixPath

import pytest

from studyforge.corpus.placement import (
    ROOT_INDEX_FILENAME,
    CorpusLocations,
    PlacementError,
    profile_for,
    registered,
)
from studyforge.render.index import Placement
from studyforge.render.pageassets import SCRIPT_NAME, STYLESHEET_NAME
from tests.studyforge.render.index.indexes import A_HOME_PATH


def a_placement() -> Placement:
    return Placement(shared=profile_for(registered()[0]).corpus())


def test_the_two_shared_assets_are_addressed_relative_to_the_index():
    where = a_placement()
    assert where.stylesheet().endswith(STYLESHEET_NAME)
    assert where.script().endswith(SCRIPT_NAME)
    assert not where.stylesheet().startswith("/")


def test_every_registered_profile_puts_the_index_in_the_same_place():
    # ⭐ `Profile.corpus()` is the same under every profile, which is why this
    # page needs no profile at all — stated in the module and asserted here so a
    # third profile that broke it would say so.
    assert len({profile_for(name).corpus() for name in registered()}) == 1
    assert profile_for(registered()[0]).corpus().root_index == PurePosixPath(ROOT_INDEX_FILENAME)


def test_a_unit_page_is_addressed_from_the_index_and_never_composed():
    where = a_placement()
    assert where.unit(PurePosixPath("a/b/one.unit.html")) == "a/b/one.unit.html"
    assert where.unit(PurePosixPath(".studyforge/a/units/unit-01/one.unit.html")) == (
        ".studyforge/a/units/unit-01/one.unit.html"
    )


def test_the_index_sits_at_the_root_so_no_href_it_writes_climbs():
    # ⚠️ The one page where an off-by-one in the arithmetic looks most like a
    # plain filename, which is why the acceptance resolves every href rather
    # than spelling it.
    where = a_placement()
    assert ".." not in where.unit(PurePosixPath("a/b/one.unit.html"))
    assert ".." not in where.stylesheet()


def test_an_absolute_path_on_either_side_is_refused():
    # ⛔ R7 and R8 in one: an absolute path carries a home directory, and an
    # href built from it breaks the moment the page is opened from a file.
    where = a_placement()
    with pytest.raises(PlacementError):
        where.unit(PurePosixPath(A_HOME_PATH))
    rooted = Placement(
        shared=CorpusLocations(
            root_index=PurePosixPath("/index.html"),
            assets=PurePosixPath("assets"),
            archive=PurePosixPath("archive"),
            site_cache=PurePosixPath("site.json"),
        )
    )
    with pytest.raises(PlacementError):
        rooted.stylesheet()


def test_the_refusal_never_reproduces_the_offending_path():
    where = a_placement()
    with pytest.raises(PlacementError) as refused:
        where.unit(PurePosixPath(A_HOME_PATH))
    assert "jane" not in str(refused.value)
