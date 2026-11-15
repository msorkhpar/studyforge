"""Mirror of `src/studyforge/render/page/unitmeta.py` (R12)."""

from __future__ import annotations

from studyforge.render.page.navigation import Crumb
from studyforge.render.page.rail import RailContainer, RailUnit
from studyforge.render.page.unitmeta import (
    SECONDS_PER_CODE_LINE,
    WORDS_PER_MINUTE,
    container_of,
    line,
    minutes,
    position,
)

TRAIL = (Crumb("Course", "Graphs", "index.html"), Crumb("Track", "Search"), Crumb("", "BFS"))
RAIL = (
    RailContainer(
        "Search",
        units=(RailUnit("DFS"), RailUnit("BFS", current=True), RailUnit("A*")),
    ),
)


def _words(count: int) -> str:
    return "<p>" + " ".join(["word"] * count) + "</p>"


def test_the_container_is_the_step_above_the_unit_and_needs_a_container_step():
    assert container_of(TRAIL) == "Search"
    assert container_of(TRAIL[1:]) == ""
    assert container_of(None) == ""


def test_the_position_counts_units_in_the_container_holding_this_page():
    assert position(RAIL) == "Unit 2 of 3"
    assert position((RailContainer("Other", units=(RailUnit("x"),)),)) == ""
    assert position(None) == ""


def test_reading_time_is_prose_at_the_rate_plus_code_lines_rounded_up_and_at_least_one():
    assert minutes("") == 1
    assert minutes(_words(WORDS_PER_MINUTE)) == 1
    assert minutes(_words(WORDS_PER_MINUTE + 1)) == 2
    listing = "<pre>" + "\n".join(["x = 1"] * (60 // SECONDS_PER_CODE_LINE)) + "</pre>"
    assert minutes(_words(WORDS_PER_MINUTE) + listing) == 2


def test_a_practice_and_a_quiz_are_doing_not_reading():
    quiz = '<section data-practice-quiz="q">' + _words(10 * WORDS_PER_MINUTE) + "</section>"
    assert minutes(_words(10) + quiz) == 1


def test_the_line_names_each_part_with_something_to_say():
    body = (
        _words(10)
        + '<ul><li data-practice-card="1">a</li><li data-practice-card="2">b</li></ul>'
        + '<ol><li data-practice-question="1">q</li></ol>'
    )
    assert line(body, TRAIL, RAIL) == (
        '<ul data-section="unit-meta"><li>Search</li><li>Unit 2 of 3</li><li>1 min read</li>'
        "<li>2 practices</li><li>1 question</li></ul>"
    )


def test_a_part_with_nothing_true_to_say_is_left_out_and_no_dot_is_typed():
    made = line(_words(10))
    assert made == '<ul data-section="unit-meta"><li>1 min read</li></ul>'
    assert "·" not in line(_words(10), TRAIL, RAIL)
