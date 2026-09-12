"""Mirror of `tools/quality/handoffs/sections.py` (R12) — `W172`'s predicate.

⭐ **Every test here is asserted in BOTH directions**: a document whose region
holds the line, paired with the same document one edit away where it does not.
⛔ The predicate is the half of gate three that decides what the marker rule
reads, so a region that is one line too wide is a rule firing on prose.
"""

from __future__ import annotations

from tools.quality.handoffs.sections import findings_region, in_findings


def test_a_section_runs_from_its_heading_to_the_next_of_the_same_depth():
    text = "# T\n\n## Findings\n\na\nb\n\n## For dependents\n\nc\n"
    assert findings_region(text) == ((3, 7),)
    # ⛔ The other direction: the closing heading's own line is OUTSIDE.
    assert 7 in in_findings(text)
    assert 8 not in in_findings(text)


def test_a_deeper_heading_does_NOT_close_the_section():
    # ⭐ A record writes its findings as `###` subsections under a `##`
    # heading. Ending at the next heading of ANY depth would admit the first
    # finding and silently drop every one after it.
    text = "## Findings\n\n### `CTO-99/1`\n\nx\n\n### `CTO-99/2`\n\ny\n"
    assert findings_region(text) == ((1, 9),)
    assert 7 in in_findings(text)


def test_a_shallower_heading_DOES_close_it():
    text = "## T\n\n### Findings\n\nx\n\n## Later\n\ny\n"
    assert findings_region(text) == ((3, 6),)
    assert 5 in in_findings(text)
    assert 9 not in in_findings(text)


def test_a_section_nobody_closes_runs_to_the_end_of_the_document():
    # ⚠️ The ordinary shape: a record owes none of the six, so *Findings* is
    # usually the last thing in it.
    text = "# T\n\n## Findings\n\nx\ny\n"
    assert findings_region(text) == ((3, 6),)


def test_a_document_with_no_findings_heading_has_no_region():
    text = "# T\n\n## Decisions\n\nx\n"
    assert findings_region(text) == ()
    assert in_findings(text) == frozenset()


def test_a_findings_heading_inside_a_FENCE_opens_nothing():
    # ⛔ A record that transcribes another document is quoting, not writing a
    # section — the same rule `contract.marker_lines` already applies.
    quoted = "# T\n\n```text\n## Findings\nx\n```\n\ny\n"
    assert findings_region(quoted) == ()
    # ⭐ The pair: the identical heading outside the fence DOES open one.
    live = "# T\n\n## Findings\nx\n\ny\n"
    assert findings_region(live) == ((3, 6),)


def test_the_heading_is_matched_past_the_markup_an_office_writes():
    # ⭐ Emphasis and attention glyphs are stripped, never enumerated into the
    # title pattern — Ruling 29's closed-list failure, avoided the same way.
    for heading in ("## Findings", "## ⛔ Findings, by id", "### **The findings**"):
        assert findings_region(f"{heading}\nx\n") == ((1, 2),), heading
    # ⛔ The other direction: a heading that merely mentions the word is not it.
    assert findings_region("## What the findings cost\nx\n") == ()
    assert findings_region("## Surprises\nx\n") == ()


def test_two_findings_sections_are_two_regions():
    text = "## Findings\na\n\n## Decisions\nb\n\n## Findings — mine\nc\n"
    assert findings_region(text) == ((1, 3), (7, 8))
    assert in_findings(text) == frozenset({1, 2, 3, 7, 8})


def test_a_hash_that_is_not_a_heading_is_not_read():
    # ⚠️ `#Findings` has no space, and a fenced `#!/bin/sh` is not markup.
    assert findings_region("#Findings\nx\n") == ()
    assert findings_region("####### Findings\nx\n") == ()
