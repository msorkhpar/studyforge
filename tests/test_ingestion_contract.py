r"""`W214`: the ingestion contract has one shape, and three pages must not spell it three ways.

**What it asserts.** `skills/adapter/SKILL.md` draws the tree an adapter writes.
That drawing is `archive_tree()`, byte for byte, so the page is the layout
rather than a copy of it (R19) — and the spec's §6 contract names no part of
that tree the skill leaves out.

⛔ **This module never types an archive path.** It reads the skill's fence, the
spec's fence and `corpus.placement`'s three segment names, and compares them.
A fourth spelling introduced anywhere it can see turns it RED.

## ⚠️ The direction the spec agreement is asserted in, and why it is one-way

⭐ **Measured here: §6's fence enumerates `container.json` and
`raw/<variant>/unit-NN/<kind>-M.json` and stops.** A unit's OWN files — where
every `assets` and `attachments` entry's `local` resolves, and where §5's
contract table already places `<address>/units/unit-NN/content.json` — are in
the tree the build reads and in no line of §6.

⛔ **A `docs/specs/` edit needs the register's agreement**, so this asserts the
half that holds today: **the spec names nothing the skill omits**, and the
skill may exceed it only by the drawn root and by segments `corpus.placement`
owns. ⚠️ It keeps holding the day §6 gains the row, so nothing here has to be
touched to accept the amendment.
"""

from __future__ import annotations

import re

import pytest

from studyforge.corpus.placement import ARCHIVE_DIRNAME, RAW_DIRNAME, UNITS_DIRNAME
from studyforge.skills.adapter import TREE_ROOT, archive_tree
from tests.authoring.support import fences, section
from tests.support import repository_root

#: The page that hands an adapter author the tree.
SKILL = "src/studyforge/skills/adapter/SKILL.md"

#: The heading whose fence draws it.
SKILL_STEP = "3. Scaffold, and let the framework own every path"

#: The design, and the section that locates the contract.
SPEC = "docs/specs/2026-09-08-studyforge-v1-design.md"
SPEC_SECTION = "6. The ingestion contract"

#: A comment column: two or more spaces, then prose about the line beside it.
#: ⚠️ Read off the STRIPPED line, never the raw one — §6 indents its
#: continuation lines four spaces, and a pattern that ran before the strip
#: would delete every one of them and call the result agreement.
_COMMENT = re.compile(r"\s{2,}.*$")

#: What the two pages spell differently for one thing. ⛔ Declared as a table
#: rather than resolved by preferring one page: each spelling is its own
#: document's, and this module is where they are stated to be the same thing.
#: ⚠️ `<kind>` is `archive.document.KINDS`, which is why one row covers both.
SAME_THING = {
    "<archive-root>": ARCHIVE_DIRNAME,
    "lesson-M.json": "<kind>-N.json",
    "practice-M.json": "<kind>-N.json",
}

#: What the skill may draw that §6 does not: the root a reader substitutes, and
#: the directory names the framework owns. ⛔ A closed set — anything else in
#: the difference is a segment one page invented.
MAY_EXCEED = {TREE_ROOT, ARCHIVE_DIRNAME, RAW_DIRNAME, UNITS_DIRNAME}


def text(where: str) -> str:
    """Return one tracked document's text."""
    return (repository_root() / where).read_text(encoding="utf-8")


def drawn_fence() -> str:
    """Return the one tree the skill draws, failing unless it draws exactly one."""
    found = fences(section(text(SKILL), SKILL_STEP), "text")
    assert len(found) == 1, f"{SKILL} step 3 draws {len(found)} trees; it must draw exactly one"
    return found[0]


def contract_fence() -> str:
    """Return the one tree §6 draws, failing unless it draws exactly one."""
    found = fences(section(text(SPEC), SPEC_SECTION), "")
    assert len(found) == 1, f"{SPEC} §6 draws {len(found)} trees; it must draw exactly one"
    return found[0]


def segments(fence: str) -> set[str]:
    """Every path segment one drawn tree names, with the two pages' spellings reconciled.

    ⛔ Split on `/` rather than matched: a reader of this instrument must be
    able to see that no path is typed here at all.
    """
    found: set[str] = set()
    for line in fence.splitlines():
        bare = _COMMENT.sub("", line.strip())
        found.update(part for part in bare.split("/") if part)
    assert found, "a drawn tree named no segment at all"
    return {SAME_THING.get(part, part) for part in found}


# --- the skill's tree is the layout, not a copy of it ----------------------


def test_the_skill_draws_the_tree_the_layout_computes():
    # ⛔ Byte for byte. A page that drew it a line at a time would be a second
    # spelling, and `W214` is what a second spelling costs: media written where
    # no build looks, every media-bearing page a broken glyph, nothing failing.
    assert drawn_fence() == archive_tree()


def test_the_skill_states_where_a_units_own_files_go():
    # ⭐ Clause 1: the line that was in no page under `src/` at all.
    assert f"{UNITS_DIRNAME}/unit-NN/" in drawn_fence()
    assert UNITS_DIRNAME in segments(drawn_fence())


def test_the_skill_names_the_directory_the_placement_package_owns():
    # ⛔ Not a literal compared against itself: the drawing joins
    # `corpus.placement`'s value and this reads the page after the join.
    for segment in (ARCHIVE_DIRNAME, RAW_DIRNAME, UNITS_DIRNAME):
        assert segment in segments(drawn_fence()), f"the skill's tree lost {segment!r}"


# --- and the spec's contract names nothing it leaves out -------------------


def test_the_contract_names_no_part_of_the_tree_the_skill_omits():
    # ⛔ `W16`'s class: the spec's canonical example is a hand-maintained copy
    # of a contract the code owns, so the agreement is asserted rather than read.
    unnamed = segments(contract_fence()) - segments(drawn_fence())
    assert unnamed == set(), f"{SPEC} §6 names {sorted(unnamed)}, which {SKILL} does not draw"


def test_the_skill_exceeds_the_contract_only_where_the_framework_owns_the_name():
    """⚠️ The gap `W214` found, held closed rather than described.

    ⭐ Today the difference is the drawn root and `units/` — the row §6 does
    not carry. ⛔ It may never be a segment neither `corpus.placement` nor the
    reader supplies, because that would be a page inventing a location.
    """
    extra = segments(drawn_fence()) - segments(contract_fence())
    assert extra <= MAY_EXCEED, f"{SKILL} draws {sorted(extra - MAY_EXCEED)}, which §6 does not"


# --- the reader is strict enough to fail -----------------------------------


def test_a_fence_that_says_nothing_is_refused_rather_than_read_as_agreement():
    # ⛔ The empty-population control. Without it every assertion above passes
    # against a fence somebody emptied, which is the one failure nobody reads.
    with pytest.raises(AssertionError):
        segments("\n   \n")


def test_the_reader_tells_one_tree_from_another():
    # ⭐ `unit-3/` for `unit-NN/` is the measured five-joins-deep typo, and it
    # must not compare equal to the drawn tree.
    assert segments(archive_tree().replace("unit-NN", "unit-3")) != segments(archive_tree())


def test_the_two_pages_spellings_are_reconciled_rather_than_ignored():
    # ⛔ The table is what makes the subset assertion mean anything: without the
    # `<archive-root>` row, §6's root would read as a segment the skill omits.
    assert ARCHIVE_DIRNAME in segments("<archive-root>/<address>/")
    assert segments("raw/<variant>/unit-NN/lesson-M.json") == segments(
        "raw/<variant>/unit-NN/practice-M.json"
    )


def test_a_comment_column_is_read_as_prose_and_not_as_a_path():
    # ⚠️ §6 writes `corpus.json    the manifest (§4)`; a reader that split the
    # whole line would find `the`, `manifest` and `(§4)` among its segments.
    assert segments("corpus.json                the manifest (§4)") == {"corpus.json"}
