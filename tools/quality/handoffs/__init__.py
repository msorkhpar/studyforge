r"""Ruling 49: the handoff contract, as a build failure rather than a grep.

**What it does.** Reads every document under `docs/tasks/handoffs/` and holds
the ones that **declare themselves task handoffs** to `agent-protocol.md`'s
contract: the title, the six sections, and rubric §8a's marker discipline.
Everything else in that directory is held to one rule only — it must say what
it is.

**How you use it.** `check_handoffs(repo_root)` returns findings; it is
registered in `tools.quality.CHECKS`. `DOCUMENT_KINDS` is the registry of what
may live in that directory, and a new kind of document is one entry.

**Depends on.** `config` for the tree and `re`. Nothing else.

## ⛔ The binding is a declaration, never the filename

⚠️ **`<TASK-ID>.md` is the wrong binding and it was already false when this
landed.** Measured 2026-09-10: of that directory's **53** documents, **10 were
not task handoffs** — and **8 of those 10 already carried `— handoff` in their
own title**, because their authors started from the template. ⛔ Neither the
filename nor the title can be read as a declaration: both are free text and
both had already drifted.

⭐ *Enumerate the legal, never the illegal*, read with its domain limit: the
domain "filenames that are not handoffs" is free text, and the domain **"kinds
of document that may live here"** is writable — so it is the one enumerated.
`docs/tasks/handoffs/README.md` carries the reasoning and the six spellings; an
undeclared document is **refused**, and the direction is declaration →
filename, never back.

## ⛔ `0` is never self-certifying — so "none" is a marker

Rubric §8a, Ruling 29: **a finding *is* a marked item**, one spelling, and an
unmarked finding *unrepresentable* rather than counted-and-compared. ⚠️ What
that ruling could not express is a handoff with genuinely nothing to report,
and its own answer — *"a `0` result must force a sentence"* — was addressed to
the reviewer who did not run the grep. ⭐ So `` `[none]` `` is a third marker
with the same rule: it carries a sentence, it may not stand beside a real
finding, and zero markers is a **failure**.

## ⛔ A finding is numbered inside its own document — and 20–62 is closed

`agent-protocol.md`, *A finding is numbered inside its own document*: the form
is `<TASK-ID>/<n>`, `n` starts at 1, and there is no allocator because a branch
cannot hold one. ⭐ **The `<TASK-ID>` must be one the document itself declared**,
which is the half a shape check can actually assert.

⛔ **The legacy global numbers are NOT migrated** — a handoff is a record and a
check that demands a record be rewritten is a check this project forbids — so
bare numbers up to `LEGACY_GLOBAL_MAX` pass and anything above it must carry its
document's ID. ⚠️ **That bound is pinned from a measurement, not from a ruling:
`BOARD.md` says 20–58 and the merged tree runs to 62**, because `SF-10` minted
four more on a branch before the ruling landed. Ruling 55, in one line.
"""

from __future__ import annotations

import re
from pathlib import Path

from tools.quality import config
from tools.quality.handoffs.contract import (
    FINDING_MARKERS,
    LEGACY_GLOBAL_MAX,
    MARKER_LOCAL,
    MARKER_NONE,
    MARKER_STRUCTURAL,
    MIN_NONE_CHARS,
    SECTIONS,
    check_markers,
    check_sections,
    marker_lines,
)
from tools.quality.report import Finding

__all__ = [
    "DOCUMENT_KINDS",
    "FINDING_MARKERS",
    "HANDOFF_DIR",
    "KIND_MARKER",
    "LEGACY_GLOBAL_MAX",
    "MARKER_LOCAL",
    "MARKER_NONE",
    "MARKER_STRUCTURAL",
    "MIN_NONE_CHARS",
    "OFFICE_HANDOFF",
    "SECTIONS",
    "TASK_HANDOFF",
    "TASK_ID",
    "check_handoffs",
    "declared_kind",
    "marker_lines",
]
RULE_KIND = "handoff-kind"
RULE_TITLE = "handoff-title"
RULE_FILENAME = "handoff-filename"

#: The one directory this check reads. ⛔ Documents, never modules: the
#: exemption mechanism here is a document's own declaration, and there is
#: nothing under `src/` or `tools/` that could claim one.
HANDOFF_DIR = "docs/tasks/handoffs"

#: The literal, case-sensitive declaration. One spelling, by the same argument
#: as `config.SIZE_EXCEPTION_MARKER`: a marker that differs by a capital would
#: pass the checker and fail review, which is the worst available outcome.
KIND_MARKER = "**Kind:**"

#: ⛔ The closed set of documents permitted in `HANDOFF_DIR`, and what each
#: owes. Adding a kind is a decision made here, in one place, with its sentence
#: — never an entry on an exclusion list somewhere else.
TASK_HANDOFF = "task handoff"
#: ⛔ A supervising office's handoff for work commissioned outside the id space.
#: ⚠️ **It owes EXACTLY what a task handoff owes** — the six sections and the
#: markers — ⭐ **and it exists because the alternative was worse: the id space
#: has ONE MINTER, so an office asked to restructure something has no id to
#: declare, and every kind it could otherwise borrow owes NOTHING.** ⛔ A kind
#: that lets a document escape the contract is not a kind, it is a hole.
OFFICE_HANDOFF = "office handoff"
DOCUMENT_KINDS: dict[str, str] = {
    TASK_HANDOFF: "one task's handoff; owes the title, the six sections and the markers",
    OFFICE_HANDOFF: "a supervising office's handoff, with no task ID because the id "
    "space has one minter; owes the six sections and the markers, and no ID",
    "ruling record": "a CTO or PO round, or one ruling written up; a record, owes nothing further",
    "session log": "a coordinator's record of one session; owes nothing further",
    "survey": "a read-only investigation or review; nothing landed, so nothing to hand over",
    "index": "the directory's own README, which describes the others and is not one of them",
}

#: Lines from the top of the file within which the declaration must sit. ⚠️ A
#: window rather than a fixed line, because the shape above it varies — a
#: title, sometimes an italic subtitle — and a declaration a reader has to
#: scroll for is not one they will trust.
DECLARATION_WINDOW = 10

#: A task ID: an epic-and-number (`FND-01`, `SF-05a`, `EX-00`) or a wave item
#: (`W3`, `W25`). ⛔ Closed, because the declaration is the binding and a
#: typo in it would otherwise become a new obligation-free document.
TASK_ID = re.compile(r"^(?:[A-Z]{2,4}-\d{2}[a-z]?|W\d+)$")

_DECLARATION = re.compile(
    r"^\*\*Kind:\*\*[ \t]+(?P<kind>[a-z][a-z ]*[a-z])(?:[ \t]*—[ \t]*(?P<ids>.+?))?[ \t]*$"
)


def declared_kind(text: str) -> tuple[str | None, list[str], int]:
    """`(kind, declared IDs, line number)` for the document's own declaration.

    Returns `(None, [], 0)` when there is no declaration inside
    `DECLARATION_WINDOW`, which is what the check refuses.
    """
    for number, line in enumerate(text.splitlines()[:DECLARATION_WINDOW], start=1):
        if not line.startswith(KIND_MARKER):
            continue
        match = _DECLARATION.match(line)
        if match is None:
            return (None, [], number)
        raw = match.group("ids") or ""
        ids = [part.strip() for part in raw.split(",") if part.strip()]
        return (match.group("kind"), ids, number)
    return (None, [], 0)


def _check_declaration(relative: str, text: str) -> tuple[str | None, list[str], list[Finding]]:
    """Enforce the one rule every document here owes: say what you are."""
    kind, ids, line = declared_kind(text)
    known = ", ".join(sorted(DOCUMENT_KINDS))
    if kind is None:
        return (
            None,
            [],
            [
                Finding(
                    relative,
                    line,
                    RULE_KIND,
                    f"no `{KIND_MARKER} <kind>` declaration in the first "
                    f"{DECLARATION_WINDOW} lines. Every document here declares what it "
                    f"is, because a filename cannot: one of {known}.",
                )
            ],
        )
    if kind not in DOCUMENT_KINDS:
        return (
            None,
            [],
            [
                Finding(
                    relative,
                    line,
                    RULE_KIND,
                    f"declares kind {kind!r}, which is not one of {known}. Add it to "
                    f"`DOCUMENT_KINDS` with what it owes, or use an existing kind.",
                )
            ],
        )
    return (kind, ids, [])


def _check_identity(relative: str, text: str, ids: list[str]) -> list[Finding]:
    """Check the declared IDs, the filename that follows them, and the title."""
    findings: list[Finding] = []
    if not ids:
        findings.append(
            Finding(
                relative,
                1,
                RULE_KIND,
                f"declares `{TASK_HANDOFF}` and names no task. Write "
                f"`{KIND_MARKER} {TASK_HANDOFF} — <ID>[, <ID>…]`.",
            )
        )
        return findings
    for identifier in ids:
        if not TASK_ID.match(identifier):
            findings.append(
                Finding(
                    relative,
                    1,
                    RULE_KIND,
                    f"declares task {identifier!r}, which is not a task ID "
                    f"(`FND-01`, `SF-05a`, `W25`).",
                )
            )
    stem = relative.rsplit("/", 1)[-1].removesuffix(".md")
    if not stem.startswith(ids[0]):
        findings.append(
            Finding(
                relative,
                0,
                RULE_FILENAME,
                f"is the handoff for {ids[0]} and its filename does not begin with it. "
                f"`agent-protocol.md` writes `docs/tasks/handoffs/<TASK-ID>.md`.",
            )
        )
    title = next((line for line in text.splitlines() if line.strip()), "")
    missing = [identifier for identifier in ids if identifier not in title]
    if not title.startswith("# ") or not title.rstrip().endswith("— handoff") or missing:
        findings.append(
            Finding(
                relative,
                1,
                RULE_TITLE,
                f"title is {title.strip()!r}; rubric §8 wants "
                f"`# {' + '.join(ids)} — handoff` — every declared task named, "
                f"and the word that makes it findable.",
            )
        )
    return findings


def _check_office_identity(relative: str, text: str, ids: list[str]) -> list[Finding]:
    """Check an office handoff's SCOPE, which is never a task, and its title.

    ⛔ **Naming a task would be minting one**, which is the PO's and nobody
    else's. ⭐ So the identity rule inverts: the declaration carries the prefix
    its findings are numbered inside — `ARCH` — and a value that parses as a
    task ID is the finding.
    """
    findings: list[Finding] = []
    if len(ids) != 1 or TASK_ID.match(ids[0]):
        findings.append(
            Finding(
                relative,
                1,
                RULE_KIND,
                f"declares `{OFFICE_HANDOFF}` and names {', '.join(ids) or 'nothing'}. "
                f"Write `{KIND_MARKER} {OFFICE_HANDOFF} — <SCOPE>` with ONE scope that "
                f"is NOT a task ID: it is what this document's findings are numbered "
                f"inside, and a task ID here would be minting one.",
            )
        )
    title = next((line for line in text.splitlines() if line.strip()), "")
    if not title.startswith("# ") or not title.rstrip().endswith("— handoff"):
        findings.append(
            Finding(
                relative,
                1,
                RULE_TITLE,
                f"title is {title.strip()!r}; rubric §8 wants `# <subject> — handoff`, "
                f"and the word that makes it findable.",
            )
        )
    return findings


def check_handoffs(root: Path) -> list[Finding]:
    """Every document in `HANDOFF_DIR` that breaks the contract it declares."""
    directory = root / HANDOFF_DIR
    if not directory.is_dir():
        return []
    findings: list[Finding] = []
    for path in sorted(directory.rglob("*.md")):
        relative = config.relative(path, root)
        text = config.read_text(path)
        if text is None:
            continue
        kind, ids, declaration = _check_declaration(relative, text)
        findings.extend(declaration)
        if kind not in (TASK_HANDOFF, OFFICE_HANDOFF):
            continue
        if kind == TASK_HANDOFF:
            findings.extend(_check_identity(relative, text, ids))
        else:
            findings.extend(_check_office_identity(relative, text, ids))
        findings.extend(check_sections(relative, text))
        findings.extend(check_markers(relative, text, ids or [kind]))
    return findings
