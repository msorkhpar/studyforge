"""Mirror of `src/studyforge/render/page/part.py` (R12).

A section is followed by its panel; a language edition is tagged as an edition and never as a
language, so no reading mode hides it, while any other practice is tagged as it always was.
"""

from __future__ import annotations

import dataclasses

from studyforge.render.page import part
from studyforge.render.page.narration import SILENT
from tests.studyforge.render.page.pages import sample_placement
from tests.studyforge.render.page.test_editions import LANGS, edition, four, offer
from tests.studyforge.render.page.test_practice import document, section


def one(sections: list[dict], at: int, *, with_offer: bool = True) -> str:
    placement = sample_placement()
    if with_offer:
        placement = dataclasses.replace(placement, offer=offer())
    unit = document(sections=sections)
    return part.render(sections[at], placement, SILENT, unit, heads_page=False)


def test_an_edition_and_its_panel_carry_data_edition_and_never_data_lang():
    found = one(four(), 1)
    assert 'data-edition="typescript"' in found
    assert "data-lang=" not in found
    assert found.count('<section data-practice="') == 1
    assert LANGS[1] in found


def test_an_ordinary_tagged_practice_keeps_its_language_tag_on_the_panel():
    tagged = section(key="practice-solo")
    tagged["lang"] = "java"
    found = one([tagged], 0)
    assert 'data-lang="java"' in found
    assert "data-edition" not in found


def test_a_section_with_no_work_has_no_panel():
    lesson = section(kind="lesson", workspace=None, key="lesson-java")
    assert "<section data-practice=" not in one([lesson], 0, with_offer=False)
