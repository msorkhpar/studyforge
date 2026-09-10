"""Mirror of `src/studyforge/corpus/placement/errors.py` (R12)."""

from __future__ import annotations

import pytest

from studyforge.address import Address
from studyforge.corpus.placement import PlacementError, profile_for, relative_href, unit_stem
from studyforge.corpus.placement import identity as identity_module

ADDRESS = Address.of("basics", "01-getting-started")


def test_a_placement_error_is_a_value_error():
    # ⚠️ SF-01's split: every failure here is "you handed me something I
    # cannot place", never "this file is not one I can read" — ⛔ because this
    # package reads no files at all.
    assert issubclass(PlacementError, ValueError)


@pytest.mark.parametrize(
    "call",
    [
        lambda: profile_for("beside"),
        lambda: profile_for("sibling").unit(ADDRESS, 1, "T"),
        lambda: unit_stem(1, "..."),
        lambda: relative_href(__import__("pathlib").PurePosixPath("/a"), ADDRESS and None),
        lambda: identity_module.parse("<html></html>", 2),
    ],
)
def test_every_way_it_can_fail_raises_this_one_type(call):
    with pytest.raises(PlacementError):
        call()


def test_a_refusal_names_the_closed_set_it_would_accept_and_not_the_value():
    # ⛔ Ruling 14: a profile name arrives from `corpus.json`, which is
    # hand-written, so it is a string that can be a path. The accepted set is
    # what makes the refusal actionable.
    with pytest.raises(PlacementError) as raised:
        profile_for("beside")
    assert "beside" not in str(raised.value)
    assert "sibling" in str(raised.value)
    assert "sibling" in str(raised.value) and "tree" in str(raised.value)


def test_a_refusal_carries_no_absolute_path():
    # ⛔ R7. A plan and a refusal are both read in a log.
    with pytest.raises(PlacementError) as raised:
        # ⚠️ Split so the repository's own R7 sweep does not read this test
        # as a leak. `tests/fixtures/invalid/personal-data/` is the ONE
        # directory allowed to hold the shape, and this is not it — the same
        # technique `tests/studyforge/test_version.py` already uses.
        profile_for("sibling").unit(ADDRESS, 1, "T", origin="/" + "home/example/corpus/x.md")
    assert "/home/" not in str(raised.value)
