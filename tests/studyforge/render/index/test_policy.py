"""Mirror of `src/studyforge/render/index/policy.py` (R12).

⭐ **Subtask (b), and the population before the verdict.** `row_counts` is
asserted against corpora whose shape is declared as a number, so a test can sit
exactly on `VISIBLE_ROW_BUDGET` and see both sides of it.
"""

from __future__ import annotations

import pytest

from studyforge.render.index import VISIBLE_ROW_BUDGET, open_to, row_counts, visible_rows
from tests.studyforge.render.index.indexes import cases, planted


@pytest.mark.parametrize("shape", [(1, 3), (2, 4), (2, 3, 4), (2, 2, 2, 3)])
def test_row_counts_reports_the_shape_the_corpus_was_built_to(shape):
    # ⭐ The population, printed as a tuple before anything reduces it to a
    # verdict: level 1 is the top containers, and level n+1 is everything the
    # level above it reveals.
    document = planted(shape).document
    expected = []
    reached = 1
    for how_many in shape:
        reached *= how_many
        expected.append(reached)
    assert row_counts(document) == tuple(expected)
    assert len(row_counts(document)) == len(shape)


def test_a_corpus_smaller_than_the_budget_opens_all_the_way_down():
    # ⭐ A one-level corpus reads as a plain nested list, with no flag anywhere.
    document = planted((2, 4)).document
    assert visible_rows(document, open_to(document)) <= VISIBLE_ROW_BUDGET
    assert open_to(document) == document.depth


def test_a_level_that_would_break_the_budget_becomes_opt_in():
    # ⛔ (10, 5, 10): level 1 shows 10, opening it shows 50 more — exactly the
    # budget — and opening level 2 would show 500. So level 1 opens and level 2
    # does not, and the boundary is sat on rather than approached.
    document = planted((10, 5, 10)).document
    assert row_counts(document) == (10, 50, 500)
    assert visible_rows(document, 1) == VISIBLE_ROW_BUDGET
    assert open_to(document) == 1


def test_one_more_row_at_the_boundary_closes_the_level():
    # ⭐ The negative control for the row above: the same shape plus one section
    # crosses the budget, and the level that opened stops opening.
    assert open_to(planted((11, 5, 10)).document) == 0
    assert open_to(planted((10, 5, 10)).document) == 1


def test_the_top_level_is_visible_however_many_of_it_there_are():
    # ⛔ Its summaries are the rows of the outermost list and there is no
    # disclosure above them to close, so the budget stops the NEXT level
    # unfolding rather than deciding whether to render this one.
    document = planted((VISIBLE_ROW_BUDGET + 5, 2)).document
    assert open_to(document) == 0
    assert visible_rows(document, 0) > VISIBLE_ROW_BUDGET


def test_both_fixtures_render_entirely_open():
    # ⭐ Both are far inside the budget, which is why the goldens show the whole
    # tree and why the collapsed case has to be planted rather than found.
    for built in cases():
        assert open_to(built.document) == built.document.depth


def test_visible_rows_is_monotone_so_the_deepest_affordable_level_is_the_last_that_fits():
    # ⛔ The argument `open_to` rests on, asserted rather than reasoned: if the
    # count could fall as a level opened, "deepest affordable" and "last that
    # fits" would be different searches.
    document = planted((4, 4, 4)).document
    seen = [visible_rows(document, opened) for opened in range(document.depth + 1)]
    assert seen == sorted(seen)
    assert seen[0] == row_counts(document)[0]
