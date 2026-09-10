"""The board is a register, and this is what keeps it one.

**What it does.** Reads `docs/tasks/BOARD.md` and the per-row files beside it in
`docs/tasks/rows/`, and fails the build on the four ways a register stops being
one: a row whose argument has no home, a detail file with no row, one id written
twice, and **narrative** — prose or a fat cell — accreting in a file every agent
in this project is told to read.

**How you use it.** `check_board(root)` is registered in `tools.quality.CHECKS`;
`board_state(root)` is registered in `NOTICES` and prints the population every
run, because a `0` with no denominator is `0 = 0` (Ruling 48).

**Depends on.** `config` for the tree and `report` for the answer. Nothing else.

## ⛔ Why this exists, and the number is the argument

⚠️ **`BOARD.md` was split once already, in round 25, for being 1,615 lines and
~180KB.** ⛔ **Twelve rounds later it was 8,545 lines and 753KB — four times the
size that triggered the split — and the paragraph announcing the split still
said the live board was "~56KB".** ⭐ **Nothing noticed, because nothing was
measuring.**

⛔ **The rule was never missing.** `docs/conventions/delivery-flow.md` has said
since it was written that *"a status change is one cell"* and that an event goes
to the Log rather than into the tables. ⚠️ **A rule recorded only in prose has
not landed** — this project's own most-repeated finding, committed by the
document that governs the board.

## ⭐ The two bounds, and why neither is a line count

⛔ **Ruling 149 retired a line-count governor on `review-rubric.md`** because it
*"alarmed seven times while the property improved seven times"* — the document
was growing because it had more to say, and the governor could not tell that
from accretion. ⚠️ **A line ceiling on this file would fail the same way**: a
backlog with more rows in it is a longer board and a *better* one.

⭐ **So both bounds here are invariant to the number of rows.**

| Bound | What it measures | Why adding rows cannot trip it |
|---|---|---|
| `BOARD_NARRATIVE_CEILING` | bytes **not inside a table** | the frame is fixed; a new
  row is a table line and contributes **nothing** to it |
| `BOARD_ROW_CEILING` | bytes of **one table row** | a row's width is a property of
  that row, not of how many there are |
| `BOARD_FRAME` + `BOARD_PER_ROW` | the **whole file**, against what its register
  indexes | a row raises the allowance by more than it costs |

⛔ **The second bound is not decoration, and the measurement says so.** At
`bfb8c8c` the board's table rows carried **388,649 bytes** against **382,194**
of prose — ⭐ **the cells were as fat as the narrative**, and a governor watching
only prose would have called that board half-clean. ⚠️ **The widest single row
was 3,485 bytes.** ⛔ **A cell that needs more than `BOARD_ROW_CEILING` is an
argument, and an argument goes behind a pointer.**

## ⚠️ The evasion this is built against (Ruling 140)

⛔ **The adversarial move is not more prose; it is prose written as a table**, so
that a narrative-blind byte count reads it as rows. ⚠️ **That plant was run
against the first two bounds before this module shipped and IT GOT THROUGH:**
⛔ **320 lines of round 33's narrative, pasted one line per table row, moved the
narrative reading by ZERO and tripped the width rule exactly ONCE.**

⭐ **`board-size` is the answer, and it is the third bound rather than a tweak to
the other two**, because the property it measures is different: not *how much
prose* but *how much file per row of state a reader gets for it*. ⛔ **Text that
indexes nothing raises the numerator and not the denominator**, which is the
whole of the evasion and the whole of the bound.

⚠️ **The other two are kept, and they are kept as DIAGNOSIS.** `board-size` says
the board is too big; ⭐ **`board-narrative` and `board-row-width` say WHERE**,
and a governor that only says *too big* is one somebody raises rather than
obeys.

## ⛔ What this deliberately does NOT assert

⚠️ **Nothing about a row's *content*.** Whether a naming is a good naming, an
owner right, or a state current, is the PO's judgement and check 4's job. ⭐ This
module asserts **shape**: that every fact has exactly one home, and that the
home a reader is told to load stays loadable.

⛔ **And nothing about `BOARD-ARCHIVE.md`'s size.** A record is *supposed* to
grow monotonically; that is what makes it a record. ⭐ **Bounding it would push
the reasoning back onto the board**, which is the defect, not the remedy.
"""

from pathlib import Path

from tools.quality.config import read_text, relative
from tools.quality.report import Finding

#: The register itself. ⛔ One file, named here rather than discovered, because
#: a check that hunts for the board would pass on a repository that had lost it.
BOARD = "docs/tasks/BOARD.md"

#: The directory holding one file per live row. ⛔ Its name is part of the
#: contract in `docs/conventions/board.md`, not an implementation detail.
ROWS = "docs/tasks/rows"

#: ⛔ The register is DELIMITED, and this check reads nothing outside the
#: markers. ⚠️ **The first version inferred it — *any five-cell row whose first
#: cell names a `W` id* — and the very next edit broke it**: an *In flight*
#: table naming four rows was read as four duplicate register rows, and
#: `board-duplicate` fired on the author of `board-duplicate`.
#:
#: ⭐ **A board may hold as many `W`-shaped tables as it likes; exactly one of
#: them is the register, and it says so.** ⛔ An inferred boundary is a boundary
#: that moves when somebody writes an ordinary table.
REGISTER_OPEN = "<!-- register -->"
REGISTER_CLOSE = "<!-- /register -->"

#: ⛔ Bytes of `BOARD.md` outside any table. Measured **3,811** at the split;
#: this is 2.1× that, which is room for the frame to gain a section and not
#: room for a round's narrative — round 33's alone was 833 lines.
BOARD_NARRATIVE_CEILING = 8192

#: ⛔ Bytes of one table row. Measured widest **415** at the split against
#: **3,485** before it. ⭐ 600 is the project's own test-file ceiling, reused so
#: a reader has one number to remember rather than two.
BOARD_ROW_CEILING = 600

#: ⛔ The board's whole size is bounded as `BOARD_FRAME + BOARD_PER_ROW × register
#: rows`. ⭐ **This is the bound that has no gap**, and it exists because the
#: Ruling 140 plant found one in the other two before this shipped: 320 lines of
#: a round's narrative, pasted as one-cell table rows, moved the narrative count
#: by ZERO and tripped the width rule ONCE.
#:
#: ⚠️ Measured at the split: **23,839 B** total over **78** register rows, of
#: which the register itself is the majority — **~170 B a row**. ⭐ A ratio
#: rather than a ceiling is Ruling 149's own
#: remedy for a governor that alarms while the property improves: adding rows
#: raises the allowance by more than a row costs, so a longer backlog can never
#: trip this, and only text that indexes nothing can.
BOARD_FRAME = 14336
BOARD_PER_ROW = 224

#: ⛔ The one state that means a row is finished and its argument belongs in a
#: record rather than in a file that can still be amended. ⚠️ `accepted` is NOT
#: here: an accepted row still carries a trigger and a remedy, so its argument
#: is still amendable and still needs a file that can be edited.
CLOSED_STATES = ("done",)

RULE_DETAIL = "board-detail"
RULE_ORPHAN = "board-orphan"
RULE_DUPLICATE = "board-duplicate"
RULE_NARRATIVE = "board-narrative"
RULE_WIDTH = "board-row-width"
RULE_SIZE = "board-size"


def _cells(line: str) -> list[str]:
    """Return the cells of a markdown table row, outer pipes stripped."""
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def _identifiers(cell: str) -> list[str]:
    """Return every `W`-row id a register's first cell names.

    ⚠️ A cell may name two — `W17 + W19` are one commit and one row — so this
    returns a list. ⛔ A cell naming none is a header or a separator and is not
    a register row.
    """
    found = []
    for token in cell.replace("*", "").replace("`", "").replace("+", " ").split():
        if len(token) > 1 and token[0] == "W" and token[1:].isdigit():
            found.append(token)
    return found


def _register(text: str) -> list[tuple[int, list[str], str]]:
    """Return `(line number, ids, state cell)` for every register row.

    ⛔ Only between `REGISTER_OPEN` and `REGISTER_CLOSE`. ⚠️ A board with no
    markers has no register as far as this is concerned, and `board_state`
    prints `0 register rows` rather than guessing — ⭐ **`0 = 0` is visible;
    a wrong denominator is not.**
    """
    rows = []
    inside = False
    for number, line in enumerate(text.split("\n"), 1):
        if line.strip() == REGISTER_OPEN:
            inside = True
            continue
        if line.strip() == REGISTER_CLOSE:
            inside = False
            continue
        if not inside or not line.startswith("|"):
            continue
        cells = _cells(line)
        if len(cells) < 5:
            continue
        ids = _identifiers(cells[0])
        if ids:
            rows.append((number, ids, cells[3]))
    return rows


def _is_closed(state: str) -> bool:
    return any(word in state.lower() for word in CLOSED_STATES)


def _rows_on_disk(root: Path) -> dict[str, Path]:
    directory = root / ROWS
    if not directory.is_dir():
        return {}
    return {path.stem: path for path in sorted(directory.glob("*.md"))}


def _table_lines(text: str) -> list[tuple[int, str]]:
    return [(n, line) for n, line in enumerate(text.split("\n"), 1) if line.startswith("|")]


def _narrative_bytes(text: str) -> int:
    return sum(len(line.encode()) + 1 for line in text.split("\n") if not line.startswith("|"))


def check_board(root: Path) -> list[Finding]:
    """Report every way this board has stopped being a register.

    ⛔ **The bijection is asserted in BOTH directions**, and that is deliberate:
    a live row with no detail file is an argument with no home, and a detail
    file with no row is a file nobody will ever be sent to. ⭐ One of the two
    always survives a careless edit, which is exactly why the check that only
    looks one way is the one that misses.
    """
    text = read_text(root / BOARD)
    if text is None:
        # ⛔ Not a finding, and this is `check_knowledge_index`'s split, reused.
        # The floor runs over ARBITRARY roots — a temp tree, a corpus
        # repository — and a check that failed every tree that is not this one
        # would be asserting *which repository you are in*. ⭐ Absence is
        # reported by `board_state` and enforced by
        # `test_this_repository_has_a_board`, which is the only place that
        # knows the answer should be yes.
        return []

    findings: list[Finding] = []
    on_disk = _rows_on_disk(root)
    seen: dict[str, int] = {}
    expected: set[str] = set()

    for number, ids, state in _register(text):
        for identifier in ids:
            if identifier in seen:
                findings.append(
                    Finding(
                        BOARD,
                        number,
                        RULE_DUPLICATE,
                        f"{identifier} already has a register row at line {seen[identifier]}. "
                        f"An id gets ONE row; a second one is how a status disagrees with itself.",
                    )
                )
            else:
                seen[identifier] = number
        if _is_closed(state):
            continue
        # The first id of a multi-id row owns the file; the rest ride with it.
        expected.add(ids[0])
        if ids[0] not in on_disk:
            findings.append(
                Finding(
                    BOARD,
                    number,
                    RULE_DETAIL,
                    f"{ids[0]} is not closed and has no {ROWS}/{ids[0]}.md. A live row's argument "
                    f"is AMENDED, so it may not live in the archive, and it may not live in this "
                    f"cell either.",
                )
            )

    for identifier, path in on_disk.items():
        if identifier not in expected:
            findings.append(
                Finding(
                    relative(path, root),
                    1,
                    RULE_ORPHAN,
                    f"{identifier} has a detail file and no live register row. Either the row "
                    f"closed — in which case its argument belongs in BOARD-ARCHIVE.md — or the "
                    f"register lost it.",
                )
            )

    narrative = _narrative_bytes(text)
    if narrative > BOARD_NARRATIVE_CEILING:
        findings.append(
            Finding(
                BOARD,
                1,
                RULE_NARRATIVE,
                f"{narrative} bytes of narrative against a ceiling of {BOARD_NARRATIVE_CEILING}. "
                f"The board is a register: a round's reasoning goes to BOARD-ARCHIVE.md and a "
                f"row's goes to {ROWS}/. See docs/conventions/board.md.",
            )
        )

    allowed = BOARD_FRAME + BOARD_PER_ROW * len(seen)
    size = len(text.encode())
    if size > allowed:
        findings.append(
            Finding(
                BOARD,
                1,
                RULE_SIZE,
                f"{size} bytes against {allowed} allowed — {BOARD_FRAME} of frame plus "
                f"{BOARD_PER_ROW} for each of {len(seen)} register rows. ⛔ The board grew "
                f"without indexing anything more. See docs/conventions/board.md.",
            )
        )

    for number, line in _table_lines(text):
        width = len(line.encode())
        if width > BOARD_ROW_CEILING:
            findings.append(
                Finding(
                    BOARD,
                    number,
                    RULE_WIDTH,
                    f"row is {width} bytes against a ceiling of {BOARD_ROW_CEILING}. A cell that "
                    f"long is an argument, and an argument goes behind a pointer.",
                )
            )

    return findings


def board_state(root: Path) -> list[str]:
    """Print the population before it is reduced to a verdict (Ruling 128).

    ⛔ Where there is no board this SAYS SO rather than returning nothing: a
    silent notice about an absent register is the `0 = 0` this exists to stop
    (Ruling 48), and the honest line names who does enforce presence.
    """
    text = read_text(root / BOARD)
    if text is None:
        return [
            f"board: none — no {BOARD} in this checkout. This is not a failure: the floor "
            f"runs over trees that are not this repository. ⛔ In THIS repository its "
            f"absence is a build failure, and tools/tests/quality/test_board.py says so."
        ]
    register = _register(text)
    identifiers = {i for _n, ids, _s in register for i in ids}
    live = [row for row in register if not _is_closed(row[2])]
    rows_on_disk = _rows_on_disk(root)
    table = _table_lines(text)
    widest = max((len(line.encode()) for _n, line in table), default=0)
    return [
        f"board: {len(register)} register rows, {len(live)} live, "
        f"{len(rows_on_disk)} detail files in {ROWS}/; "
        f"{_narrative_bytes(text)} bytes narrative of {BOARD_NARRATIVE_CEILING}, "
        f"widest row {widest} of {BOARD_ROW_CEILING}, "
        f"{len(text.encode())} bytes total of "
        f"{BOARD_FRAME + BOARD_PER_ROW * len(identifiers)} allowed."
    ]
