"""Mirror of `src/studyforge/skills/exercises/aspects.py` (R12) — how every aspect ends.

**What it asserts.** `W453`'s accounting, one refusal per rule: an aspect with
neither an exercise nor a reason, one with both, one id twice, one sentence
under two ids (a near-duplicate), a basis that is empty or resolves to nothing
the page carries, and a zero with no reason — ⭐ each beside the positive
control that the same rule accepts a well-formed aspect.

**Depends on.** The module under test.
"""

from __future__ import annotations

import pytest

from studyforge.skills.exercises.aspects import (
    ASPECT_KEYS,
    Aspect,
    AspectError,
    aspect_document,
    require_aspects,
    require_read,
)

#: A written reason, as the user's refinement words a minor aspect's.
MINOR = "incidental detail, not practised"

#: A well-formed aspect: a token, a sentence, a basis and one ending.
GOOD = Aspect("totals", "a basket totals its prices", ("section:Totals",), exercise="total")


def refused(*aspects, nothing_checkable=None) -> str:
    with pytest.raises(AspectError) as refusal:
        require_aspects(aspects, nothing_checkable, "the plan")
    return str(refusal.value)


def test_a_well_formed_aspect_is_accepted_and_held_in_id_order():
    other = Aspect("empty", "an empty basket totals nothing", ("section:Totals",), reason=MINOR)
    held, zero = require_aspects((GOOD, other), None, "the plan")
    assert [a.id for a in held] == ["empty", "totals"] and zero is None


def test_an_aspect_with_neither_an_exercise_nor_a_reason_is_refused():
    assert "checked by no exercise and carries no" in refused(Aspect("x", "x", ("section:T",)))


def test_an_aspect_with_both_an_exercise_and_a_reason_is_refused():
    assert "cannot both be true" in refused(Aspect("x", "x", ("section:T",), "total", MINOR))


def test_one_id_twice_is_refused():
    twin = Aspect("totals", "something else entirely", ("section:Totals",), "total")
    assert "named twice" in refused(GOOD, twin)


def test_a_near_duplicate_is_refused_so_two_exercises_never_check_one_aspect():
    """⭐ The same sentence under two ids, set aside case, spacing and punctuation."""
    again = Aspect("sum", "A basket  totals its prices.", ("section:Totals",), "other")
    assert "say the same thing" in refused(GOOD, again)


@pytest.mark.parametrize("basis", [(), ("",), ["section:Totals"], (1,)])
def test_an_aspect_read_from_nothing_is_refused(basis):
    bad = Aspect("x", "x", basis, "total")
    assert refused(bad)


@pytest.mark.parametrize("says", ["", "   ", None])
def test_an_aspect_that_says_nothing_is_refused(says):
    assert "says nothing" in refused(Aspect("x", says, ("section:T",), "total"))


@pytest.mark.parametrize("reason", ["", "  ", 3])
def test_a_reason_that_is_not_a_sentence_is_refused(reason):
    assert "one sentence" in refused(Aspect("x", "x", ("section:T",), reason=reason))


@pytest.mark.parametrize("token", ["has space", "", "é"])
def test_an_id_or_an_exercise_name_that_is_not_a_token_is_refused(token):
    assert refused(Aspect(token, "x", ("section:T",), "total"))
    assert refused(Aspect("x", "x", ("section:T",), token))


def test_zero_is_legitimate_only_with_its_reason_and_never_beside_an_aspect():
    assert require_aspects((), "the page is a list of links", "the plan") == (
        (),
        "the page is a list of links",
    )
    assert "says nothing about why" in refused()
    assert "says nothing about why" in refused(nothing_checkable="  ")
    assert "cannot both be true" in refused(GOOD, nothing_checkable="nothing here")


def test_a_basis_resolves_to_the_pages_own_entry_or_a_heading_it_carries_once():
    code = Aspect("reads", "a field is read", ("example:p.md:1", "section:Totals"), "field")
    require_read((code,), ("example:p.md:1",), ("Page", "Totals"), "the plan")
    for keys, headings in [((), ("Totals",)), (("example:p.md:1",), ("Totals", "Totals"))]:
        with pytest.raises(AspectError):
            require_read((code,), keys, headings, "the plan")


def test_the_document_writes_every_key_in_order():
    assert tuple(aspect_document(GOOD)) == ASPECT_KEYS
    assert aspect_document(GOOD)["basis"] == ["section:Totals"]
