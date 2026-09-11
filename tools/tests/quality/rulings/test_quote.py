"""Mirror of `tools/quality/rulings/quote.py` (R12).

⛔ **The one property that cannot be allowed to fail silently is the window's:**
a cell that cut `Ruling 70` out of Ruling 70's own quote would read as a
perfectly good sentence about something else. ⭐ So it is asserted over a
passage deliberately longer than the limit, with the citation at each end.
"""

from __future__ import annotations

from tools.quality.rulings.quote import ELLIPSIS, QUOTE_LIMIT, cell, passage

#: `(line number, line)` pairs as `prose_lines` returns them: a heading, a
#: wrapped paragraph, a gap, a table row. ⚠️ The gap is a LINE-NUMBER gap, which
#: is what a fenced block leaves behind.
LINES = [
    (1, "## ⛔ A heading"),
    (2, "⭐ **The first line of a paragraph** that continues"),
    (3, "onto a second line and mentions Ruling 7 here."),
    (9, "a line with no neighbours, after a fence"),
    (10, "| a table row | with Ruling 8 in it |"),
]


def test_a_paragraph_is_quoted_whole():
    """⭐ Measured on Rulings 65, 70, 71 and 76: one wrapped line is a fragment."""
    assert passage(LINES, 2) == (
        "⭐ **The first line of a paragraph** that continues onto a second line and "
        "mentions Ruling 7 here."
    )


def test_a_standalone_line_is_its_own_unit():
    """A heading, a table row and a list item are each quoted alone."""
    assert passage(LINES, 0) == "## ⛔ A heading"
    assert passage(LINES, 4) == "| a table row | with Ruling 8 in it |"


def test_a_line_number_gap_ends_the_paragraph():
    """⛔ The line after a fence is not a continuation of the line before it."""
    assert passage(LINES, 3) == "a line with no neighbours, after a fence"


def test_a_short_passage_is_carried_whole_and_unmarked():
    """Nothing is cut, so nothing is marked."""
    assert cell("⛔ Ruling 7 — short enough", 7) == "⛔ Ruling 7 — short enough"


def test_a_long_passage_keeps_the_citation_when_it_sits_at_the_front():
    """The cut is at the end, and it is marked."""
    long = "⛔ Ruling 7 — " + ("x" * (QUOTE_LIMIT * 2))
    quoted = cell(long, 7)
    assert "Ruling 7" in quoted
    assert quoted.endswith(ELLIPSIS)


def test_a_long_passage_keeps_the_citation_when_it_sits_at_the_back():
    """⛔ The reading that must differ: a head-first cut would drop the subject."""
    long = ("x" * (QUOTE_LIMIT * 2)) + " and that is Ruling 7's clause."
    quoted = cell(long, 7)
    assert "Ruling 7" in quoted, "the window is anchored on the citation, not on the start"
    assert quoted.startswith(ELLIPSIS)
    assert len(quoted) <= QUOTE_LIMIT + 2 * (len(ELLIPSIS) + 1)


def test_a_quote_that_opens_mid_sentence_says_so():
    """A paragraph beginning under a list marker is marked at the front too."""
    assert cell("so the clause stands, per Ruling 7.", 7).startswith(ELLIPSIS)


def test_one_ellipsis_and_never_two():
    """The front mark is not applied twice to a window that already carries one."""
    long = ("x" * (QUOTE_LIMIT * 2)) + " per Ruling 7."
    assert not cell(long, 7).startswith(f"{ELLIPSIS} {ELLIPSIS}")


def test_a_pipe_is_escaped_and_nothing_else_is_changed():
    """⚠️ A quoted table row is still a quote, and has to survive being in a table."""
    assert cell("| a | b |", 7) == r"\| a \| b \|"
    assert cell("`code` **bold** *italic* — ⛔", 7) == "`code` **bold** *italic* — ⛔"
