r"""Reading a register out of a markdown table, and it is the parser that is hard.

**What it does.** Turns `BOARD.md`'s delimited register into
`(line number, ids, state cell)` rows, and answers what state a cell DECLARES.

**How you use it.** `tools.quality.board` imports `register`, `state`,
`is_closed`, `cells` and the two markers. Nothing else does.

**Depends on.** `re` and `pointers.strip_code_spans`. Nothing else, ever.

## ⛔ Two defects live here, and both shipped before they were caught

⚠️ **A naive `split("|")` tore three register rows apart in mid-sentence**, at
``(py|md under tests/fixtures/)``, ``'gated BEFORE\|gated before'`` and
``` `\| wc -l` ``` — ⭐ **every one a pipe INSIDE A CODE SPAN, which is a pipe
no renderer splits on either.** ⛔ **The text of the wrong cell was then written
into `rows/W38.md`, `rows/W40.md` and `rows/W53.md`, where it existed nowhere
else in the tree** — and the migration's own line-count assertion passed while
it happened. ⭐ **Ruling 177 is the general lesson; `cells` is the specific fix.**

⚠️ **`is_closed` was a SUBSTRING TEST.** ⛔ **A live row reading
`` `todo` — after `W44` is done `` was therefore closed**: no detail file owed,
out of the bijection, floor green, no finding. ⭐ **28 cells carry the
`✅ done — <ref>` idiom today**, so the failure was one clause from routine
rather than exotic. ⛔ **The remedy is the standard one — make the illegal value
unrepresentable: a cell DECLARES its state as its first word or it is a
finding.**
"""

import re

from tools.quality.pointers import strip_code_spans

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

#: ⛔ **The closed vocabulary of states, and it is CLOSED because the first
#: version was a substring test that a live row could walk straight out of.**
#:
#: ⚠️ `is_closed` used to ask whether `"done"` appeared ANYWHERE in the cell.
#: ⛔ **A live row reading `` `todo` — after `W44` is done `` was therefore
#: CLOSED**: it needed no detail file, left the bijection, and the floor stayed
#: green with no finding. ⭐ **28 cells carry the `✅ done — <ref>` idiom today
#: and the whole backlog is one clause away from it** — the failure was not
#: rare, it was one sentence from routine.
#:
#: ⭐ **The remedy is this project's most-repeated one: make the illegal value
#: unrepresentable rather than enumerate it.** A state cell now DECLARES its
#: state as its first word, from this set; ⛔ **a cell that declares nothing is
#: `board-state`, not a guess.** ⚠️ The value is whether the row is closed.
STATES: dict[str, bool] = {
    "done": True,
    "todo": False,
    "in flight": False,
    "in-flight": False,
    "in-progress": False,
    "in-review": False,
    "accepted": False,
    "blocked": False,
    "routed": False,
}

#: Emoji, emphasis and backticks a state cell may wear before its word.
STATE_LEAD = re.compile(r"^[\s*`~⛔⭐✅⚠️⏳◐→️]+")

RULE_DETAIL = "board-detail"
RULE_ORPHAN = "board-orphan"
RULE_DUPLICATE = "board-duplicate"
RULE_NARRATIVE = "board-narrative"
RULE_WIDTH = "board-row-width"
RULE_SIZE = "board-size"
RULE_STATE = "board-state"

#: A backslash-escaped pipe, which markdown renders as a literal `|`.
ESCAPED_PIPE = "\\|"


def cells(line: str) -> list[str]:
    r"""Return the cells of a markdown table row, outer pipes stripped.

    ⛔ **Code-span aware, and that is not a refinement — it is the defect.**
    ⚠️ A naive `split("|")` tore three register rows apart mid-sentence, at
    ``(py|md under tests/fixtures/)``, ``'gated BEFORE\\|gated before'`` and
    ``` `\\| wc -l` ``` — ⭐ **every one a pipe inside a code span, which is a
    pipe a renderer does not split on either.**

    ⭐ `strip_code_spans` blanks spans while keeping every column, so the
    positions found in the masked line index the ORIGINAL — the same trick
    `pointers.py` uses, and for the same reason: a table cell is defined by the
    pipes a reader can see.
    """
    body = line.strip().strip("|")
    masked = strip_code_spans(body).replace(ESCAPED_PIPE, "  ")
    cells, start = [], 0
    for index, character in enumerate(masked):
        if character == "|":
            cells.append(body[start:index].strip())
            start = index + 1
    cells.append(body[start:].strip())
    return cells


def state(cell: str) -> str | None:
    """Return the state a cell DECLARES, or `None` when it declares none.

    ⛔ The longest match wins, so `in-review` is never read as `in`, and the
    match ends on a WORD BOUNDARY, so `DONE-ish` declares nothing.
    """
    text = STATE_LEAD.sub("", cell).lower()
    for word in sorted(STATES, key=len, reverse=True):
        if not text.startswith(word):
            continue
        rest = text[len(word) :]
        # ⛔ A word BOUNDARY, not merely a prefix. ⚠️ `DONE-ish` would otherwise
        # declare `done`, which is the same looseness as the substring test one
        # layer in — ⭐ found by the impossible reading, not by argument.
        if rest and (rest[0].isalnum() or rest[0] == "-"):
            continue
        return word
    return None


def identifiers(cell: str) -> list[str]:
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


def register(text: str) -> list[tuple[int, list[str], str]]:
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
        columns = cells(line)
        if len(columns) < 5:
            continue
        ids = identifiers(columns[0])
        if ids:
            rows.append((number, ids, columns[3]))
    return rows


def is_closed(cell: str) -> bool:
    """Whether a cell's DECLARED state means the row is finished.

    ⛔ A cell that declares nothing is not closed — it is `board-state`.
    """
    word = state(cell)
    return word is not None and STATES[word]


def table_lines(text: str) -> list[tuple[int, str]]:
    """Return `(line number, line)` for every markdown table row in `text`."""
    return [(n, line) for n, line in enumerate(text.split("\n"), 1) if line.startswith("|")]


def narrative_bytes(text: str) -> int:
    """Return the bytes of `text` that sit outside any table row.

    ⭐ Newline included, so this and `table_lines` account for the whole file
    between them — which is what makes `board-narrative` a bound rather than a
    sample.
    """
    return sum(len(line.encode()) + 1 for line in text.split("\n") if not line.startswith("|"))
