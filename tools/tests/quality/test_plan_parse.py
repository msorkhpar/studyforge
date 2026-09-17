"""Mirror of `tools/quality/plan_parse.py` (R12).

⭐ The parse's own tests, moved from `test_creators.py` unchanged when the module split
(`W285`). What the parse refuses is asserted through the floor check in `test_creators.py`.
"""

from __future__ import annotations

from tools.quality.plan_parse import placement, rows


def test_placement_blanks_parentheses_and_spans_and_the_FIRST_step_line_wins():
    steps = placement(
        "- **5.1** — TC-00, **SF-20** · `SF-99`\n"
        "- **9.1** — JS-01, EX-00  *(needs TC-00's pinned image)*\n"
        "- **9.2** — TC-00\n"
        "- ⭐ **alongside 1.4** — **FND-08**\n"
    )
    assert steps == {"TC-00": "5.1", "SF-20": "5.1", "JS-01": "9.1", "EX-00": "9.1"}


def test_a_CANCELLED_row_is_not_read_and_a_wrapped_Owns_cell_is():
    text = (
        "### FND-05b — cancelled\n**Milestone** — · **Depends on** — · **Team** —\n"
        "**Owns** — **Context** —\n\n"
        "### SF-35 — wrapped\n**Milestone** **M2** · **Depends on** SF-02, *SF-05* · **Team** x\n"
        "**Owns** `corpus/manifest/content/`, and `KNOWN` in\n`version.py`\n**Context** ~5k\n"
    )
    [row] = rows("E01.md", text)
    assert (row.id, row.depends, row.context) == ("SF-35", ("SF-02", "SF-05"), "~5k")
    assert "`version.py`" in row.owns
