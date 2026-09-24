"""Mirror of `src/studyforge/render/page/assets.py` (R12)."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from pathlib import PurePosixPath

import pytest

from studyforge.address import Address
from studyforge.corpus import placement as placement_module
from studyforge.corpus.placement import UNIT_MEDIA_DIRNAMES
from studyforge.render.page import assets
from studyforge.render.page.errors import PageError
from studyforge.render.pageassets import SCRIPT_NAME, STYLESHEET_NAME
from tests.studyforge.render.page.pages import sample_placement


def tree_placement() -> assets.Placement:
    """A real `tree` placement, so the href arithmetic is the shipped one."""
    profile = placement_module.profile_for("tree")
    return assets.Placement(
        corpus="demo",
        unit=profile.unit(Address(("depth-one",)), 2, "A Unit"),
        shared=profile.corpus(),
    )


def test_the_audio_attribute_is_named_once_for_both_sides():
    # ⛔ The page renderer writes none; narration writes them at M3. The spelling is here so
    # the two cannot differ — the same move `identity.py` made ahead of SF-04.
    assert assets.AUDIO_ATTRIBUTE == "data-audio"


def test_the_shared_assets_are_addressed_relative_to_the_page():
    where = tree_placement()
    assert where.stylesheet() == "../../../assets/" + STYLESHEET_NAME
    assert where.script() == "../../../assets/" + SCRIPT_NAME


def test_no_href_is_ever_rooted_or_absolute():
    # ⛔ R8: a rooted href works under a server and breaks the moment the page is
    # opened from a file; an absolute one carries a home directory (R7).
    where = tree_placement()
    for href in (where.stylesheet(), where.script(), where.media("images", "a.png")):
        assert not href.startswith("/")
        assert not href.startswith("~")


def test_the_same_page_addresses_its_own_media_by_the_profile_s_shape():
    where = sample_placement()
    assert where.media("images", "media/diagram.svg") == "images/diagram.svg"
    assert where.media("audio", "x.mp3") == "audio/x.mp3"


def test_a_sibling_placement_gives_a_different_shape_for_the_same_call():
    # ⭐ The invariant that survives every profile is "relative to the page", not
    # the literal string. A renderer that spelled `images/` would be correct
    # under one profile and silently wrong under the other.
    profile = placement_module.profile_for("sibling")
    where = assets.Placement(
        corpus="demo",
        unit=profile.unit(
            Address(("basics", "01-getting-started")),
            1,
            "A Unit",
            origin="basics/01-getting-started/README.md",
        ),
        shared=profile.corpus(),
    )
    assert where.media("images", "a.png") == (
        "images/basics.01-getting-started.unit-01-a-unit/a.png"
    )


def test_only_the_filename_of_a_media_reference_survives():
    assert assets.filename("media/deep/diagram.svg") == "diagram.svg"
    assert assets.filename("diagram.svg") == "diagram.svg"


@pytest.mark.parametrize(
    "source",
    [
        "/absolute/elsewhere/a.png",
        "~/a.png",
        "../outside/a.png",
        "C:/somewhere/a.png",
        "\\\\host\\share\\a.png",
        "",
        "   ",
        None,
        7,
    ],
)
def test_a_media_reference_outside_the_corpus_is_refused(source):
    with pytest.raises(PageError):
        assets.filename(source)


def test_the_refusal_never_quotes_the_reference():
    offending = "/absolute/elsewhere/material/a.png"
    with pytest.raises(PageError) as raised:
        assets.filename(offending)
    assert offending not in str(raised.value)


def test_a_legal_reference_is_the_negative_control():
    assert assets.filename("media/a.png") == "a.png"


@pytest.mark.parametrize("source", ["https://x/y.mp4", "http://x/y.mp4", "scheme://x"])
def test_a_reference_carrying_a_scheme_is_remote(source):
    assert assets.is_remote(source)


@pytest.mark.parametrize("source", ["media/a.mp4", "a.mp4", "", None])
def test_a_reference_with_no_scheme_is_local(source):
    assert not assets.is_remote(source)


def test_a_block_type_maps_to_the_media_directory_the_profile_names():
    assert assets.media_kind("image") == "images"
    assert assets.media_kind("video") == "video"
    assert set(UNIT_MEDIA_DIRNAMES) >= {"images", "video"}


def test_a_block_type_with_no_media_directory_is_refused():
    with pytest.raises(PageError):
        assets.media_kind("para")


def test_a_placement_is_frozen_so_a_page_cannot_move_while_it_renders():
    where = sample_placement()
    with pytest.raises(FrozenInstanceError):
        where.corpus = "other"
    assert where.shared.assets == PurePosixPath("out/assets")
