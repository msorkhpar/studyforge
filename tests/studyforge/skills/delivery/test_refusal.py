"""Mirror of `src/studyforge/skills/delivery/refusal.py` (R12)."""

from __future__ import annotations

import pytest

from studyforge.skills.delivery.refusal import PREAMBLE, SEPARATOR, one_or_all


def test_one_reason_is_the_identity_so_nothing_that_was_right_moved():
    # ⭐ The other direction: a refusal with one reason reads as that reason
    # alone, byte for byte.
    assert one_or_all(("a task waits on a task in a later milestone",)) == (
        "a task waits on a task in a later milestone"
    )


def test_several_reasons_are_all_named_and_the_count_comes_first():
    rendered = one_or_all(("first", "second", "third"))
    assert rendered.startswith(PREAMBLE.format(count=3))
    assert rendered.endswith(f"first{SEPARATOR}second{SEPARATOR}third")


def test_no_reason_is_dropped_however_many_there_are():
    reasons = tuple(f"reason {number}" for number in range(40))
    rendered = one_or_all(reasons)
    assert all(reason in rendered for reason in reasons)
    assert rendered.count(SEPARATOR) == len(reasons) - 1


def test_a_refusal_over_no_reasons_is_itself_refused():
    # ⛔ R6: `0 refusals` is a reading from an empty population, and a
    # caller that got here with nothing to say has a bug rather than a finding.
    with pytest.raises(ValueError, match="refuses nothing"):
        one_or_all(())
