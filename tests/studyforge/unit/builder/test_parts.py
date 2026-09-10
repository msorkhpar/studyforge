"""Mirror of `src/studyforge/unit/builder/parts.py` (R12)."""

from __future__ import annotations

from studyforge.archive.document import VIDEO_KEYS
from studyforge.unit.builder.parts import SECTION_KEYS, section, video_of, workspace_of
from tests.studyforge.unit.builder import support


def test_a_section_carries_exactly_its_keys_in_order():
    # ⛔ R10: these bytes are compared, so the order is the format.
    document = support.lesson()
    built = section(
        key="prose", kind="lesson", heading="H", blocks=document["blocks"], document=document
    )
    assert tuple(built) == SECTION_KEYS


def test_video_is_written_as_null_rather_than_omitted():
    # ⛔ A key that disappears when it is empty cannot be told from one nobody
    # wrote, and "the archive had no video" and "this build could not see it"
    # must not render the same.
    document = support.lesson()
    built = section(key="prose", kind="lesson", heading="H", blocks=[], document=document)
    assert "video" in built
    assert built["video"] is None


def test_a_video_record_is_carried_through_key_for_key():
    # ⛔ Carried, never re-derived: the archive is the only record of what was
    # downloaded and where it was filed.
    document = support.lesson(video=dict(support.VIDEO))
    carried = video_of(document)
    assert tuple(carried) == VIDEO_KEYS
    assert carried == support.VIDEO


def test_a_lesson_has_no_workspace():
    assert workspace_of(support.lesson(), "prose") is None


def test_a_practice_carries_the_exercise_record_the_archive_holds():
    built = workspace_of(support.practice(exercise=support.EXERCISE), "practice-prose")
    assert built == support.EXERCISE


def test_an_ungraded_practice_has_no_workspace():
    # ⭐ §7's three states: ungraded is first-class and is not a gap.
    assert workspace_of(support.practice(), "practice-prose") is None


def test_the_trust_rule_is_not_re_spelled_here():
    # ⚠️ Asserted by delegation, like SF-23's own guard: `unit.trust` owns R5
    # and this module asks rather than answers.
    import inspect

    from studyforge.unit.builder import parts

    source = inspect.getsource(parts)
    for forbidden in ("authoritative", "advisory", "provenance ="):
        assert forbidden not in source, f"parts.py spells {forbidden!r} itself"


def test_the_blocks_are_whatever_was_passed_and_not_the_archives():
    # ⭐ Where the two shapes differ in content rather than in order: a derived
    # section's blocks are the archive's, an authored section's are the
    # author's, and this function is told which.
    document = support.lesson()
    authored = [{"type": "para", "text": "The author's own."}]
    built = section(key="prose", kind="lesson", heading="H", blocks=authored, document=document)
    assert built["blocks"] == authored
    assert built["blocks"] != document["blocks"]
