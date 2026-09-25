"""Mirror of `src/studyforge/unit/practice.py` (R12)."""

from __future__ import annotations

from studyforge.unit import bare_lesson
from tests.studyforge.render.page.test_section import exercise


def test_bare_lesson_reads_only_a_level_two_lesson_heading_over_disclosures():
    blocks = exercise([])["blocks"]
    assert bare_lesson(blocks) == 2
    titled = [*blocks[:2], {**blocks[2], "text": "Lesson: Streams"}, *blocks[3:]]
    assert bare_lesson(titled) == 2
    assert bare_lesson([*blocks[:3], *blocks[4:]]) == 2, "an empty run is bare"
    over = exercise([{"type": "para", "text": "Here is how."}])["blocks"]
    assert bare_lesson(over) is None
    deeper = [*blocks[:2], {**blocks[2], "level": 3}, *blocks[3:]]
    assert bare_lesson(deeper) is None
    assert bare_lesson([]) is None
