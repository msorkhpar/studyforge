"""Mirror of `src/studyforge/skills/exercises/scan.py` (R12).

**What it asserts.** The one thing the framework had no answer to — *which
headings enclose this fenced block?* — and the three properties the ledger's
accounting rests on: the chain is outermost first, a `#` inside a fence is not
a heading, and an unclosed fence is **reported** rather than refused here.

⭐ **Read against `validate.headings` itself where the claim is shared.** The
heading population this scan sees must be the one that module sees, and that is
asserted by comparison rather than by both being believed.
"""

from __future__ import annotations

from studyforge.skills.exercises.scan import scan
from studyforge.validate.headings import headings as raw_headings
from tests.studyforge.skills.exercises.pages import PAGE


def test_the_chain_is_every_enclosing_heading_outermost_first():
    read = scan(PAGE)
    assert [fence.sections for fence in read.fences] == [
        ("Adding up",),
        ("Adding up", "Edge cases"),
        ("Elsewhere",),
    ]


def test_a_heading_of_the_same_depth_closes_the_one_before_it():
    """⛔ Ruling 92's region boundary, read from the other end."""
    read = scan("# One\n\n## Under\n\n# Two\n\n```py\nx\n```\n")
    assert read.fences[0].sections == ("Two",), "a sibling's subsection is not an ancestor"


def test_a_heading_inside_a_fence_is_not_a_heading():
    """⚠️ Fence awareness is the whole difficulty — a `#` in a fence is a comment."""
    read = scan("# Real\n\n```py\n# not a heading\n```\n")
    assert read.headings == ("Real",)
    assert read.fences[0].sections == ("Real",)


def test_the_headings_it_sees_are_the_ones_validate_headings_sees():
    """⭐ The shared claim, asserted by comparison rather than by trusting both."""
    for text in (PAGE, "# A\n\n```\n# B\n```\n\n## C\n", "#nospace\n####### seven\n# real\n"):
        assert scan(text).headings == tuple(heading.text for heading in raw_headings(text)), (
            "the scan and the module it borrows the pattern from disagree"
        )


def test_the_headings_it_sees_keep_their_repeats():
    """⛔ A name a file carries twice is what makes a region ambiguous."""
    assert scan("# Same\n\n## Same\n").headings == ("Same", "Same")


def test_the_language_is_the_fences_own_info_word():
    read = scan("```java\nx\n```\n\n```\ny\n```\n\n```python title=a b\nz\n```\n")
    assert [fence.language for fence in read.fences] == ["java", None, "python"]


def test_the_body_is_the_lines_between_the_markers_and_neither_marker():
    read = scan("```py\nfirst\nsecond\n```\n")
    assert read.fences[0].body == "first\nsecond\n"


def test_a_marker_of_the_other_character_inside_an_open_fence_is_body():
    read = scan("```md\n~~~\nstill inside\n~~~\n```\n")
    assert len(read.fences) == 1
    assert "still inside" in read.fences[0].body


def test_a_tilde_fence_is_a_fence_and_takes_its_own_ordinal():
    read = scan("~~~py\na\n~~~\n\n```py\nb\n```\n")
    assert [fence.ordinal for fence in read.fences] == [1, 2]


def test_an_unclosed_fence_is_reported_and_not_raised():
    """⛔ `Region.occurrences` is the precedent: this module reports, the caller refuses."""
    read = scan("# Open\n\n```py\nno closing marker\n")
    assert read.unclosed is True
    assert read.fences == (), "an unfinished fence is not an example"
    assert scan(PAGE).unclosed is False, "the control: a well-formed page reports False"


def test_a_page_with_no_fence_scans_to_nothing():
    read = scan("# Only prose\n\nNothing fenced at all.\n")
    assert read.fences == () and read.headings == ("Only prose",) and not read.unclosed


def test_the_ordinals_are_one_to_n_in_the_order_the_file_carries_them():
    read = scan(PAGE)
    assert [fence.ordinal for fence in read.fences] == list(range(1, len(read.fences) + 1))
