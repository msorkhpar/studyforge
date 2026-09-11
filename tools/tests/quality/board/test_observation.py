"""Mirror of `tools/quality/board/observation.py` (R12), and Ruling 189(b)'s three readings.

⛔ **The three PLANTED readings here are not invented: they are the THREE MEASURED
FAILURES, replayed from their own bytes**, each quoted with the ref it was taken
at (Ruling 97's standing rule).

| Replay | The bytes | Taken at |
|---|---|---|
| 350 commits | `W14`+`W18` and `W27`, `none` / `0` / started | `cae114e^` |
| bidirectional | `SF-34` and `W85`+`W86`+`W87`, a checkout that had gone | `679a6c5^` |
| the Checkout cell | `SF-15` and `W95`, a checkout and `0` ahead — ⭐ **a PASS** | `7559398` |

⭐ **The third is the CONTROL and it is the one that constrains the predicate:**
⛔ **both its rows pass on the `Checkout` cell and NOT on `ahead`**, so no single
cell is the rule and a predicate demanding `ahead > 0` would have flagged the two
rows that were correct (Ruling 130, and Ruling 179's cost).
"""

from __future__ import annotations

import pytest

from tests.support import repository_root
from tools.quality.board import (
    BOARD,
    RULE_DISAGREEMENT,
    RULE_INFLIGHT,
    RULE_UNOBSERVED,
    check_board,
)
from tools.quality.board.observation import (
    ABSENT,
    INFLIGHT_CLOSE,
    INFLIGHT_OPEN,
    NOT_STARTED,
    STAND_INS,
    STARTED,
    asserted,
    observation_findings,
    observation_reading,
    observations,
)
from tools.quality.board.register import STATES

#: The observation table's header, verbatim from every In-flight table this board
#: has carried. ⛔ Written out rather than generated: the header is the
#: DECLARATION the locator reads, and a paraphrase would test a shape the board
#: does not author.
HEADER = "| Row | Owner | Checkout | Commits ahead | State |\n|---|---|---|---|---|\n"

#: ⛔ **`cae114e^`, and these two lines are this module's founding bytes.**
THREE_HUNDRED_AND_FIFTY = (
    "| `W14` + `W18` | Developer 1 | none | 0 | in flight |\n"
    "| `W27` | Developer 2 | none | 0 | ◐ in-review @ `655b527` |\n"
)

#: ⛔ **`7559398`, and it must PASS** — a checkout and `0` commits ahead.
THE_CHECKOUT_CELL = (
    "| `SF-15` | Developer 1 | `wt/dev1`, `feat/SF-15-contents` | 0 | in flight |\n"
    "| `W95` | Developer 2 | `wt/dev2`, `fix/W95-shared-origin-fixture` | 0 | in flight |\n"
)

#: ⛔ **`679a6c5^`, the bidirectional wave** — ⚠️ **both cells CLAIM a checkout that
#: had gone, so this table is a PASS here and is refuted only by `corroborate.py`.**
BIDIRECTIONAL = (
    "| `SF-34` | Developer 1 | `wt/dev1`, `feat/SF-34-chrome` | 0 | in flight |\n"
    "| `W85` + `W86` + `W87` | Developer 2 | `wt/dev2`, `fix/board-instrument` | **+1** "
    "| in-review |\n"
)

REGISTER = "<!-- register -->\n| # | Row | Owner | State | Detail |\n|---|---|---|---|---|\n"
REGISTER_END = "<!-- /register -->\n"


def _board(observation: str = "", register: str = "", delimited: bool = False) -> str:
    """A board with a register and, optionally, a delimited observation table."""
    table = ""
    if observation:
        table = HEADER + observation
        if delimited:
            table = f"{INFLIGHT_OPEN}\n{table}{INFLIGHT_CLOSE}\n"
    return f"# Board\n\n## In flight\n\n{table}\n{REGISTER}{register}{REGISTER_END}"


def _rules(findings: list) -> list[str]:
    return sorted(finding.rule for finding in findings)


# --------------------------------------------------------------------------
# Reading 1 — LIVE, and the population is printed before any verdict
# --------------------------------------------------------------------------


def test_live_the_observation_population_is_INHABITED() -> None:
    """⛔ Ruling 191(a): print the population size BEFORE the verdict, and `0` is missing.

    ⚠️ **This rule's subject is empty between waves by construction** — the
    In-flight table is replaced at a wave's close and the started register cells
    go with it — ⭐ **so the live reading asserts INHABITATION and the planted
    readings below carry the verdicts.**
    """
    text = (repository_root() / BOARD).read_text(encoding="utf-8")
    rows = observations(text)
    reading = observation_reading(text)
    assert rows, f"⛔ born vacuous: no observation table on the live board — {reading}"
    assert f"{len(rows)} rows" in reading
    assert "NONE FOUND" not in reading


def test_live_no_row_on_this_board_contradicts_itself() -> None:
    """⭐ The one-row contradiction is ABSENT on the live board, against a live population.

    ⛔ **Only `board-inflight` is asserted clean here, and the narrowness is
    deliberate**: a test that asserted *every* rule clean on the live tree would
    be pinning today's board, and the day the PO corrects a cell the test would
    go red for the tree being RIGHT (Ruling 190's shape). ⭐ `check_board`'s own
    live reading is `test_init.py`'s, which is where a board defect belongs.
    """
    text = (repository_root() / BOARD).read_text(encoding="utf-8")
    started = [row for row in observations(text) if row.started]
    if not started:
        pytest.skip("no row of this board's observation table declares a started state")
    assert [f for f in observation_findings(text) if f.rule == RULE_INFLIGHT] == []


def test_live_the_stand_in_is_named_in_the_reading_rather_than_excluded_in_silence() -> None:
    """⛔ `CTO-49/4` and Ruling 185: an exemption narrows the POPULATION, by NAME.

    ⚠️ **`W73`'s carrier is a checkout in a repository this one does not own**, so
    no framework-side instrument can observe it without reading across the seam
    (R20, Ruling 151). ⭐ **Excluded BY NAME is still a total reading; excluded in
    silence is not** — so the name is in the line every floor run prints.
    """
    text = (repository_root() / BOARD).read_text(encoding="utf-8")
    reading = observation_reading(text)
    for name in STAND_INS:
        assert name in reading
    assert name not in [identifier for _n, identifier, _w in asserted(text)]


# --------------------------------------------------------------------------
# Reading 2 — PLANTED: the three measured failures, from their own bytes
# --------------------------------------------------------------------------


def test_planted_the_350_COMMIT_case_fires_on_both_rows() -> None:
    """⛔ `cae114e^`: two rows declaring a started state with `none` and `0`.

    ⭐ **Every git instrument read CORRECTLY for 350 commits** — `worktree list`
    saw no checkout because the work had FINISHED, and `--no-merged` saw nothing
    because it had MERGED — ⚠️ **and the board printed `Checkout: none` beside a
    started state the whole time.** ⛔ **Read DOWN A COLUMN, every instrument was
    right; read ACROSS THE ROW, the board refutes itself.**
    """
    findings = observation_findings(_board(THREE_HUNDRED_AND_FIFTY))
    assert _rules(findings) == [RULE_INFLIGHT, RULE_INFLIGHT]
    assert "W14" in findings[0].message and "W18" in findings[0].message
    assert "W27" in findings[1].message, "⛔ the `◐ in-review @ …` idiom declares in-review"
    assert all("CONTRADICTION PRINTED ON ONE ROW" in f.message for f in findings)


def test_planted_a_started_REGISTER_cell_that_no_observation_row_names() -> None:
    """⛔ The ABSENT half of the bidirectional failure, SYNTHESISED (Ruling 191(b)).

    ⚠️ **The live population is empty today**, because this board's recent practice
    leaves a dispatched row's register cell at `` `todo` `` — ⛔ **which is itself
    the departure that let `W95`'s staleness live in one table only.** ⭐ **Measured
    at `cae114e^` and `679a6c5^`, the register declared `in flight` for every
    dispatched row of rounds 37 and 38**, so this shape is the board's own and not
    a hypothetical.
    """
    register = "| W42 | a naming | Developer 2 | in flight — `fix/W42` | [d](rows/W42.md) |\n"
    findings = observation_findings(_board(THE_CHECKOUT_CELL, register))
    assert _rules(findings) == [RULE_UNOBSERVED]
    assert "W42" in findings[0].message
    assert "NO observation row" in findings[0].message


def test_planted_the_two_tables_of_ONE_FILE_disagree() -> None:
    """⛔ STARTED against FINISHED, which cannot both be true of one row.

    ⚠️ **This is the shape the board reaches the moment a row is closed in the
    register and the observation table is not re-taken** — ⭐ the 350-commit case's
    sibling, and the one cross-table pairing no convention explains.
    """
    register = "| W95 | a naming | Developer 2 | ✅ done — `cfe0e0c` | [record](a.md#w95) |\n"
    findings = observation_findings(_board(THE_CHECKOUT_CELL, register))
    assert _rules(findings) == [RULE_DISAGREEMENT]
    assert "W95" in findings[0].message and "done" in findings[0].message


def test_a_started_row_whose_register_cell_reads_todo_is_PRINTED_and_NOT_FLAGGED() -> None:
    """⛔ Ruling 179, and the plant that CONTRADICTED this module's first predicate.

    ⚠️ **The first version of `board-disagreement` fired on any started-against-not-
    started pairing, and its first live reading hit `W95` — a row the PO had just
    dispatched correctly.** ⭐ **Measured at `7559398`: this board dispatches a row
    by naming it in the observation table and leaving its register cell at
    `` `todo` ``**, so the rule as first written flagged the convention rather than
    a defect.

    ⛔ **A reading that is not a finding is PRINTED rather than dropped** (Ruling
    183's form) — ⚠️ **and the row whose `todo` hides a CLOSED branch is refuted by
    `corroborate.py`, because only `git` can tell *just dispatched* from *merged
    five waves ago*.**
    """
    register = "| W95 | a naming | Developer 2 | `todo` — before `SF-16` | [d](rows/W95.md) |\n"
    text = _board(THE_CHECKOUT_CELL, register)
    assert observation_findings(text) == []
    assert "started here and `todo` in the register" in observation_reading(text)
    assert "Ruling 179): W95" in observation_reading(text)


def test_planted_the_CHECKOUT_CELL_case_is_a_PASS_and_that_is_the_constraint() -> None:
    """⭐ `7559398`: a checkout and `0` ahead is CORROBORATED, not a finding.

    ⛔ **This is the reading that stops the predicate being `ahead > 0`.** ⚠️ **A
    branch with no commit is not in `--no-merged` BY CONSTRUCTION** (Ruling 130),
    so a just-dispatched row passes on the `Checkout` cell alone — ⛔ **and a rule
    that flagged it would fire on two correct rows in its first wave**, which is
    Ruling 179's measured cost.
    """
    assert observation_findings(_board(THE_CHECKOUT_CELL)) == []
    assert observation_findings(_board(BIDIRECTIONAL)) == [], (
        "⛔ both cells CLAIM a checkout; a cell that LIES is corroborate.py's subject"
    )


@pytest.mark.parametrize("declared", sorted(STARTED))
def test_planted_EVERY_started_word_is_in_the_population(declared: str) -> None:
    """⛔ Ruling 48: parametrised over the DERIVATION, so an empty set SKIPS.

    ⭐ **`in-progress` is in this population and that is a DECISION**, not an
    oversight: the three words that mean *started and not finished* are admitted
    and ⚠️ **leaving one out would be the defect this row exists to close — a
    closed set with a hole in it.**
    """
    if not STARTED:
        pytest.skip("the started vocabulary is empty, so there is no population to read")
    row = f"| `W42` | Developer 2 | none | 0 | ⏳ **{declared}** — taken |\n"
    assert _rules(observation_findings(_board(row))) == [RULE_INFLIGHT]


@pytest.mark.parametrize("absent", sorted(ABSENT - {""}))
def test_planted_the_plant_is_adversarial_to_the_SEARCH_TERM_not_the_subject(absent: str) -> None:
    """⛔ Ruling 140: the forbidden thing in a form the clause did not picture.

    ⚠️ **The clause pictured the word `none`.** ⭐ Every spelling of *no carrier*
    this board could reach for reads the same way, because the vocabulary is
    CLOSED and the cell is normalised before it is read.
    """
    row = f"| `W42` | Developer 2 | {absent} | 0 | in flight |\n"
    assert _rules(observation_findings(_board(row))) == [RULE_INFLIGHT]


#: ⛔ **What the board can AUTHOR, each as a `(header, row)` pair so the row
#: follows its own header.** ⚠️ **The first version of this population passed four
#: shapes and FAILED on the reordered one — and the fixture was wrong, not the
#: recogniser: it reordered the header and left the row in the old order, so
#: `state` read the checkout cell.** ⭐ **That is the plant contradicting its
#: author, and it is why a reordered column is tested as a PAIR.**
AUTHORABLE = [
    (
        "| Row | Owner | Checkout | Commits ahead | State |",
        "| `W42` | Dev | none | 0 | in flight |",
    ),
    (
        "| **Row** | **Owner** | **Checkout** | **Commits ahead** | **State** |",
        "| `W42` | Dev | none | 0 | **in flight** |",
    ),
    ("| Row | Owner | Checkout | Ahead | State |", "| `W42` | Dev | — | 0 | in-review |"),
    ("| Row | Owner | Checkout | Commits | Status |", "| `W42` | Dev | none | 0 | in-progress |"),
    (
        "| Row | Owner | State | Checkout | Commits ahead |",
        "| `W42` | Dev | in flight | none | 0 |",
    ),
    (
        "| Task | Owner | ⭐ Checkout | Commits ahead | State |",
        "| `W42` + `W43` | Dev | none | **+0** | ⏳ **in flight** — taken |",
    ),
]


@pytest.mark.parametrize(("header", "row"), AUTHORABLE)
def test_ruling_192_what_the_board_can_AUTHOR_is_a_SUBSET_of_what_this_RECOGNISES(
    header: str, row: str
) -> None:
    """⛔ Ruling 192: a census of what the tree EMITS owes the population it can AUTHOR.

    ⛔ **`authorable ⊆ recognisable`, never the equality** — the recogniser may
    read more shapes than the board writes, and that is safe; ⚠️ **the shape the
    board writes and the recogniser cannot see is how `test_chrome.py` went blind
    to `nav[aria-label=…]`.** ⭐ **So the roles are read FROM THE HEADER**: emphasis,
    a renamed column, a reordered column and an emoji are all shapes this board
    authors elsewhere, and none of them moves the reading.
    """
    text = _board(row + "\n").replace("| Row | Owner | Checkout | Commits ahead | State |", header)
    assert _rules(observation_findings(text)) == [RULE_INFLIGHT], (header, row)


def test_the_DELIMITED_form_is_read_and_the_reading_says_which_locator_answered() -> None:
    """⭐ Ruled round 49: a population grows BY A DELIMITER, never by inference.

    ⛔ **`board-duplicate` once fired on the author of `board-duplicate`** because
    the register's boundary was inferred from row shape and an ordinary *In
    flight* table satisfied it. ⚠️ **This board does not carry the markers yet —
    it is the PO's file and this instrument may not edit it** — ⭐ **so both
    locators are implemented and the reading NAMES which one answered**, which is
    what makes the missing markers visible on every run instead of assumed.
    """
    delimited = _board(THREE_HUNDRED_AND_FIFTY, delimited=True)
    assert _rules(observation_findings(delimited)) == [RULE_INFLIGHT, RULE_INFLIGHT]
    assert "delimited" in observation_reading(delimited)
    assert "header-declared" in observation_reading(_board(THREE_HUNDRED_AND_FIFTY))


# --------------------------------------------------------------------------
# Reading 3 — IMPOSSIBLE, and each must DIFFER from the pass
# --------------------------------------------------------------------------


def test_impossible_a_board_with_no_observation_table_DIFFERS_from_a_clean_one() -> None:
    """⛔ `0 rows` and `NONE FOUND` are different answers, and silence is neither.

    ⚠️ **A board whose observation table somebody deleted would otherwise read
    exactly like a board with nothing in flight** — ⭐ which is the false empty
    this project pays for twice over (check 3's own defect, `CTO-48/3`).
    """
    bare = _board()
    assert observation_findings(bare) == []
    assert "NONE FOUND" in observation_reading(bare)
    assert "NONE FOUND" not in observation_reading(_board(THE_CHECKOUT_CELL))


def test_impossible_a_W_shaped_table_that_declares_no_OBSERVATION_columns() -> None:
    """⛔ The distant reading this must not move: `test_init.py`'s five-cell plant.

    ⚠️ **Ruling 190(b): adding a member to a derived population edits every
    distant test that iterates it.** ⭐ **The locator requires a HEADER that
    DECLARES a `Checkout` column and a commits-ahead column**, so an ordinary
    five-cell table — including the one `test_init.py` plants outside the register
    markers — is not an observation table and this rule is silent on it.
    """
    ordinary = "| Order | Row | Why it is here | Placed |\n|---|---|---|---|\n"
    ordinary += "| 1 | `W96` | in flight, jumped `W74` | round 38 |\n"
    assert observation_findings(_board() + ordinary) == []
    assert "NONE FOUND" in observation_reading(_board() + ordinary)


@pytest.mark.parametrize("declared", sorted(NOT_STARTED))
def test_impossible_a_row_declaring_an_UNSTARTED_state_owes_no_carrier(declared: str) -> None:
    """⭐ The five excluded words, each excluded for a STATED reason.

    ⛔ `todo` is not started, so no carrier is owed; `done` carries a merge ref
    instead; `accepted` and `routed` are terminal; `blocked` owes a named
    unblocking condition, which IS its carrier.
    """
    row = f"| `W42` | Developer 2 | none | 0 | {declared} |\n"
    assert observation_findings(_board(row)) == []


def test_the_two_sides_of_the_vocabulary_are_a_TOTAL_partition_of_STATES() -> None:
    """⛔ A closed set with a HOLE in it is the defect this row was nearly shipped with.

    ⭐ **Derived against `STATES` rather than listed**, so a tenth state word
    cannot join the board's vocabulary without somebody classifying it — ⚠️ and
    `NOT_STARTED` is DECLARED rather than subtracted, because a subtraction would
    have swallowed the new word in silence.
    """
    assert STARTED | NOT_STARTED == set(STATES)
    assert not STARTED & NOT_STARTED
    assert {word for word in STARTED if STATES[word]} == set(), "a started row is never closed"


def test_a_cell_that_counts_NO_commits_is_not_a_cell_that_counts_ZERO() -> None:
    """⚠️ `—` declares no ahead observation; `0` declares one that refutes the row.

    ⛔ Both are findings and the MESSAGES DIFFER, because *"the board offered no
    reading"* and *"the board offered a reading that refutes it"* are different
    repairs.
    """
    none = observation_findings(_board("| `W42` | Dev | none | — | in flight |\n"))
    zero = observation_findings(_board("| `W42` | Dev | none | 0 | in flight |\n"))
    assert _rules(none) == _rules(zero) == [RULE_INFLIGHT]
    assert "counts no commit at all" in none[0].message
    assert "counts 0 commits ahead" in zero[0].message


def test_check_board_carries_the_three_rules_and_nothing_about_a_tree_without_a_board() -> None:
    """⭐ The wiring, asserted rather than assumed: the rules reach the floor's check."""
    findings = check_board.__doc__ or ""
    assert "189(b)" in findings
    board = _board(THREE_HUNDRED_AND_FIFTY)
    assert {f.rule for f in observation_findings(board)} == {RULE_INFLIGHT}
    assert all(f.path == BOARD for f in observation_findings(board))
