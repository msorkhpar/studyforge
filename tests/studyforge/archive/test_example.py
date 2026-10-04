"""Mirror of `src/studyforge/archive/example.py` (R12): what an example's tabs may say."""

from __future__ import annotations

from studyforge.archive import example
from studyforge.archive.blocks import BLOCK_FIELDS
from studyforge.validate import blocks as validated


def test_the_words_validate_spells_are_the_archives():
    # ⛔ The archive's names do not cross the package edge, so `validate` spells them
    # again and this is what keeps the two the same.
    assert validated.EXAMPLE_TAB_KEYS == example.EXAMPLE_TAB_KEYS
    assert validated.EXAMPLE_TAB_OPTIONAL == example.EXAMPLE_TAB_OPTIONAL
    assert validated.EXAMPLE_MAX_TABS == example.EXAMPLE_MAX_TABS
    assert validated.EXAMPLE_OUTPUTS == example.EXAMPLE_OUTPUTS
    assert validated.EXAMPLE_BLOCKS == example.EXAMPLE_BLOCKS


def test_a_tab_is_a_language_and_a_span_and_an_example_holds_code():
    assert example.EXAMPLE_TAB_KEYS == ("lang", "span")
    assert example.EXAMPLE_BLOCKS == ("code",)
    assert BLOCK_FIELDS["example"] == ("type", "id", "tabs", "blocks")


def test_the_outputs_are_the_two_a_compiler_gives():
    assert example.EXAMPLE_OUTPUTS == ("compiler", "warning")
