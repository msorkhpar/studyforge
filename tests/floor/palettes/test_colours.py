"""Mirror of `tests/floor/palettes/colours.py` (R12).

⛔ **The reason this module exists at all is asserted here**, not only stated in
its docstring: the ACCEPTED paper is a near-white, HSL calls it
saturated, and chroma does not. A bound written in saturation would have refused
the remedy on its first run.
"""

from __future__ import annotations

import pytest

import tests.floor.palettes.colours as colours_module
from tests.floor.palettes.colours import colour, measure
from tests.support import assert_package_contract


def test_states_its_contract():
    assert_package_contract(colours_module, "tests.floor.palettes.colours")


def test_a_colour_is_read_as_hue_chroma_and_light():
    read = colour("#a64d07")
    assert (round(read.hue), round(read.chroma), round(read.light)) == (26, 62, 34)
    assert colour("#fff").light == 100
    assert colour("#000") == colour("#000000")


def test_rgb_and_rgba_are_read_and_anything_else_is_not():
    assert colour("rgba(251, 239, 122, .35)") == measure(251, 239, 122)
    assert colour("rgb(0 0 0)") == measure(0, 0, 0)
    assert colour("var(--bg)") is None
    assert colour("none") is None


def test_a_grey_has_no_hue_and_no_chroma():
    read = measure(120, 120, 120)
    assert (read.hue, read.chroma) == (0.0, 0.0)
    assert read.light == pytest.approx(47.06, abs=0.01)


def test_a_near_white_reads_LOW_chroma_where_HSL_saturation_reads_high():
    # ⛔ The module's own reason for chroma, asserted rather than asserted-in-prose.
    read = colour("#f1f5f9")
    high, low = 0xF9 / 255, 0xF1 / 255
    saturation = (high - low) / (2 - high - low) * 100
    assert saturation > 35
    assert read.chroma < 5


def test_the_reading_is_the_three_measures_a_person_can_check_by_hand():
    assert measure(255, 0, 0).reading() == "hue 0, chroma 100%, light 50%"
