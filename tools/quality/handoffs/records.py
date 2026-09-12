"""A `ruling record`'s SCOPE: what its findings are numbered inside (`W64`).

**What it does.** Gives a `ruling record` the one thing it has never had — a
scope — so that the finding-ID rule can reach the 106 records this directory
holds. The scope is **derived from the filename** and may be **declared** on
the `**Kind:**` line; nothing in a record is rewritten to produce it.

**How you use it.** `record_scopes(stem, declared)` is the derivation, shipped
rather than described (`W121/2`). `check_record(relative, stem, declared,
text)` returns findings: the declaration rules, then `check_finding_ids` over
the record's own finding lines.

**Depends on.** `contract` and `report.Finding`. ⛔ Never its own package: the
dependency runs one way, exactly as `contract`'s does.

## ⛔ This is GATE TWO of three, and it is not the whole gate (Ruling 218)

⛔ **Ruling 218 stopped `W64` and priced three gates.** ⭐ Gate one was `W121`'s
table-cell boundary. ⭐ **Gate two is this module.** ⚠️ **Gate three — a rule
separating a record's Findings section from its prose — is NOT YET A ROW**, so
`check_markers`, `check_sections` and the *marks no finding* rule are
deliberately **not** applied to a record here. ⛔ Applying them would print
*marks no finding* and *a marker is not on its own finding line* across a corpus
that may not be rewritten (Ruling 106) — which is the exit-`0` chase Ruling 193
forbids.

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

⚠️ **What is held off by CONVENTION and not by construction** (Ruling 220): 8
records derive no scope and declare none — the ones written before the
`<OFFICE>-<DATE>-round<N>` filename settled, plus the three surveys. ⭐ They are
held to the legacy-ceiling rule and nothing else, and this module does NOT
refuse them: refusing would demand a rename or a declaration inside a record
Ruling 106 protects. ⛔ Every record written under the settled filename derives
a scope, so the uncovered set does not grow.
"""

from __future__ import annotations

import re

from tools.quality.handoffs.contract import check_finding_ids, marker_lines
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
    """`declared` as a scope, or `None` when it is not one."""
    match = _ROUND_DECLARATION.match(declared)
    if match is not None:
        return f"{match.group('office')}-{match.group('number')}"
    return declared if _SCOPE.match(declared) else None


def derived_scope(stem: str) -> str | None:
    """The scope a record's FILENAME derives, or `None` (Ruling 219)."""
    match = _ROUND_FILENAME.match(stem)
    return None if match is None else f"{match.group('office')}-{match.group('number')}"


def record_scopes(stem: str, declared: list[str]) -> list[str]:
    """Every scope this record owns — the derived one first, then declared ones.

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
    """The declaration rules: one scope, a scope, and the filename's own."""
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


def check_record(relative: str, stem: str, declared: list[str], text: str) -> list[Finding]:
    """A `ruling record`'s scope, and the finding IDs that rule now reaches.

    ⛔ **Gate two only.** The marker rule, the six sections and *marks no
    finding* are gate three's and are not applied here — see the module
    docstring for why an exit-`0` chase is refused rather than attempted.
    """
    findings = _check_declaration(relative, stem, declared)
    scopes = record_scopes(stem, declared)
    lines = [(number, line) for number, line, own_line in marker_lines(text) if own_line]
    findings.extend(check_finding_ids(relative, lines, scopes, cites_elsewhere=True))
    return findings
