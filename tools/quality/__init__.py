"""The repository's quality floor: size, mirrored tests, contracts, style, personal data.

**What it does.** Reads the tree and reports every place it falls below the
floor the conventions describe — R11's size ceiling, R12's mirror, R17's
contract, style, and R7's ban on personal data reaching a tracked file. Exit
code, not advice — `python3 -m tools.quality` returns 1 when anything is found,
so the rules hold without anybody policing them in review.

**How you use it.**

    python3 -m tools.quality            # from the repository root
    python3 -m tools.quality --root .   # explicit

or, from Python:

    from tools.quality import run_all, format_findings
    findings = run_all(Path("."))

`tests/test_quality_floor.py` is a thin wrapper that runs exactly that and
fails the suite on any finding, so `pytest` alone is enough — there is no
separate command a contributor has to remember, and no way to land a violation
by forgetting one. ⛔ The wrapper calls this package; it never re-implements a
rule, so "400 lines" has one definition and one place to change it.

**Depends on.** The standard library, and nothing else, ever. This has to run
on a clean checkout with no network and no installs (FND-03 gives it a
container; it must not need one).

⛔ **Why this lives in `tools/` and not in `src/studyforge/`** (ruled, not
chosen). Spec §3.2 enumerates what the framework ships, package by package,
and a lint tool is not on that list. Putting it under `src/` would make the
ceiling check part of `studyforge`'s importable API — versioned under R9,
depended on by consumers, impossible to change without a contract discussion —
to buy nothing a build script wanted. It is excluded from packaging by
construction: `[tool.setuptools.packages.find]` looks only in `src`, so an
installed `studyforge` contains no `tools`.

⛔ **And its tests sit beside it, at `tools/tests/`**, not in the framework's
`tests/` tree. R12's requirement is that a failing test names a module rather
than a subsystem — locality — and that is satisfied by a mirror wherever the
mirror is rooted. `config.MIRRORS` names the pair, so `tools/quality/size.py`
is required to have `tools/tests/quality/test_size.py` exactly as a source
module is required to have its own.

⭐ **It checks itself.** `tools/` is one of `config.SCAN_ROOTS`, so this
package is held to its own ceiling, its own mirror and its own contract rule.
A checker exempt from what it checks is a checker nobody has tested.
"""

from __future__ import annotations

from pathlib import Path

from tools.quality.approach import approach_notice
from tools.quality.board import board_state, check_board
from tools.quality.collisions import check_anchor_collisions, collision_census
from tools.quality.config import (
    LINE_LENGTH,
    MIN_JUSTIFICATION_CHARS,
    SIZE_EXCEPTION_MARKER,
    SOURCE_LINE_CEILING,
    TEST_LINE_CEILING,
)
from tools.quality.docstrings import check_docstrings
from tools.quality.handoffs import check_handoffs
from tools.quality.handoffs.existence import check_handoff_existence, handoff_existence
from tools.quality.lint import lint_notice
from tools.quality.mirror import check_mirrors
from tools.quality.personal_data import check_personal_data
from tools.quality.pointers import check_pointers, pointer_coverage
from tools.quality.reach import check_rulings_reach, reach_notice
from tools.quality.report import Finding, format_findings
from tools.quality.rulings import check_rulings_index, rulings_notice
from tools.quality.size import check_sizes
from tools.quality.source_names import check_source_names
from tools.quality.style import check_style

#: Every check, in the order their findings are reported. Adding a check means
#: adding it here and nowhere else.
#:
#: ⚠️ `check_personal_data` is the only one that reads the WHOLE tree rather
#: than the Python files under `SCAN_ROOTS`. R7 has been violated in this
#: repository once already and it was in a document, so a sweep confined to
#: `.py` would have missed the only instance there has been.
#:
#: ⚠️ `check_source_names` is its mirror image: the only one that reads
#: **less** than `SCAN_ROOTS`, because R1 binds framework source and a
#: document must be able to name a corpus or the measurements it holds become
#: unattributable. ⛔ That narrowing is the whole exemption mechanism — a
#: module cannot be excused, and nothing is scanned that would need excusing.
#:
#: ⚠️ `check_handoffs` is the only one that reads **documents alone** — Ruling
#: 49 mechanises a contract that lives in `docs/`, and there is no module it
#: could be about. ⛔ Its exemption mechanism is neither a scan root nor a
#: list: a document in that directory **declares what it is**, and an
#: undeclared one is refused.
#:
#: ⛔ `check_handoff_existence` is that check's MISSING HALF and it is here
#: because `check_handoffs` iterates `rglob("*.md")`: its population is
#: *documents that exist*, so *the handoff is missing* is unreachable by
#: construction (`W167`, `CTO-67/10`). ⭐ Its population is the other one — rows
#: `BOARD.md`'s register DECLARES CLOSED — so it is the only check here whose
#: subject is a document that is NOT there. ⚠️ Its exemption mechanism is a
#: SIXTH distinct one and it is two pinned readings rather than a declaration:
#: a legacy bound and the board's own owner vocabulary, both measured, because
#: `closed → owes` fires 11 times on the shipped tree and 5 of those are office
#: rounds recording in the archive (Ruling 179).
#:
#: ⚠️ `check_pointers` reads **documents alone** as `check_handoffs` does, but
#: every document rather than one directory's — Ruling 43's second walk. ⛔ Its
#: exemption mechanism is a third distinct one and it is the interesting part:
#: neither a scan root, nor a list, nor a declaration, but the **parser**. A
#: link inside backticks is a *mention* and is not a pointer, so a document is
#: excused by saying what it means rather than by being named somewhere.
#:
#: ⚠️ `check_anchor_collisions` reads the same documents as `check_pointers`
#: and asks the question that one CANNOT (`W140`): `heading_slugs` returns a
#: `set`, so a duplicate anchor name is folded away before anything can count
#: it and the floor reports `0 unresolved` about a question nobody asked it.
#: ⛔ Its exemption mechanism is `check_pointers`'s — the parser — plus one of
#: its own: a duplicate heading with NOTHING pointing at it is printed by the
#: notice and is not a finding, because it costs a reader nothing. ⭐ That is
#: also what keeps it from firing 22 times on its first wave over frozen
#: archived bytes no office may edit (Ruling 106).
#:
#: ⚠️ `check_rulings_index` is the only one whose subject is a GENERATED
#: document, and its exemption mechanism is a fourth distinct one: there isn't
#: any. ⛔ The rulings index is derived from the ruling records on every run, so
#: the check cannot be satisfied by declaring anything — only by regenerating
#: (`W91`, R19). ⭐ That is what makes the index's completeness ASSERTED rather
#: than typed: the day a ruling is minted without a row, this returns `no`.
#:
#: ⚠️ `check_rulings_reach` is its complement and the distinction is the whole
#: point of `W126`: `check_rulings_index` asks whether the index is DERIVED, and
#: this asks whether the newest ruling REACHED A CONVENTION. ⛔ Ruling 245
#: measured rulings `217`–`241` reaching `docs/conventions/` **0 of 25**, against
#: a control of 17 of 21 for the older practice — so a derivation that is
#: perfectly fresh is fully compatible with twenty-five rulings nobody can read.
#: ⭐ Its exemption mechanism is a FIFTH distinct one: the SUBJECT is one named
#: directory, so the three non-artifacts Ruling 212 enumerates — a handoff, the
#: archive, the generated index — are excluded structurally rather than by a
#: filter a reader has to remember.
CHECKS = (
    check_sizes,
    check_board,
    check_mirrors,
    check_docstrings,
    check_style,
    check_personal_data,
    check_source_names,
    check_handoffs,
    check_handoff_existence,
    check_pointers,
    check_anchor_collisions,
    check_rulings_index,
    check_rulings_reach,
)

#: ⛔ **The second channel, and it exists because some of the floor's answers
#: are not failures.** A tree can legitimately be missing something the reader
#: still needs told about — an absent linter, a module approaching its ceiling
#: — and a red run for a condition nobody may be failed for is a red run that
#: gets muted, which is how a check stops being read (FND-07).
#:
#: ⚠️ A notice never affects the exit code. Anything that should fail a build
#: is a `Finding`, and nothing here is a quieter way to report one.
#:
#: ⭐ **`pointer_coverage` is the first of them, and it is here for the
#: opposite reason to `lint_notice`.** That one speaks when something is
#: missing; this
#: speaks when nothing is wrong — it prints the denominator a green run would
#: otherwise swallow. ⛔ Ruling 48: `0 dangling` is `0 = 0` until it says *out of how
#: many*, and FND-08's own acceptance names it: a check reports its coverage,
#: not just its hits.
#:
#: ⭐ **`collision_census` is the third, and it exists to QUALIFY the second.**
#: ⛔ `pointer_coverage`'s `0 unresolved` is true and reads as *no anchor here
#: is ambiguous*, which it does not say (`W140`). ⚠️ So this prints immediately
#: under it — the anchor names more than one heading answers to, every one of
#: them with its count, grouped by the document that is the unit of remedy.
#: ⛔ A notice rather than a finding for the ones nothing points at: the
#: population is mostly frozen archived bytes (Ruling 106), and a notice whose
#: first wave fires on work nobody may correct is a notice nobody reads twice.
#:
#: ⛔ **`lint_notice` is the fourth, and it is Ruling 78.** `check_style` is the
#: standard-library half of lint and Ruling 77 forbids it growing the other
#: half — the floor's exit code may not depend on whether somebody ran
#: `pip install`. ⚠️ But the floor was then printing `quality floor: clean` over
#: a run where no linter existed, and three agents in one wave read that as a
#: lint verdict; one shipped four `D401` errors under it, and the CTO's `SF-12`
#: sweep produced a mutant that passes all 2923 tests and is killed only by
#: `ruff F401`. ⭐ **The resolution is that a notice reporting a tool's absence
#: does not depend on that tool**, so this reports the lint state — including
#: its absence — while enforcement stays in `tests/test_repository.py`.
#:
#: ⚠️ **It is deliberately last**, so it prints immediately above `quality
#: floor:` — the line it exists to qualify.
#:
#: ⭐ **`reach_notice` is the fifth, and it carries a BACKLOG rather than an
#: absence.** ⛔ Ruling 245 scopes the *finding* to the index's tail on purpose —
#: *"a notice whose first wave fires 25 times is a notice nobody reads twice"* —
#: so the wider window cannot be a `Finding` without making the floor red for
#: rulings no office has been assigned. ⚠️ It is printed, enumerated by number,
#: immediately beside the index's own line, because the cliff was invisible for
#: twenty-five rounds for exactly one reason: nobody printed the population.
#:
#: ⭐ **`approach_notice` is the sixth, and it is FIRST here to mirror
#: `check_sizes` being first in `CHECKS`** — the ceiling's finding and the
#: ceiling's approach printed by the same reader in the same order. ⛔ **A
#: notice and never a finding** (`W155`): R11's ceiling already fails the
#: build, and a second hard gate *below* the first makes the real one
#: unreachable. ⚠️ **Its predicate is proximity × GROWTH and not proximity**,
#: because a static module under an enforced ceiling is the ceiling WORKING and
#: an instrument that flagged it would cry on its own successes — measured at
#: `7a7a178`, proximity alone flags 20 modules where proximity × growth flags 0.
#:
#: ⭐ **`handoff_existence` is the seventh, and it ships WITH its check rather
#: than after it** (`W167`): its denominator is EMPTY on the tree that minted it
#: — one closed row lies above the pinned bound and it is an office round — so
#: `0 findings` reads as a clean bill unless the population is printed beside
#: it. ⛔ **Ruling 191, and Ruling 48 one row over: `0 = 0` is not a result.**
#: ⚠️ It sits beside `board_state` because it reads the same register.
NOTICES = (
    approach_notice,
    pointer_coverage,
    collision_census,
    board_state,
    handoff_existence,
    rulings_notice,
    reach_notice,
    lint_notice,
)

__all__ = [
    "CHECKS",
    "NOTICES",
    "LINE_LENGTH",
    "MIN_JUSTIFICATION_CHARS",
    "SIZE_EXCEPTION_MARKER",
    "SOURCE_LINE_CEILING",
    "TEST_LINE_CEILING",
    "Finding",
    "approach_notice",
    "format_findings",
    "run_all",
    "run_notices",
]


def run_all(root: Path) -> list[Finding]:
    """Every finding in the tree at `root`, sorted.

    Sorted rather than in check order so the report is identical on any
    machine — R10's argument, applied to the tool that guards R10's neighbours.
    """
    findings: list[Finding] = []
    for check in CHECKS:
        findings.extend(check(root))
    return sorted(findings)


def run_notices(root: Path) -> list[str]:
    """Every non-failing line the floor wants to print, in order.

    ⛔ Separate from `run_all` because the two answer different questions.
    `run_all` answers *"is this tree below the floor?"*; this answers *"is
    there something you are missing that nobody can fail you for?"*
    """
    lines: list[str] = []
    for notice in NOTICES:
        lines.extend(notice(root))
    return lines
