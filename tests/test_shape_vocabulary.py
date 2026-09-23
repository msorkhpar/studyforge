"""The framework gate's column of Ruling 47's shared table.

⛔ **One shape vocabulary, two policies.** `archive.scrub` and
`tools/quality/personal_data` are ruled to have different *subjects* and
therefore different *policies* — one may know this machine, the other may know
nothing — ⛔ and that never justified differing in what they **recognise**.
They had drifted, and nobody noticed for eleven rounds because nothing
compared them.

⚠️ Ruling 31 forbids the tool from importing the framework, so the two sides
share **evidence, not code**: `docs/conventions/personal-data-shapes.md` holds
one table — read here through the product's copy of it, `tests/support.py`'s
`SHAPE_VOCABULARY` (`REL-02`) — this module asserts the `gate` and `scrub` columns of it, and
`tools/tests/quality/personal_data/test_shapes.py` asserts the `quality`
column. Neither module imports the other's subject.
"""

import pytest

from studyforge.archive.scrub import scrub, shape_in
from tests.support import personal_data_shapes, shapes_agree

VOCABULARY = personal_data_shapes()
BY_SHAPE = [pytest.param(row, id=row["shape"]) for row in VOCABULARY]


@pytest.mark.parametrize("row", BY_SHAPE)
def test_the_gate_does_what_the_shared_table_says(row):
    said = "refuse" if shape_in(row["example"]) is not None else "pass"
    assert said == row["gate"], row["shape"]


@pytest.mark.parametrize("row", BY_SHAPE)
def test_and_so_does_the_scrubber(row):
    did = "rewrite" if scrub(row["example"]) != row["example"] else "keep"
    assert did == row["scrub"], row["shape"]


def test_every_divergence_carries_a_reason():
    # ⭐ The mechanism itself. A row whose three columns disagree is allowed —
    # the two gates have different powers — but only with the reason written
    # down beside it, which is what turns a divergence into a decision.
    undeclared = [
        row["shape"] for row in VOCABULARY if not shapes_agree(row) and not row.get("why")
    ]
    assert undeclared == [], undeclared
    for row in VOCABULARY:
        if row.get("why"):
            assert len(row["why"]) > 80, row["shape"]


def test_the_table_is_inhabited_and_holds_both_verdicts():
    # ⛔ **Ruling 48.** Every test above is a comparison, and a table that
    # emptied would satisfy all of them: no rows, no mismatches, green.
    # ⚠️ Both verdicts must appear in each column too — a table of nothing but
    # `pass` would be satisfied by a gate that had been deleted.
    assert len(VOCABULARY) >= 12
    assert {row["gate"] for row in VOCABULARY} == {"refuse", "pass"}
    assert {row["scrub"] for row in VOCABULARY} == {"rewrite", "keep"}
    assert {row["quality"] for row in VOCABULARY} == {"report", "ignore"}
    assert [row for row in VOCABULARY if not shapes_agree(row)], "no divergence is a red flag"


def test_no_row_writes_its_shape_whole():
    # ⚠️ The document is swept by the check its own last column describes, so
    # a real shape written whole into it would be a finding against it. The
    # fragments are how it stays both swept and clean, and this is what keeps
    # somebody from "tidying" them into one string.
    for row in VOCABULARY:
        assert len(row["spelling"]) >= 2, row["shape"]
