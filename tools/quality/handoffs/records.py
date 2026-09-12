"""A `ruling record`'s SCOPE and its MARKERS (`W64` gate two, `W172` gate three).

**What it does.** Gives a `ruling record` the two things it has never had — a
scope, and a rule that reads the markers on its findings. The scope is
**derived from the filename** and may be **declared** on the `**Kind:**` line;
the marker rule reads only its *Findings* section. ⛔ Nothing in a record is
rewritten to produce either (Ruling 106).

**How you use it.** `record_scopes(stem, declared)` is the derivation, shipped
rather than described (`W121/2`). `check_record(relative, stem, declared,
text)` returns findings: the declaration rules, `check_finding_ids` over the
record's own finding lines, and `check_record_markers` over its Findings
section.

**Depends on.** `contract`, `sections` and `report.Finding`. ⛔ Never its own
package: the dependency runs one way, exactly as `contract`'s does.

## ⛔ GATE TWO: the scope (Ruling 218, `W64`)

⛔ **Ruling 218 stopped `W64` and priced three gates.** ⭐ Gate one was `W121`'s
table-cell boundary; gate two is the scope below; gate three is the marker rule
that follows it.

## ⛔ GATE THREE: the marker rule reaches a record, and it is DOUBLY narrowed (`W172`)

⭐ **Ruling 218's third gate in one sentence: a rule that separates a record's
Findings section from its prose, so `check_markers` can be applied without
firing on every sentence that discusses a marker.** ⛔ **The predicate alone is
not enough, and that is this gate's measured result.** All figures below: the
110 `ruling record` documents in `docs/tasks/handoffs`, at `bec9d5c`, HOST,
through the shipped readers.

```text
what the marker rule fires, dry-run over the 110 records
  fully widened, whole document      181 findings in 53 documents
  restricted to the Findings section  27 findings in  7 documents
  ...and to lines claiming a SCOPE     0 findings
```

⛔ **So the gate is narrowed TWICE, and the second narrowing is not tuning: it
is gate two's own ruling read forward.** ⭐ Gate two established that a record's
findings are numbered inside a SCOPE. ⭐ **So a line in the Findings section
that claims a scoped number is a FINDING, and a line that claims none is
PROSE** — the disposition arguing whether something was `[local]` or
`[structural]`, the count of what was filed, the table documenting the
vocabulary. ⚠️ **Measured: 80 marker-bearing lines inside a Findings section
claim no scope, and 219 do.** ⛔ Every one of the 80 is prose, and reading them
was the whole of the 27.

### ⛔ THREE ARMS ARE REFUSED, EXPLICITLY RATHER THAN BY OMISSION

⛔ **1. The six sections (`check_sections`) — RATIFIED ABSENT.** ⚠️ `W64` left
this a silence and pinned it in a test; this gate ends the silence. ⭐ **A
record is not a handoff**: it hands nothing over, so *Status*, *What landed*
and *For dependents* name nothing it has. ⚠️ **Measured: applying them prints
437 findings in 98 of the 110 records** — a debt no record ever owed.

⛔ **2. *Marks no finding* — REFUSED, and this is the measurement that decides
gate three.** ⚠️ **A record does not TRIAGE-mark its findings, and the corpus
says so: of 311 numbered claims inside a Findings section, 92 in 27 documents
carry no marker at all** — every finding in the most recent CTO round among
them. ⭐ **A record's findings are DISPOSITIONS, not triage items**: Ruling 29's
*a finding is a marked item* is a task handoff's contract, written for a
document whose findings are routed onward. ⛔ Demanding a marker would be
Ruling 193's chase in its purest form, against 106 documents that may not be
edited.

⛔ **3. `[none]` standing beside a real finding — REFUSED for a record.** ⭐ In a
handoff `[none]` means *nothing outside this task's scope*, so it cannot stand
beside a finding. ⚠️ **A record uses it per-finding, to mean a recorded
negative** — measured, all 4 of the `[none]` lines in the corpus's Findings
sections do exactly that, beside real findings. ⛔ **The other `[none]` arm IS
applied**: a marker that carries no sentence is a quieter way of writing `0`,
and that argument does not turn on the kind of document.

### ⛔ WHAT DOES FIRE, and Ruling 189(b) is why it is not stricter

⭐ **A line in the Findings section claiming a scoped number must carry its
marker where no CLAIM has preceded it** — in the line's lead, or at the start of
one of its cells. ⛔ **Every cell, never a column index** (Ruling 189(b)):
`contract.claim_free_markers` tests each, ⚠️ **because a record's findings table
is written `| # | Finding | Marker |` and the marker sits behind a cell of
prose.** ⛔ `marker_lines`'s `own_line` reads the LINE's lead only and therefore
refuses that table — the stricter reading a task handoff is held to, and the
one Ruling 189(b) says is not the rule.

⭐ **Two markers in claim-free positions is still one finding claiming to be
two**, and that half of Ruling 65's count rule survives. ⚠️ A marker QUOTED
inside the finding's own prose does not, because that is the sentence gate
three exists to stop reading.

## ⛔ WHAT GATE THREE DOES NOT TAKE, and it is a decision rather than an oversight

⛔ **`survey` is still outside every one of these rules, and a record that
derives no scope is still not refused.** ⭐ Both were named as residue by `W64`
and re-measured at `bec9d5c`, HOST, unmoved: **3 surveys, 5 scopeless records.**
⚠️ Admitting `survey` widens a kind Ruling 218 names, and refusing a scopeless
record demands a rename or an edit inside a record — so both are declined out
loud rather than left silent.

⛔ **`W64/11`'s citation-resolution rule is REFUSED PERMANENTLY, not deferred.**
⭐ Requiring a cited scope to EXIST is green today — **re-measured at `bec9d5c`,
HOST: 170 citation lines in 14 records, 0 dangling, against a universe of 340
scopes that exist.** ⚠️ **Its failure mode is a red nobody may discharge:** the
offending line is inside a record, a record is annotated and never edited, so
the day a row file is retired the floor goes red and the only repair is
forbidden. ⛔ **A check whose failure cannot be fixed is worse than the hole it
closes**, and no narrowing available here changes that, so it is refused for
good rather than routed to a fourth gate.

## ⛔ The scope is DERIVED, at zero record edits (Ruling 219)

⭐ **A record's scope is already written on its face, in its FILENAME.**
`CTO-2026-09-12-round69.md` files its findings inside `CTO-69`, and every one of
them says so. ⛔ **So the remedy is a derivation, never a declaration added to a
hundred records** — Ruling 219's whole point, and the reason this row was
re-priced downward rather than refused.

⚠️ **A record MAY declare its scope**, and 37 of them already do, in the
office's own spelling: `**Kind:** ruling record — CTO round 69`. ⭐ **That
spelling is READ, not corrected** — `_ROUND_DECLARATION` normalises it to
`CTO-69` — because demanding the punctuation this module prefers would be an
edit to 37 records for no reading gained. ⛔ A declaration that disagrees with
the filename is the finding; a declaration that agrees costs nothing.

## ⛔ For a record, a scope it does not own is a CITATION, not a heading

⚠️ **This is the one rule that inverts between a handoff and a record**, and it
is measured rather than assumed. A task handoff numbering `W91/1` inside
`W99.md` has taken another task's name. ⭐ **A review record's disposition table
does exactly that on purpose** — it rules on the findings it reviewed, and the
row it reviewed is where they are numbered.

⛔ **Measured at `7a7a178`, over the 109 `ruling record` and `survey` documents
under the handoff directory: 170 finding lines in 14 documents claim a scope the
document does not own, and every one of the 170 resolves to a scope that exists
in the tree.** ⚠️ So `cites_elsewhere` is a permission this module grants with a
population behind it, not a hole left open.

⚠️ **What is held off by CONVENTION and not by construction** (Ruling 220): **5
of the 106 records** derive no scope and declare none — the ones written before
the `<OFFICE>-<DATE>-round<N>` filename settled. ⭐ They are
held to the legacy-ceiling rule and nothing else, and this module does NOT
refuse them: refusing would demand a rename or a declaration inside a record
Ruling 106 protects. ⛔ Every record written under the settled filename derives
a scope, so the uncovered set does not grow.
"""

from __future__ import annotations

import re

from tools.quality.handoffs.contract import (
    MARKER_NONE,
    MIN_NONE_CHARS,
    RULE_FINDINGS,
    RULE_MARKER,
    check_finding_ids,
    claim_free_markers,
    claimed_scope,
    marker_lines,
)
from tools.quality.handoffs.sections import in_findings
from tools.quality.report import Finding

RULE_RECORD_SCOPE = "handoff-record-scope"

#: ⛔ The kind this module governs. ⚠️ `survey` is measured in the same
#: population by every reading this row inherited, and is deliberately NOT
#: admitted here: the row names one kind, and widening to a second is a
#: decision the row does not make.
RULING_RECORD = "ruling record"

#: A round record's filename: `<OFFICE>-<YYYY>-<MM>-<DD>-round<N>`. ⭐ The
#: office and the round are the whole of the scope; the date is what makes the
#: directory sort, and it is not part of the name a finding carries.
_ROUND_FILENAME = re.compile(r"^(?P<office>[A-Z]{2,4})-\d{4}-\d{2}-\d{2}-round(?P<number>\d+)$")

#: The same scope in the spelling an office actually writes on its `**Kind:**`
#: line — `CTO round 69`. ⛔ Read, not corrected: see the module docstring.
_ROUND_DECLARATION = re.compile(r"^(?P<office>[A-Z]{2,4}) round (?P<number>\d+)$")

#: A scope written the way a finding carries it: `CTO-69`, `PO-54`. ⭐ Accepted
#: as a declaration too, so an office that writes the finding's own spelling is
#: not refused for agreeing with the derivation more directly than the others.
_SCOPE = re.compile(r"^[A-Z]{2,4}-\d+$")


def _normalise(declared: str) -> str | None:
    """Read `declared` as a scope, or `None` when it is not one."""
    match = _ROUND_DECLARATION.match(declared)
    if match is not None:
        return f"{match.group('office')}-{match.group('number')}"
    return declared if _SCOPE.match(declared) else None


def derived_scope(stem: str) -> str | None:
    """Derive a record's scope from its FILENAME, or `None` (Ruling 219)."""
    match = _ROUND_FILENAME.match(stem)
    return None if match is None else f"{match.group('office')}-{match.group('number')}"


def record_scopes(stem: str, declared: list[str]) -> list[str]:
    """List every scope this record owns — the derived one first, then declared.

    ⛔ A list rather than one value, and in that order, because the derivation
    is the authority and a declaration that agrees with it must not appear
    twice. ⭐ An unparseable declaration contributes nothing here and is
    reported by `check_record`, so a typo cannot quietly widen what a record
    owns.
    """
    scopes: list[str] = []
    for scope in [derived_scope(stem), *(_normalise(value) for value in declared)]:
        if scope is not None and scope not in scopes:
            scopes.append(scope)
    return scopes


def _check_declaration(relative: str, stem: str, declared: list[str]) -> list[Finding]:
    """Enforce the declaration rules: one scope, a scope, the filename's own."""
    findings: list[Finding] = []
    derived = derived_scope(stem)
    if len(declared) > 1:
        findings.append(
            Finding(
                relative,
                1,
                RULE_RECORD_SCOPE,
                f"declares {len(declared)} scopes ({', '.join(declared)}). A record files "
                f"its findings inside ONE scope; the others are citations, and a citation "
                f"is written on the finding line, not on the declaration.",
            )
        )
    for value in declared:
        scope = _normalise(value)
        if scope is None:
            findings.append(
                Finding(
                    relative,
                    1,
                    RULE_RECORD_SCOPE,
                    f"declares scope {value!r}, which is not a scope. Write "
                    f"`<OFFICE> round <N>` or `<OFFICE>-<N>` — it is what this record's "
                    f"findings are numbered inside.",
                )
            )
        elif derived is not None and scope != derived:
            findings.append(
                Finding(
                    relative,
                    1,
                    RULE_RECORD_SCOPE,
                    f"declares scope {value!r} ({scope}) and its filename derives "
                    f"{derived}. One of the two is wrong, and the filename is the one "
                    f"every reader sees first.",
                )
            )
    return findings


def record_finding_lines(text: str) -> list[tuple[int, str]]:
    """Return every line gate three reads as one of `text`'s findings (`W172`).

    ⛔ **Two conditions, and the module docstring measures both:** the line is
    inside a *Findings* section, and it claims a SCOPED finding number.
    ⭐ Everything else carrying a marker is a record's prose about markers,
    which is the thing this gate exists not to read.
    """
    region = in_findings(text)
    return [
        (number, line)
        for number, line, _own_line in marker_lines(text)
        if number in region and claimed_scope(line) is not None
    ]


def check_record_markers(relative: str, text: str) -> list[Finding]:
    """Gate three: the marker discipline a `ruling record` DOES owe (`W172`).

    ⛔ **Three arms of `check_markers` are deliberately absent** — the six
    sections, *marks no finding*, and `[none]` standing beside a real finding.
    Each is refused in the module docstring against a measurement, not omitted.
    """
    findings: list[Finding] = []
    for number, line in record_finding_lines(text):
        markers = claim_free_markers(line)
        if markers == 0:
            findings.append(
                Finding(
                    relative,
                    number,
                    RULE_MARKER,
                    "numbers a finding and buries its marker in the finding's own prose. "
                    "Rubric §8a: a marker in explanatory text counts as a finding that "
                    "does not exist. Put it in the lead, or in a cell of its own — "
                    "any cell (Ruling 189(b)), never a named column.",
                )
            )
        elif markers > 1:
            findings.append(
                Finding(
                    relative,
                    number,
                    RULE_MARKER,
                    f"numbers one finding and marks it {markers} times. Two markers where "
                    f"no claim precedes them is one finding claiming to be two; a marker "
                    f"QUOTED inside the prose is not one of them and is not counted.",
                )
            )
        if MARKER_NONE in line and len(line.split(MARKER_NONE, 1)[1].strip(" *—-:`|")) < (
            MIN_NONE_CHARS
        ):
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


def check_record(relative: str, stem: str, declared: list[str], text: str) -> list[Finding]:
    """Check a `ruling record`'s scope, its finding IDs, and its markers.

    ⛔ **Gates two and three.** ⚠️ The finding-ID rule reads the WHOLE document
    and the marker rule reads only the Findings section, and that asymmetry is
    deliberate: *is this number legal* is a safe question anywhere, and *is
    this line a finding at all* is exactly the question a record's prose
    defeats. ⭐ Narrowing gate two to the region would REDUCE the floor's reach
    by **475 of the 790** claims it judges across the 110 records — measured at
    `bec9d5c`, HOST — and close no defect.
    """
    findings = _check_declaration(relative, stem, declared)
    scopes = record_scopes(stem, declared)
    lines = [(number, line) for number, line, own_line in marker_lines(text) if own_line]
    findings.extend(check_finding_ids(relative, lines, scopes, cites_elsewhere=True))
    findings.extend(check_record_markers(relative, text))
    return findings
