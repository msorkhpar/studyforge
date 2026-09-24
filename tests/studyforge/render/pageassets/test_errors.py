"""Mirror of `src/studyforge/render/pageassets/errors.py` (R12)."""

from __future__ import annotations

import pytest

from studyforge.render.pageassets import AssetError, licence_for, text


def test_an_asset_error_is_not_a_value_error():
    # ⚠️ The package split: a *document* error ("this file is not one I
    # can read") subclasses Exception; a *value* error subclasses ValueError.
    # Every failure here is the first kind.
    assert issubclass(AssetError, Exception)
    assert not issubclass(AssetError, ValueError)


@pytest.mark.parametrize(
    "call",
    [
        lambda: text("no-such-part.css"),
        lambda: text("../secrets.css"),
        lambda: licence_for("reading.css"),
    ],
)
def test_every_way_it_can_fail_raises_this_one_type(call):
    with pytest.raises(AssetError):
        call()


def test_a_missing_part_is_loud_rather_than_empty():
    # ⛔ R6. A page rendered without its stylesheet is well-formed, unreadable,
    # and fails nothing.
    with pytest.raises(AssetError, match="cannot read the page asset"):
        text("palette.scss")


def test_a_refusal_carries_no_absolute_path():
    # ⛔ R7: never format an exception
    # object into a message. `OSError` renders with the absolute path it was
    # given, which in a build log is the user's home directory.
    with pytest.raises(AssetError) as raised:
        text("no-such-part.css")
    message = str(raised.value)
    assert "/home/" not in message and "/Users/" not in message
    assert "no-such-part.css" in message


def test_a_name_that_is_not_one_filename_is_refused_before_it_is_read():
    with pytest.raises(AssetError, match="one filename"):
        text("../../pyproject.toml")
