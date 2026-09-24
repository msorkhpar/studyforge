"""Mirror of `src/studyforge/address/slug.py` (R12)."""

from __future__ import annotations

import pytest

from studyforge.address import AddressError, is_slug, require_slug, slugify
from studyforge.address.slug import SLUG_PERMITTED, SLUG_PERMITTED_DESCRIBED, slug_fault

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
    # ⛔ The package's acceptance: a title passed where a slug is required raises.
    # ⚠️ And the message has to be actionable — "invalid" would send the
    # reader to the wrong place, because the value is not malformed, it is
    # the wrong KIND of string.
    #
    # ⛔ The message never contains "Getting Started".
    # Echoing it would be an R7 defect: the branch fires BECAUSE the value is
    # not a slug, which is exactly when it may be an absolute path. What the
    # refusal says instead is below, and it is more actionable than an echo.
    with pytest.raises(AddressError) as raised:
        require_slug("Getting Started", "address segment 1 of 2")
    message = str(raised.value)
    assert "address segment 1 of 2" in message
    assert "Getting Started" not in message
    assert "character 1" in message
    assert SLUG_PERMITTED_DESCRIBED in message
    assert "did you pass a title" in message


def test_the_diagnosis_survives_the_removal_of_the_echo():
    # ⭐ The refusal keeps its diagnosis while it drops the value. A refusal
    # that says nothing is a different defect from one that says too much,
    # and both are avoided at once: "did you pass a title?" is the most
    # useful sentence in this module.
    for title in ["Getting Started", "Введение в потоки", "Café Décor"]:
        with pytest.raises(AddressError) as raised:
            require_slug(title, "segment")
        assert "did you pass a title" in str(raised.value)
        assert "slugify()" in str(raised.value)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("Getting Started", "whose character 1 is outside"),
        ("basics 2", "whose character 7 is outside"),
        ("café", "whose character 4 is outside"),
        ("-lead", "which begins or ends with a hyphen"),
        ("trail-", "which begins or ends with a hyphen"),
        ("a--b", "whose hyphens are doubled"),
    ],
)
def test_slug_fault_names_the_class_and_the_position(value, expected):
    assert not is_slug(value)
    assert expected in slug_fault(value)


def test_slug_fault_is_total_over_every_non_slug_it_can_meet():
    # ⭐ Watch the claim fail without the mechanism, applied to a describer:
    # the three branches are claimed to be exhaustive over non-slugs, so the
    # claim is exercised rather than asserted. Any string of permitted
    # characters that is not a slug must be explained by one of them, and no
    # explanation may reproduce the string.
    alphabet = "ab-0"
    for length in range(1, 5):
        values = [""]
        for _ in range(length):
            values = [prefix + character for prefix in values for character in alphabet]
        for value in values:
            if is_slug(value):
                continue
            fault = slug_fault(value)
            assert fault.startswith(("whose", "which")), value
            assert value not in fault


def test_the_permitted_set_is_derived_and_pinned():
    # ⛔ A permitted set (R8): the class is asked of `is_slug`, never re-typed — and the
    # resulting set is pinned literally, so widening `is_slug` is a decision
    # somebody makes rather than one that arrives.
    assert "".join(sorted(SLUG_PERMITTED)) == "-0123456789abcdefghijklmnopqrstuvwxyz"


def test_require_slug_never_slugifies_for_you():
    # The whole point of the function. Accepting a title here would make the
    # mistake silent, and it would surface as a link nobody can follow.
    with pytest.raises(AddressError):
        require_slug(slugify("Getting Started").upper(), "segment")


@pytest.mark.parametrize("value", ["", None, 7, ["basics"]])
def test_require_slug_refuses_a_non_string(value):
    with pytest.raises(AddressError, match="non-empty str"):
        require_slug(value, "segment")
