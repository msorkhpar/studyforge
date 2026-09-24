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
    with pytest.raises(TerminalRefused, match="RS-20"):
        Terminal(milestone="M2", evidence=("no graders",), unused=()).checked(plans.index())


def test_a_corpus_finishing_at_an_empty_milestone_still_forgoes_what_runs_after_it():
    # ⛔ the fixture runs `M6` before `M5`, so `RS-20` is forgone at `M6`
    # — which an index comparing ids would have called already reached.
    with pytest.raises(TerminalRefused, match="RS-20"):
        Terminal(milestone="M6", evidence=("no graders",), unused=()).checked(plans.index())


def test_the_refusal_counts_what_is_missing_rather_than_stopping_at_the_first():
    index = plans.index()
    with pytest.raises(TerminalRefused, match="2 capabilities are unaccounted for"):
        Terminal(milestone="M1", evidence=("no graders",), unused=()).checked(index)


def test_naming_a_capability_this_corpus_does_reach_is_refused():
    # ⛔ SUBSET, the other direction: calling RS-01 unused when it lands at M1
    # and the corpus finishes at M2 says nothing about this corpus.
    unused = (
        Unused("RS-20", "nothing here is runnable"),
        Unused("RS-01", "this corpus does not use it"),
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
        Unused("RS-20", "n/a")


def test_a_capability_named_twice_is_refused():
    with pytest.raises(TerminalRefused, match="1 capability is named twice"):
        Terminal(
            milestone="M2",
            evidence=("no graders",),
            unused=(Unused("RS-20", "nothing is runnable"), Unused("RS-20", "still nothing is")),
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


# --- the population narrows to THIS side, and the rest are sayable -----


def sided() -> Terminal:
    """A corpus finishing at M2 over the index that carries a second side."""
    return Terminal(
        milestone="M2",
        evidence=("0 runnable units", "0 graders anywhere in the repository"),
        unused=(Unused("RS-20", "no unit asks the reader to run anything"),),
    )


def test_a_capability_delivered_elsewhere_needs_no_why_and_the_statement_passes():
    # ⛔ THE ROW. `TV-00` lands after M2 and is not this framework's to
    # deliver, so a statement that does not explain it away is complete.
    statement = sided().checked(plans.sided_index())
    assert statement.elsewhere == ("TV-00",)
    assert {item.capability for item in statement.unused} == {"RS-20"}


def test_a_capability_no_document_places_needs_no_why_either():
    assert sided().checked(plans.sided_index()).undeclared == ("TV-01",)


def test_writing_a_why_for_a_capability_delivered_elsewhere_is_refused():
    # ⛔ The false sentence stops being WRITABLE rather than merely
    # discouraged: this corpus may be the very thing that delivers it.
    unused = (
        Unused("RS-20", "no unit asks the reader to run anything"),
        Unused("TV-00", "this corpus never builds an image"),
    )
    with pytest.raises(TerminalRefused, match="TV-00"):
        Terminal(milestone="M2", evidence=("no graders",), unused=unused).checked(
            plans.sided_index()
        )


def test_writing_a_why_for_an_undeclared_capability_is_refused_too():
    unused = (
        Unused("RS-20", "no unit asks the reader to run anything"),
        Unused("TV-01", "this corpus never reaches the release record"),
    )
    with pytest.raises(TerminalRefused, match="not this framework's to deliver"):
        Terminal(milestone="M2", evidence=("no graders",), unused=unused).checked(
            plans.sided_index()
        )


def test_a_capability_of_this_side_is_still_unaccounted_for_when_it_is_missing():
    # ⛔ The narrowing did not weaken the coverage test: the negative control
    # for every assertion above.
    with pytest.raises(TerminalRefused, match="RS-20"):
        Terminal(milestone="M2", evidence=("no graders",), unused=()).checked(plans.sided_index())


def test_the_statement_renders_the_other_two_populations_named_and_counted():
    document = "\n".join(sided().checked(plans.sided_index()).lines())
    assert "1 more are NOT this framework's to deliver" in document
    assert "1 more declare no path in any document" in document
    assert "  - `TV-00`" in document and "  - `TV-01`" in document


def test_a_statement_over_an_index_with_one_side_renders_neither_extra_section():
    # ⭐ Asserted both ways: where the distinction does not apply, the
    # statement is exactly the statement it always was.
    statement = plans.terminal().checked(plans.index())
    assert statement.elsewhere == () and statement.undeclared == ()
    document = "\n".join(statement.lines())
    assert "NOT this framework's" not in document
    assert "declare no path" not in document


def test_the_checked_statement_is_what_the_plan_carries_and_not_the_one_declared():
    # ⛔ A statement checked and then thrown away would render nothing about
    # either population, which is the defect arriving one call later.
    plan = plans.backlog(terminal=sided()).checked(plans.sided_index())
    assert plan.terminal.elsewhere == ("TV-00",)
    assert "NOT this framework's" in "\n".join(plan.lines())
