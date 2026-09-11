"""Mirror of `tools/quality/board/bounds.py` (R12) — the three bounds, each planted alone.

⛔ **These readings MOVED here from `test_init.py` with the code they measure** (`W100`'s
split), and they moved rather than being copied: ⭐ **a fixture or a reading with two homes
is the defect this package's own instrument exists to forbid, one layer up.**

⚠️ **They also got SHARPER in the move.** ⛔ **They used to run through `check_board`, so
each had to build a register whose bijection was satisfied** — row files on disk, 400 of
them in one case — ⭐ **where `size_findings(text)` is a pure function of the board's TEXT
and can be asked the question directly.** ⚠️ **The composition is asserted separately and
once**, below, because *the arm works* and *the arm is wired in* are two claims.
"""

from __future__ import annotations

import math
from pathlib import Path

from tests.support import repository_root
from tools.quality.board import (
    BOARD,
    BOARD_FRAME,
    BOARD_NARRATIVE_CEILING,
    BOARD_PER_OBSERVATION_ROW,
    BOARD_PER_ROW,
    BOARD_PER_SCHEDULED_ROW,
    BOARD_ROW_CEILING,
    RULE_NARRATIVE,
    RULE_SIZE,
    RULE_WIDTH,
    check_board,
)
from tools.quality.board.bounds import allowance, size_findings
from tools.quality.board.register import is_closed, register
from tools.quality.report import Finding

from .support import REGISTER, REGISTER_END, rules

#: One closed register row, so the register is INHABITED: ⛔ `board-size`'s denominator is
#: the ids the register names, and a bound measured against an empty register would be
#: measuring the frame alone.
CLOSED = "| W1 | a naming | PO | ✅ done — `abc1234` | [record](BOARD-ARCHIVE.md#w1) |\n"


def _board(extra: str = "", register: str = CLOSED) -> str:
    """A board carrying `register` and then `extra`, with nothing else in it."""
    return f"# Board\n\n{REGISTER}{register}{REGISTER_END}{extra}"


def test_planted_narrative() -> None:
    """⛔ Prose outside every table, one byte over the ceiling."""
    prose = "x" * (BOARD_NARRATIVE_CEILING + 1) + "\n"
    findings = size_findings(_board(prose))
    assert rules(findings) == [RULE_NARRATIVE]
    assert str(BOARD_NARRATIVE_CEILING) in findings[0].message


def test_planted_narrative_disguised_as_a_table() -> None:
    """⛔ Ruling 140 — the plant is adversarial to the SEARCH TERM.

    ⚠️ A round's narrative written as `| … |` lines contributes **zero** to the narrative
    count. ⭐ **`board-row-width` is what closes that gap**, and this is the reading that
    proves the two bounds have none between them.
    """
    fat = "| " + "x" * (BOARD_ROW_CEILING + 1) + " |\n"
    found = rules(size_findings(_board(fat)))
    assert RULE_NARRATIVE not in found, "the narrative bound is blind to this, by construction"
    assert found == [RULE_WIDTH]


def test_planted_narrative_as_MANY_SHORT_table_rows() -> None:
    """⛔ The plant that GOT THROUGH, and the reason `board-size` exists.

    ⚠️ **Run against the first two bounds before this module shipped: 320 lines of round
    33's narrative, one line per table row, moved the narrative reading by ZERO and
    tripped the width rule ONCE.** ⭐ Neither bound sees text that is short per line and
    enormous in total.

    ⛔ **`board-size` does, because the evasion raises the numerator and leaves the
    denominator alone.**
    """
    prose = "".join(f"| a line of a round's reasoning, number {n} |\n" for n in range(400))
    found = rules(size_findings(_board(prose)))
    assert RULE_NARRATIVE not in found
    assert RULE_WIDTH not in found
    assert found == [RULE_SIZE]


def test_more_rows_can_never_trip_the_size_bound() -> None:
    """⭐ Ruling 149's failure mode, asserted absent rather than argued absent.

    ⛔ **The line-count governor it retired *"alarmed seven times while the property
    improved seven times"*.** ⚠️ **A ratio cannot do that only if a row raises the
    allowance by MORE than a row costs** — so that is what is measured here, at a row
    width well over this board's live mean of 170 B.
    """
    row = "| W{n} | " + "n" * (BOARD_PER_ROW - 60) + " | PO | `todo` | [d](rows/W{n}.md) |\n"
    many = "".join(row.format(n=100 + i) for i in range(400))
    assert RULE_SIZE not in rules(size_findings(_board(register=many)))


def test_the_size_bound_allows_the_frame_and_says_so() -> None:
    """⚠️ A board with NO register row still gets `BOARD_FRAME`, and nothing more."""
    found = size_findings(_board("x" * (BOARD_FRAME + 1), register=""))
    assert rules(found) == [RULE_NARRATIVE, RULE_SIZE]
    message = next(finding.message for finding in found if finding.rule == RULE_SIZE)
    assert f"{BOARD_FRAME} of frame, plus {BOARD_PER_ROW} for each of 0 register rows" in message
    # ⛔ `W130`: the two new terms are printed with their OWN counts, and both read `0`
    # here. ⭐ A term printed only when inhabited is a term nobody can audit (Ruling 48).
    assert f"{BOARD_PER_OBSERVATION_ROW} for each of 0 delimited observation rows" in message
    assert f"{BOARD_PER_SCHEDULED_ROW} for each of 0 delimited scheduled rows" in message
    assert "Raising a term is NOT the remedy" in message, "⛔ Ruling 271, in the message"


def test_the_denominator_is_the_IDS_the_register_NAMES_and_not_the_rows_it_carries() -> None:
    """⛔ `W17 + W19` are ONE register row naming TWO ids, and the allowance follows the IDS.

    ⚠️ **The arm used to be handed a count computed by `check_board`'s own loop**, and a
    second reading of one population is two readings that can disagree — ⭐ **so it
    derives the set itself, and this is the row that would have caught a drift.**
    """
    two = "| W17 + W19 | one commit, two ids | PO | `todo` | [d](rows/W17.md) |\n"
    over = BOARD_FRAME + 2 * BOARD_PER_ROW + 1
    findings = size_findings(_board("x" * over, register=two))
    assert "for each of 2 register rows" in (
        next(finding.message for finding in findings if finding.rule == RULE_SIZE)
    )


def test_the_bounds_arm_is_WIRED_INTO_check_board(tmp_path: Path) -> None:
    """⭐ *The arm works* and *the arm is called* are two claims, and this is the second.

    ⛔ **Asserted through the real entry point over a real tree**, because the split moved
    the code out of `check_board`'s own body and a `findings.extend` that was never added
    would leave every reading above green and the floor blind.
    """
    (tmp_path / "docs" / "tasks").mkdir(parents=True)
    (tmp_path / BOARD).write_text(_board("x" * (BOARD_NARRATIVE_CEILING + 1)), encoding="utf-8")
    found: list[Finding] = check_board(tmp_path)
    assert RULE_NARRATIVE in rules(found)


# --------------------------------------------------------------------------
# ⛔ `W130` / Ruling 271 — the DENOMINATOR counts the things the board HOLDS
# --------------------------------------------------------------------------


#: ⭐ A DELIMITED observation block with `count` rows in it, in the board's own shape.
def _inflight(count: int) -> str:
    rows = "".join(
        f"| `W{100 + n}` | Dev | `wt/dev1`, `fix/W{100 + n}-a-row` | +1 | in flight |\n"
        for n in range(count)
    )
    return (
        "<!-- inflight -->\n| Row | Owner | Checkout | Commits ahead | State |\n"
        "|---|---|---|---|---|\n" + rows + "<!-- /inflight -->\n"
    )


#: ⭐ A DELIMITED `## Scheduled` block with `count` rows in it.
def _scheduled(count: int) -> str:
    rows = "".join(
        f"| a thing, number {n} | when the wave after next opens | `pending` |\n"
        for n in range(count)
    )
    return (
        "<!-- scheduled -->\n| Item | Trigger | State |\n|---|---|---|\n"
        + rows
        + "<!-- /scheduled -->\n"
    )


def test_the_allowance_has_THREE_TERMS_and_each_counts_its_OWN_delimited_table() -> None:
    """⛔ Ruling 271's whole subject: the two tables that GREW are not register rows.

    ⚠️ **MEASURED by the PO at `6c4e3d0`: the board was 99.82 % consumed with 77 bytes of
    headroom, and `## In flight` had grown +1 880 B** — ⛔ **so the numerator moved and
    the denominator could not see it.** ⭐ **Here the three terms are read apart, so a
    term that stopped counting cannot be hidden by another that still does.**
    """
    bare = allowance(_board())
    assert bare == (BOARD_FRAME + BOARD_PER_ROW, 1, 0, 0)
    observed = allowance(_board(_inflight(3)))
    assert observed[2:] == (3, 0), observed
    assert observed[0] - bare[0] == 3 * BOARD_PER_OBSERVATION_ROW
    planned = allowance(_board(_scheduled(5)))
    assert planned[2:] == (0, 5), planned
    assert planned[0] - bare[0] == 5 * BOARD_PER_SCHEDULED_ROW
    both = allowance(_board(_inflight(3) + _scheduled(5)))
    assert both[0] == bare[0] + 3 * BOARD_PER_OBSERVATION_ROW + 5 * BOARD_PER_SCHEDULED_ROW


def test_DIRECTION_ONE_a_board_that_grows_by_an_OBSERVATION_ROW_PASSES() -> None:
    """⭐ The direction Ruling 271 asks for, and the slope is asserted as a NUMBER.

    ⛔ **The defect was the SLOPE, not the size** — ⚠️ **before this, an observation row
    raised the numerator by its own bytes and the allowance by ZERO, so obeying Ruling
    246 in an observation column cost the board headroom it could never earn back.**

    ⭐ **Now a row of EITHER delimited table earns more than it costs, which is the
    property `BOARD_PER_ROW` has always had for the register.**
    """
    base = _board(_inflight(1) + _scheduled(1))
    grown = _board(_inflight(2) + _scheduled(2))
    assert rules(size_findings(base)) == [], "the control: the base board is clean"
    assert rules(size_findings(grown)) == [], "⭐ and growing by one row of each stays clean"
    slope = (allowance(grown)[0] - allowance(base)[0]) - (len(grown.encode()) - len(base.encode()))
    assert slope > 0, f"⛔ a row of a delimited table must EARN, and this one earned {slope}"


def test_DIRECTION_TWO_prose_written_as_TABLE_ROWS_still_FAILS() -> None:
    """⛔ The evasion `bounds.py`'s own docstring says this bound exists to catch.

    ⚠️ **It GOT THROUGH once: 320 lines of round 33's narrative, one line per table row,
    moved the narrative reading by ZERO and tripped the width rule ONCE.** ⭐ **`W130`
    widened the DENOMINATOR, so this is the direction that had to be re-asserted** —
    ⛔ **a wider denominator that also admitted the evasion would have traded one defect
    for the one the bound was built against.**

    ⭐ **The reason it still fails is structural and is asserted, not hoped: both table
    parsers require a data row to carry at least as many cells as their DECLARED HEADER
    has roles**, so one-cell prose rows are read by neither — ⚠️ **and the plant is put
    INSIDE both delimited blocks, which is the adversarial placement.**
    """
    prose = "".join(f"| a line of a round's reasoning, number {n} |\n" for n in range(400))
    inside = (
        "<!-- inflight -->\n| Row | Owner | Checkout | Commits ahead | State |\n"
        "|---|---|---|---|---|\n" + prose + "<!-- /inflight -->\n"
        "<!-- scheduled -->\n| Item | Trigger | State |\n|---|---|---|\n"
        + prose
        + "<!-- /scheduled -->\n"
    )
    board = _board(inside)
    allowed, indexed, observations, scheduled = allowance(board)
    assert (observations, scheduled) == (0, 0), (
        "⛔ 800 prose rows inside the two delimited blocks raised NEITHER denominator"
    )
    assert allowed == BOARD_FRAME + BOARD_PER_ROW * indexed
    found = rules(size_findings(board))
    assert RULE_NARRATIVE not in found, "the narrative bound is blind to this, by construction"
    assert RULE_WIDTH not in found, "and every line is short"
    assert found == [RULE_SIZE], "⛔ only `board-size` sees it, which is the whole of the bound"


def test_only_DELIMITED_rows_count_so_a_RAMP_located_table_earns_NOTHING() -> None:
    """⛔ A population grows BY A DELIMITER and never by inference (ruled round 49).

    ⚠️ **`observation.read` still answers for a board with NO marker, through Ruling
    196(b)'s header RAMP** — ⭐ **that reading is right for its own purpose and WRONG in a
    denominator:** ⛔ **an inferred population here would let anyone write an ordinary
    five-column table declaring `Checkout` and `State` and collect the allowance, which
    is the Ruling 140 evasion with a header on it.**
    """
    ramp = _inflight(4).replace("<!-- inflight -->\n", "").replace("<!-- /inflight -->\n", "")
    assert "| `W100` |" in ramp, "⛔ born vacuous: the plant must carry real rows"
    assert allowance(_board(ramp))[2] == 0, "⭐ a header-located table earns nothing"
    assert allowance(_board(_inflight(4)))[2] == 4, "and the DELIMITED one earns four"


def test_the_DERIVATION_RULE_re_derives_BOARD_PER_ROW_from_the_LIVE_REGISTER() -> None:
    """⛔ Ruling 277: the figure is DERIVED, and the rule is validated against a constant
    nobody chose for it.

    ⭐ **THE RULE: a per-row term is its population's MEASURED MEAN LINE, rounded UP to
    the next multiple of 32, plus one further 32.** ⚠️ **Applied to the LIVE register of
    the real board it must return `BOARD_PER_ROW` — 224 — which is the constant that has
    shipped since the split and was set from the `~170 B` measured there.**

    ⛔ **This is the test that stops the new terms being numbers somebody liked.** ⚠️ **It
    reads the LIVE board, so it is a reading of the COMMIT and not of the host** — the
    board is a tracked file and `test_host_population.py` names that distinction.
    """
    text = (repository_root() / BOARD).read_text(encoding="utf-8")
    lines = text.split("\n")
    live = [lines[number - 1] for number, _ids, cell in register(text) if not is_closed(cell)]
    assert len(live) >= 10, f"born vacuous: {len(live)} live register lines"
    mean = sum(len(line.encode()) + 1 for line in live) / len(live)
    assert _rule(mean) == BOARD_PER_ROW, (
        f"⛔ the derivation rule returns {_rule(mean)} for a live register mean of "
        f"{mean:.1f} B and `BOARD_PER_ROW` is {BOARD_PER_ROW}. ⭐ Either the rule or the "
        f"constant has moved, and `bounds.py`'s derivation table says which is which."
    )
    # ⭐ And the two new terms obey the SAME rule, so there is one rule and not three.
    assert _rule(97.5) == BOARD_PER_OBSERVATION_ROW
    assert _rule(418.4) == BOARD_PER_SCHEDULED_ROW


def _rule(mean: float) -> int:
    """The derivation rule, written once: ceil to the next multiple of 32, plus 32."""
    return 32 * math.ceil(mean / 32) + 32
