"""Mirror of `src/studyforge/skills/delivery/terminal.py` (R12)."""

from __future__ import annotations

import pytest

from studyforge.skills.delivery import Terminal, TerminalRefused, Unused
from tests.studyforge.skills.delivery import plans


def test_a_corpus_that_finishes_at_m2_accounts_for_everything_after_it():
    # ⭐ A corpus with no graders is complete here, not short (§7, C5).
    statement = plans.terminal().checked(plans.index())
    assert statement.milestone == "M2"
    assert "will never use" in "\n".join(statement.lines())


def test_a_capability_delivered_later_and_not_accounted_for_is_named():
    # ⛔ COVERAGE, not subset. Naming ten capabilities that exist proves
    # nothing; the claim is about the ones that were not named.
    with pytest.raises(TerminalRefused, match="SF-20"):
        Terminal(milestone="M2", evidence=("no graders",), unused=()).checked(plans.index())


def test_the_refusal_counts_what_is_missing_rather_than_stopping_at_the_first():
    index = plans.index()
    with pytest.raises(TerminalRefused, match="2 capabilities are unaccounted for"):
        Terminal(milestone="M1", evidence=("no graders",), unused=()).checked(index)


def test_naming_a_capability_this_corpus_does_reach_is_refused():
    # ⛔ SUBSET, the other direction: calling SF-01 unused when it lands at M1
    # and the corpus finishes at M2 says nothing about this corpus.
    unused = (
        Unused("SF-20", "nothing here is runnable"),
        Unused("SF-01", "this corpus does not use it"),
    )
    with pytest.raises(TerminalRefused, match="1 named capability is not delivered"):
        Terminal(milestone="M2", evidence=("no graders",), unused=unused).checked(plans.index())


def test_a_terminal_milestone_with_no_evidence_is_a_preference():
    with pytest.raises(TerminalRefused, match="no evidence"):
        Terminal(milestone="M2", evidence=(), unused=())


def test_a_reason_filled_in_to_pass_is_refused():
    # ⛔ A partial table is worse than none, because it looks like the check
    # was done — and so is a full one made of `n/a`.
    with pytest.raises(TerminalRefused, match="is not a reason"):
        Unused("SF-20", "n/a")


def test_a_capability_named_twice_is_refused():
    with pytest.raises(TerminalRefused, match="1 capability is named twice"):
        Terminal(
            milestone="M2",
            evidence=("no graders",),
            unused=(Unused("SF-20", "nothing is runnable"), Unused("SF-20", "still nothing is")),
        )


def test_a_statement_with_no_milestone_states_nothing():
    with pytest.raises(TerminalRefused, match="states nothing"):
        Terminal(milestone="", evidence=("x" * 20,), unused=())


def test_an_unused_capability_with_no_name_is_refused():
    with pytest.raises(TerminalRefused, match="names nothing"):
        Unused("", "nothing here is runnable")


def test_the_table_carries_one_row_per_capability_forgone():
    index = plans.index()
    statement = plans.terminal().checked(index)
    rows = [line for line in statement.lines() if line.startswith("| `")]
    assert len(rows) == len(index.after("M2")) == len(statement.unused)
