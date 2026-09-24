"""Mirrors `render/container/progress.py`: the markup of where the reader is."""

from __future__ import annotations

import re

from studyforge.render.container import progress
from studyforge.render.markup import anchor


def test_the_progress_line_ships_hidden_with_its_numbers_at_zero():
    # ⛔ The marks are the browser's, so with no script nothing here may claim a
    # count; the script fills the two numbers and unhides the region.
    line = progress.line(38)
    assert line.startswith('<section aria-label="Progress" hidden>')
    assert "<strong>0</strong> of 38 units read" in line
    assert "<b>38</b> to go" in line


def test_one_unit_is_said_in_the_singular():
    assert "of 1 unit read" in progress.line(1)
    assert progress.units_phrase(1) == "1 unit"
    assert progress.units_phrase(11) == "11 units"


def test_the_strip_is_one_link_per_group_sized_by_its_units_and_pointing_at_it():
    strip = progress.strip([("basics", "Basics", 4), ("advanced", "Advanced", 2)])
    assert strip.count("<li ") == 2
    assert 'style="--units: 4"' in strip and 'style="--units: 2"' in strip
    assert f'href="{anchor("basics")}"' in strip


def test_a_course_of_one_group_draws_no_strip():
    # A strip of one segment says nothing the progress line has not said.
    assert progress.strip([("basics", "Basics", 4)]) == ""


def test_the_slip_names_the_unit_and_carries_the_all_read_state_hidden():
    slip = progress.up_next("Basic setup", "study/unit-01.unit.html")
    assert slip.startswith('<nav aria-label="Up next">')
    assert '<a href="study/unit-01.unit.html"><span>Up next</span> Basic setup</a>' in slip
    assert "<p hidden><span>Up next</span> You have read every unit</p>" in slip


def test_the_all_read_state_is_not_a_link_into_the_page():
    # ⛔ Chrome points off the page (`test_no_script`): the finished state has
    # nowhere to go, so it is a paragraph and never an inward anchor.
    slip = progress.up_next("Basic setup", "study/unit-01.unit.html")
    assert re.findall(r'href="([^"]+)"', slip) == ["study/unit-01.unit.html"]


def test_a_unit_with_no_page_gives_no_slip():
    assert progress.up_next("Basic setup", None) == ""


def test_a_refused_href_gives_no_slip_rather_than_a_dangerous_link():
    assert progress.up_next("Basic setup", "javascript:alert(1)") == ""


def test_the_filter_ships_hidden_and_its_two_controls_do_one_thing_each():
    finder = progress.finder()
    assert finder.startswith('<form role="search" aria-label="Filter units" hidden>')
    assert '<button type="button" value="expand">Expand all</button>' in finder
    assert '<button type="button" value="collapse">Collapse all</button>' in finder
    assert 'autocomplete="off"' in finder and 'spellcheck="false"' in finder
    assert 'placeholder="Filter units…"' in finder
    assert 'role="status"' in finder


def test_every_word_is_markup_and_the_titles_are_escaped():
    slip = progress.up_next("<b>Bold</b>", "u.html")
    assert "<b>Bold</b>" not in slip
