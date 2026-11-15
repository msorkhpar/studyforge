"""Mirror of `src/studyforge/skills/intake/__init__.py`."""

from __future__ import annotations

from studyforge.skills import intake


def test_the_constants_are_the_agreed_values():
    assert intake.TRACKS == ("topic", "interview", "exam", "bridge", "convert")
    assert intake.DEPTHS == ("core", "deep", "survey", "prose")
    assert intake.BRIEF_PATH == ".studyforge/brief.json"


def test_the_package_re_exports_its_public_names():
    from studyforge.skills.intake import bank, brief, check, questions, render

    assert intake.Question is questions.Question
    assert intake.BANK is bank.BANK
    assert intake.Brief is brief.Brief
    assert intake.BriefError is brief.BriefError
    assert intake.load is brief.load and intake.parse is brief.parse
    assert callable(intake.check) and callable(intake.render)
