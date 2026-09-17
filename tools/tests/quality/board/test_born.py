"""Mirror of `tools/quality/board/born.py` (R12) — ⛔ the MINT, against its own clause.

⭐ **Ruling 123's three readings, all three here:** ⛔ **LIVE** — the real `rows/` and
the real convention pass, and the exemption is measured rather than asserted;
⛔ **PLANTED** — each direction of the clause fires on a tree built to break exactly it,
adversarial to the SEARCH TERM rather than to the subject (Ruling 140); ⛔ **IMPOSSIBLE**
— a tree with no row files reports NOTHING, and the reading DIFFERS from the pass by
naming its own `0` (Ruling 48).

## ⛔ THE ONE READING THIS MODULE EXISTS FOR, and it is not *the check is green*

⚠️ **`W305` was minted WITHOUT the pointer while the round record truthfully said
*"pointers verified"*** — ⭐ **both true at once, because a resolution check has nothing
to resolve when the pointer is ABSENT.** ⛔ **So the assertion that matters here is that
the verdict MOVES WITH THE CLAUSE**
(`test_the_verdict_MOVES_when_the_clause_MOVES`): an instrument carrying its own copy of
the pattern would pass that test's setup and fail its point.

## ⛔ THE EXEMPTION IS ASSERTED IN BOTH DIRECTIONS, because one alone is free

⭐ **`PRE_CLAUSE` is INHABITED and EXACTLY inhabited** — every name in it is a row the
clause's own command really does refuse, and every row NOT in it passes. ⚠️ **An
exemption nobody measures is an exemption that outlives its reason**, and this one exists
only because Ruling 244(e) says in terms that it binds the MINT and is not a retroactive
sweep of `rows/`. ⛔ **The predicate is never widened to let those rows through**, which
`test_the_exemption_is_BY_NAME_and_not_a_widened_predicate` asserts by moving one of the
same bodies to a name the clause DID bind.
"""

from __future__ import annotations

import re
from pathlib import Path

from tests.support import repository_root
from tools.quality.board.born import (
    CLAUSE,
    CLAUSE_SUBJECT,
    PRE_CLAUSE,
    RULE_BORN,
    RULE_CLAUSE,
    born_findings,
    born_reading,
    clause_pattern,
    refused,
)
from tools.quality.board.register import ROW_FRAME, ROWS
from tools.quality.config import read_text

#: ⭐ A row file that PASSES: its argument ends in an anchored pointer at the archive.
ARCHIVE_ARM = "[the mint](../BOARD-ARCHIVE.md#po-round-94)\n"

#: ⭐ The clause's OTHER arm, and it is not decoration: a row minted out of a handoff
#: cites that handoff. ⛔ A predicate reading only the archive would refuse correct work,
#: which is the narrowing the brief for `W306` named as `PO-94`'s shape all over again.
HANDOFF_ARM = "[the finding](../handoffs/W302.md#findings)\n"


def _row(body: str, name: str = "W2") -> str:
    """Return a row file with its frame and `body` as its argument."""
    frame = f"⛔ This file carries the ARGUMENT for board row `{name}` {ROW_FRAME}"
    return f"# {name}\n\n{frame}\n\n{body}"


def _live_pattern() -> str:
    """Return Ruling 244(e)'s pattern, read from THIS repository's convention."""
    pattern = clause_pattern(read_text(repository_root() / CLAUSE) or "")
    assert pattern is not None, f"⛔ the clause is not readable in {CLAUSE}"
    return pattern


def _tree(tmp_path: Path, rows: dict[str, str], pattern: str | None = None) -> Path:
    """Build a tree with `rows` beside a board and a convention carrying the clause.

    ⭐ **`pattern` defaults to the LIVE one**, so a fixture cannot quietly test a
    predicate this repository does not ship; ⛔ passing a different one is how
    `test_the_verdict_MOVES_when_the_clause_MOVES` proves the clause is RUN.
    """
    (tmp_path / ROWS).mkdir(parents=True, exist_ok=True)
    for name, body in rows.items():
        (tmp_path / ROWS / f"{name}.md").write_text(body, encoding="utf-8")
    if pattern is not None:
        (tmp_path / CLAUSE).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / CLAUSE).write_text(
            f"```bash\n# a comment naming {CLAUSE_SUBJECT}<ID>.md, which is NOT the command\n"
            f"grep -LE '{pattern}' {CLAUSE_SUBJECT}<ID>.md\n```\n",
            encoding="utf-8",
        )
    return tmp_path


# --------------------------------------------------------------------------
# Reading 1 — LIVE
# --------------------------------------------------------------------------


def test_live_tree_passes_the_clause_it_ships() -> None:
    """⭐ Every row file in this repository outside `PRE_CLAUSE` carries the pointer.

    ⛔ **This is the reading that makes every planted one mean something**, and it is
    the reading `W306` could not have taken before this arm existed.
    """
    assert born_findings(repository_root()) == []


def test_the_live_population_is_INHABITED_so_the_green_is_a_reading() -> None:
    """⛔ Ruling 191: a pass over an empty population is not a pass.

    ⭐ **The denominator is printed on every run**, so a `0` here is never `0 = 0`
    (Ruling 48).
    """
    reading = born_reading(repository_root())
    judged = int(reading.split(f"over {ROWS}/: ")[1].split(" row file(s)")[0])
    assert judged > 0, f"⛔ born vacuous — nothing was judged: {reading}"
    assert f"READ from {CLAUSE}" in reading, "⛔ the predicate was not read from the clause"


def test_the_live_reading_NAMES_the_exemption_rather_than_hiding_it() -> None:
    """⭐ Ruling 185's form: the population is narrowed and the NAME is printed."""
    reading = born_reading(repository_root())
    assert "excluded BY NAME as minted before the clause" in reading
    for name in PRE_CLAUSE:
        assert name in reading, f"⛔ {name} is excluded and not printed"


def test_the_exemption_is_EXACTLY_INHABITED_on_the_live_tree() -> None:
    """⛔ Every excluded name is really refused, and every other row really passes.

    ⚠️ **This is the assertion that stops `PRE_CLAUSE` outliving its reason.** ⭐ The day
    one of those rows gains its pointer, or a row the clause DID bind loses one, this
    reddens and somebody has to decide — which is the closed-set failure mode this
    project prefers to a silent admission.
    """
    root = repository_root()
    pattern = re.compile(_live_pattern())
    population = sorted((root / ROWS).glob("*.md"))
    assert population, f"⛔ born vacuous: no row files under {ROWS}/"
    refused_now = {path.stem for path in population if refused(pattern, read_text(path) or "")}
    assert refused_now == set(PRE_CLAUSE), (
        f"⛔ the clause's own command refuses {sorted(refused_now)} and `PRE_CLAUSE` "
        f"names {sorted(PRE_CLAUSE)}. ⭐ A row the clause DID bind is NOT excused here — "
        f"add its pointer. ⚠️ A name in `PRE_CLAUSE` that now passes has outlived its "
        f"reason and the tuple should lose it."
    )


def test_the_instrument_holds_NO_COPY_of_the_clauses_pattern() -> None:
    """⛔ `W306`'s own defect, one layer down: a second spelling is free to disagree.

    ⭐ **The source of the arm is read and the clause's pattern must NOT appear in it.**
    ⚠️ A restatement would pass every other test in this module and fail the row.
    """
    source = read_text(repository_root() / "tools/quality/board/born.py") or ""
    assert source, "⛔ the arm's own source was not readable"
    assert _live_pattern() not in source, (
        "⛔ the arm carries a COPY of Ruling 244(e)'s pattern. ⭐ It must PARSE the "
        "clause's own fenced command instead — a second spelling is the defect `W306` "
        "exists to close."
    )


# --------------------------------------------------------------------------
# Reading 2 — PLANTED
# --------------------------------------------------------------------------


def test_a_row_born_with_NO_pointer_is_REFUSED(tmp_path: Path) -> None:
    """⛔ The mint `W305` actually took, planted: an argument with no pointer at all."""
    root = _tree(tmp_path, {"W2": _row("The argument, with no pointer home.\n")}, _live_pattern())
    findings = born_findings(root)
    assert [finding.rule for finding in findings] == [RULE_BORN]
    assert findings[0].path == f"{ROWS}/W2.md"


def test_an_UNANCHORED_pointer_is_NOT_a_pass(tmp_path: Path) -> None:
    """⚠️ Ruling 140 — adversarial to the SEARCH TERM: the pointer is there, the `#` is not.

    ⭐ **The clause's own sentence is that the address must resolve to the ARGUMENT, not
    to the document that contains it** — a bare link lands the reader at the top of a
    record hundreds of sections long.
    """
    root = _tree(tmp_path, {"W2": _row("[the mint](../BOARD-ARCHIVE.md)\n")}, _live_pattern())
    assert [finding.rule for finding in born_findings(root)] == [RULE_BORN]


def test_BOTH_ARMS_of_the_clause_are_a_pass(tmp_path: Path) -> None:
    """⭐ An anchored pointer into the ARCHIVE or into `handoffs/` satisfies it.

    ⛔ **A narrower predicate is a different check** — the brief's own words — and a
    fixture carrying only the archive arm would never have noticed.
    """
    root = _tree(
        tmp_path,
        {"W2": _row(ARCHIVE_ARM), "W3": _row(HANDOFF_ARM, name="W3")},
        _live_pattern(),
    )
    assert born_findings(root) == []


def test_a_pointer_that_is_not_RELATIVE_TO_ROWS_is_refused(tmp_path: Path) -> None:
    """⛔ The clause's `../` is load-bearing: it is addressed from `docs/tasks/rows/`."""
    root = _tree(
        tmp_path, {"W2": _row("[the mint](BOARD-ARCHIVE.md#po-round-94)\n")}, _live_pattern()
    )
    assert [finding.rule for finding in born_findings(root)] == [RULE_BORN]


def test_the_match_is_PER_LINE_exactly_as_grep_matches(tmp_path: Path) -> None:
    """⛔ A pointer split across a newline is NOT a match, because `grep` reads lines.

    ⚠️ **The clause's `[^)]*` excludes `)` and nothing else, so a whole-file search would
    let it run across a newline** and admit a pointer the command itself refuses.
    ⭐ **A predicate WIDER than the clause it claims to run is the same defect as a
    narrower one, pointing the other way.**
    """
    split = _row("[the mint](../handoffs/W302\n.md#findings)\n")
    root = _tree(tmp_path, {"W2": split}, _live_pattern())
    assert [finding.rule for finding in born_findings(root)] == [RULE_BORN]


def test_the_verdict_MOVES_when_the_clause_MOVES(tmp_path: Path) -> None:
    """⛔ THE ROW'S OWN CLAUSE: the mint path RUNS Ruling 244(e)'s command, never a copy.

    ⭐ **One row body, two conventions.** ⚠️ Under the shipped clause the archive arm
    PASSES; under a clause amended to accept only `handoffs/`, the SAME body is refused.
    ⛔ **An instrument holding its own copy of the pattern reports the same verdict
    twice**, which is exactly the failure this row exists to make impossible.
    """
    body = {"W2": _row(ARCHIVE_ARM)}
    assert born_findings(_tree(tmp_path / "shipped", body, _live_pattern())) == []

    amended = r"\]\(\.\./(handoffs/[^)]*)#"
    findings = born_findings(_tree(tmp_path / "amended", body, amended))
    assert [finding.rule for finding in findings] == [RULE_BORN], (
        "⛔ the verdict did not move with the clause — the arm is not running it"
    )


def test_a_clause_it_cannot_READ_is_a_FINDING_and_never_a_silence(tmp_path: Path) -> None:
    """⛔ Ruling 191: an empty population is never the pass reading.

    ⚠️ **The convention IS THERE and its command is gone** — somebody removed the
    predicate out from under the gate. ⭐ That is the `W306` shape itself, a signal whose
    exit nothing reads, so it fails the build rather than passing it.
    """
    root = _tree(tmp_path, {"W2": _row("no pointer here\n")}, pattern=None)
    (root / CLAUSE).parent.mkdir(parents=True, exist_ok=True)
    (root / CLAUSE).write_text(
        "### Ruling 244(e)\n\nThe clause's prose, with its command REMOVED.\n", encoding="utf-8"
    )
    findings = born_findings(root)
    assert [finding.rule for finding in findings] == [RULE_CLAUSE]
    assert findings[0].path == CLAUSE
    assert "NOT READABLE" in born_reading(root)


def test_a_tree_with_NO_CONVENTION_AT_ALL_asserts_nothing(tmp_path: Path) -> None:
    """⛔ An ABSENT document is not a REMOVED clause, and only the second is a finding.

    ⚠️ **The floor runs over arbitrary roots** (R10) — a corpus repository, a temp tree —
    ⛔ **so a finding here would assert WHICH repository you are in.** ⭐ **The presence
    half is `test_the_live_population_is_INHABITED_so_the_green_is_a_reading`**, which
    knows the answer for THIS repository should be yes.

    ⚠️ **This arm's first draft collapsed the two and reddened every synthetic board
    fixture in this package** — the reading is recorded here so it is not re-derived.
    """
    root = _tree(tmp_path, {"W2": _row("no pointer here\n")}, pattern=None)
    assert not (root / CLAUSE).exists()
    assert born_findings(root) == []
    assert "ABSENT" in born_reading(root)


def test_the_exemption_is_BY_NAME_and_not_a_widened_predicate(tmp_path: Path) -> None:
    """⛔ Ruling 185: the POPULATION is narrowed in the instrument; the PREDICATE is not.

    ⭐ **The SAME body passes under an excluded name and is refused under a bound one.**
    ⚠️ A predicate quietly tolerant of a missing pointer would let both through, and the
    next mint with it.
    """
    body = _row("A pre-clause argument, with no pointer home.\n")
    excluded = PRE_CLAUSE[0]
    assert born_findings(_tree(tmp_path / "old", {excluded: body}, _live_pattern())) == []

    findings = born_findings(_tree(tmp_path / "new", {"W999": body}, _live_pattern()))
    assert [finding.rule for finding in findings] == [RULE_BORN]


# --------------------------------------------------------------------------
# Reading 3 — IMPOSSIBLE
# --------------------------------------------------------------------------


def test_impossible_no_row_files_at_all(tmp_path: Path) -> None:
    """⛔ A tree with no rows is CLEAN, and the reading DIFFERS from the pass by saying so.

    ⚠️ **The floor runs over arbitrary roots** (R10) — a temp tree, a corpus repository —
    ⛔ **so a finding here would be asserting which repository you are in.** ⭐ The
    presence half is `test_live_tree_passes_the_clause_it_ships`, which knows the answer
    for THIS repository should be yes.
    """
    root = _tree(tmp_path, {}, _live_pattern())
    assert born_findings(root) == []
    assert f"over {ROWS}/: 0 row file(s)" in born_reading(root)
