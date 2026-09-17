"""Mirror of `src/studyforge/unit/builder/parts.py` (R12)."""

from __future__ import annotations

from studyforge.archive.document import MEDIA_ENTRY_KEYS, VIDEO_KEYS
from studyforge.unit.builder.parts import (
    SECTION_KEYS,
    attachments_of,
    section,
    video_of,
    workspace_of,
)
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


# --------------------------------------------------------------------------
# ⭐ `attachments` — spec C4's companion files, carried for the page to link
# --------------------------------------------------------------------------


def test_attachments_are_written_as_an_empty_list_rather_than_omitted():
    # ⛔ The argument `video` is built around: "the archive declared none" and
    # "this build could not read them" must not render the same.
    built = section(key="prose", kind="lesson", heading="H", blocks=[], document=support.lesson())
    assert "attachments" in built
    assert built["attachments"] == []


def test_an_attachment_entry_is_carried_through_key_for_key():
    # ⛔ Carried, never re-derived: the archive is the only record of what was
    # fetched and where it was filed — `video`'s rule, for the other list.
    carried = attachments_of(support.lesson(attachments=[dict(support.ATTACHMENT)]))
    assert [tuple(entry) for entry in carried] == [MEDIA_ENTRY_KEYS]
    assert carried == [support.ATTACHMENT]


def test_a_key_the_entry_vocabulary_does_not_name_is_dropped():
    # ⚠️ What this build serves is its own format: an adapter that wrote a
    # sixteenth field does not widen the document a page is rendered from (R10).
    declared = {**support.ATTACHMENT, "notes": "an adapter's own field"}
    assert attachments_of(support.lesson(attachments=[declared])) == [support.ATTACHMENT]


def test_a_declaration_that_is_not_a_list_of_objects_carries_nothing():
    # ⛔ A malformed declaration is the archive's defect and `studyforge
    # validate` names it; a page that raised here would lose the whole lesson
    # over a companion file.
    assert attachments_of({"attachments": "media/small-graph.ttl"}) == []
    assert attachments_of({"attachments": ["media/small-graph.ttl"]}) == []
    assert attachments_of({}) == []


def test_the_assets_a_block_already_shows_are_not_carried():
    # ⛔ `W215`: an asset is reached through the block that names it, so listing
    # it as well would offer the reader the diagram they are looking at.
    document = support.lesson()
    document["assets"] = [dict(support.ATTACHMENT)]
    built = section(key="prose", kind="lesson", heading="H", blocks=[], document=document)
    assert built["attachments"] == []
