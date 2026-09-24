"""What a run found, and — just as loudly — what it could not check.

⭐ The line between a `Finding` and an `Unchecked` is where the design lives.
Every test here is about that line, or about the promise that neither of them
ever disappears from the output.
"""

from studyforge.validate.report import INVALID, OK, Finding, Report, Unchecked


def finding(rule="digest", where="a/b.json", message="does not match"):
    return Finding(rule, where, message)


def unchecked(rule="short-read", where=".", why="the source tree is absent"):
    return Unchecked(rule, where, why)


# --------------------------------------------------------------------------
# one line each, greppable
# --------------------------------------------------------------------------


def test_a_finding_renders_as_where_rule_message():
    assert finding().line() == "a/b.json: [digest] does not match"


def test_an_unchecked_claim_says_it_was_not_checked():
    # ⚠️ The words "not checked" are the whole point: a reader scanning output
    # must not have to know the rule ids to tell a verdict from an absence.
    assert unchecked().line() == ".: [short-read] not checked — the source tree is absent"


def test_the_two_shapes_are_never_confused_for_one_another():
    assert "not checked" not in finding().line()
    assert "not checked" in unchecked().line()


# --------------------------------------------------------------------------
# every failure, never just the first
# --------------------------------------------------------------------------


def test_a_report_drains_every_check_rather_than_stopping_at_the_first():
    # ⛔ An adapter author fixing one problem per run against 166 units is an
    # adapter author who stops using the tool.
    report = Report.of([finding(rule="a"), finding(rule="b"), finding(rule="c")])
    assert len(report.findings) == 3


def test_findings_and_unchecked_claims_are_sorted_into_their_own_halves():
    report = Report.of([finding(), unchecked(), finding(rule="counts")])
    assert len(report.findings) == 2
    assert len(report.unchecked) == 1


def test_an_empty_run_is_valid():
    report = Report.of([])
    assert report.ok
    assert report.exit_code == OK


# --------------------------------------------------------------------------
# an unchecked claim is loud, and it does not fail the run
# --------------------------------------------------------------------------


def test_an_unchecked_claim_does_not_make_an_archive_invalid():
    # ⚠️ It is not a failure and not a silence. An integrator who ships anyway
    # has been *told* which question went unanswered — R6's sibling.
    report = Report.of([unchecked()])
    assert report.ok
    assert report.exit_code == OK


def test_but_it_still_appears_in_the_output():
    assert any("not checked" in line for line in Report.of([unchecked()]).lines())


def test_one_finding_makes_the_whole_archive_invalid():
    report = Report.of([finding()])
    assert not report.ok
    assert report.exit_code == INVALID


# --------------------------------------------------------------------------
# the summary, and the number that is never omitted
# --------------------------------------------------------------------------


def test_the_summary_names_the_unchecked_count_even_when_it_is_zero():
    # ⛔ A number that disappears when it is zero cannot be told from a number
    # nobody wrote — the same argument the archive's `counts` makes.
    assert "0 unchecked claim(s)" in Report.of([finding()]).summary()


def test_the_summary_says_which_verdict_in_words():
    assert Report.of([]).summary().startswith("valid:")
    assert Report.of([finding()]).summary().startswith("NOT valid:")


def test_the_summary_is_always_the_last_line():
    lines = Report.of([finding(), unchecked()]).lines()
    assert lines[-1] == Report.of([finding(), unchecked()]).summary()
    assert len(lines) == 3


def test_findings_are_printed_before_unchecked_claims():
    lines = Report.of([unchecked(), finding()]).lines()
    assert "[digest]" in lines[0]
    assert "not checked" in lines[1]


# --------------------------------------------------------------------------
# `rules` is what a test asserts on, so its order is a contract
# --------------------------------------------------------------------------


def test_rules_lists_each_broken_rule_once_in_the_order_first_seen():
    report = Report.of([finding(rule="b"), finding(rule="a"), finding(rule="b")])
    assert report.rules == ("b", "a")


def test_rules_counts_findings_only():
    # ⚠️ An unchecked claim is not a broken rule, and folding it into `rules`
    # would make every test that asserts `rules == (...)` fail for the one
    # reason that is not a failure.
    assert Report.of([unchecked()]).rules == ()
