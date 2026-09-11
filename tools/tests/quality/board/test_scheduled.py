"""Mirror of `tools/quality/board/scheduled.py` (R12) — `W100`, and the PO handed over its
pass conditions before it was dispatched.

⛔ **Two of them are asserted here rather than discovered** (`rows/W100.md`, `PO-42/4` and
the hazard note beneath it):

| Handed over | Asserted by |
|---|---|
| ⛔ a board line that MENTIONS the marker inside a cell is NOT a declaration |
  `test_planted_a_cell_that_MENTIONS_the_marker_declares_NOTHING` |
| ⭐ the vocabulary is FOUR words and a standing trigger is `fired` (Ruling 233) |
  `test_the_vocabulary_is_the_RULED_four_and_a_STANDING_trigger_is_fired` |

⭐ **The three readings are LIVE, PLANTED and IMPOSSIBLE** (Ruling 123), and the live one
is deliberately written so that it cannot go red for the board being RIGHT: ⛔ **it asserts
the arithmetic of the population, never its size** — ⚠️ **a pinned `7` would be a
measurement in a test, stale the next time the PO schedules anything** (Ruling 181's
family, one layer down).
"""

from __future__ import annotations

from pathlib import Path

from tools.quality.board import (
    BOARD,
    RULE_TRIGGER,
    RULE_UNREADABLE,
    SCHEDULED_CLOSE,
    SCHEDULED_OPEN,
    TRIGGER_STATES,
    check_board,
)
from tools.quality.board.register import BOARD as BOARD_PATH
from tools.quality.board.scheduled import (
    DELIMITED,
    NONE_FOUND,
    read,
    scheduled_findings,
    scheduled_reading,
)

from .support import rules

#: The header the live `## Scheduled` table declares, verbatim. ⛔ Written out rather than
#: generated: the header is the DECLARATION the locator reads, and a paraphrase would test
#: a shape the board does not author.
HEADER = "| Item | Owner | State | Trigger | Decision |\n|---|---|---|---|---|\n"

#: ⛔ **A header declaring NEITHER role** — `W111`'s subject one table over: a table that is
#: still a table, with its two load-bearing columns renamed to nothing the locator knows.
RENAMED = "| Item | Owner | Phase | When | Decision |\n|---|---|---|---|---|\n"

#: ⭐ One row per inhabited state, and the `fired` one is the STANDING trigger Ruling 233
#: settled: ⛔ **it has fired and it will fire again, and `fired` is the correct value.**
ROWS = (
    "| a skill is authored | PO | `discharged` — carried into `E11` | `SK-07` is authored | x |\n"
    "| the `Effort` field | PO | `fired` — ⚠️ a STANDING trigger | as each task is assigned | x |\n"
    "| the ISO pin | PO | `pending` | the ISO track reaches a finish line | x |\n"
    "| the back-triage | PO | `expired` — the event passed unfired | ⛔ M1's wave opens | x |\n"
)

#: ⛔ **A cell that MENTIONS a state word without DECLARING one** — the anti-substring
#: reading, and it is `is_closed`'s founding defect one table over: ⚠️ the first `is_closed`
#: asked whether `done` appeared ANYWHERE and a live row walked straight out of the
#: register.
MENTIONS = "| the triage | PO | ⚠️ the work was discharged round by round | an event | x |\n"


def _board(table: str = HEADER + ROWS, *, delimited: bool = True, extra: str = "") -> str:
    """A board whose `## Scheduled` table is DELIMITED, as the contract requires."""
    if delimited:
        table = f"{SCHEDULED_OPEN}\n{table}{SCHEDULED_CLOSE}\n"
    return f"# Board\n\n## Scheduled\n\n{table}{extra}"


# --------------------------------------------------------------------------
# Reading 1 — LIVE, against the board this repository actually carries
# --------------------------------------------------------------------------


def test_live_the_real_scheduled_table_DECLARES_A_STATE_ON_EVERY_ROW() -> None:
    """⭐ The reading that makes the planted ones mean something.

    ⛔ **No size is pinned.** ⚠️ **`7` rows on the day this landed, and the PO schedules
    things** — ⭐ so what is asserted is the ARITHMETIC: the table is located by its
    delimiter, it is inhabited, every row declares a state from the closed set, and the
    per-state counts sum to the rows.
    """
    text = Path(BOARD_PATH).read_text(encoding="utf-8")
    schedule = read(text)
    assert schedule.locator == DELIMITED and schedule.blocks == 1
    assert schedule.unreadable == ()
    assert schedule.rows, "⛔ born vacuous: this repository's board carries scheduled items"
    assert [row.line for row in schedule.rows if row.declared is None] == []
    declaring = [row.declared for row in schedule.rows if row.declared in TRIGGER_STATES]
    assert len(declaring) == len(schedule.rows)
    assert scheduled_findings(text) == []


def test_live_the_reading_names_EVERY_word_of_the_vocabulary_with_its_count() -> None:
    """⛔ Ruling 191: the UNINHABITED states are named, not silently absent.

    ⚠️ **`expired` was inhabited only as a trigger's PROSE and not as a STATE on the day
    the column landed**, which is a real gap in the inhabitation — ⭐ **so the line prints
    every word with its count and says which words no row carries**, and a reader can see
    the gap without being told about it.

    ⛔ **Both marker numbers are printed WITH THEIR UNITS** (Ruling 224): the lines that ARE
    a declaration, and the lines that MENTION the marker inside a cell.
    """
    line = scheduled_reading(Path(BOARD_PATH).read_text(encoding="utf-8"))
    assert line.startswith("scheduled (delimited")
    for word in TRIGGER_STATES:
        assert f"{word} " in line, word
    assert "states with no row at all:" in line
    assert "declaration line(s)" in line and "MENTIONING the marker inside a cell" in line


# --------------------------------------------------------------------------
# Reading 2 — PLANTED, one per clause the ruling and the PO handed over
# --------------------------------------------------------------------------


def test_planted_a_row_that_DECLARES_NO_STATE_is_board_trigger() -> None:
    """⛔ The whole defect: a cell carrying an obligation that could not say what it was."""
    findings = scheduled_findings(_board(HEADER + MENTIONS))
    assert rules(findings) == [RULE_TRIGGER]
    # ⛔ The board's OWN path and the row's own line: `# Board`, a blank, `## Scheduled`,
    # a blank, the marker at 5, the header at 6, its separator at 7, the row at 8.
    assert (findings[0].path, findings[0].line) == (BOARD, 8)
    assert "expired" in findings[0].message, "⭐ the remedy names the word the cell needed"


def test_planted_a_cell_that_MENTIONS_the_marker_declares_NOTHING() -> None:
    """⛔ The PO's own hazard, handed over with its pass condition (`rows/W100.md`).

    ⚠️ **MEASURED by the PO at `0ba512d`: three board lines contain the marker text and
    two of them ARE a marker** — ⛔ **the third is a table cell naming this row's own
    gate.** ⭐ **So the locator tests `line.strip() ==` and never `in line`**, and an `in`
    test would have read that cell as a block opener and swallowed the register beneath it.
    """
    cell = f"| W100 | its gate is the {SCHEDULED_OPEN} marker | PO | `todo` | x |\n"
    only_a_mention = f"# Board\n\n{HEADER}{ROWS}{cell}"
    assert read(only_a_mention).locator == NONE_FOUND, "⛔ a MENTION declares no block"
    assert scheduled_findings(only_a_mention) == []

    both = _board(extra=cell)
    schedule = read(both)
    assert (schedule.blocks, schedule.mentions) == (1, 1)
    assert len(schedule.rows) == 4, "⭐ the four real rows, and not the cell beneath them"
    assert scheduled_findings(both) == []


def test_planted_a_DECLARED_block_whose_header_declares_NEITHER_role_is_REFUSED() -> None:
    """⛔ `W111`'s clause, one table over: a DECLARED block that did not read is a FINDING.

    ⚠️ **The delimiter alone does not fix it** — inside the markers the roles are still
    taken from the header — ⭐ **so the refusal is what makes the declaration load-bearing**,
    and without it a renamed column reads as *there is nothing scheduled* on a green floor.
    """
    findings = scheduled_findings(_board(RENAMED + ROWS))
    assert rules(findings) == [RULE_UNREADABLE]
    assert findings[0].line == 5, "⛔ the line of the MARKER, which is what the author wrote"
    assert read(_board(RENAMED + ROWS)).rows == ()


def test_planted_the_ROLES_are_read_FROM_the_header_and_the_columns_may_MOVE() -> None:
    """⭐ Ruling 189(b)'s own prohibition: this must NOT pin the column names.

    ⛔ **Renamed, reordered, emphasised and prefixed headers all READ** — ⚠️ **the refusal
    fires on a header declaring NO role and never on one declaring them differently**, or
    the instrument would forbid the PO the edits the board is theirs to make.
    """
    authorable = (
        "| Item | Owner | **State** | Trigger | Decision |\n|---|---|---|---|---|\n",
        "| Item | Owner | Status | Trigger fires when | Decision |\n|---|---|---|---|---|\n",
        "| ⭐ Item | Owner | State of it | ⛔ Trigger | Decision |\n|---|---|---|---|---|\n",
    )
    for header in authorable:
        schedule = read(_board(header + ROWS))
        assert schedule.unreadable == (), header
        assert len(schedule.rows) == 4, header
    moved = "| State | Item | Trigger |\n|---|---|---|\n| `pending` | a thing | an event |\n"
    schedule = read(_board(moved))
    assert [(row.declared, row.subject) for row in schedule.rows] == [("pending", "a thing")]


def test_planted_the_state_is_the_FIRST_WORD_and_a_BOUNDARY_ends_the_match() -> None:
    """⛔ The anti-substring reading, inherited from `register.declared` and asserted here.

    ⚠️ **`is_closed` was once a substring test and a live row reading `` `todo` — after
    `W44` is done `` was therefore CLOSED.** ⭐ **`pendingish` declares nothing, a trailing
    narrative does not matter, and a cell that merely MENTIONS a state word declares
    nothing** — which is the same remedy applied to a second vocabulary.
    """
    declaring = "| a thing | PO | ⛔ **`discharged`** — and then a whole sentence | e | x |\n"
    boundary = "| a thing | PO | pendingish | e | x |\n"
    assert [row.declared for row in read(_board(HEADER + declaring)).rows] == ["discharged"]
    assert [row.declared for row in read(_board(HEADER + boundary)).rows] == [None]
    assert rules(scheduled_findings(_board(HEADER + boundary))) == [RULE_TRIGGER]


def test_the_vocabulary_is_the_RULED_four_and_a_STANDING_trigger_is_fired() -> None:
    """⛔ Ruling 233 — there is NO fifth state, and `PO-42/4` was answered before dispatch.

    ⭐ **The four words are points on one LIFECYCLE and are mutually exclusive.** ⚠️ **A
    standing trigger is `fired` (it has fired) AND `pending` (it will fire again) at once**,
    so `standing` would make the set non-exclusive — ⛔ **the one property a closed
    vocabulary must keep.** ⭐ **If a genuine standing trigger that is not a convention ever
    appears, the answer is a `once`/`standing` KIND column, never a fifth state.**

    ⚠️ **So this asserts the set is EXACTLY four, and the `fired` cell is CORRECT rather
    than tolerated** — the row file's first candidate answer, ruled.
    """
    assert sorted(TRIGGER_STATES) == ["discharged", "expired", "fired", "pending"]
    standing = "| the `Effort` field | PO | `fired` — a STANDING trigger | as assigned | x |\n"
    rows = read(_board(HEADER + standing)).rows
    assert [row.declared for row in rows] == ["fired"]
    assert scheduled_findings(_board(HEADER + standing)) == []
    assert [row.settled for row in rows] == [False], "⭐ it owes its next firing"


def test_an_EXPIRED_trigger_is_REPRESENTABLE_and_is_not_a_disposition() -> None:
    """⭐ The member the whole row is about: the trigger that expired could not SAY so.

    ⛔ **`expired` declares cleanly and yields NO finding** — ⚠️ **the defect is a cell that
    cannot report its state, never a cell reporting a bad one** — ⭐ **and `expired` is not
    `settled`: an expired trigger still owes whatever it scheduled.** ⚠️ **That reading is
    this module's and not the ruling's, so it decides NOTHING that can fail a build: it is
    printed by the notice and nowhere else.**
    """
    expired = "| the back-triage | PO | `expired` — it named M1's wave open | ⛔ passed | x |\n"
    rows = read(_board(HEADER + expired)).rows
    assert [(row.declared, row.settled) for row in rows] == [("expired", False)]
    assert scheduled_findings(_board(HEADER + expired)) == []


def test_planted_an_UNCLOSED_block_is_still_judged_at_END_OF_FILE() -> None:
    """⛔ Otherwise deleting ONE line restores `NONE FOUND` to a table the author declared.

    ⭐ **The same property `observation.py` asserts of its own markers**, and it is asserted
    here rather than assumed shared: the two parsers are two modules.
    """
    unclosed = f"# Board\n\n{SCHEDULED_OPEN}\n{RENAMED}{ROWS}"
    assert read(unclosed).unreadable == (3,)
    assert rules(scheduled_findings(unclosed)) == [RULE_UNREADABLE]


def test_the_scheduled_arm_is_WIRED_INTO_check_board(tmp_path: Path) -> None:
    """⭐ *The arm works* and *the arm is called* are two claims, and this is the second."""
    (tmp_path / "docs" / "tasks").mkdir(parents=True)
    (tmp_path / BOARD).write_text(_board(HEADER + MENTIONS), encoding="utf-8")
    assert rules(check_board(tmp_path)) == [RULE_TRIGGER]


# --------------------------------------------------------------------------
# Reading 3 — IMPOSSIBLE: a board with no marker, which is most boards
# --------------------------------------------------------------------------


def test_impossible_a_board_with_NO_MARKER_yields_nothing_and_the_reading_SAYS_SO() -> None:
    """⛔ The floor runs over ARBITRARY ROOTS, so absence may not be a finding.

    ⚠️ **A temp tree or a corpus repository's own board has no `## Scheduled` table at
    all** — ⭐ **a refusal there would be asserting which repository you are in**, which is
    `check_knowledge_index`'s split and `check_board`'s own answer for a missing board.

    ⛔ **And the reading DIFFERS from the delimited one** (Ruling 191(a)): *nothing was
    read* and *nothing is scheduled* are not the same answer, so the locator is in the
    line.
    """
    bare = _board(delimited=False)
    assert scheduled_findings(bare) == []
    assert read(bare).locator == NONE_FOUND
    assert read(bare).rows == (), "⛔ and NO header branch: there is no ramp to fall back to"
    reading = scheduled_reading(bare)
    assert NONE_FOUND in reading and "not the same answer" in reading
    assert reading != scheduled_reading(_board()), "⭐ the two readings must DIFFER"


def test_impossible_an_EMPTY_DECLARED_block_is_read_and_says_nothing_is_scheduled() -> None:
    """⭐ A DECLARED, READABLE, EMPTY table is a real answer and not a refusal.

    ⛔ **`W111`'s settled distinction, one table over:** the header declares the roles, so
    the block READ — ⚠️ **and *nothing is scheduled* must not fire on a PO who has
    scheduled nothing.**
    """
    empty = _board(HEADER)
    schedule = read(empty)
    assert (schedule.locator, schedule.blocks, schedule.rows, schedule.unreadable) == (
        DELIMITED,
        1,
        (),
        (),
    )
    assert scheduled_findings(empty) == []
    assert "0 rows" in scheduled_reading(empty)
