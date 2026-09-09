"""Mirror of `src/studyforge/address/slug.py` (R12)."""

from __future__ import annotations

import pytest

from studyforge.address import AddressError, is_slug, require_slug, slugify

#: `(title, slug)` — the derivations that are load-bearing rather than obvious.
DERIVATIONS = [
    ("Senior Java Engineer", "senior-java-engineer"),
    ("Getting Started with Kotlin", "getting-started-with-kotlin"),
    ("16 Streams API", "16-streams-api"),
    ("Executors & Thread Pools", "executors-thread-pools"),
    ("  leading and trailing  ", "leading-and-trailing"),
    ("Already-A-Slug", "already-a-slug"),
    ("under_scores_become_hyphens", "under-scores-become-hyphens"),
    ("dots.and/slashes", "dots-and-slashes"),
]


@pytest.mark.parametrize("title,expected", DERIVATIONS)
def test_slugify_derives_the_expected_slug(title, expected):
    assert slugify(title) == expected


@pytest.mark.parametrize("title", ["A Beginner's Guide", "A Beginner’s Guide"])
def test_an_apostrophe_is_dropped_rather_than_separated(title):
    # ⛔ Measured, not tasteful. The extraction source serves a lesson at
    # `...-a-beginners-guide`; the derived `...-a-beginner-s-guide` 404s. An
    # apostrophe sits INSIDE a word where every other mark sits BETWEEN words.
    # Both the typewriter and the curly form, because a title copied out of a
    # rendered page carries U+2019 far more often than U+0027.
    assert slugify(title) == "a-beginners-guide"


@pytest.mark.parametrize("text", ["", "   ", "!!!", "---", "—", None])
def test_a_title_with_nothing_sluggable_yields_the_empty_string(text):
    # Returns rather than raises: "this has no slug" is an answer a caller
    # often wants to handle. `require_slug` is where it becomes an error.
    assert slugify(text) == ""


def test_slugify_is_idempotent():
    # ⭐ The property the whole definition rests on: a slug is a fixed point.
    for title, _ in DERIVATIONS:
        once = slugify(title)
        assert slugify(once) == once


@pytest.mark.parametrize("value", ["a", "basics", "01-getting-started", "16-streams-api"])
def test_is_slug_accepts_a_slug(value):
    assert is_slug(value) is True


@pytest.mark.parametrize(
    "value",
    [
        "Senior Java Engineer",  # a title
        "Basics",  # capitals
        "a--b",  # a doubled separator, which slugify collapses
        "-leading",
        "trailing-",
        "has_underscore",
        "has/slash",
        "",
        None,
        7,
        ("basics",),
    ],
)
def test_is_slug_rejects_everything_that_is_not_one(value):
    assert is_slug(value) is False


def test_require_slug_returns_the_value_unchanged():
    assert require_slug("01-getting-started", "segment") == "01-getting-started"


def test_require_slug_refuses_a_title_and_says_so():
    # ⛔ SF-01's acceptance: a title passed where a slug is required raises.
    # ⚠️ And the message has to be actionable — "invalid" would send the
    # reader to the wrong place, because the value is not malformed, it is
    # the wrong KIND of string.
    with pytest.raises(AddressError) as raised:
        require_slug("Getting Started", "address segment 1 of 2")
    message = str(raised.value)
    assert "address segment 1 of 2" in message
    assert "Getting Started" in message
    assert "did you pass a title" in message


def test_require_slug_never_slugifies_for_you():
    # The whole point of the function. Accepting a title here would make the
    # mistake silent, and it would surface as a link nobody can follow.
    with pytest.raises(AddressError):
        require_slug(slugify("Getting Started").upper(), "segment")


@pytest.mark.parametrize("value", ["", None, 7, ["basics"]])
def test_require_slug_refuses_a_non_string(value):
    with pytest.raises(AddressError, match="non-empty str"):
        require_slug(value, "segment")
