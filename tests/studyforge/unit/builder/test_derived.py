"""Mirror of `src/studyforge/unit/builder/derived.py` (R12)."""

from __future__ import annotations

import inspect

from studyforge.unit.builder import derived
from studyforge.unit.builder.material import of
from tests.studyforge.unit.builder import support


def sections(documents):
    return derived.sections(of(documents, "unit-01"))


# --------------------------------------------------------------------------
# ⭐ a unit nobody curated is readable the day it is ingested
# --------------------------------------------------------------------------


def test_one_section_per_archive_file_lessons_first():
    built = sections([support.practice(1), support.lesson(1)])
    assert [s["kind"] for s in built] == ["lesson", "practice"]
    assert [s["key"] for s in built] == ["prose", "practice-prose"]


def test_the_heading_is_the_documents_own_title():
    built = sections([support.lesson(1, title="What a class is")])
    assert built[0]["heading"] == "What a class is"


def test_a_second_file_of_a_kind_gets_a_numbered_key():
    built = sections([support.lesson(1), support.lesson(2)])
    assert [s["key"] for s in built] == ["prose", "prose-2"]


def test_a_gap_in_the_ordinals_does_not_leave_a_hole_in_the_keys():
    # ⛔ The position is the file's place among its own kind, never its
    # ordinal: those keys name audio files on disk, and an ingestion that
    # skipped `lesson-2` must not orphan a unit's narration.
    built = sections([support.lesson(1), support.lesson(7)])
    assert [s["key"] for s in built] == ["prose", "prose-2"]


def test_every_section_is_inhabited_and_carries_its_blocks():
    # ⚠️ Ruling 48: a build that produced zero sections would satisfy any
    # "every section has …" loop, and zero is the bug.
    built = sections([support.lesson(1), support.practice(1)])
    assert len(built) == 2
    assert all(section["blocks"] for section in built)


# --------------------------------------------------------------------------
# ⛔ the seam: this module computes order, and its sibling holds none
# --------------------------------------------------------------------------


def test_this_module_is_where_the_ordering_lives():
    # ⭐ The positive half of the seam, so the negative half below means
    # something: the ordering really is here.
    source = inspect.getsource(derived)
    assert "for kind in" in source


def test_the_authored_module_contains_no_ordering_code_at_all():
    # ⛔ **The seam asserted, not described.** Two consumers ordering one unit
    # differently mint different speech ids for the same section, so the page
    # asks for audio belonging to another sentence — every page renders, every
    # clip exists, and they no longer correspond. ⚠️ The failure is silent,
    # which is why this is a test and not a comment.
    from studyforge.unit.builder import authored

    source = inspect.getsource(authored)
    for forbidden in ("sorted(", ".sort(", "reverse=", "key=lambda"):
        assert forbidden not in source, f"authored.py reaches for {forbidden!r}"
