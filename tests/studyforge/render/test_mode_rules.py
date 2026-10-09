"""Mirror of `src/studyforge/render/mode_rules.py` (R12): the per-mode rules and the script swap."""

from __future__ import annotations

import pytest

from studyforge.render import mode_rules, modes
from tests.studyforge.render.test_modes import MIXED, READING


def test_the_script_line_is_swapped_only_for_a_mode_reading_several_languages():
    script = "x\n" + modes.SINGLE_READ + "\ny"
    assert mode_rules.reads(script, READING) == script
    assert modes.LISTED_READ in mode_rules.reads(script, MIXED)


def test_a_script_without_the_line_is_refused():
    with pytest.raises(ValueError):
        mode_rules.reads("nothing", MIXED)


def test_a_locking_corpus_hides_the_page_outside_the_mode():
    choice = READING.choices[0]
    assert "body > :not(header)" in mode_rules.rule(choice, True)
    assert "body > :not(header)" not in mode_rules.rule(choice, False)
