"""Ruling 245's cliff, mechanised: the rulings index's TAIL is reachable from `docs/conventions/`.

**What it does.** Asserts that the newest ruling in `docs/tasks/rulings-index.md`
— its **tail** — is cited inside `docs/conventions/`, and prints TWO censuses
through the notice channel: the newest `REACH_WINDOW` rulings, and the members
still uncited **below** that window. ⛔ A ruling that only its own record
remembers is a ruling whose cost is paid by the next office that did not read
that round (Ruling 245).

**How you use it.** `check_rulings_reach(root)` is registered in
`tools.quality.CHECKS`; `reach_notice(root)` is registered in `NOTICES` and
returns two lines on any tree that has rulings. The remedy a finding gives is an
edit, never a regeneration: a convention document has to carry the clause.

**Depends on.** `tools.quality.citations` for the citation grammar —
`cited_numbers`, `spellings` and `MAX_RANGE_SPAN` are re-exported here so a
caller needs one import — `tools.quality.rulings.derive` for the population and
the tail, `tools.quality.report` for the answer, and `pathlib`. Standard library
only. ⛔ It does **not** read `config.SCAN_ROOTS`: its subject is one named
directory of documents, which is the whole exemption mechanism (see below).

## ⛔ Why the CHECK is the TAIL and the NOTICE is the WINDOW

⭐ **Ruling 245 scoped the instrument to the tail deliberately, and the scope is
the part most likely to be widened by a well-meaning taker** — quoted rather
than paraphrased (Ruling 195):

> ⚠️ **Scoped deliberately to the TAIL and not to all 241: a sweep demanding
> every ruling reach a convention would fire on 25 at once and on rulings that
> correctly landed in code, and a notice whose first wave fires 25 times is a
> notice nobody reads twice.**

⛔ **So the FINDING binds one ruling — the tail — and that is the ruling a round
has just minted.** ⭐ It fires on exactly the failure the cliff was made of: a
round mints a ruling, writes it into its own record, and lands it nowhere. ⚠️ It
cannot fire twenty-five times on its first wave, which is the property that
makes it readable.

⭐ **The NOTICE carries the backlog instead, enumerated by number**, because a
hole nobody can fail you for still has to be visible (FND-07's argument, and
Ruling 48's: the unreached count means nothing without its denominator).

## ⛔ AND THE WINDOW SLIDES, SO THE NOTICE REPORTS BELOW IT TOO (Ruling 304)

⛔ **`REACH_WINDOW` is 25 wide and it MOVES with the tail, so a ruling still
uncited BELOW it is invisible to the one number that reports the hole** —
⭐ **which makes `unreached 0` satisfiable by MINTING: an instrument built to
report a cliff can be cleared by walking away from it.** ⚠️ **MEASURED across
two refs by two offices: at `428223c` the notice read *"over the 25 newest
(272–296) … unreached 3 — 273, 274, 275"*; at `270296d` it read `285–309,
unreached 0` while all three of those were still uncited. Nothing landed. The
hole AGED OUT.** ⛔ Ruling 304's own words are the obligation this discharges:

> ⛔ **AND THE INSTRUMENT OWES A ROW, not an edit by me: the notice should report
> members that are still uncited BELOW the window, or its `unreached 0` means
> *none in the last 25* while reading as *none*.**

⭐ **THE TWO FIGURES ARE NEVER SUMMED, and that is a rule rather than a layout
choice.** They answer different questions — *is the round that minted paying?*
(Ruling 286's minter-pays clause, which the window measures) and *is the backlog
being worked?* — ⛔ **and one merged scalar would make a paying minter and a
growing backlog indistinguishable, which is the defect one bound over.** ⚠️ So
they are printed as two lines, each with its own denominator, and
`tools/tests/quality/test_reach.py` asserts each moves WITHOUT the other.

⛔ **AND IT IS NOT A WIDENING OF `REACH_WINDOW`.** ⭐ 25 is what makes the
minter-pays reading cheap and legible; widening it to 100 would replace a sharp
question with a blunt one and bury Ruling 286's signal. **The remedy is a SECOND
reading, not a bigger first one.**

## ⛔ THE GRAMMAR IS A SIBLING MODULE, and the split is Ruling 261's

⚠️ **MEASURED at `6aef480`: this module was `385` of R11's `400`.** ⭐ **Ruling
261 — a ceiling is not a budget — so the next edit was the SPLIT `W133`'s taker
had already named: the citation grammar moved to `tools/quality/citations.py`,
which owns the spellings, the two narrowings, the code-span exclusion and three
of the four declared gaps.** ⛔ **The seam runs ONE WAY: this module imports that
one, and that one imports nothing back.**

## ⛔ Why `docs/conventions/` and nothing else

⭐ **Ruling 200 and Ruling 212 already decided what is NOT an artifact**, and
`board.md` carries their three exclusions by name: `docs/tasks/handoffs/` is a
record; `BOARD-ARCHIVE.md` is also a record; and `docs/tasks/rulings-index.md` is
GENERATED from the records, so every ruling is in it by construction. ⛔ **A
subject confined to `docs/conventions/` excludes all three structurally rather
than by a filter a reader has to remember** — which is the same exemption shape
`source_names` uses, and for the same reason.

## ⛔ THE FOURTH DECLARED GAP, which is this module's own

⛔ **Ruling 258: a declared-gaps list is a CLOSED CLAIM.** ⭐ **Three of the four
gaps belong to the grammar and are declared in `citations.py`; this one belongs
to what this module CONCLUDES, so it is declared here: a CITATION is not a
LANDING.** ⚠️ A convention that merely *mentions* `Ruling N` in passing — inside
a neighbouring ruling's prose, say — satisfies this exactly as a section that
carries the clause does. ⛔ **MEASURED, and it is why the gap is stated rather
than implied: at `6c4e3d0` rulings `235`, `238`, `240` and `241` all read REACHED
over Ruling 245's own population of `217`–`241`, and three of those four were
incidental mentions inside round 58's sections rather than the clause `W126` was
routed to land.** ⭐ **Ruling 200 already drew this boundary and drew it the same
way — *"the reviewer confirms one of them is the document the rule was WRITTEN
INTO"*** — so the machine's half is the citation and the reviewer's half is
whether it teaches anything. ⚠️ **A check that tried to judge the second would be
judging prose, which is the one thing this floor never does.**

## ⚠️ An empty population is a REFUSAL here, not a pass

⛔ **Ruling 191: an empty population returns the PASS reading rather than no
reading.** ⭐ So the two empties are separated: a tree with **no ruling records**
is not this repository and owes nothing (the notice says so); a tree that HAS
ruling records and **no readable `docs/conventions/`** is this repository with
its subject missing, and that is a finding. ⚠️ Without the split, deleting the
conventions directory would turn this check green. ⭐ **A third empty joins them
with the below-window reading: a tree whose whole series FITS inside the window
has nothing below it, and the notice SAYS SO rather than printing `0 of 0`.**
"""

from __future__ import annotations

from pathlib import Path

from tools.quality.citations import MAX_RANGE_SPAN, cited_numbers, spellings
from tools.quality.report import Finding
from tools.quality.rulings.derive import records, series, sites

RULE_UNREACHED = "rulings-reach"

#: The directory a ruling must reach. ⛔ Ruling 245's subject, and the structural
#: form of Ruling 212's three exclusions — see the contract above.
CONVENTIONS_DIR = "docs/conventions"

#: How many of the newest rulings the NOTICE's FIRST line reports on. ⭐ 25
#: because that is the population Ruling 245 measured (`217`–`241`, reached 0),
#: so the notice's window is the cliff's own width rather than a number somebody
#: liked. ⛔ It bounds the notice's first line only; the FINDING binds the tail
#: alone and the SECOND line reports everything below this.
#:
#: ⚠️ `citations.MAX_RANGE_SPAN` is this figure, written there because the seam
#: cannot import backwards; the equality is asserted in this module's mirror.
REACH_WINDOW = 25

#: ⭐ The declared gaps, named where the number is READ rather than in a module
#: docstring the reader of a failure never opens (Ruling 280's first arm, Ruling
#: 281's audience clause). ⛔ It is why both notice lines say UPPER BOUND.
_GAPS = (
    "emphasis inside the number, a citation wrapped across a line break, a word "
    "between the plural and its members"
)


def _conventions(root: Path) -> list[Path]:
    """Return every markdown document under `CONVENTIONS_DIR`, sorted for R10."""
    directory = root / CONVENTIONS_DIR
    if not directory.is_dir():
        return []
    return sorted(path for path in directory.rglob("*.md") if path.is_file())


def _citations(documents: list[str]) -> set[int]:
    r"""Return every ruling number cited anywhere in `documents`.

    ⛔ Computed ONCE for the whole population rather than per number: the
    predicate is no longer a single `re.search` per ruling, and re-deriving it
    three hundred times over eight documents would read the same prose
    twenty-four hundred times.
    """
    found: set[int] = set()
    for text in documents:
        found |= cited_numbers(text)
    return found


def _population(root: Path) -> tuple[int, ...]:
    """Return the index's contiguous ruling series, lowest first, or empty.

    ⚠️ CONTIGUOUS, so a probe number written as a ruling (`9999`) is outside it.
    ⛔ If the tail were `max()`, an impossible control in somebody's probe table
    would become the thing every convention had to cite.
    """
    written = {site.number for record in records(root) for site in sites(record)}
    if not written:
        return ()
    return series(written).numbers


def check_rulings_reach(root: Path) -> list[Finding]:
    """Return a finding when the newest ruling is cited in no convention document.

    ⛔ **A tree with no ruling records passes and says so through the notice**
    (Ruling 191, and `check_rulings_index`'s own precedent): the floor runs over
    a corpus, a consumer repository and an installed tree, and none of those
    owes a rulings index or a conventions directory.
    """
    population = _population(root)
    if not population:
        return []
    tail = population[-1]
    paths = _conventions(root)
    if not paths:
        return [
            Finding(
                CONVENTIONS_DIR,
                0,
                RULE_UNREACHED,
                "this tree has ruling records and no readable convention documents, so "
                "no ruling can reach one. An empty population is refused here rather "
                "than passed (Ruling 191).",
            )
        ]
    documents = [path.read_text(encoding="utf-8") for path in paths]
    if tail in _citations(documents):
        return []
    return [
        Finding(
            CONVENTIONS_DIR,
            0,
            RULE_UNREACHED,
            f"Ruling {tail} is the tail of docs/tasks/rulings-index.md and no document "
            f"under {CONVENTIONS_DIR}/ cites it. A ruling is not LANDED until a "
            f"convention document carries it, and the reviewer who mints it owns that "
            f"edit (Ruling 245). Quote it, do not paraphrase it (Ruling 195) — and "
            f"regenerating the index cannot satisfy this, only an edit can. "
            f"⭐ THE SPELLINGS THAT CLEAR THIS (Ruling 280): {spellings(tail)}.",
        )
    ]


def _window_line(tail: int, window: range, unreached: list[int], documents: int) -> str:
    """Render the first census: the newest `REACH_WINDOW` rulings, and nothing else."""
    members = ", ".join(str(number) for number in unreached) or "none"
    return (
        f"rulings reach: tail {tail} is "
        f"{'CITED' if tail not in unreached else 'UNREACHED'} in {CONVENTIONS_DIR}/; "
        f"over the {len(window)} newest rulings ({window.start}–{tail}) reached "
        f"{len(window) - len(unreached)}, unreached {len(unreached)} IN THIS WINDOW "
        f"ALONE — an UPPER BOUND on the hole (Rulings 280, 281), because reach is "
        f"read from the declared citation spellings outside code spans and fences, "
        f"and the three declared gaps ({_GAPS}) read UNREACHED. Read from "
        f"{documents} convention document(s). Unreached: {members}."
    )


def _below_line(window: range, below: tuple[int, ...], uncited: list[int]) -> str:
    """Render the second census: the members still uncited BELOW the window.

    ⛔ **Ruling 304, and the two clauses that shape it.** The members are NAMED
    rather than counted, because a bare scalar is the form that produced the
    defect — `unreached 0` on a tree carrying dozens of uncited rulings. ⚠️ And
    this figure is NEVER added to the window's: see the contract above.

    ⭐ An empty population below the window is the third empty (Ruling 191): it
    is REPORTED as the window covering the whole series, never as `0 of 0`.
    """
    if not below:
        return (
            f"rulings reach below the window: the {REACH_WINDOW}-newest window covers "
            f"the whole derived series ({len(window)} ruling(s)), so there is nothing "
            f"below it. Still uncited below the window: none."
        )
    members = ", ".join(str(number) for number in uncited) or "none"
    return (
        f"rulings reach below the window: {len(uncited)} of the {len(below)} rulings "
        f"below {window.start} are still uncited in {CONVENTIONS_DIR}/ — a SECOND "
        f"reading, and it is NEVER added to the figure above (Ruling 304). That one "
        f"asks whether the round that minted is paying (Ruling 286); this one asks "
        f"whether the backlog is being worked, and minting SLIDES the window, so a "
        f"member leaves it whether it LANDED or AGED OUT. Also an UPPER BOUND, for "
        f"the same three declared gaps ({_GAPS}). Still uncited below the window: "
        f"{members}."
    )


def reach_notice(root: Path) -> list[str]:
    """Return the two reach censuses, printed whether or not anything failed.

    ⛔ The unreached members are enumerated rather than counted in BOTH: Ruling
    245's finding was invisible for twenty-five rounds precisely because nobody
    had printed the population, and `0 reached` is `0 = 0` until it says out of
    how many (Ruling 48, Ruling 128).
    """
    population = _population(root)
    if not population:
        return [
            f"rulings reach: no ruling records in this checkout, so no ruling is owed a "
            f"{CONVENTIONS_DIR}/ citation. This is not a failure — the floor runs over "
            f"trees that are not this repository."
        ]
    tail = population[-1]
    paths = _conventions(root)
    citations = _citations([path.read_text(encoding="utf-8") for path in paths])
    window = range(max(1, tail - REACH_WINDOW + 1), tail + 1)
    below = tuple(number for number in population if number < window.start)
    return [
        _window_line(tail, window, [n for n in window if n not in citations], len(paths)),
        _below_line(window, below, [n for n in below if n not in citations]),
    ]


#: ⭐ Re-exported so a caller needs one import, and named so the mirror test can
#: assert the module's surface rather than its internals. ⛔ `cited_numbers`,
#: `spellings` and `MAX_RANGE_SPAN` now LIVE in `tools.quality.citations`; they
#: stay addressable here because `docs/conventions/review-rubric.md` teaches
#: `from tools.quality.reach import cited_numbers` as the way to diff a predicate
#: over its whole population (Ruling 302), and a split may not break a documented
#: import out from under the document that teaches it.
__all__ = [
    "CONVENTIONS_DIR",
    "MAX_RANGE_SPAN",
    "REACH_WINDOW",
    "RULE_UNREACHED",
    "check_rulings_reach",
    "cited_numbers",
    "reach_notice",
    "spellings",
]
