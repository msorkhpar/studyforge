r"""Ruling 43's second walk: a pointer between documents resolves, or it fails.

**What it does.** Reads every markdown document the repository TRACKS, finds
every link that names a path inside it, and fails the build on one that
resolves to nothing, on one whose target git IGNORES, and on an `#anchor` that
names no heading in the document it points at. It also reports its **coverage**
through the notice channel, because a `0` with no denominator is `0 = 0`
(Ruling 48).

**How you use it.** `check_pointers(root)` is registered in
`tools.quality.CHECKS`; `pointer_coverage(root)` is registered in `NOTICES`.
`scan(root)` is the one pass both read, so the findings and the denominator can
never describe different walks.

**Depends on.** `markdown` for the parser, `config` for the tree, `report` for
the answer, and `pathlib`. Nothing else, ever.

## ⛔ THE PARSER MOVED OUT, AND THE ADDRESS DID NOT (`W148`)

⭐ **`prose_lines`, `strip_code_spans`, `pointers`, `slug`, `heading_bases` and
`heading_slugs` now live in `markdown.py`**, which carries the
measurement that split them out and the reason the shape is a sibling rather
than the package `docs/conventions/module-structure.md` prefers. ⛔ **They are
re-exported here**, so every existing `from tools.quality.pointers import …`
names the same objects and no importer moved.

## ⛔ THE DOCUMENT POPULATION IS WHAT GIT TRACKS, AND IT SAYS SO (`W148`)

⛔ **A figure whose denominator comes off the DISK is not reproducible between
two correct checkouts at ONE ref.** ⚠️ MEASURED: one untracked markdown file at
a main checkout's root gave `458 markdown files` there and `457` in every
linked worktree — ⭐ **the denominator moved and the numerator did not**, so a
reader comparing `1528 pointers` across the two would have concluded, wrongly,
that both figures were checkout-invariant. ⛔ That defeats Ruling 277's ROLE
discipline exactly where it is meant to work.

⭐ **So the walk is `config.markdown_population`, and every figure NAMES it:**
`(tracked walk)` or `(disk walk)`, with `report.WALK_CAVEAT` spelling out what
the second costs a reader. ⛔ **Git failing to answer is Ruling 216's THIRD
answer** — it neither falls through to the disk in silence nor fails the build.

⛔ **AND THE NARROWING IS NOT IN `config.text_files`**, which is the R7
personal-data sweep's population and is ignore-based on purpose: a file written
and not yet added is exactly what that gate must catch, *before* it enters.
⚠️ Narrowing that walk to the index would have made this figure look fixed by
blinding the gate — which is `W148`'s own hard constraint, and it is a user
rule rather than a style note.

## ⛔ AN IGNORED TARGET DOES NOT RESOLVE (`W35`, Ruling 80)

⛔ **A floor check's verdict may not depend on untracked state.** ⚠️ Resolving a
link by `Path.exists()` alone made a pointer into a generated artifact clean on
the machine that built it and a finding on a fresh clone — one tree, two
verdicts, and nothing in either reading naming the cause. ⭐ **The ASYMMETRY was
the defect:** this walk already honoured `.gitignore` when choosing what to
READ, and now honours it when deciding what RESOLVES.

⚠️ **The ignore question is asked BEFORE existence**, so the MESSAGE is stable
and not only the verdict. ⛔ **ONE `check-ignore` call for every target in the
tree**, never one per pointer, which is why `scan` reads the whole population
before it judges any of it.

⭐ **Exposure measured at this row's own base, `bec9d5c`, role `wt/dev2`: `0`
ignored targets among `308` distinct existing targets reached by `1528`
pointers.** ⚠️ The fix therefore adds no finding to the tree it lands in, which
is what `PO-24/8` measured and why `W35` was queued last rather than ranked —
⛔ **and a `0` with no denominator would have been `0 = 0`, which is why the
denominator is quoted with it.**

## ⛔ A HANDOFF'S OWN ROW IS DEFERRED, NOT DANGLING (`W315`)

⛔ **The floor had two arms reading a handoff's citation of a register row, and
they CONTRADICTED each other across a merge.** ⚠️ A row is minted in the register
round that merges the branch: absent from the developer's tree, present on the
merged one. ⭐ **MEASURED at `787b24d`, role `wt/dev2`, HOST — one handoff, one
citation, two wordings, two trees:**

| The wording | branch, row absent | merged, row present |
|---|---|---|
| the pointer `[W99](../rows/W99.md)` | ⛔ RED `pointer` | GREEN |
| the bare name in a code span | GREEN | ⛔ RED `handoff-bare-citation` |

⛔ **So NO wording was green in both places, and a CORRECT branch was
unmergeable** — measured twice in one evening, on `W313`'s refused merge and on
`W312`'s hand-back.

⭐ **THE LINK ARM IS THE ONE THAT MOVED, and the bare arm is untouched.** ⛔ The
other repair — exempting `docs/tasks/rows/` from `handoffs.citing` — was REFUSED:
it would make the bare name the only wording a handoff could use for the one
document it cites most, which is exactly Ruling 163's harm (`W150`: a bare
basename is invisible to every instrument) and the hole Ruling 285(b) was minted
to close. ⚠️ **A reader of a handoff would lose the click, permanently, in every
tree.**

⛔ **THE DEFERRAL IS SELF-EVIDENCING AND IS NOT A LIST**: a handoff at
`docs/tasks/handoffs/<ID>.md` may link `docs/tasks/rows/<ID>.md` while that file
is absent, because the id is the citing document's OWN NAME. ⭐ Nothing is
registered, nothing is remembered, and the next handoff needs no entry.

⛔ **AND IT COSTS ONE POINTER PER HANDOFF, never a directory.** ⚠️ A handoff
linking any OTHER absent row, a handoff linking an absent file that is not a row,
and any other document linking an absent row are all findings exactly as before —
and on the merged tree the row EXISTS, so the deferral never runs there and the
anchor is resolved for real.

⚠️ **Declared gap (Ruling 258): a handoff whose id names a row the register never
mints keeps a deferred pointer forever.** ⛔ Nothing in the tree would catch it,
because nothing binds a handoff's id to an existing row —
`handoffs/existence.py` walks the other way, from a CLOSED row to the handoff it
owes. ⭐ The exposure is one pointer, in a document the register reads by id.

## ⛔ The question this module's `0 unresolved` does NOT answer (`W140`)

⭐ **An anchor that names SIX headings resolves**, so nothing here reports it —
and `heading_slugs` could not report it if it wanted to, because a set has
folded the duplicates away by the time it returns. ⛔ **That is not a bug to be
fixed in this module**: its callers ask *does this document answer to this
anchor*, which is a set question. ⭐ **The fold is undone by `heading_bases`,
and the census built on it lives in `tools/quality/collisions.py`** — a sibling
that imports this module and is imported back by nothing.

"""

from __future__ import annotations

import posixpath
from dataclasses import dataclass
from pathlib import Path

from tools.quality import config
from tools.quality.ids import is_row_id
from tools.quality.markdown import (
    Pointer,
    heading_bases,
    heading_slugs,
    pointers,
    prose_lines,
    slug,
    strip_code_spans,
)
from tools.quality.report import WALK_CAVEAT, DocumentPopulation, Finding, unread_caveat

#: ⭐ Re-exported so no importer moved when the parser did (`W148`). ⛔ Named
#: explicitly rather than left implicit: `ruff` refuses an unused import, and a
#: per-import suppression comment would say nothing about why they are here.
#: ⚠️ Spelling that comment's literal token here made `ruff` warn on every run
#: about an invalid directive in a `#:` comment — measured, and reworded.
__all__ = [
    "HANDOFF_HOME",
    "ROW_HOME",
    "RULE_ANCHOR",
    "RULE_POINTER",
    "Pointer",
    "Scan",
    "check_pointers",
    "deferred_row",
    "heading_bases",
    "heading_slugs",
    "pointer_coverage",
    "pointers",
    "prose_lines",
    "resolve_target",
    "scan",
    "slug",
    "strip_code_spans",
]

RULE_POINTER = "pointer"
RULE_ANCHOR = "anchor"

#: ⛔ The two register directories the deferral is spelled over, WRITTEN here
#: rather than imported, because the seam runs one way: `handoffs.HANDOFF_DIR`
#: and `board.register.ROWS` are the homes of these spellings, and both of those
#: packages import THIS module. ⭐ **So the equality is ASSERTED, in
#: `tools/tests/quality/test_pointers.py`** — the same construction, and the same
#: reason, as `citations.MAX_RANGE_SPAN` against `reach.REACH_WINDOW`. ⚠️ A
#: reader who moves either directory has a red test, not a silent divergence.
HANDOFF_HOME = "docs/tasks/handoffs"
ROW_HOME = "docs/tasks/rows"


@dataclass(frozen=True)
class Scan:
    """One pass over the tree: what was read, how it was found, and what was wrong.

    ⛔ `walk` is `report.TRACKED_WALK` or `report.DISK_WALK` and is carried
    rather than re-derived, so the denominator and the sentence naming how it
    was reached can never describe different walks (`W148`).

    ⚠️ **The whole `population` is carried and `walk` READS it**, rather than the
    walk being copied out: the notice now owes a second sentence about what the
    walk did NOT read (`W315`, for `W232/5`), and two fields copied off one
    object are two chances for a figure and its caveat to disagree.
    """

    files: int
    pointers: tuple[Pointer, ...]
    findings: tuple[Finding, ...]
    population: DocumentPopulation

    @property
    def walk(self) -> str:
        """How this population was found — `report.TRACKED_WALK` or `DISK_WALK`."""
        return self.population.walk


def resolve_target(root: Path, document: Path, pointer: Pointer) -> Path | None:
    """Return the file a pointer names, or None when it leaves the repository.

    ⛔ Leaving the tree is refused rather than followed: R18 pins the sibling
    components and R20 makes the extraction one-way, so a link that reaches
    out of this checkout is asserting something no checkout can guarantee.

    ⭐ **Public because `tools.quality.collisions` asks the same question of
    the same pointers** (`W140`), and a second resolver would be free to
    disagree with this one about what "inside the repository" means.
    """
    if not pointer.path_part:
        return document
    candidate = (document.parent / pointer.path_part).resolve()
    root = root.resolve()
    if candidate != root and root not in candidate.parents:
        return None
    return candidate


def deferred_row(pointer: Pointer) -> str | None:
    """Return the row id a handoff DEFERS by linking it, or `None` (`W315`).

    ⛔ **A handoff may link its OWN row before that row is on this branch.** The
    register mints the row in the round that merges the branch, so the target is
    absent here and present on the merged tree — and the id is not taken from a
    list, it is the citing document's own filename. ⚠️ **Public so the mirror can
    assert the predicate directly**: every other wording of this citation is a
    finding on one of the two trees, and that is the property under test.
    """
    home = posixpath.dirname(pointer.document)
    identifier = posixpath.basename(pointer.document).removesuffix(".md")
    if home != HANDOFF_HOME or not is_row_id(identifier):
        return None
    target = posixpath.normpath(posixpath.join(home, pointer.path_part))
    return identifier if target == f"{ROW_HOME}/{identifier}.md" else None


def _check(
    root: Path, document: Path, pointer: Pointer, text: str, ignored: frozenset[Path]
) -> Finding | None:
    """Return the finding this pointer earns, or None when it resolves.

    ⛔ `ignored` is asked BEFORE existence, and that order is `W35`: the same
    pointer must earn the same finding with the same message on the machine
    that generated the artifact and on a fresh clone (Ruling 80).
    """
    target = resolve_target(root, document, pointer)
    if target is None:
        return Finding(
            pointer.document,
            pointer.line,
            RULE_POINTER,
            f"points at {pointer.target!r}, which leaves this repository. A sibling "
            f"component is pinned by `workspace.json` (R18) and the extraction source "
            f"is never cited by path (R20); name the ruling or the contract instead.",
        )
    if target.resolve() in ignored:
        return Finding(
            pointer.document,
            pointer.line,
            RULE_POINTER,
            f"points at {pointer.target!r}, which git IGNORES. It is present on the "
            f"machine that generated it and absent from a fresh clone, so resolving it "
            f"by existence makes this verdict depend on untracked state (Ruling 80). "
            f"Name the generator, the ruling or the contract instead, or put the link "
            f"in backticks if it is an example rather than a reference.",
        )
    if not target.exists():
        # ⛔ `W315`: a handoff linking the row it is the handoff FOR is deferred
        # to the register, not dangling — the merge writes that file, and every
        # other wording of the citation is red on one of the two trees.
        if deferred_row(pointer) is not None:
            return None
        return Finding(
            pointer.document,
            pointer.line,
            RULE_POINTER,
            f"points at {pointer.target!r} — no such file. A pointer that resolves to "
            f"nothing is worse than no pointer: it reads as evidence. Fix the path, or "
            f"put the link in backticks if it is an example rather than a reference.",
        )
    if not pointer.anchor:
        return None
    if target.is_dir() or target.suffix != ".md":
        return Finding(
            pointer.document,
            pointer.line,
            RULE_ANCHOR,
            f"points at anchor {pointer.anchor!r} in {pointer.path_part!r}, which is not "
            f"a markdown document and has no headings to name.",
        )
    body = text if target == document else config.read_text(target)
    if body is None:
        return None
    if pointer.anchor.lower() not in heading_slugs(body):
        return Finding(
            pointer.document,
            pointer.line,
            RULE_ANCHOR,
            f"points at anchor {pointer.anchor!r}, which names no heading in "
            f"{pointer.path_part or 'this document'!r}. An anchor that resolves to "
            f"nothing scrolls the reader to the top and says nothing went wrong.",
        )
    return None


def scan(root: Path) -> Scan:
    """One pass over every markdown document: coverage and findings together.

    ⛔ **One pass, read by both channels.** A check that counted its links in
    one walk and reported its findings from another could say `0 dangling in
    45` while having looked at 45 different links — which is Ruling 48's
    defect wearing a denominator.

    ⚠️ **The findings come after the whole read rather than during it** (`W35`):
    every target git might ignore is asked about in ONE `check-ignore` call,
    because the alternative is one subprocess per pointer.
    """
    population = config.markdown_population(root)
    read: list[tuple[Path, str, tuple[Pointer, ...]]] = []
    for path in population.paths:
        text = config.read_text(path)
        if text is None:
            continue
        read.append((path, text, tuple(pointers(config.relative(path, root), text))))
    found = [pointer for _path, _text, carried in read for pointer in carried]
    # ⚠️ The ignore query is asked in the RESOLVED frame, and every target is
    # resolved into it. `root` need not be absolute — `python3 -m tools.quality`
    # hands it `Path(".")` — and `resolve_target` hands back a same-document
    # link exactly as it was given, so a mixed frame reaches `relative()` and
    # raises on the first target.
    inside = root.resolve()
    targets = {
        target.resolve()
        for path, _text, carried in read
        for pointer in carried
        if (target := resolve_target(root, path, pointer)) is not None
    } - {inside}
    ignored = frozenset(config.ignored_paths(inside, sorted(targets)))
    findings = [
        finding
        for path, text, carried in read
        for pointer in carried
        if (finding := _check(root, path, pointer, text, ignored)) is not None
    ]
    return Scan(len(read), tuple(found), tuple(findings), population)


def check_pointers(root: Path) -> list[Finding]:
    """Every pointer in the repository's documents that resolves to nothing."""
    return list(scan(root).findings)


def pointer_coverage(root: Path) -> list[str]:
    """Return the denominator, printed whether or not anything failed (Ruling 48).

    ⛔ **A notice and never a finding**, because coverage is not a violation —
    and because the number a reader needs on a green run is precisely the one
    a green run would otherwise never print. ⚠️ It also makes Ruling 55
    mechanical here: the next agent to re-price this walk reads the current
    number off the floor instead of rebuilding the instrument.
    """
    result = scan(root)
    anchored = sum(1 for pointer in result.pointers if pointer.anchor)
    return [
        f"document pointers: {len(result.pointers)} read in {result.files} markdown "
        f"files ({result.walk} walk), {anchored} carrying an anchor, "
        f"{len(result.findings)} unresolved.{WALK_CAVEAT[result.walk]}"
        f"{unread_caveat(result.population)}"
    ]
