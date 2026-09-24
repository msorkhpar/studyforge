"""Mirror of `src/studyforge/address/identifier.py` (R12)."""

from __future__ import annotations

import pytest

from studyforge.address import DIGIT_PREFIX, AddressError, identifier, is_slug

#: `(slug, identifier)`. The numbered ones are the Java corpus's real shape —
#: every module there is numbered, so the leading-digit rule runs 45 times in
#: one corpus rather than being a corner case.
CONVERSIONS = [
    ("basics", "basics"),
    ("clean-code", "clean_code"),
    ("01-getting-started", "_01_getting_started"),
    ("16-streams-api", "_16_streams_api"),
    ("9", "_9"),
    ("a", "a"),
]

#: Pairs that a weaker rule collapses. ⛔ Each is a real failure, not a
#: hypothetical: two practice modules named the same thing means one silently
#: overwrites the other.
MUST_NOT_COLLIDE = [
    # Dropping the leading digit — what the rule exists to prevent.
    ("01-basics", "basics"),
    ("16-streams-api", "streams-api"),
    # Prefixing with a letter instead — the inherited rule's own blind spot.
    ("01-a", "c01-a"),
    ("9-records", "c9-records"),
    # Ordinary neighbours.
    ("01-basics", "02-basics"),
    ("1-basics", "01-basics"),
]


@pytest.mark.parametrize("slug,expected", CONVERSIONS)
def test_identifier_converts_as_documented(slug, expected):
    assert identifier(slug) == expected


@pytest.mark.parametrize("slug,expected", CONVERSIONS)
def test_every_conversion_starts_from_a_real_slug(slug, expected):
    # ⚠️ Guards the table itself. A row whose input is not a slug would be
    # asserting behaviour the function is documented never to reach.
    assert is_slug(slug)


@pytest.mark.parametrize("left,right", MUST_NOT_COLLIDE)
def test_two_different_slugs_never_share_an_identifier(left, right):
    # ⛔ The package's acceptance: two slugs differing only by a leading digit yield
    # different identifiers. The `c01-a` rows go further — they are why the
    # prefix is `_` and not a letter.
    assert left != right
    assert identifier(left) != identifier(right)


def test_the_prefix_is_one_no_slug_can_begin_with():
    # ⭐ This is *why* the function is injective, and it is the property to
    # break loudly if `slugify` ever changes: no slug contains an underscore,
    # so no slug can produce an identifier that starts with one, so a prefixed
    # identifier can never equal an unprefixed one.
    assert DIGIT_PREFIX == "_"
    assert not is_slug(DIGIT_PREFIX)
    for slug, _ in CONVERSIONS:
        assert "_" not in slug


def test_identifier_is_injective_over_the_slugs_we_have():
    slugs = [slug for slug, _ in CONVERSIONS]
    slugs += [value for pair in MUST_NOT_COLLIDE for value in pair]
    identifiers = [identifier(slug) for slug in slugs]
    assert len(set(identifiers)) == len(set(slugs))


def test_a_leading_digit_is_prefixed_and_never_dropped():
    assert identifier("01-basics").endswith("01_basics")
    assert identifier("01-basics") != identifier("basics")


@pytest.mark.parametrize("value", ["Getting Started", "has_underscore", "", None, 7])
def test_identifier_refuses_anything_that_is_not_a_slug(value):
    with pytest.raises(AddressError):
        identifier(value)
