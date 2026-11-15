"""Mirror of `src/studyforge/skills/lessons/__init__.py` (R12)."""

from __future__ import annotations

from studyforge.skills import documents, lessons
from tests.support import assert_package_contract


def test_states_its_contract():
    assert_package_contract(lessons, "studyforge.skills.lessons")


def test_the_skill_document_ships_beside_it_and_is_found():
    assert "lessons" in documents.names()
    assert documents.text("lessons").strip()
