"""Mirror of `src/studyforge/skills/delivery/terminal.py` (R12)."""

from __future__ import annotations

import pytest

from studyforge.skills.delivery import Terminal, TerminalRefused, Unused
from tests.studyforge.skills.delivery import plans

#: What the shared plan's tasks use: every offered capability but the one that runs code.
USED = frozenset({plans.READ, plans.RENDER})


def test_a_reading_floor_corpus_accounts_for_everything_it_does_not_use():
    # ⭐ A corpus with no graders is complete here, not short (§7, C5).
    statement = plans.terminal().checked(plans.offer(), used=USED)
    assert statement.finishes == "the reading floor"
    assert "will never use" in "\n".join(statement.lines())


def test_an_offered_capability_neither_used_nor_accounted_for_is_named():
    # ⛔ COVERAGE, not subset. Naming ten capabilities that exist proves
    # nothing; the claim is about the ones that were not named.
    with pytest.raises(TerminalRefused, match="tool run"):
        Terminal("the reading floor", ("no graders",), ()).checked(plans.offer(), used=USED)


def test_the_refusal_counts_what_is_missing_rather_than_stopping_at_the_first():
    with pytest.raises(TerminalRefused, match="2 offered capabilities are neither used"):
        Terminal("the reading floor", ("no graders",), ()).checked(
            plans.offer(), used=frozenset({plans.READ})
        )


def test_naming_a_capability_a_task_uses_is_refused():
    # ⛔ SUBSET, one way: calling a used capability unused contradicts the plan.
    unused = (
        Unused(plans.RUN, "nothing here is runnable"),
        Unused(plans.READ, "this corpus does not use it"),
    )
    with pytest.raises(TerminalRefused, match="1 named capability is used by a task"):
        Terminal("the reading floor", ("no graders",), unused).checked(plans.offer(), used=USED)


def test_naming_a_capability_nobody_offers_is_refused_and_its_name_withheld():
    # ⛔ SUBSET, the other way: a capability the framework does not offer says
    # nothing about what this corpus forgoes. The name is caller text.
    unused = (
        Unused(plans.RUN, "nothing here is runnable"),
        Unused("tool slides", "this corpus has no slides at all"),
    )
    with pytest.raises(TerminalRefused) as refused:
        Terminal("the reading floor", ("no graders",), unused).checked(plans.offer(), used=USED)
    assert "1 named capability is not offered" in str(refused.value)
    assert "tool slides" not in str(refused.value)


def test_every_kind_of_refusal_is_named_at_once():
    unused = (
        Unused(plans.READ, "this corpus does not use it"),
        Unused("tool slides", "this corpus has no slides at all"),
    )
    with pytest.raises(TerminalRefused) as refused:
        Terminal("the reading floor", ("no graders",), unused).checked(plans.offer(), used=USED)
    assert str(refused.value).startswith("3 refusals")


def test_a_terminal_statement_with_no_evidence_is_a_preference():
    with pytest.raises(TerminalRefused, match="no evidence"):
        Terminal("the reading floor", (), ())


def test_a_reason_filled_in_to_pass_is_refused():
    # ⛔ A partial table is worse than none, because it looks like the check
    # was done — and so is a full one made of `n/a`.
    with pytest.raises(TerminalRefused, match="is not a reason"):
        Unused(plans.RUN, "n/a")


def test_a_capability_named_twice_is_refused():
    with pytest.raises(TerminalRefused, match="1 capability is named twice"):
        Terminal(
            "the reading floor",
            ("no graders",),
            (Unused(plans.RUN, "nothing is runnable"), Unused(plans.RUN, "still nothing is")),
        )


def test_a_statement_that_says_nowhere_states_nothing():
    with pytest.raises(TerminalRefused, match="states nothing"):
        Terminal("", ("x" * 20,), ())


def test_an_unused_capability_with_no_name_is_refused():
    with pytest.raises(TerminalRefused, match="names nothing"):
        Unused("", "nothing here is runnable")


def test_the_table_carries_one_row_per_capability_forgone():
    offer = plans.offer()
    statement = plans.terminal().checked(offer, used=USED)
    rows = [line for line in statement.lines() if line.startswith("| `")]
    assert len(rows) == len(offer.ids - USED) == len(statement.unused)
