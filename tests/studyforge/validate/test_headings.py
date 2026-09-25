"""The parser-independent heading scan, and the region a section bounds.

⛔ **Every expectation here is a literal.** The module under test owns a regex
and a bound; a test that built its expected depth or its expected count out of
the module's own constants would move with them and prove only
self-consistency.
"""

import ast

import pytest

from studyforge.validate.headings import Heading, count_headings, headings, region
from tests.support import repository_root

#: ⭐ **The shape the ruling was written from**, in miniature: three units that
#: are regions of one file, each with a subsection of its own, plus a fourth
#: heading at the file's own depth that closes the last region.
SHARED = """# Test cases

Preamble.

## 1. Cardholder enrolment

Prose.

### 1.1 Happy path

More.

## 2. Balance enquiry

Prose.

### 2.1 Happy path

More.

### 2.2 Timeout

More.

## 3. Card issuance

Prose.

### 3.1 Happy path

More.

## Appendix

Not a unit.
"""


def test_a_heading_carries_its_depth_and_its_text():
    assert headings("# One\n\n## Two\n") == [Heading(1, "One"), Heading(2, "Two")]


def test_a_heading_with_no_text_is_still_a_heading():
    assert headings("###\n") == [Heading(3, "")]


def test_the_hashes_and_the_surrounding_whitespace_are_not_the_text():
    assert headings("   ##   Card issuance   \n") == [Heading(2, "Card issuance")]


def test_a_closing_hash_run_stays_in_the_text_and_that_is_deliberate():
    # ⛔ Recorded rather than stripped. Stripping it would be this module
    # holding an opinion about a *rendering* convention, which is exactly the
    # coupling a heading was chosen to avoid. A corpus that writes the section
    # differently from the file gets `occurrences == 0`, which is loud.
    assert headings("## Card issuance ##\n") == [Heading(2, "Card issuance ##")]


def test_a_hash_inside_a_fence_is_not_a_heading():
    assert headings("# One\n\n```python\n# not a heading\n```\n") == [Heading(1, "One")]


#: ⛔ Measured on a real course, in miniature: an item's fence opener
#: written four spaces in under `1. `, its body and closer three in. CommonMark
#: reads the opener one space into the item, so the fence holds the `#` comment
#: and the heading after the list is a heading. The counts are CommonMark's,
#: taken by hand, and were checked against a CommonMark parser.
ITEM_FENCE = """# Returning several values

1. Return an array:
    ```java
   # not a heading
   int[] pair() { return new int[]{1, 2}; }
   ```

2. Return an object:
   ```java
   # still not a heading
   ```

## Key points

Done.
"""


def test_a_fence_opened_four_spaces_in_under_an_item_is_that_items_fence():
    assert headings(ITEM_FENCE) == [
        Heading(1, "Returning several values"),
        Heading(2, "Key points"),
    ]


@pytest.mark.parametrize(
    ("text", "count"),
    [
        # ⭐ The same fence at the top level is indented code: its `#` line is a heading.
        ("    ```\n# a heading\n", 1),
        # ⭐ A nested item's fence, measured from the nested item.
        ("- a\n  - b\n      ```\n      # comment\n      ```\n# after\n", 1),
        # ⛔ A line left of the item ends the item and its fence with it.
        ("1. a\n   ```\n# heading\n", 1),
        # ⭐ A blank line does not close the item the fence opens in.
        ("1. a\n\n    ```\n    # comment\n    ```\n", 0),
        # ⭐ A lazy line keeps the item open, so the next indented fence is still its own.
        ("1. a\nlazy\n    ```\n    # comment\n    ```\n", 0),
        # ⛔ A thematic break is not a list marker.
        ("- - -\n    ```\n# heading\n", 1),
        # ⭐ A tilde fence is closed only by tildes, measured from the item as well.
        ("- a\n    ~~~\n  # comment\n  ```\n  ~~~\n# after\n", 1),
    ],
)
def test_a_list_item_measures_its_fences_as_commonmark_does(text, count):
    assert count_headings(text) == count


def test_the_count_is_the_length_of_the_scan():
    assert count_headings(SHARED) == 9


# --------------------------------------------------------------------------
# ⛔ The region ends at the next heading of the same or shallower depth
# --------------------------------------------------------------------------


def test_a_region_holds_its_own_heading_and_its_subsections():
    found = region(SHARED, "2. Balance enquiry")
    assert (found.occurrences, found.headings) == (1, 3)


def test_the_region_does_not_end_at_the_first_deeper_heading():
    # ⛔ **The clause that would be wrong the other way.** Ending at the next
    # heading of *any* depth gives 1 here, and every unit with a subsection
    # short-reads.
    assert region(SHARED, "1. Cardholder enrolment").headings == 2


def test_a_region_ends_at_the_next_heading_of_the_same_depth():
    assert region(SHARED, "3. Card issuance").headings == 2


def test_a_region_ends_at_a_shallower_heading_too():
    text = "## A\n\n### A.1\n\n# Back to the top\n\n## B\n"
    assert region(text, "A").headings == 2


def test_the_last_region_in_a_file_runs_to_the_end():
    assert region(SHARED, "Appendix").headings == 1


def test_the_regions_of_one_file_are_disjoint_and_their_sum_is_not_the_file():
    # ⭐ **The finding, arithmetically.** Three units sharing one path are
    # three comparisons against 2, 3 and 2 — never three against 9.
    counts = [region(SHARED, s).headings for s in ("1. Cardholder", "2. Balance", "3. Card")]
    assert counts == [0, 0, 0]  # a prefix is not the exact text
    exact = [
        region(SHARED, s).headings
        for s in ("1. Cardholder enrolment", "2. Balance enquiry", "3. Card issuance")
    ]
    assert exact == [2, 3, 2]
    assert sum(exact) != count_headings(SHARED)


def test_a_heading_inside_a_fence_cannot_open_a_region():
    text = "# One\n\n```\n## Two\n```\n"
    assert region(text, "Two").occurrences == 0


# --------------------------------------------------------------------------
# ⛔ exactly once, or the caller refuses
# --------------------------------------------------------------------------


def test_a_section_the_file_does_not_carry_is_reported_as_zero():
    found = region(SHARED, "4. Reversal")
    assert (found.occurrences, found.headings) == (0, 0)


def test_a_section_carried_twice_is_reported_as_two_and_not_resolved():
    # ⚠️ `1.1 Happy path` is unique; the bare `Happy path` shape is what a
    # real file repeats, and picking the first is sixteen silent short reads.
    text = "## A\n\n### Happy path\n\n## B\n\n### Happy path\n"
    found = region(text, "Happy path")
    assert (found.occurrences, found.headings) == (2, 0)


@pytest.mark.parametrize("section", ["2. Balance enquiry", "Appendix"])
def test_the_section_is_carried_back_on_the_result(section):
    assert region(SHARED, section).section == section


# --------------------------------------------------------------------------
# ⛔ the independence the whole check rests on
# --------------------------------------------------------------------------


def test_the_scan_does_not_come_from_the_markdown_reader():
    # ⛔ **The assertion this module exists under.** `check_completeness` is
    # the check that disagrees with the parser; a bound taken from the parser
    # would make the disagreement impossible and the suite would stay green.
    source = (repository_root() / "src/studyforge/validate/headings.py").read_text("utf-8")
    tree = ast.parse(source)
    imported = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module and "markdown" in node.module
    }
    assert imported == set(), f"the region bound comes from the reader: {imported}"
    assert {node.names[0].name for node in ast.walk(tree) if isinstance(node, ast.Import)} == {"re"}


def test_the_bound_needs_no_slug_and_no_line_number():
    # ⛔ An anchor would couple the manifest to a renderer's slug rules and a
    # line range to a file's byte layout. Neither word appears in the module.
    source = (repository_root() / "src/studyforge/validate/headings.py").read_text("utf-8")
    body = source.split('"""', 2)[2]
    assert "slug" not in body
    assert "lineno" not in body
