"""`W91`'s freshness arm: the rulings index is derived, or the floor says so.

**What it does.** Re-derives `docs/tasks/rulings-index.md` from the ruling
records on every floor run and fails the build when the document on disk is not
what the records say — which is the only way the index's completeness claim is
**asserted rather than typed**. ⭐ It also prints the derived population through
the notice channel, because `0 unindexed` is `0 = 0` until it says out of how
many (Ruling 48).

**How you use it.** `check_rulings_index(root)` is registered in
`tools.quality.CHECKS`; `rulings_notice(root)` is registered in `NOTICES`. The
remedy a finding gives is one command: `python3 -m tools.quality.rulings`.

**Depends on.** `derive` for the derivation, `document` for the rendering, and
`tools.quality.report` for the answer.

⛔ **Why this is a package INSIDE `tools.quality` and not a sibling of it**
(decided, not drifted). The derivation writes 197 anchors and `check_pointers`
reads every one, so the slug algorithm must have exactly one definition —
`pointers.slug`. ⚠️ A sibling package could not import it: `tools.knowledge`'s
standing rule is that a generator stays importable by a tree whose floor will
not import, and honouring that here would have meant a second copy of the
anchor algorithm. ⭐ **`tools/quality/board/` is the precedent**: a package
inside the floor, reading and asserting one document's shape.

## ⛔ Why this is a FINDING and not a notice, unlike the knowledge index

⚠️ **`check_knowledge_index` had to become a notice because its subject is
git-ignored** (Ruling 80): the same commit read clean on a fresh clone and red on
a machine that had built an index, so the verdict depended on untracked state.
⭐ **Nothing here is untracked.** The records are tracked, the index is tracked,
and the derivation is pure — so the same commit gives the same answer on every
machine, which is exactly the condition Ruling 80 sets for a check to be allowed
an exit code.

## ⚠️ The disagreement channel, and why it never fails a build

⛔ **Two independent derivations of a ruling's mint round exist** — the round's
own `Rulings minted:` declaration, and the best-ranked site where the number is
written — ⭐ **and the notice prints where they differ.** ⚠️ A difference is a
reading about the RECORDS, which are frozen (Ruling 106): it cannot be fixed by
anybody, so it is reported and never failed on. ⛔ What the index does with it is
already decided: the declaration wins, so the row quotes the minting round.
"""

from __future__ import annotations

from pathlib import Path

from tools.quality.report import Finding
from tools.quality.rulings.derive import INDEX_PATH, disagreements, entries, records, series, sites
from tools.quality.rulings.document import text

RULE_STALE = "rulings-index"

#: The one command that fixes every finding this module can report.
REBUILD_COMMAND = "python3 -m tools.quality.rulings"


def check_rulings_index(root: Path) -> list[Finding]:
    """Every way the index on disk disagrees with the records it is derived from.

    ⛔ **A tree with no ruling records passes, and says so through the notice.**
    The floor runs over arbitrary roots — a corpus, a consumer repository, an
    installed tree — and none of those owes a rulings index. ⚠️ An empty
    population returns the PASS reading rather than no reading (Ruling 191), and
    ⭐ THIS repository's requirement that the index exist is asserted by
    `tools/tests/quality/rulings/test_init.py`, which is where `board`'s absent
    `BOARD.md` is handled too.
    """
    if not records(root):
        return []
    expected = text(root)
    target = root / INDEX_PATH
    if not target.exists():
        return [
            Finding(
                INDEX_PATH,
                0,
                RULE_STALE,
                f"the rulings index does not exist, so every bare `(Ruling N)` in this "
                f"repository resolves to nothing. Run `{REBUILD_COMMAND}`.",
            )
        ]
    current = target.read_text(encoding="utf-8")
    if current == expected:
        return []
    rows = len(entries(root))
    return [
        Finding(
            INDEX_PATH,
            0,
            RULE_STALE,
            f"stale: the records derive {rows} rulings and this document is not what that "
            f"derivation renders. A hand-edit here is a finding, not a fix (R19) — the "
            f"index is generated. Run `{REBUILD_COMMAND}`.",
        )
    ]


def rulings_notice(root: Path) -> list[str]:
    """Return the derived population, printed whether or not anything failed.

    ⛔ The denominator is the point: a reader of `0 unindexed` learns nothing
    until the line says how many rulings were derived, from how many records,
    and what fell outside the series (Ruling 48, Ruling 128).
    """
    found = records(root)
    if not found:
        return [
            "rulings index: no ruling records in this checkout, so nothing is indexed and "
            "nothing is owed. This is not a failure — the floor runs over trees that are "
            "not this repository."
        ]
    rows = entries(root)
    written = {site.number for record in found for site in sites(record)}
    population = series(written)
    outside = ", ".join(str(number) for number in population.outside) or "none"
    differing = disagreements(root)
    return [
        f"rulings index: {len(rows)} rulings derived from {len(found)} ruling records, "
        f"tail {population.tail}, outside the series: {outside}, "
        f"mint round disputed for {len(differing)} of {len(rows)}."
    ]
