"""Mirror of `tools/quality/markdown.py` (R12).

⛔ **Every positive here is paired with the mention it is one backtick from.**
That pairing is not a style choice: the whole finding this parser was scoped on
is that the naive walker's hits were **11 of 11 false**, so a suite that only
proved the parser fires would prove the wrong half.

⭐ **The mention corpus is verbatim.** `MEASURED_MENTIONS` holds the real lines
from the real documents, at the sha they were measured on, rather than invented
lookalikes — because the shapes that broke the naive walker are ones nobody
would have thought to invent (a double-backtick span wrapping a single-backtick
one; a regex whose character classes read as a link).

⚠️ **`W148` moved these from `test_pointers.py` with the parser they mirror.**
⛔ The mention assertions were routed through `check_pointers` there, for want
of a parser to address directly; here they address `pointers()` itself, which
is STRICTLY stronger — the old form also passed if the parser found a link and
the link happened to resolve.
"""

from __future__ import annotations

import pytest

from tools.quality.markdown import (
    Pointer,
    heading_slugs,
    pointers,
    prose_lines,
    slug,
    strip_code_spans,
)

MEASURED_MENTIONS = [
    "| markup carrying it (line 310) | `# [Test cases](TestCases.md)` |",
    "in `handoffs/FND-05a.md`, `` `# [Test cases](TestCases.md)` `` quoted in a board",
    "cell, `` `- [1.1. Title](path)` `` in an epic. A repo-wide check that is",
    "`- [1.1. Title](path)`, a handful read `- 1.5. [Title](path)` — the number",
    "way. `SAFE_NAME` is `^[A-Za-z0-9](?:[A-Za-z0-9._-]*[A-Za-z0-9])?$`: no",
    "  in a handoff, `` `# [Test cases](TestCases.md)` `` quoted in a board cell.",
    "`1. [Title](src/1.md)` — the form every top-level entry of all three",
    "| Java-senior | 205 as `- [1.1. Title](x)` | **6 as `- 1.5. [Title](x)`**"
    ", ordinal outside the link |",
    "| all three | `N. [Title](x)`, the ordinal **as** the list marker | — |",
]

#: How many links a fence-aware walker that does **not** strip code spans finds
#: in the corpus above. ⛔ This number is the task's whole justification, so it
#: is asserted rather than described.
NAIVE_HITS = 11


# --- the negative direction: a mention is not a pointer --------------------


def test_the_measured_mentions_are_what_broke_the_naive_walker():
    # ⛔ Watch the naive walker fail on this corpus first. Without this the
    # next assertion is satisfied by a corpus that contains no links at all,
    # which is Ruling 48's defect wearing a passing test.
    import re

    naive = re.compile(r"\[[^\]\n]*\]\(([^)\s]+)\)")
    hits = [match for line in MEASURED_MENTIONS for match in naive.finditer(line)]
    assert len(hits) == NAIVE_HITS


def test_not_one_measured_mention_is_read_as_a_pointer():
    # ⛔ Addressed at the parser, not through a check that would also pass if
    # every mention were read as a link and every link happened to resolve.
    assert pointers("mentions.md", "\n".join(MEASURED_MENTIONS) + "\n") == []


@pytest.mark.parametrize("line", MEASURED_MENTIONS)
def test_each_measured_mention_alone_is_not_a_pointer(line):
    # Parametrised as well as collectively: a failure names the shape.
    assert pointers("one.md", line + "\n") == []


def test_a_fence_hides_a_link_from_the_parser():
    # ⭐ The pair of the above: the parser DOES read the same link out of a fence.
    text = "```\n[gone](nowhere.md)\n```\n\n[found](there.md)\n"
    assert pointers("d.md", text) == [Pointer("d.md", 5, "there.md")]


def test_an_external_target_is_out_of_scope_at_the_parser():
    line = "[a](https://example.invalid/x) [b](mailto:contact@example.com) [c](//host/x)\n"
    assert pointers("d.md", line) == []


# --- slugs and headings ----------------------------------------------------


def test_the_trees_one_real_anchor_slugs_to_its_heading():
    # ⛔ Re-measured: the task was scoped on "zero anchors in the tree" and the
    # tree now carries one. This is that exact pair, and it is the reason the
    # hyphen-run collapse below is a decision rather than an accident.
    heading = "The wave checks — ⛔ **SIX at open, and check 4 AGAIN at close**"
    assert slug(heading) == "the-wave-checks-six-at-open-and-check-4-again-at-close"


@pytest.mark.parametrize(
    ("heading", "expected"),
    [
        ("Simple Heading", "simple-heading"),
        ("**Bold** and `code`", "bold-and-code"),
        ("Trailing punctuation!", "trailing-punctuation"),
        ("A — B", "a-b"),
        ("  Padded  ", "padded"),
        ("R11's ceiling", "r11s-ceiling"),
        ("⛔ leading emoji", "leading-emoji"),
    ],
)
def test_slug_shapes(heading, expected):
    assert slug(heading) == expected


def test_headings_inside_a_fence_are_not_headings():
    # ⚠️ A shell transcript in a fence is full of `#` comments; reading those
    # as headings invents anchors no renderer offers.
    text = "# Real\n\n```bash\n# not a heading\n```\n"
    assert heading_slugs(text) == {"real"}


def test_a_duplicated_heading_takes_a_suffix():
    assert heading_slugs("# Same\n\n# Same\n\n# Same\n") == {"same", "same-1", "same-2"}


def test_a_closed_atx_heading_drops_its_closing_hashes():
    assert heading_slugs("## Closed ##\n") == {"closed"}


# --- the parser's own seam -------------------------------------------------


def test_prose_lines_keeps_real_line_numbers():
    text = "a\n```\nb\n```\nc\n"
    assert prose_lines(text) == [(1, "a"), (5, "c")]


def test_strip_code_spans_preserves_columns():
    line = "x `abc` y"
    stripped = strip_code_spans(line)
    assert len(stripped) == len(line)
    assert stripped == "x       y"


def test_pointers_reports_the_line_it_was_written_on():
    text = "one\ntwo\n[three](a.md)\n"
    assert pointers("doc.md", text) == [Pointer("doc.md", 3, "a.md")]


def test_a_pointer_splits_its_target_into_path_and_anchor():
    assert Pointer("d.md", 1, "a/b.md#sec").path_part == "a/b.md"
    assert Pointer("d.md", 1, "a/b.md#sec").anchor == "sec"
    assert Pointer("d.md", 1, "#sec").path_part == ""
    assert Pointer("d.md", 1, "a/b.md").anchor == ""
