"""The contract a task handoff owes: the six sections, the markers, the numbers.

**What it does.** Holds the half of Ruling 49 that reads a handoff's *body* —
`agent-protocol.md`'s six sections in either accepted spelling, where a triage
marker may sit, and `<TASK-ID>/<n>` finding numbering. The half that decides
whether a document is a task handoff **at all** is its package.

**How you use it.** `check_sections(path, text)` and `check_markers(path, text,
ids)` return findings. `SECTIONS`, `FINDING_MARKERS` and `LEGACY_GLOBAL_MAX`
are the vocabulary; `marker_lines(text)` is the reader they share.

**Depends on.** `report.Finding` and `re`. ⛔ Never its own package: the
dependency runs one way, so this module reads without the declaration rules and
those rules cannot quietly start depending on a section.

⚠️ **Split out of one module at 422 lines**, at the seam that module's own
handoff had named one commit earlier — *declaration* and *contract* are two
subjects. ⭐ The prediction and the split are in the same wave, which is the
only reason the split cost nothing.
"""

from __future__ import annotations

import re

from tools.quality.report import Finding

RULE_SECTION = "handoff-section"
RULE_MARKER = "handoff-marker"
RULE_FINDINGS = "handoff-findings"
RULE_FINDING_ID = "handoff-finding-id"

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
#: Markup a finding line may carry *before* its marker: a bullet, a heading, a
#: number, bold. ⭐ Derived by reading all 199 marker lines on the tip rather
#: than guessed — every genuine one is a heading, a list item or a numbered
#: item, and every prose mention has a word in front of the marker.
#:
#: ⚠️ **`<TASK-ID>/<n>` had to be added here as well as to `_FINDING_NUMBER`**,
#: and it went red the way a missing shape does: not "wrong number" but *"that
#: is not a finding line at all"*, so the new form was invisible to every rule
#: downstream of it. A vocabulary is read in two places or in neither.
_FINDING_LEAD = re.compile(
    r"^[ \t]*(?:[-*+][ \t]+|#{1,6}[ \t]+)?(?:\*\*)?"
    r"(?:(?:[A-Za-z][\w.-]*/)?\d+[.)]?[ \t]+)?(?:\*\*)?"
)

_MARKERS_ON_LINE = re.compile(r"`\[(?:local|structural|none)\]`")
#: ⛔ The closed legacy range of globally-minted finding numbers. **Pinned from
#: a measurement of the merged tree, 2026-09-10** — `BOARD.md`'s ruling says
#: 20–58 and the tree runs to **62**, because `SF-10` minted 59–62 on a branch
#: before the ruling landed. ⚠️ Ruling 55: a number in a ruling is an
#: instrument reading, never a property of the tree.
#:
#: ⭐ It is a *ceiling*, not a list, and it never rises: a new finding above it
#: must carry its document's ID. `test_handoffs.py` asserts the tree still
#: holds nothing above it, so the constant cannot quietly stop being true.
LEGACY_GLOBAL_MAX = 62

#: Just the markup, without the number. ⛔ Separate from `_FINDING_LEAD`, which
#: *consumes* the number: reading the claim off a line the lead had already
#: eaten returned "this line claims nothing", so every scoped number passed and
#: every bad one did too. Found by the two negative controls going green.
_MARKUP_LEAD = re.compile(r"^[ \t]*(?:[-*+][ \t]+|#{1,6}[ \t]+)?(?:\*\*)?")

#: The number a finding line claims, and how it claims it: `W25/3` (scoped, the
#: form going forward) or a bare `47` (the closed legacy range).
_FINDING_NUMBER = re.compile(r"^(?:(?P<scope>[A-Za-z][\w.-]*)/)?(?P<number>\d+)[.)]?\s")


def _section_pattern(section: str) -> re.Pattern[str]:
    """Rubric §8's two accepted spellings for one section heading."""
    escaped = re.escape(section)
    return re.compile(rf"^(?:\*\*{escaped}:\*\*|#{{2,3}} {escaped}\b)", re.MULTILINE)


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


def check_sections(relative: str, text: str) -> list[Finding]:
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


def check_finding_ids(relative: str, lines: list[tuple[int, str]], ids: list[str]) -> list[Finding]:
    """Check `<TASK-ID>/<n>` on new findings, without renumbering the record."""
    findings: list[Finding] = []
    for number, line in lines:
        claim = _FINDING_NUMBER.match(line[_MARKUP_LEAD.match(line).end() :])
        if claim is None:
            continue  # an unnumbered finding claims no name, so it collides with none
        scope, claimed = claim.group("scope"), int(claim.group("number"))
        if scope is None:
            if claimed <= LEGACY_GLOBAL_MAX:
                continue  # ⛔ grandfathered: a record is never rewritten
            findings.append(
                Finding(
                    relative,
                    number,
                    RULE_FINDING_ID,
                    f"finding {claimed} continues the global sequence, which is closed at "
                    f"{LEGACY_GLOBAL_MAX}. A finding is numbered inside its own document: "
                    f"write `{ids[0]}/<n>`, starting at 1. There is no allocator, because a "
                    f"branch cannot hold one.",
                )
            )
        elif scope not in ids:
            findings.append(
                Finding(
                    relative,
                    number,
                    RULE_FINDING_ID,
                    f"finding {scope}/{claimed} is scoped to a task this document does not "
                    f"declare ({', '.join(ids)}). A finding is numbered inside the document "
                    f"that files it; a number scoped elsewhere is a citation, not a heading.",
                )
            )
    return findings


def check_markers(relative: str, text: str, ids: list[str]) -> list[Finding]:
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
    findings.extend(check_finding_ids(relative, good, ids))
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
