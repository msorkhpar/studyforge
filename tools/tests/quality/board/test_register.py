r"""Mirror of `tools/quality/board/register.py` (R12), and it is a regression suite.

⛔ **Both halves of this module shipped BROKEN and were caught by review, not by
me.** ⭐ **So every positive here is paired with the real text that defeated the
first version**, in the shape `test_pointers.py` established: the corpus is
verbatim from the tree at the ref it was measured on, because ⚠️ **the shapes
that broke the naive versions are ones nobody would have thought to invent.**

| Defect | `CTO-45/x` | The plant |
|---|---|---|
| `split("|")` tore three rows mid-sentence at a pipe in a code span | `/1` |
  `MEASURED_ROWS`, verbatim from `bfb8c8c` |
| `is_closed` was a SUBSTRING test, so a live row that MENTIONED `done`
  closed | `/2` | `LIVE_CELLS_THAT_MENTION_DONE` |

⚠️ **The second is the one to keep staring at.** ⛔ **A live row whose state cell
merely mentioned `done` needed no detail file, left the bijection, and the floor
printed `quality floor: clean` with no finding at all.** ⭐ **28 of the 78 cells
on the board today carry the `✅ done — <ref>` idiom, so the failure was one
subordinate clause from routine.**
"""

from __future__ import annotations

import pytest

from tests.support import repository_root
from tools.quality.board import BOARD
from tools.quality.board.register import (
    REGISTER_CLOSE,
    REGISTER_OPEN,
    STATES,
    cells,
    identifiers,
    is_closed,
    narrative_bytes,
    register,
    state,
    table_lines,
)

#: ⛔ **The three rows a naive `split("|")` tore apart, verbatim from
#: `bfb8c8c:docs/tasks/BOARD.md`** — abbreviated to the cell boundaries and the
#: offending span, because the originals are 1,799, 3,393 and 2,998 bytes and
#: the defect is in none of the prose.
#:
#: ⚠️ Every one is a pipe **inside a code span**, which is a pipe no renderer
#: splits on either — ⭐ so a cell parser that does is not merely strict, it
#: disagrees with what the reader sees.
MEASURED_ROWS = (
    # W38: an unescaped pipe in a code span
    "| **W38** | the floor and `ruff` disagree | framework agent | "
    "`todo` — the identity is `py + md − (py|md under tests/fixtures/)` and it holds | "
    "round 22's mint block above |",
    # W40: a backslash-escaped pipe inside a code span (a regex alternation)
    "| ⛔ **W40** | no module sits at zero headroom | framework agent | "
    "`todo` — `git grep -n 'gated BEFORE\\|gated before' -- docs/` returns 4 | "
    "[Ruling 119](#w40) |",
    # W53: a backslash-escaped pipe opening a shell pipeline in a code span
    "| ⭐ **W53** | a clause naming an instrument is not final | framework agent | "
    "`todo` — *`\\| wc -l` is added AFTER the members have been read* | "
    "[round 28's mints](#w53) |",
)

#: ⛔ **The plant that is adversarial to the PREDICATE rather than the subject**
#: (Ruling 140). ⚠️ Every one is a plausible LIVE cell whose text contains the
#: word `done`; ⭐ under the substring test every one was CLOSED.
LIVE_CELLS_THAT_MENTION_DONE = (
    "`todo` — after `W44` is done",
    "`todo` — not done, and the branch is byte-identical to `HEAD`",
    "blocked — until `W40` is done",
    "in-progress — half done; the asserting test is owed",
    "in flight — the `done` column moved underneath it",
    "in-review — done in spirit, not on the release branch",
    "accepted — cost named; nothing to be done",
    "routed — folded into `SF-10`, where it will be done",
)


# --------------------------------------------------------------------------
# `cells` — CTO-45/1
# --------------------------------------------------------------------------


@pytest.mark.parametrize("row", MEASURED_ROWS)
def test_a_pipe_inside_a_code_span_does_not_split_a_cell(row: str) -> None:
    """⛔ Five cells, every time — the reading the first version got wrong.

    ⭐ **The assertion that matters is not the count but cell 3**: the naive
    split produced a SIXTH cell out of the state column's tail, and that tail
    is what was written into `rows/W38.md`, `rows/W40.md` and `rows/W53.md`,
    where it existed nowhere else in the tree.
    """
    columns = cells(row)
    assert len(columns) == 5, columns
    assert columns[2] == "framework agent", "the owner column moved"
    assert columns[3].startswith(("`todo`", "⭐", "⛔")), columns[3]
    assert "|" in columns[3], "the plant must still contain the pipe it hides"


def test_the_naive_split_is_shown_to_disagree() -> None:
    """⚠️ A negative control: without the span parser these rows over-split.

    ⛔ **Ruling 155 — a recorded negative is a reading, not a shrug.** This is
    the reading that says the corpus is adversarial at all; without it, a suite
    of passing rows proves nothing about the parser that replaced.
    """
    for row in MEASURED_ROWS:
        naive = row.strip().strip("|").split("|")
        assert len(naive) > len(cells(row)), row[:60]


def test_a_row_with_no_code_spans_is_split_identically() -> None:
    """⭐ The parser is not doing anything else — 74 of the 78 rows are plain."""
    row = "| W1 | a naming | PO | ✅ done — `abc1234` | [record](x.md#w1) |"
    assert cells(row) == [c.strip() for c in row.strip().strip("|").split("|")]


# --------------------------------------------------------------------------
# `state` and `is_closed` — CTO-45/2
# --------------------------------------------------------------------------


@pytest.mark.parametrize("cell", LIVE_CELLS_THAT_MENTION_DONE)
def test_a_live_cell_that_merely_mentions_done_is_not_closed(cell: str) -> None:
    """⛔ THE defect. ⭐ A cell DECLARES its state; it does not mention one.

    ⚠️ Under the substring test each of these returned `True`, so the row owed
    no detail file, left the bijection, and the floor stayed green — ⛔ **the
    silent failure, which is the only kind this project treats as urgent.**
    """
    assert state(cell) is not None, "the plant must still declare a state"
    assert not is_closed(cell), cell


@pytest.mark.parametrize("word", sorted(STATES))
def test_every_word_in_the_vocabulary_is_reachable(word: str) -> None:
    """⛔ Ruling 48 — a vocabulary with an unreachable member is a dead branch."""
    assert state(f"✅ **{word}** — `abc1234`") == word
    assert is_closed(f"{word} — x") is STATES[word]


def test_the_longest_match_wins() -> None:
    """⚠️ `in-review` must never be read as `in flight`, nor `todo` as nothing."""
    assert state("in-review — `655b527`") == "in-review"
    assert state("in-progress — spec text landed") == "in-progress"
    assert state("in flight, with `W14`") == "in flight"


@pytest.mark.parametrize(
    "cell",
    [
        "→ folded into `SF-10`",
        "◐ spec text landed; the asserting test is owed",
        "",
        "⚠️ see the round record",
        "DONE-ish",
    ],
)
def test_a_cell_that_declares_nothing_is_not_closed_and_not_guessed(cell: str) -> None:
    """⛔ The IMPOSSIBLE reading: no declaration is not a state, and not `done`.

    ⭐ **Two of these are real** — `W5` and `W16` carried them until this check
    was written, and both were LIVE. ⚠️ `DONE-ish` is the shape that shows the
    rule is a prefix on a closed set rather than a looser substring in a hat.
    """
    assert state(cell) is None
    assert not is_closed(cell)


# --------------------------------------------------------------------------
# `register`, and the live board
# --------------------------------------------------------------------------


def test_the_live_board_declares_a_state_on_every_row() -> None:
    """⭐ The population, printed by `board_state` and asserted here.

    ⛔ Expected before running: **78 rows, 0 undeclared** — 43 `todo`,
    28 `done`, 2 `accepted`, 2 `in flight`, 1 each of `routed`, `in-progress`
    and `in-review`.
    """
    text = (repository_root() / BOARD).read_text(encoding="utf-8")
    rows = register(text)
    undeclared = [ids[0] for _n, ids, cell in rows if state(cell) is None]
    assert undeclared == [], undeclared
    assert len(rows) >= 78


def test_the_register_stops_at_its_markers() -> None:
    """⛔ A `W`-shaped table outside the markers is not the register."""
    inside = "| W2 | a naming | PO | `todo` | [d](rows/W2.md) |"
    outside = "| W3 | in flight | Dev | none | +3 |"
    text = f"{REGISTER_OPEN}\n{inside}\n{REGISTER_CLOSE}\n{outside}\n"
    assert [ids for _n, ids, _s in register(text)] == [["W2"]]


def test_identifiers_reads_a_two_id_row_and_refuses_a_header() -> None:
    assert identifiers("W17 **+ W19**") == ["W17", "W19"]
    assert identifiers("# | Row | Owner") == []


def test_table_lines_and_narrative_bytes_partition_the_file() -> None:
    """⭐ Every byte is one or the other, which is what makes the bound a bound."""
    text = "prose\n| a | b |\nmore prose\n"
    table = sum(len(line.encode()) + 1 for _n, line in table_lines(text))
    assert table + narrative_bytes(text) == len(text.encode()) + 1
