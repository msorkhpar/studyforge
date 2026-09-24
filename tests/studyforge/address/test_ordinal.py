"""Mirror of `src/studyforge/address/ordinal.py` (R12)."""

from __future__ import annotations

import pytest

from studyforge.address import FIRST_ORDINAL, AddressError, require_ordinal, unit_name


@pytest.mark.parametrize(
    "ordinal,expected",
    [(1, "unit-01"), (7, "unit-07"), (9, "unit-09"), (10, "unit-10"), (99, "unit-99")],
)
def test_unit_name_pads_to_two_digits(ordinal, expected):
    assert unit_name(ordinal) == expected


def test_padding_makes_a_plain_sort_agree_with_a_numeric_one():
    # ⭐ This is what the padding is FOR. Unpadded, `unit-10` sorts before
    # `unit-2` and a contents listing comes out in an order nobody chose —
    # and every ordering in this project is meant to derive from a declared
    # ordinal rather than from however a filesystem enumerates (R10).
    ordinals = [1, 2, 9, 10, 11, 20]
    names = [unit_name(n) for n in ordinals]
    assert sorted(names) == names


def test_a_hundredth_unit_widens_rather_than_truncating():
    # ⚠️ No source in scope has one, but truncating would COLLIDE — `unit-00`
    # for both 100 and nothing — and a format that silently collides is worse
    # than one that grows a digit.
    assert unit_name(100) == "unit-100"
    assert unit_name(100) != unit_name(10)


def test_ordinals_count_from_one():
    assert FIRST_ORDINAL == 1
    assert require_ordinal(1) == 1
    with pytest.raises(AddressError, match="1 or greater"):
        require_ordinal(0)


@pytest.mark.parametrize("value", [0, -1, -99])
def test_require_ordinal_refuses_a_non_positive_ordinal(value):
    # §6 requires unit ordinals contiguous from 1, so a zeroth unit is an
    # off-by-one upstream and is refused here rather than filed.
    with pytest.raises(AddressError):
        require_ordinal(value)


@pytest.mark.parametrize("value", ["1", 1.0, None, [1], ()])
def test_require_ordinal_refuses_a_non_int(value):
    with pytest.raises(AddressError, match="must be an int"):
        require_ordinal(value)


@pytest.mark.parametrize("value", [True, False])
def test_a_bool_is_not_an_ordinal_even_though_python_says_it_is_an_int(value):
    # ⛔ `True` would otherwise be accepted as unit 1 and format as `unit-01`,
    # filing a whole unit's material under a flag somebody passed by mistake.
    with pytest.raises(AddressError, match="must be an int"):
        require_ordinal(value)


def test_the_message_names_the_field_and_the_type_but_not_the_value():
    # ⛔ A refusal never echoes the value (R7): the type branch fires on
    # whatever a caller passed where an
    # ordinal was wanted — including a path — so it names the field and the
    # TYPE, never the payload.
    with pytest.raises(AddressError) as raised:
        require_ordinal("3", "declared practice count")
    assert "declared practice count" in str(raised.value)
    assert "a str" in str(raised.value)
    assert "'3'" not in str(raised.value)


def test_an_out_of_range_ordinal_is_still_quoted():
    # ⭐ Not an inconsistency. By this branch the value is an `int`, which is
    # the one shape that cannot carry an identifier, and a refusal that will
    # not say `got 0` is a refusal nobody can act on.
    with pytest.raises(AddressError) as raised:
        require_ordinal(0)
    assert "got 0" in str(raised.value)


def test_unit_name_refuses_what_require_ordinal_refuses():
    with pytest.raises(AddressError):
        unit_name(0)
