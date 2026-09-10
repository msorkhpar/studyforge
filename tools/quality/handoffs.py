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
landed.** Measured 2026-09-10: `docs/tasks/handoffs/` held **53** documents, of
which **10 were not task handoffs** — a survey, seven ruling records, two
coordinator session logs — and **8 of those 10 already carried `— handoff` in
their own title**, because their authors started from the template. ⛔ So
neither the filename nor the title can be read as a declaration: both are free
text, and both had already drifted.

⭐ **The decision, and the reason.** `module-structure.md` says *enumerate the
legal, never the illegal*, and bounds itself: enumerability is a property of the
**domain**. The domain "filenames that are not handoffs" is free text — a
longer exclusion list, known-incomplete, and the next survey lands next wave.
The domain **"kinds of document that may live in this directory"** is
enumerable and *writable*, so it is enumerated here, and every document
declares which one it is:

    **Kind:** task handoff — W25

⛔ **An undeclared document is refused**, which is the closed set failing the
way a closed set should: loudly, at the boundary, naming the thing it did not
expect. A new kind of document costs one entry and a sentence saying what it
owes; it does not cost an exclusion list that nobody will remember to extend.

⭐ **And the direction is declaration → filename, never back.** The stem must
begin with the first declared ID, so a handoff stays findable; the check never
infers a kind, an ID or an obligation from a name.

## ⛔ `0` is never self-certifying — so "none" is a marker

Rubric §8a, Ruling 29: **a finding *is* a marked item**, the marker is a
literal string with one spelling, and an unmarked finding is *unrepresentable*
rather than counted-and-compared. Four earlier versions of a "filed findings"
counter each worked on the handoffs their author tested.

⚠️ ⛔ **What that ruling could not express is a handoff with genuinely nothing
to report**, and its own answer — *"a `0` result must force a sentence"* — was
addressed to a reviewer, who is the person Ruling 49 exists because they did
not run the grep. ⭐ So `` `[none]` `` is a third marker with the same spelling
rule: it says *nothing outside this task's scope*, it must carry a sentence
saying so, and ⛔ it may not stand beside a real finding. Zero markers is a
**failure**, not a pass — which is the half of Ruling 29 that catches the class.
"""

from __future__ import annotations

import re
from pathlib import Path

from tools.quality import config
from tools.quality.report import Finding

RULE_KIND = "handoff-kind"
RULE_TITLE = "handoff-title"
RULE_SECTION = "handoff-section"
RULE_MARKER = "handoff-marker"
RULE_FINDINGS = "handoff-findings"
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
DOCUMENT_KINDS: dict[str, str] = {
    TASK_HANDOFF: "one task's handoff; owes the title, the six sections and the markers",
    "ruling record": "a CTO round or a single ruling written up; a record, owes nothing further",
    "session log": "a coordinator's record of one session; owes nothing further",
    "survey": "a read-only investigation or review; nothing landed, so nothing to hand over",
    "index": "the directory's own README, which describes the others and is not one of them",
}

#: Lines from the top of the file within which the declaration must sit. ⚠️ A
#: window rather than a fixed line, because the shape above it varies — a
#: title, sometimes an italic subtitle — and a declaration a reader has to
#: scroll for is not one they will trust.
DECLARATION_WINDOW = 10

#: `agent-protocol.md`'s template, in order. Rubric §8 accepts two spellings
#: for each — the bold label the template writes, and the heading a long
#: handoff reads better with. ⛔ The sections are the contract; the emphasis
#: markers are not.
SECTIONS = ("Status", "What landed", "Decisions", "Surprises", "Findings", "For dependents")

#: The triage markers, spelled once. `[none]` is the representable form of
#: "nothing outside my scope"; see the module docstring for why it exists.
MARKER_LOCAL = "`[local]`"
MARKER_STRUCTURAL = "`[structural]`"
MARKER_NONE = "`[none]`"
FINDING_MARKERS = (MARKER_LOCAL, MARKER_STRUCTURAL, MARKER_NONE)

#: Minimum characters after `[none]` on its line. Not a quality bar — it only
#: stops a bare marker from being a quieter way of writing `0`.
MIN_NONE_CHARS = 20

#: A task ID: an epic-and-number (`FND-01`, `SF-05a`, `EX-00`) or a wave item
#: (`W3`, `W25`). ⛔ Closed, because the declaration is the binding and a
#: typo in it would otherwise become a new obligation-free document.
TASK_ID = re.compile(r"^(?:[A-Z]{2,4}-\d{2}[a-z]?|W\d+)$")

_DECLARATION = re.compile(
    r"^\*\*Kind:\*\*[ \t]+(?P<kind>[a-z][a-z ]*[a-z])(?:[ \t]*—[ \t]*(?P<ids>.+?))?[ \t]*$"
)

#: Markup a finding line may carry *before* its marker: a bullet, a heading, a
#: number, bold. ⭐ Derived by reading all 199 marker lines on the tip rather
#: than guessed — every genuine one is a heading, a list item or a numbered
#: item, and every prose mention has a word in front of the marker.
_FINDING_LEAD = re.compile(
    r"^[ \t]*(?:[-*+][ \t]+|#{1,6}[ \t]+)?(?:\*\*)?(?:\d+[.)]?[ \t]+)?(?:\*\*)?"
)

_MARKERS_ON_LINE = re.compile(r"`\[(?:local|structural|none)\]`")


def _section_pattern(section: str) -> re.Pattern[str]:
    """Rubric §8's two accepted spellings for one section heading."""
    escaped = re.escape(section)
    return re.compile(rf"^(?:\*\*{escaped}:\*\*|#{{2,3}} {escaped}\b)", re.MULTILINE)


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


def marker_lines(text: str) -> list[tuple[int, str, bool]]:
    """`(line number, line, is a finding line)` for every line holding a marker.

    A line is a **finding line** when exactly one marker sits on it and nothing
    but list, heading, numbering or emphasis markup comes before it. ⛔ Rubric
    §8a: a marker in explanatory text counts as a finding that does not exist,
    and two markers on one line is one finding claiming to be two.

    ⭐ **A fenced block is quoted material and is not read.** A handoff that
    documents this vocabulary — a transcript of the check firing, the migration
    table — necessarily contains the literal markers, and every one of them is
    evidence rather than a claim. ⚠️ Found the way everything else here was:
    this module's own handoff went red on the transcript of its own negative
    controls.
    """
    found: list[tuple[int, str, bool]] = []
    fenced = False
    for number, line in enumerate(text.splitlines(), start=1):
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue
        if fenced:
            continue
        markers = _MARKERS_ON_LINE.findall(line)
        if not markers:
            continue
        rest = line[_FINDING_LEAD.match(line).end() :]
        own_line = len(markers) == 1 and rest.lstrip("*").startswith(FINDING_MARKERS)
        found.append((number, line, own_line))
    return found


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


def _check_sections(relative: str, text: str) -> list[Finding]:
    """Check `agent-protocol.md`'s six, in either spelling rubric §8 accepts."""
    return [
        Finding(
            relative,
            0,
            RULE_SECTION,
            f"has no {section!r} section. The six are `agent-protocol.md`'s "
            f"contract; write `**{section}:**` or `## {section}`.",
        )
        for section in SECTIONS
        if _section_pattern(section).search(text) is None
    ]


def _check_markers(relative: str, text: str) -> list[Finding]:
    """Enforce rubric §8a: a finding *is* a marked item, and `0` forces a sentence."""
    findings: list[Finding] = []
    lines = marker_lines(text)
    for number, _line, own_line in lines:
        if not own_line:
            findings.append(
                Finding(
                    relative,
                    number,
                    RULE_MARKER,
                    "a marker is not on its own finding line — two on one line, or one "
                    "in prose. Rubric §8a: a marker in explanatory text counts as a "
                    "finding that does not exist. Drop the backticks in prose.",
                )
            )
    good = [(number, line) for number, line, own_line in lines if own_line]
    if not good:
        findings.append(
            Finding(
                relative,
                0,
                RULE_FINDINGS,
                f"marks no finding. A finding is a marked item, so this says there were "
                f"none — say it: a {MARKER_NONE} line with the sentence that explains it, "
                f"or mark what you saw {MARKER_LOCAL} / {MARKER_STRUCTURAL}.",
            )
        )
        return findings
    nones = [(number, line) for number, line in good if MARKER_NONE in line]
    if nones and len(nones) != len(good):
        number, _ = nones[0]
        findings.append(
            Finding(
                relative,
                number,
                RULE_FINDINGS,
                f"{MARKER_NONE} stands beside a real finding. It means *nothing outside "
                f"this task's scope*; one of the two is wrong.",
            )
        )
    for number, line in nones:
        after = line.split(MARKER_NONE, 1)[1].strip(" *—-:")
        if len(after) < MIN_NONE_CHARS:
            findings.append(
                Finding(
                    relative,
                    number,
                    RULE_FINDINGS,
                    f"{MARKER_NONE} carries no sentence. `0` is never self-certifying: "
                    f"say what was looked at and found clean.",
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
        if kind != TASK_HANDOFF:
            continue
        findings.extend(_check_identity(relative, text, ids))
        findings.extend(_check_sections(relative, text))
        findings.extend(_check_markers(relative, text))
    return findings
