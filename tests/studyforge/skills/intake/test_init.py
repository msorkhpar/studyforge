"""Mirror of `src/studyforge/skills/intake/__init__.py`."""

from __future__ import annotations

from studyforge.skills import intake


def test_the_constants_are_the_agreed_values():
    assert intake.TRACKS == ("topic", "interview", "exam", "bridge", "convert")
    assert intake.DEPTHS == ("core", "deep", "survey", "prose")
    assert intake.BRIEF_PATH == ".studyforge/brief.json"
