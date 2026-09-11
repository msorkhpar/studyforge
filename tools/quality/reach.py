"""Ruling 245's cliff, mechanised: the rulings index's TAIL is reachable from `docs/conventions/`.

**What it does.** Asserts that the newest ruling in `docs/tasks/rulings-index.md`
— its **tail** — is cited inside `docs/conventions/`, and prints a census of the
wider tail window through the notice channel. ⛔ A ruling that only its own
record remembers is a ruling whose cost is paid by the next office that did not
read that round (Ruling 245).

**How you use it.** `check_rulings_reach(root)` is registered in
`tools.quality.CHECKS`; `reach_notice(root)` is registered in `NOTICES`. The
remedy a finding gives is an edit, never a regeneration: a convention document
has to carry the clause.

**Depends on.** `tools.quality.rulings.derive` for the population and the tail,
`tools.quality.report` for the answer, and `re`. Standard library only. ⛔ It does
**not** read `config.SCAN_ROOTS`: its subject is one named directory of
documents, which is the whole exemption mechanism (see below).

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

## ⛔ REACHABILITY, not a grep for digits

⚠️ **`CTO-56`'s own dispatcher measured a bare `grep 231` matching a LINE COUNT**
— the use-versus-mention family at the level of a bare number. ⛔ **So the
predicate is the CITATION SPELLING `Ruling <digits>`, bounded on the right so
`Ruling 27` cannot be satisfied by `Ruling 278`** — the same literal spelling the
index's own population is derived from, and the reason a document mentioning
`278` in any other role does not count as landing.

## ⛔ Why `docs/conventions/` and nothing else

⭐ **Ruling 200 and Ruling 212 already decided what is NOT an artifact**, and
`board.md` carries their three exclusions by name: `docs/tasks/handoffs/` is a
record; `BOARD-ARCHIVE.md` is also a record; and `docs/tasks/rulings-index.md` is
GENERATED from the records, so every ruling is in it by construction. ⛔ **A
subject confined to `docs/conventions/` excludes all three structurally rather
than by a filter a reader has to remember** — which is the same exemption shape
`source_names` uses, and for the same reason.

## ⚠️ An empty population is a REFUSAL here, not a pass

⛔ **Ruling 191: an empty population returns the PASS reading rather than no
reading.** ⭐ So the two empties are separated: a tree with **no ruling records**
is not this repository and owes nothing (the notice says so); a tree that HAS
ruling records and **no readable `docs/conventions/`** is this repository with
its subject missing, and that is a finding. ⚠️ Without the split, deleting the
conventions directory would turn this check green.
"""

from __future__ import annotations

import re
from pathlib import Path

from tools.quality.report import Finding
from tools.quality.rulings.derive import records, series, sites

RULE_UNREACHED = "rulings-reach"

#: The directory a ruling must reach. ⛔ Ruling 245's subject, and the structural
#: form of Ruling 212's three exclusions — see the contract above.
CONVENTIONS_DIR = "docs/conventions"

#: How many of the newest rulings the NOTICE reports on. ⭐ 25 because that is
#: the population Ruling 245 measured (`217`–`241`, reached 0), so the notice's
#: window is the cliff's own width rather than a number somebody liked.
#: ⛔ It bounds the NOTICE only; the FINDING binds the tail alone.
REACH_WINDOW = 25


def _conventions(root: Path) -> list[Path]:
    """Return every markdown document under `CONVENTIONS_DIR`, sorted for R10."""
    directory = root / CONVENTIONS_DIR
    if not directory.is_dir():
        return []
    return sorted(path for path in directory.rglob("*.md") if path.is_file())


def _cited(number: int, documents: list[str]) -> bool:
    r"""Return whether `number` is cited as a ruling in any of `documents`.

    ⛔ The right bound is load-bearing: without `(?!\d)`, `Ruling 27` is
    satisfied by every `Ruling 278` in the tree, and the check would report a
    reach the tree does not have.
    """
    pattern = re.compile(rf"Ruling\s+{number}(?!\d)")
    return any(pattern.search(text) for text in documents)


def _tail(root: Path) -> int | None:
    """Return the highest number in the index's contiguous series, or None if none."""
    written = {site.number for record in records(root) for site in sites(record)}
    if not written:
        return None
    tail = series(written).tail
    return tail or None


def check_rulings_reach(root: Path) -> list[Finding]:
    """Return a finding when the newest ruling is cited in no convention document.

    ⛔ **A tree with no ruling records passes and says so through the notice**
    (Ruling 191, and `check_rulings_index`'s own precedent): the floor runs over
    a corpus, a consumer repository and an installed tree, and none of those
    owes a rulings index or a conventions directory.
    """
    tail = _tail(root)
    if tail is None:
        return []
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
    if _cited(tail, documents):
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
            f"regenerating the index cannot satisfy this, only an edit can.",
        )
    ]


def reach_notice(root: Path) -> list[str]:
    """Return the reach census over the tail window, printed whether anything failed.

    ⛔ The unreached members are enumerated rather than counted: Ruling 245's
    finding was invisible for twenty-five rounds precisely because nobody had
    printed the population, and `0 reached` is `0 = 0` until it says out of how
    many (Ruling 48, Ruling 128).
    """
    tail = _tail(root)
    if tail is None:
        return [
            f"rulings reach: no ruling records in this checkout, so no ruling is owed a "
            f"{CONVENTIONS_DIR}/ citation. This is not a failure — the floor runs over "
            f"trees that are not this repository."
        ]
    paths = _conventions(root)
    documents = [path.read_text(encoding="utf-8") for path in paths]
    window = range(max(1, tail - REACH_WINDOW + 1), tail + 1)
    unreached = [number for number in window if not _cited(number, documents)]
    reached = len(window) - len(unreached)
    members = ", ".join(str(number) for number in unreached) or "none"
    return [
        f"rulings reach: tail {tail} is "
        f"{'CITED' if tail not in unreached else 'UNREACHED'} in {CONVENTIONS_DIR}/; "
        f"over the {len(window)} newest rulings ({window.start}–{tail}) reached "
        f"{reached}, unreached {len(unreached)}, read from "
        f"{len(paths)} convention document(s). Unreached: {members}."
    ]


#: ⭐ Re-exported so a caller needs one import, and named so the mirror test can
#: assert the module's surface rather than its internals.
__all__ = [
    "CONVENTIONS_DIR",
    "REACH_WINDOW",
    "RULE_UNREACHED",
    "check_rulings_reach",
    "reach_notice",
]
