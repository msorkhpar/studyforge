"""The contract a task handoff owes: the six sections, the markers, the numbers.

**What it does.** Holds the half of Ruling 49 that reads a handoff's *body* —
`agent-protocol.md`'s six sections in either accepted spelling, where a triage
marker may sit, and `<TASK-ID>/<n>` finding numbering. The half that decides
whether a document is a task handoff **at all** is its package.

**How you use it.** `check_sections(path, text)` and `check_markers(path, text,
ids)` return findings. `SECTIONS`, `FINDING_MARKERS`, `LEAD_TOKENS` and
`LEGACY_GLOBAL_MAX` are the vocabulary; `marker_lines(text)` is the reader they
share.

**Depends on.** `report.Finding` and `re`. ⛔ Never its own package: the
dependency runs one way, so this module reads without the declaration rules and
those rules cannot quietly start depending on a section.

⚠️ **Split out of one module at 422 lines**, at the seam that module's own
handoff had named one commit earlier — *declaration* and *contract* are two
subjects. ⭐ The prediction and the split are in the same wave, which is the
only reason the split cost nothing.

## ⛔ The vocabulary is spelled ONCE, and the lead is a CLOSED set (`W63`)

⛔ **Ruling 193: the authority for the marker's spelling is the shipped
constant, and a second reader with a second spelling is the same defect at a
different site.** ⚠️ **This module held two spellings of its own** — the three
`MARKER_*` constants and a hand-typed `local|structural|none` alternation beside
them — ⭐ so `_MARKERS_ON_LINE` is now **derived** from `FINDING_MARKERS` and a
fourth marker becomes readable the moment it is named, rather than silently
invisible to every rule downstream.

⛔ **And the lead is a closed set of claim-free tokens, not a list of accepted
shapes.** ⚠️ Ruling 29 records four attempts at an accepted-shape list, each of
which worked on the handoffs its author had seen and failed on one they had not;
⭐ **`LEAD_TOKENS` inverts it — nothing before the marker may carry a CLAIM, and
the markup that carries none is enumerated in one place.** A word and a
blockquote's `>` are in no token, so prose stays refused **by construction**
rather than by a pattern that happens to miss it.

## ⛔ A table cell's `|` carries no claim either (`W121`)

⛔ **It was in no token, and that was the defect: the form BOTH offices actually
write was invisible to this reader, and therefore to every rule downstream of
it.** ⚠️ Ruling 218 named it two-organ — the gate above could see the document
fine and the reader behind it could not — ⭐ so widening the gate alone would
have printed *marks no finding* at documents that carry findings.

⭐ **The remedy is one token, not a table parser.** A `|` delimits a cell; it
asserts nothing, so it joins the set for the reason horizontal space is already
in it. ⛔ **No column index is named anywhere** (Ruling 189(b)): the marker may
sit in the first cell or the fifth, before its number or after it. ⚠️ And a cell
carrying PROSE still ends the lead wherever it appears, so
`| the review said | ...` is refused exactly as the un-tabled sentence is.
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

#: ⛔ DERIVED from `FINDING_MARKERS`, never typed a second time (Ruling 193).
#: ⭐ `sorted()` so the pattern is one enumeration read in a fixed order (R10);
#: the three members share no prefix, so the order cannot change what matches.
_MARKERS_ON_LINE = re.compile("|".join(re.escape(marker) for marker in sorted(FINDING_MARKERS)))

#: A finding's number, as it is written: `W25/3` scoped, or a bare `47` from the
#: closed legacy range, optionally inside backticks. ⛔ Spelled ONCE and composed
#: into both readers below, because the docstring's own warning was earned:
#: `<TASK-ID>/<n>` once had to be added in two places and went red the way a
#: missing shape does — not *"wrong number"* but *"that is not a finding line at
#: all"*, which made the new form invisible to every rule downstream.
_ID = r"(?:[A-Za-z][\w.-]*/)?\d+"

#: ⛔ The CLOSED set of markup a finding line may carry BEFORE its marker, each
#: token named by what it is. ⭐ **The rule is not a list of accepted shapes — it
#: is that nothing before the marker carries a CLAIM**, and this is the markup
#: that carries none. A word is in no token, so prose is refused by
#: construction; `>` is in no token, so a blockquote is refused the same way.
#:
#: ⛔ **A table cell boundary IS in the set (`W121`), and it is the whole of that
#: row's change.** ⭐ It names no column, so a role is still read from what a
#: cell HOLDS and never from where the cell sits (Ruling 189(b)).
#:
#: ⚠️ **Ruling 220 — what is held off by CONVENTION here and not by
#: construction:** a table that DOCUMENTS this vocabulary, one marker to a row,
#: now reads as a row of findings. ⭐ The fence rule holds it off, as it already
#: does for a transcript, and Ruling 65's *name the marker, do not spell it*
#: holds off the rest. ⛔ That is a convention, and it is written here rather
#: than left for the next author to discover.
#:
#: ⚠️ **Every token's first characters are disjoint from every other's**, which
#: is what makes the order here immaterial and the reader reproducible (R10).
#: `test_contract.py` asserts that disjointness rather than trusting it.
LEAD_TOKENS: tuple[tuple[str, str], ...] = (
    ("horizontal space", r"[ \t]+"),
    ("a heading", r"#{1,6}"),
    ("a bullet, an emphasis run or a hyphen", r"[-*+_]+"),
    ("an em dash, an en dash or a colon", r"[—–:]"),
    ("an attention glyph", "[⛔⭐⚠✅️]+"),
    ("a table cell boundary", r"\|"),
    ("a finding number, backticked or not", rf"(?:`{_ID}`|{_ID})[.)]?"),
)
_LEAD = re.compile("|".join(f"(?:{pattern})" for _name, pattern in LEAD_TOKENS))
#: The same closed set **without the number**, for `check_finding_ids`: that
#: reader has to see the number the line claims, so the lead may not eat it.
_MARKUP = re.compile(
    "|".join(f"(?:{pattern})" for name, pattern in LEAD_TOKENS if not name.startswith("a finding"))
)

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

#: The number a finding line claims, and how it claims it: `W25/3` (scoped, the
#: form going forward) or a bare `47` (the closed legacy range), in backticks or
#: not. ⛔ The backticks are matched as a PAIR — `` `13 `` with no closing tick
#: claims nothing — and what may follow is the closed markup the lead is made
#: of, so `` - **`W25/3`** — `[local]` `` is read and `W25/3x` is not.
_FINDING_NUMBER = re.compile(
    r"^(?P<tick>`?)(?:(?P<scope>[A-Za-z][\w.-]*)/)?(?P<number>\d+)(?P=tick)[.)]?(?=[ \t*—–:]|$)"
)


def _claim_free_end(line: str, token: re.Pattern[str]) -> int:
    """How far into `line` the claim-free markup in `token` reaches.

    ⛔ A loop over a closed token set, never a grammar of accepted sequences:
    the only question asked at each position is *does what starts here carry a
    claim*, and the first thing that does ends the lead.
    """
    position = 0
    while position < len(line):
        match = token.match(line, position)
        if match is None or match.end() == position:
            break
        position = match.end()
    return position


def _section_pattern(section: str) -> re.Pattern[str]:
    """Rubric §8's two accepted spellings for one section heading."""
    escaped = re.escape(section)
    return re.compile(rf"^(?:\*\*{escaped}:\*\*|#{{2,3}} {escaped}\b)", re.MULTILINE)


def marker_lines(text: str) -> list[tuple[int, str, bool]]:
    """`(line number, line, is a finding line)` for every line holding a marker.

    A line is a **finding line** when exactly one marker sits on it and
    everything before it is in `LEAD_TOKENS` — the closed set of markup that
    carries no claim. ⛔ Rubric §8a: a marker in explanatory text counts as a
    finding that does not exist, and two markers on one line is one finding
    claiming to be two.

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
        rest = line[_claim_free_end(line, _LEAD) :]
        own_line = len(markers) == 1 and rest.startswith(FINDING_MARKERS)
        found.append((number, line, own_line))
    return found


def claimed_scope(line: str) -> str | None:
    """Return the SCOPE a line's numbered claim carries, or `None` (`W172`).

    ⛔ `None` means *this line claims no scope*, and it does not distinguish a
    line carrying nothing from one carrying a bare legacy number: both are
    outside the scoped form, which is the only distinction any caller makes.
    ⭐ It reads through the same `_MARKUP` lead as `check_finding_ids`, so the
    two can never disagree about what a line claims.
    """
    claim = _FINDING_NUMBER.match(line[_claim_free_end(line, _MARKUP) :])
    return None if claim is None else claim.group("scope")


def claim_free_markers(line: str) -> int:
    """How many markers on `line` sit where no CLAIM has preceded them.

    ⛔ **Every cell is tested, not only the line (Ruling 189(b)):** *the marker
    may sit in the first cell or the fifth*, so a cell's own lead is what
    decides, and a prose cell earlier in the row does not bury a marker later
    in it. ⚠️ `marker_lines`'s `own_line` tests the LINE's lead only, which is
    the stricter reading a task handoff is held to; ⭐ this is the reading
    Ruling 189(b) states, and `records.py` explains why a record gets it.
    """
    return sum(
        1
        for cell in line.split("|")
        if cell[_claim_free_end(cell, _LEAD) :].startswith(FINDING_MARKERS)
    )


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


def check_finding_ids(
    relative: str,
    lines: list[tuple[int, str]],
    ids: list[str],
    *,
    cites_elsewhere: bool = False,
) -> list[Finding]:
    """Check `<TASK-ID>/<n>` on new findings, without renumbering the record.

    ⛔ **`cites_elsewhere` inverts ONE arm, for `ruling record` only (`W64`).**
    ⭐ A task handoff numbering a finding inside another task's name has taken
    that name; a review record's disposition table does it on purpose, because
    the row it reviewed is where those findings are numbered. ⚠️ The permission
    is measured, not assumed — `records.py`'s docstring carries the reading.
    """
    findings: list[Finding] = []
    #: ⛔ A record whose filename derives no scope and which declares none owns
    #: nothing to suggest, so the message names the SHAPE rather than crashing.
    suggestion = ids[0] if ids else "<SCOPE>"
    for number, line in lines:
        claim = _FINDING_NUMBER.match(line[_claim_free_end(line, _MARKUP) :])
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
                    f"write `{suggestion}/<n>`, starting at 1. There is no allocator, because "
                    f"a branch cannot hold one.",
                )
            )
        elif scope not in ids and not cites_elsewhere:
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
