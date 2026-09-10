"""Mirror of `src/studyforge/describe.py` (R12) — Ruling 10's one describer."""

from __future__ import annotations

import pytest

from studyforge.describe import SAFE_TO_QUOTE, describe

#: ⛔ Synthetic, and it has to be. A fixture carrying this machine's real home
#: path is the exact violation these tests exist to prevent (R7).
POISON = "/" + "home/example/project/notes"


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (None, "nothing"),
        (3, "3"),
        (0, "0"),
        (True, "True"),
        (False, "False"),
        ("anything at all", "a str"),
        (3.5, "a float"),
        (["a"], "a list"),
        (("a",), "a tuple"),
        ({"a": 1}, "a dict"),
        (object(), "an object"),
        (set(), "a set"),
    ],
)
def test_describe_names_the_type_and_quotes_only_numbers(value, expected):
    assert describe(value) == expected


def test_the_article_agrees_with_the_type_name():
    # ⚠️ Cosmetic, and it is here because the extraction had to preserve it:
    # the copy this module replaced computed the article with a `replace("  ",
    # " ")` on a doubled space, which is the kind of line a rewrite silently
    # changes.
    assert describe(object()) == "an object"
    assert describe(3.5) == "a float"


@pytest.mark.parametrize(
    "carrier",
    [
        POISON,
        [POISON],
        {"origin": POISON},
        (POISON, POISON),
        {POISON},
    ],
)
def test_nothing_that_carries_a_path_is_reproduced(carrier):
    # ⛔ Rubric §1f, at the source. Every shape a decoded JSON document can
    # take, carrying a path in the position a refusal would have quoted.
    assert POISON not in describe(carrier)
    assert "example" not in describe(carrier)


def test_a_string_is_never_safe_to_quote():
    # ⛔ The one widening that would undo the module. `str` in this tuple is
    # the whole defect Ruling 10 and Ruling 14 exist to remove, so it is
    # asserted rather than left to review.
    assert str not in SAFE_TO_QUOTE
    assert SAFE_TO_QUOTE == (int, bool)


def test_the_check_is_not_vacuous():
    # ⭐ Ruling 11: watch the assertion fail without the mechanism. A describer
    # that returned `repr(value)` would pass every "names the type" test above
    # for `None` and for integers, and fail only here.
    assert repr(POISON) != describe(POISON)


def test_the_unit_package_re_exports_rather_than_re_implements():
    # ⛔ Ruling 10's point, asserted rather than trusted: `unit.errors` used to
    # carry the third copy of this rule. It now carries the same object, which
    # is a claim a later edit cannot quietly break.
    from studyforge.unit import errors

    assert errors.describe is describe
    assert errors.SAFE_TO_QUOTE is SAFE_TO_QUOTE
