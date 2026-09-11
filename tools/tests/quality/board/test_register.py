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

import importlib

import pytest

from tests.support import repository_root
from tools.quality.board import BOARD, ROWS
from tools.quality.board.register import (
    REGISTER_CLOSE,
    REGISTER_OPEN,
    STATES,
    argument,
    cells,
    duplicates_a_state,
    identifiers,
    is_closed,
    namings,
    narrative_bytes,
    redirects_to_the_archive,
    register,
    repeats_its_naming,
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


# --------------------------------------------------------------------------
# ⛔ `CTO-47/3` — the rule codes, and why they are asserted ABSENT from here
# --------------------------------------------------------------------------


def test_every_rule_code_has_exactly_ONE_home() -> None:
    """⛔ `CTO-47/3` — the finding this very package was written to prevent.

    ⚠️ **`register.py` defined seven `RULE_*` constants that nothing imported
    and that it never used itself**, while `tools/quality/board/__init__.py`
    redefined all seven and added an eighth. ⭐ **This project's most-repeated
    finding — a fact in two places goes stale in the copy nobody re-measures —
    committed inside the module written to stop it.**

    ⛔ **Ruff cannot see a duplicated module-level assignment**, which is why
    this is a test and not a lint rule. ⭐ **Derived from the package rather than
    listed**, so a ninth code joins the population without this test being
    edited (Ruling 48: declare the population, then reduce it).
    """
    package = importlib.import_module("tools.quality.board")
    module = importlib.import_module("tools.quality.board.register")
    # ⛔ **`import tools.quality.board.register as m` does NOT give this module**,
    # and that is how the first version of this test was born vacuous: the
    # package does `from ... .register import register`, which rebinds the
    # attribute `register` from the SUBMODULE to the FUNCTION, so `vars()` read
    # a function's empty `__dict__` and the guard passed with a `RULE_*`
    # planted. ⭐ Found by writing the planted row's expected reading down first.
    assert module.__name__ == "tools.quality.board.register", module
    declared = sorted(name for name in vars(package) if name.startswith("RULE_"))
    assert declared, "Ruling 48: no rule codes at all would satisfy every assertion below"
    assert declared == sorted(n for n in package.__all__ if n.startswith("RULE_")), (
        "a code the package defines and does not export is already a second home"
    )
    second_home = sorted(name for name in vars(module) if name.startswith("RULE_"))
    assert second_home == [], (
        f"{len(second_home)} of {len(declared)} rule codes have a second definition in "
        f"register.py: {second_home}. ⛔ The emitter declares them; this module parses."
    )


# --------------------------------------------------------------------------
# ⛔ Ruling 186 — the ARGUMENT's span, and the CLOSED PREDICATE over it
# --------------------------------------------------------------------------

#: A row file, frame and all, parameterised by what it argues. ⛔ Written out
#: rather than generated, because the frame's text is the sentinel `argument`
#: locates and a paraphrase would be testing a shape nothing ships.
FRAMED = (
    "# {name}\n\n⛔ **This file carries the ARGUMENT for board row `{name}` and nothing "
    "else.**\n⭐ **Its naming, owner and state live once, in the register in "
    "[`../BOARD.md`](../BOARD.md)** — ⛔ **not here, and not in two places.**\n\n{argument}\n"
)


def test_argument_is_the_span_after_the_frame_and_not_the_FILE() -> None:
    """⛔ Ruling 186's surviving clause (c), measured as a gap.

    ⚠️ **Frame overhead runs 224–346 bytes across the live row files**, so any
    reading taken at file level is the right question over the wrong span.
    """
    body = FRAMED.format(name="W9", argument="The argument.")
    assert argument(body) == "The argument."
    assert len(argument(body).encode()) < len(body.encode()) - 200, "the frame is the 200+"


def test_argument_finds_the_frame_by_TEXT_so_an_extra_block_cannot_hide_it() -> None:
    """⛔ `rows/W17.md`'s shape: one extra frame block before the frame proper.

    ⚠️ **An index would have silently skipped that row's whole argument** — and
    silently is the word that matters, because the reading would still have been
    a string.
    """
    note = "# W17\n\n⭐ **`W19` has no file of its own: they are ONE COMMIT.**\n\n"
    body = note + FRAMED.format(name="W17", argument="Both halves, argued.").split("\n\n", 1)[1]
    assert argument(body) == "Both halves, argued."


@pytest.mark.parametrize(
    "body",
    [
        "# W9\n\n⛔ **… and nothing else.**\n",
        "# W9\n\n⛔ **… and nothing else.**\n\n\n",
        "a fragment with no frame at all\n",
    ],
)
def test_a_row_file_with_no_argument_yields_the_EMPTY_string(body: str) -> None:
    """⛔ The IMPOSSIBLE reading: a frame with nothing after it argues nothing.

    ⭐ **The frameless third is empty too, and `board-frame` is what reports
    it** — this is a notice and it does not get to hold two opinions.
    """
    assert argument(body) == ""


@pytest.mark.parametrize(
    "cell",
    [
        "the marker check judges 41 of 88 documents",
        "⛔ **the marker check judges 41 of 88 documents**",
        "`the marker check judges 41 of 88 documents`",
        "⭐ the  marker   check judges 41 of 88 documents.",
        "THE MARKER CHECK JUDGES 41 OF 88 DOCUMENTS",
    ],
)
def test_planted_a_naming_copied_under_DIFFERENT_MARKUP_is_still_a_copy(cell: str) -> None:
    """⛔ PLANTED, and adversarial to the SEARCH TERM (Ruling 140).

    ⚠️ **The evasion is not different words; it is different MARKUP** — a naming
    re-bolded, wrapped in a code span, reflowed, or given a full stop on its way
    into a file. ⭐ **A byte-verbatim comparison reports none of these five and a
    normalised one reports all five**, which is why the ruling says
    *normalised*-verbatim.
    """
    body = FRAMED.format(name="W42", argument="⛔ **the marker check judges 41 of 88 documents**")
    assert repeats_its_naming(body, cell)


def test_a_file_that_EXTENDS_its_naming_is_not_a_repeat() -> None:
    """⛔ Equality, never a prefix — and this is the assertion that keeps it usable.

    ⭐ **An argument that restates what the row is and then argues it is doing
    exactly what the file exists for.** ⚠️ **A prefix test would report 17 more
    files on the live tree**, and a notice that flags correct work is one people
    learn to scroll past.
    """
    cell = "the marker check judges 41 of 88 documents"
    assert not repeats_its_naming(
        FRAMED.format(name="W42", argument=f"{cell} — and here is why that matters."), cell
    )
    assert not repeats_its_naming(FRAMED.format(name="W42", argument="Something else."), cell)


def test_an_EMPTY_naming_cell_does_not_make_every_file_a_repeat() -> None:
    """⛔ Ruling 48 in miniature, and it is the IMPOSSIBLE reading for this predicate.

    ⚠️ **`normalised("") == normalised("")`**, so a row with no naming cell would
    otherwise report every frame-only file as a copy of it — ⭐ **a reading that
    would have been `0 = 0` wearing a finding.**
    """
    assert not repeats_its_naming(FRAMED.format(name="W42", argument=""), "")
    assert not repeats_its_naming("a fragment with no frame at all\n", "")


def test_namings_reads_the_OWNING_id_of_every_register_row() -> None:
    """⭐ The naming cell is column two, and a two-id row is owned by its first id."""
    text = (
        "| # | Row | Owner | State | Detail |\n|---|---|---|---|---|\n"
        "| W17 **+ W19** | one commit, two ids | PO | `todo` | [d](rows/W17.md) |\n"
        "| ⛔ **W5** | `origin` may name a region | Dev | `todo` | [d](rows/W5.md) |\n"
    )
    assert namings(text) == {
        "W17": "one commit, two ids",
        "W5": "`origin` may name a region",
    }


def test_the_live_tree_is_an_INHABITED_population_for_this_predicate() -> None:
    """⛔ Ruling 48: the population, never the verdict — and deliberately NOT a count.

    ⚠️ **The seven repeats measured at `798956c` are `W60 W63 W64 W66 W67 W72
    W73`** — ⛔ **and that is recorded here as a READING and not as an
    assertion**, because the PO fixing those seven files is the outcome this
    notice exists to cause and a test that reddened on it would be a test
    against the remedy. ⭐ **What is asserted is that the question can be put:
    every row file has a register naming cell to be compared against.**
    """
    text = (repository_root() / BOARD).read_text(encoding="utf-8")
    named = namings(text)
    files = sorted((repository_root() / "docs/tasks/rows").glob("*.md"))
    assert files and named, "neither side of the comparison may be empty"
    assert [path.stem for path in files if path.stem not in named] == [], (
        "a row file with no register naming cell cannot be compared; board-orphan owns that"
    )


# --------------------------------------------------------------------------
# ⛔ Ruling 186(b) clause 2 — the argument DUPLICATES A STATE
# --------------------------------------------------------------------------

#: ⛔ **The two live row arguments that OPEN by declaring a state, verbatim from
#: `798956c:docs/tasks/rows/`** — and the two candidate FALSE POSITIVES beside
#: them, also verbatim.
#:
#: ⚠️ **Embedded rather than read from the live tree, and that is Ruling
#: 186(b)(ii):** the PO closed `W14` and `W18` in the same round this clause was
#: written, so the live population is **0** and ⛔ **a clause-2 pass with no
#: planted hit is VACUOUS, not green** (Ruling 48).
MEASURED_OPENINGS = (
    ("W14", True, "⏳ **in flight** — ⛔ **TWO missing invalid fixtures on FND-04's surface**"),
    ("W18", True, "⏳ **in flight, with W14** — ⛔ **`user` + `authoritative` is accepted today**"),
    # ⛔ `done` in ordinary English, and it is the false positive a substring
    # search reports. ⭐ `state()` does not, because the word is not the opening.
    ("W5", False, "⛔ **CORRECTED — `unitdoc.py` is 827 lines; about 250 are left to port.**"),
    # ⛔ `W18`'s SECOND block. ⚠️ An *anywhere* predicate counts this a second time.
    ("W18b", False, '⭐ **The author believed the set should be `("bundled",)`** — accepted'),
)


@pytest.mark.parametrize(("name", "fires", "opening"), MEASURED_OPENINGS)
def test_the_state_duplication_predicate_reads_the_OPENING_and_not_the_prose(
    name: str, fires: bool, opening: str
) -> None:
    """⛔ Ruling 186(b)(i), and the corpus is why the predicate is what it is.

    ⚠️ **A row argument is *about* states constantly** — *"gated on `W63`"*,
    *"accepted at round 22"*, *"already DONE by …"*. ⛔ **An *anywhere* predicate
    fires on all of those, and the over-match SCALES WITH THE POPULATION:**
    measured at `798956c` (50 rows) *anywhere* reads **3** and the opening idiom
    reads **2**; at `35b63aa` (64 rows) *anywhere* reads **6** — four of them
    rows the PO had just written — and the opening idiom reads **0**, correctly,
    because both true hits were closed. ⭐ **A notice whose first wave fires on
    four rows its author just wrote is a notice nobody reads twice** (Ruling
    179).

    ⛔ **Clause 1 is immune and clause 2 as first worded was not**: clause 1 is an
    EQUALITY against the register cell, and a vocabulary search inherits
    `is_closed`'s founding defect one layer up.
    """
    body = FRAMED.format(name="W9", argument=f"{opening}\n\nAnd then the argument proper.")
    assert duplicates_a_state(body) is fires, (name, opening[:60])


@pytest.mark.parametrize("declared", sorted(STATES))
def test_every_word_of_the_closed_vocabulary_is_a_state_duplication(declared: str) -> None:
    """⭐ The whole vocabulary, derived — ⛔ an empty `STATES` SKIPS rather than passing."""
    opening = f"⏳ **{declared}** — and then the argument"
    assert duplicates_a_state(FRAMED.format(name="W9", argument=opening))


@pytest.mark.parametrize(
    "argument_text",
    ["", "The argument, which declares no state.", "Blocked by nothing; `W44` is unrelated."],
)
def test_impossible_an_argument_that_declares_no_state_does_not_duplicate_one(
    argument_text: str,
) -> None:
    """⛔ The IMPOSSIBLE reading. ⚠️ The third wears `Blocked` where the cell would."""
    assert not duplicates_a_state(FRAMED.format(name="W9", argument=argument_text))
    assert not duplicates_a_state("a fragment with no frame at all\n")


# --------------------------------------------------------------------------
# ⛔ `W129` / Ruling 270 — the REDIRECT STUB predicate, and it is IS not CONTAINS
# --------------------------------------------------------------------------

#: ⭐ Ruling 270's stub in the shape the ruling prescribes, and the two spellings of the
#: archive path a row file can legitimately carry.
_STUB_BODY = (
    "# W1\n\n⛔ **This file carries the ARGUMENT for board row `W1` and nothing else.**"
    "\n\n[the argument]({target})\n"
)


@pytest.mark.parametrize(
    "target",
    [
        "../BOARD-ARCHIVE.md#ruling-270-the-close-protocol",
        "BOARD-ARCHIVE.md#ruling-270-the-close-protocol",
    ],
)
def test_a_stub_whose_ARGUMENT_IS_one_anchored_archive_pointer_is_a_stub(target: str) -> None:
    """⭐ The positive row, in both spellings of the path a row file may carry.

    ⛔ **The `../` is optional because a row file sits one directory below the archive and
    this instrument runs over ARBITRARY roots** — a temp tree, a corpus repository — where
    the nesting is whatever that tree chose.
    """
    assert redirects_to_the_archive(_STUB_BODY.format(target=target))


@pytest.mark.parametrize(
    ("body", "why"),
    [
        ("", "a file with no frame has no argument this can locate"),
        (_STUB_BODY.format(target="../BOARD-ARCHIVE.md"), "⛔ the ANCHOR is required"),
        (_STUB_BODY.format(target="../BOARD.md#the-register"), "⛔ the TARGET is the archive"),
        (_STUB_BODY.format(target="#ruling-270"), "a same-file anchor is not the archive"),
        (
            _STUB_BODY.format(target="../BOARD-ARCHIVE.md#x").replace(
                "[the argument]", "⭐ **Closed.** [the argument]"
            ),
            "⛔ the argument IS the pointer and carries nothing beside it",
        ),
        (
            _STUB_BODY.format(target="../BOARD-ARCHIVE.md#x")
            + "\nAnd one more paragraph of argument.\n",
            "⛔ a SECOND block is an argument, not a redirect",
        ),
    ],
)
def test_planted_everything_that_is_NOT_a_stub(body: str, why: str) -> None:
    """⛔ The CLOSED predicate, planted on every near-miss it has to refuse.

    ⚠️ **The last two are the ones that matter**: ⭐ **a full argument file that ENDS with
    an archive pointer is what a `contains` test would have read as a stub**, and
    `rows/W129.md`, `rows/W130.md` and `rows/W132.md` are all that shape.
    """
    assert not redirects_to_the_archive(body), why


def test_the_LIVE_tree_reads_ZERO_stubs_and_the_CONTAINS_form_would_read_FIFTY() -> None:
    """⛔ The LIVE reading, and it is the one that makes the predicate's shape an argument.

    ⚠️ **MEASURED here rather than quoted:** of the live row files, a substantial minority
    carry an ANCHORED `BOARD-ARCHIVE.md#` pointer somewhere in their argument — ⭐ **so the
    rejected `contains` predicate would have read every one of them as a CLOSED row's
    stub, and `board-orphan` would have fallen silent on exactly the files it guards.**

    ⛔ **This predicate reads NONE of them**, and both numbers are asserted so the
    comparison is a reading rather than a claim (Ruling 128: the population, in full).
    """
    files = sorted((repository_root() / ROWS).glob("*.md"))
    assert len(files) >= 10, f"born vacuous: {len(files)} row files"
    bodies = {path.stem: path.read_text(encoding="utf-8") for path in files}
    stubs = sorted(name for name, body in bodies.items() if redirects_to_the_archive(body))
    contains = sorted(
        name for name, body in bodies.items() if "BOARD-ARCHIVE.md#" in argument(body)
    )
    assert stubs == [], (
        f"⛔ {len(stubs)} live row file(s) read as a Ruling 270 STUB — {stubs}. A live row's "
        f"argument is AMENDED, so it may not live in the archive."
    )
    assert len(contains) > 10, (
        f"⛔ born vacuous: only {len(contains)} row files carry an anchored archive pointer, "
        f"so the rejected `contains` form would have had nothing to get wrong here"
    )
