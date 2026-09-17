r"""Reading a register out of a markdown table, and it is the parser that is hard.

**What it does.** Turns `BOARD.md`'s delimited register into
`(line number, ids, state cell)` rows, and answers what state a cell DECLARES.

**How you use it.** `tools.quality.board` imports this module's parsers, its
locations and its markers, and nothing else does. ⛔ **The names are not listed
here**: that list is `tools/quality/board/__init__.py`'s import block, and a
second copy of it is `CTO-47/3` — the finding this module's own rule codes
earned.

⚠️ **The five SIZE BOUNDS lived here until `W130` moved them to `bounds.py`, the
module named for them and the only one that spends them** — ⛔ **this one is a
PARSER, and a derivation for a number it never reads is the *fact in the wrong
home* shape the rule codes above already earned.**

**Depends on.** `re`, `pointers.strip_code_spans`, and `ids` for Ruling 218's grammar (`W192`).

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
from collections.abc import Iterable

from tools.quality.ids import row_ids
from tools.quality.pointers import strip_code_spans

#: ⛔ The register itself. ⭐ One file, NAMED here rather than discovered, because
#: a check that hunted for the board would pass on a repository that had lost it.
#: ⚠️ **It moved here from the package when `W96` split the 388-line emitter at the
#: seam the CTO named** — a location is what this module already answers for, and
#: the alternative was a second copy in each half.
BOARD = "docs/tasks/BOARD.md"

#: The directory holding one file per live row.
ROWS = "docs/tasks/rows"

#: ⛔ The record a CLOSED row's argument moves into, and the only target Ruling
#: 270's REDIRECT STUB may carry. ⭐ Named here beside `BOARD` and `ROWS` for the
#: same reason they are: a location is what this module answers for, and a second
#: spelling of it in `bijection.py` would be a fact with two homes.
ARCHIVE = "BOARD-ARCHIVE.md"

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

#: ⛔ The sentence every row file carries, and it is the file's IDENTITY rather
#: than decoration: it says which row this is the argument for, and that its
#: naming, owner and state live on the board and not here.
#:
#: ⚠️ **It is checked on the LIVE tree because `test_migration.py` no longer
#: can.** ⭐ Ruling 180 bound that module to the migration's OUTPUT ref, which
#: is right — a migration is a claim about refs — ⛔ **but it means nothing was
#: left watching a live row file at all.** ⭐ This is what remains watchable
#: without forbidding an edit: a frame survives every amendment, because
#: amending a row means adding to its argument, never removing its identity.
ROW_FRAME = "and nothing else."

#: Emoji, emphasis and backticks a state cell may wear before its word.
STATE_LEAD = re.compile(r"^[\s*`~⛔⭐✅⚠️⏳◐→️]+")

#: ⛔ The opening idiom a duplicated state wears: an EMPHASISED label, set off by
#: a dash. ⚠️ **Measured verbatim from `798956c`** — `⏳ **in flight** — …` and
#: `⏳ **in flight, with W14** — …`, so the label may say more than the word.
#:
#: ⭐ **The label may not cross `*` or a backtick**, which is what stops it
#: swallowing a whole sentence and matching somewhere it should not:
#: `rows/W5.md`'s `⛔ **CORRECTED — \`unitdoc.py\` is 827 lines…**` is blocked at
#: the backtick and never reaches a dash.
_STATE_LABEL = re.compile(r"^[\s⛔⭐✅⚠️⏳◐→️]*(?P<mark>\*\*|`)(?P<label>[^*`\n]+?)(?P=mark)\s*[—–-]")

# ⛔ **The rule codes are NOT here, and their absence is `CTO-47/3`.** ⚠️ This
# module defined seven of them — `RULE_DETAIL` … `RULE_STATE` — that nothing
# imported and that it never used itself: `tools/quality/board/__init__.py`
# raises every finding and declares all eight codes, `RULE_FRAME` included.
#
# ⭐ **This project's most-repeated finding, committed inside the module written
# to stop it: a fact in two places goes stale in the copy nobody re-measures.**
# ⛔ **Ruff cannot see it** — module-level assignments are not unused imports —
# ⭐ **so `test_register.py` asserts the absence, derived rather than listed.**

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


def state(cell: str, words: Iterable[str] = STATES) -> str | None:
    """Return the state a cell DECLARES from `words`, or `None` when it declares none.

    ⛔ The longest match wins, so `in-review` is never read as `in`, and the
    match ends on a WORD BOUNDARY, so `DONE-ish` declares nothing.

    ⚠️ **`words` is a PARAMETER because this board carries TWO closed vocabularies** —
    `STATES` here and `scheduled.py`'s trigger states (`W100`) — ⛔ **and a second copy
    of the boundary rule is the defect this module's docstring opens with.**
    """
    text = STATE_LEAD.sub("", cell).lower()
    for word in sorted(words, key=len, reverse=True):
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
    """Return every `W`-row id a cell names, under Ruling 218's ONE grammar.

    ⛔ **The grammar is `tools/quality/ids.py`'s and is not respelled here**
    (`W192`): this reader took `+`, the handoff reader took `,`, and
    `` `W20`, `W21` `` read as ONE id here — the LAST, silently, at exit `0`.
    """
    return row_ids(cell)


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


def argument(body: str) -> str:
    """Return a row file's ARGUMENT — everything after its frame.

    ⛔ **The subject is the ARGUMENT and not the FILE, and that is Ruling 186's
    surviving clause (c).** ⚠️ **Frame overhead runs 224–346 bytes across the
    live row files**, so anything read at file level is the right question over
    the wrong span — the family this project has now met five times.

    ⛔ **The frame is located by its TEXT, never by an index**: `rows/W17.md`
    carries one extra frame block — the note that `W19` rides with it — and an
    index would have silently skipped that row's whole argument. ⭐ `ROW_FRAME`
    is the sentinel, so there is one home for what a frame says rather than two.

    ⚠️ **A file with no frame has no argument this can locate and returns `""`**;
    `board-frame` is what reports the missing frame.
    """
    blocks = body.split("\n\n")
    for index, block in enumerate(blocks):
        if ROW_FRAME in block:
            return "\n\n".join(blocks[index + 1 :]).strip()
    return ""


#: Markup a cell and an argument may differ by without differing in CONTENT:
#: emphasis, code spans, the emoji this project's prose wears, and runs of
#: whitespace a reflow introduces. ⛔ **This is what makes the comparison
#: NORMALISED-verbatim rather than byte-verbatim** — a copy that was re-bolded
#: on its way into a file is still a copy.
_MARKUP = re.compile(r"[*`~]")
_LEAD_EMOJI = re.compile(r"[⛔⭐✅⚠️⏳◐→️]")


def normalised(cell: str) -> str:
    """Return `cell` with markup, emoji, spacing and a trailing stop removed."""
    plain = _LEAD_EMOJI.sub(" ", _MARKUP.sub("", cell))
    return re.sub(r"\s+", " ", plain).strip().rstrip(".").lower()


def namings(text: str) -> dict[str, str]:
    """`{"W60": <naming cell>}` for every register row, by its owning id."""
    found = {}
    for line in text.split("\n"):
        if not line.startswith("|"):
            continue
        columns = cells(line)
        if len(columns) < 5:
            continue
        ids = identifiers(columns[0])
        if ids:
            found[ids[0]] = columns[1]
    return found


def repeats_its_naming(body: str, cell: str) -> bool:
    """Whether a row file's whole argument IS its own register naming.

    ⛔ **Ruling 186, narrowed: a CLOSED PREDICATE where there had been a
    threshold.** ⚠️ **Seven live files carry, as their entire argument, a
    normalised copy of the naming cell** — ⛔ **which is the one thing the frame
    sentence inside them forbids:** *"not here, and not in two places."*
    ⭐ **`board-frame` passes all seven, because `startswith` and `in` cannot
    read a contradiction.**

    ⚠️ **A file that EXTENDS its naming is not this**, and must not be reported:
    an argument that opens by restating what the row is and then argues it is
    doing exactly what the file is for. ⛔ **Equality, never a prefix.**

    ⭐ **And no byte measure and no cutoff at all.** ⚠️ **Two sweeps read 16 and
    19 thin rows under two unruled thresholds; both answered a question that
    should not have been asked**, and a predicate retires the disagreement
    instead of settling it.
    """
    wanted = normalised(cell)
    # ⛔ Ruling 48 in miniature: an empty naming would make every file a repeat.
    return bool(wanted) and normalised(argument(body)) == wanted


def duplicates_a_state(body: str) -> bool:
    """Whether a row file's argument OPENS by declaring a state.

    ⛔ **Ruling 186(b)'s second clause, and the predicate is the OPENING IDIOM —
    `⏳ **<state>** —` — never a state word anywhere past the frame.** ⚠️ **A row
    argument is *about* states constantly**: *"gated on `W63` landing"*,
    *"accepted at round 22"*, *"already DONE by `validate/structure.py`"*.
    ⛔ **An *anywhere* predicate fires on every one of those** — which is
    `board-state`'s own founding defect one layer up, where the first
    `is_closed` was a substring test and `` `todo` — after `W44` is done `` read
    as CLOSED.

    ⭐ **So this reuses `state()`**: the closed set, the leading markup stripped,
    the match ending on a word boundary — applied to the argument's FIRST BLOCK
    and nothing else. ⚠️ **Measured at `798956c`: two files declare a state this
    way (`W14`, `W18`) and the two candidate false positives are both
    excluded** — `rows/W5.md`'s *"job is already DONE by …"*, which is `done` in
    ordinary English, and `W18`'s record in `BOARD-ARCHIVE.md`, whose later
    *"is ACCEPTED today"* is not the opening.

    ⛔ **A state belongs to the register and to the record; a row file carries the
    ARGUMENT** — which is the other half of what the frame sentence forbids.

    ⚠️ **`state()` alone is not narrow enough and a planted row said so:** it
    fires on *"Blocked by nothing; `W44` is unrelated."*, which opens with a
    vocabulary word used as English. ⭐ **So the IDIOM is matched, not the word** —
    an emphasised LABEL, set off by a dash, that declares a state.
    """
    match = _STATE_LABEL.match(argument(body).split("\n\n")[0])
    return match is not None and state(match.group("label")) is not None


#: ⛔ Ruling 270's REDIRECT STUB, as a CLOSED PREDICATE: one markdown link, into
#: `BOARD-ARCHIVE.md`, carrying an ANCHOR, and nothing else in the argument at all.
#: ⭐ The `../` is optional because a row file sits one directory below the archive
#: and the instrument runs over arbitrary roots.
_STUB = re.compile(rf"^\[[^\]\n]+\]\((?:\.\./)?{re.escape(ARCHIVE)}#[^)\s]+\)$")


def redirects_to_the_archive(body: str) -> bool:
    """Whether a row file's whole ARGUMENT *is* one anchored pointer into the archive.

    ⛔ **Ruling 270's stub, and the predicate is CLOSED with NO byte threshold** —
    `repeats_its_naming`'s own remedy one function up (Ruling 186): ⚠️ **two sweeps
    once read 16 and 19 thin rows under two unruled cutoffs and both answered a
    question that should not have been asked.**

    ⛔ **It is *IS* and never *CONTAINS*, and that is the whole of the predicate.**
    ⚠️ **MEASURED at `51dee3b`, role `wt/dev1`: of the 83 live row files, **50** carry
    an ANCHORED `BOARD-ARCHIVE.md#` pointer somewhere and **42** END with one** —
    ⭐ **so a `contains` test would have read FIFTY full argument files on today's board
    as stubs, and this predicate reads ZERO of the 83** (the LIVE reading, asserted in
    `test_register.py`).

    ⚠️ **The ANCHOR is required** (Ruling 244(e)'s form): a bare `BOARD-ARCHIVE.md` lands
    the reader at the top of a record hundreds of sections long, which fails Ruling 270's
    own sentence — *"the reader lands on the argument"*.

    ⛔ **Whether the pointer RESOLVES is NOT read here.** ⭐ `tools/quality/pointers.py`
    answers that, it opens the target to do it, and a second resolver is a second answer.
    """
    return _STUB.match(argument(body).strip()) is not None


def row_order(name: str) -> tuple[int, str]:
    """Sort key for row ids: `W5` before `W10`, and deterministic (R10).

    ⛔ Length then text, rather than `int(name[1:])`, because the population is
    filenames and a filename is not guaranteed to be `W<digits>` — a key that
    raises on the one file somebody misnamed would take the notice down.
    """
    return (len(name), name)


def narrative_bytes(text: str) -> int:
    """Return the bytes of `text` that sit outside any table row.

    ⭐ Newline included, so this and `table_lines` account for the whole file
    between them — which is what makes `board-narrative` a bound rather than a
    sample.
    """
    return sum(len(line.encode()) + 1 for line in text.split("\n") if not line.startswith("|"))
