"""Mirror of `src/studyforge/render/container/placement.py` (R12).

⭐ Two hrefs and one invariant: **relative to the page**, under every profile —
and the assertion the module's docstring exists for, that a container page's
asset href is not a unit page's.
"""

from __future__ import annotations

from pathlib import PurePosixPath

import pytest

from studyforge.address import Address
from studyforge.corpus.placement import (
    ContainerLocations,
    CorpusLocations,
    PlacementError,
    profile_for,
)
from studyforge.render.container import Placement
from studyforge.render.page import Placement as UnitPlacement
from studyforge.render.pageassets import SCRIPT_NAME, STYLESHEET_NAME

ADDRESS = Address(("basics", "01-getting-started"))


def a_placement(page: str) -> Placement:
    """A placement for a container page at `page`, with no corpus behind it.

    ⭐ Built from `ContainerLocations` directly rather than from a profile, so a
    test of the renderer cannot fail because a placement profile changed its
    shape — the profiles have their own tests, and this is not one of them.
    """
    return Placement(
        corpus="demo",
        container=ContainerLocations(page=PurePosixPath(page)),
        shared=CorpusLocations(
            root_index=PurePosixPath("index.html"),
            assets=PurePosixPath(".studyforge/assets"),
            archive=PurePosixPath(".studyforge/archive"),
            site_cache=PurePosixPath(".studyforge/site.json"),
        ),
    )


def test_the_stylesheet_and_script_are_relative_to_the_page():
    where = a_placement("basics/01-getting-started/getting-started.section.html")
    assert where.stylesheet() == f"../../.studyforge/assets/{STYLESHEET_NAME}"
    assert where.script() == f"../../.studyforge/assets/{SCRIPT_NAME}"


def test_a_page_at_the_root_needs_no_steps_up():
    where = a_placement("one.section.html")
    assert where.stylesheet() == f".studyforge/assets/{STYLESHEET_NAME}"


def test_neither_href_is_ever_rooted_or_absolute():
    # ⛔ R8's floor and R7 together: a rooted href resolves to the filesystem
    # root over `file://`, and an absolute one carries a home directory.
    where = a_placement("a/b/c/deep.section.html")
    for href in (where.stylesheet(), where.script()):
        assert not href.startswith("/")
        assert not PurePosixPath(href).is_absolute()


def test_an_absolute_page_path_is_refused_rather_than_joined():
    where = a_placement("/" + "home/example/site/x.section.html")
    with pytest.raises(PlacementError):
        where.stylesheet()


def test_the_refusal_does_not_reproduce_the_absolute_path():
    poison = "/" + "home/example/material/private-corpus/x.section.html"
    with pytest.raises(PlacementError) as raised:
        a_placement(poison).stylesheet()
    assert poison not in str(raised.value)


#: ⛔ Whether a container page reaches the shared assets the way its units do —
#: **declared per profile, because the answer differs and both answers are
#: right.** Under `tree` the units sit two directories below their container's
#: page (`units/unit-NN/`); under `sibling` every artifact of a container shares
#: one directory, so the two hrefs are the same string.
#:
#: ⚠️ Written down rather than derived, so a profile that changed its shape
#: fails this row instead of quietly agreeing with whatever it now does.
SAME_AS_ITS_UNITS = {"tree": False, "sibling": True}


@pytest.mark.parametrize("profile_name", sorted(SAME_AS_ITS_UNITS))
def test_a_container_page_reaches_the_assets_from_where_it_actually_sits(profile_name):
    # ⭐ The module docstring's point, and the measurement that corrected it: a
    # container page is at or ABOVE its units, never below, so it needs no more
    # `../` steps than they do — and under `tree` it needs strictly fewer. A
    # renderer that assumed a unit page's href would load nothing there, render
    # every word, and be unstyled with no error anywhere.
    profile = profile_for(profile_name)
    origin = "basics/01-getting-started/README.md"
    shared = profile.corpus()
    container_where = Placement(
        corpus="demo",
        container=profile.container(ADDRESS, ("Basics", "Getting Started"), origin=origin),
        shared=shared,
    )
    unit_where = UnitPlacement(
        corpus="demo",
        unit=profile.unit(ADDRESS, 1, "Your first class", origin=origin),
        shared=shared,
    )
    assert container_where.stylesheet().count("../") <= unit_where.stylesheet().count("../")
    same = container_where.stylesheet() == unit_where.stylesheet()
    assert same is SAME_AS_ITS_UNITS[profile_name]
