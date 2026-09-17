r"""`W106`: the marker's repository-wide sweep, as a shipped reader and not a typed pattern.

**What it does.** Two readers over one vocabulary. `sweep(root)` is the wave-open
triage list: every line under `HANDOFF_DIR` holding a marker, labelled by
`contract.marker_lines` — a FINDING line, or IN-TEXT (prose, or two markers on
one line). `pattern_sites(root)` is the census of every marker PATTERN typed into
a convention document, each with its form; `check_marker_patterns(root)` fails
the floor on a WEAK one.

**How you use it.** From the shell, `COMMAND` — this package's `__main__`,
which carries the flags and the exit codes. From Python, the three functions
above; `check_marker_patterns` is registered in `tools.quality.CHECKS`.

**Depends on.** `contract` for the vocabulary and the reader, this package for
`HANDOFF_DIR`, `config` for the tracked walk, `report`, `re`.

## ⛔ ONE HOME FOR WHAT THE MARKER IS

⚠️ **The sweep existed only as a command typed inside a convention document**,
and it went wrong exactly that way twice: one copy dropped the backticks and
counted every prose mention, the other dropped the backslashes as well and
matched `44,821` lines as a character class. ⭐ **This module spells no marker.**
Every marker it reads is `FINDING_MARKERS`, every line it labels is
`marker_lines`' label, and `test_sweep.py` refuses a marker spelled in this file.

⛔ **The answer includes MENTIONS by construction** (rubric, *the marker cannot
be quoted in prose*), so the LINES are printed and not only a count: triage is a
person reading a list. ⚠️ A fence is quoted material and `marker_lines` does not
read it — so the lines it skips are COUNTED and printed, never dropped silently.

## ⛔ WHAT A WEAK PATTERN IS, AND WHY THIS IS NOT A LIST OF ACCEPTED SHAPES

⭐ **A pattern is a marker's bracket written ESCAPED** — `\[`, a marker's name,
`\]` — and it is RULED when backticks flank it, because Ruling 65 puts the
backticks inside the marker. That is one property of one spelling, derived from
the constant; ⛔ no shape is enumerated (Ruling 65 records four that failed).

⚠️ **The one weak form that is not a finding is a CONTROL:** a weak pattern in
the same fence as a ruled one. Ruling 193's pass is *run both over one
population and print both counts* — the delta IS the mentions reading — so the
rubric's pair is the instrument that measures this defect and is never "fixed".
A weak pattern in prose, or alone in its fence, measures nothing.

⚠️ **Not reached, stated rather than discovered:** a marker's bracket written
UNESCAPED as a grep argument is indistinguishable, by spelling alone, from
Ruling 155's deliberate unbackticked vocabulary fence; this reader does not
guess between them.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from tools.quality import config
from tools.quality.handoffs import HANDOFF_DIR
from tools.quality.handoffs.contract import FINDING_MARKERS, MARKER_STRUCTURAL, marker_lines
from tools.quality.report import WALK_CAVEAT, Finding

COMMAND = "python3 -m tools.quality.handoffs"
#: The documents that INSTRUCT a reader. ⛔ Records are not in it: a handoff or an
#: archived round is frozen (Ruling 106), and chasing the corpus is Ruling 193's
#: named mistake.
CONVENTIONS_DIR = "docs/conventions"
RULE_PATTERN = "marker-pattern"

FINDING_LINE = "finding"
IN_TEXT = "in-text"
RULED = "ruled"
WEAK = "weak"
CONTROL = "control"

#: A marker's NAME, as `--marker` takes it, read off the constant.
NAMES = {marker.strip("`[]"): marker for marker in FINDING_MARKERS}

#: An escaped bracket pair and what flanks it. ⛔ It names no marker: whether the
#: inner text is one is decided against `NAMES`, so the vocabulary lives once.
_ESCAPED = re.compile(r"(`?)\\\[([^\]\n]*?)\\\](`?)")


@dataclass(frozen=True)
class SweepLine:
    """One line holding the marker, with `marker_lines`' label."""

    document: str
    number: int
    label: str
    text: str


@dataclass(frozen=True)
class Sweep:
    """The whole reading: the population, the lines, and what was not read."""

    marker: str
    walk: str
    documents: int
    lines: tuple[SweepLine, ...]
    fenced: int

    def count(self, label: str) -> int:
        """How many reported lines carry `label`."""
        return sum(1 for line in self.lines if line.label == label)


@dataclass(frozen=True)
class PatternSite:
    """One marker pattern typed into a document, and its form."""

    document: str
    number: int
    form: str
    text: str


def _population(root: Path, directory: str) -> tuple[list[Path], str]:
    """Return the tracked markdown documents under `directory` and their walk."""
    population = config.markdown_population(root)
    base = root / directory
    return [path for path in population.paths if base in path.parents], population.walk


def sweep(root: Path, marker: str = MARKER_STRUCTURAL, directory: str = HANDOFF_DIR) -> Sweep:
    """Every line under `directory` holding `marker`, labelled by `marker_lines`."""
    paths, walk = _population(root, directory)
    lines: list[SweepLine] = []
    fenced = 0
    for path in paths:
        text = config.read_text(path) or ""
        relative = config.relative(path, root)
        read = [(n, line, own) for n, line, own in marker_lines(text) if marker in line]
        fenced += sum(1 for line in text.splitlines() if marker in line) - len(read)
        lines.extend(
            SweepLine(relative, n, FINDING_LINE if own else IN_TEXT, line.strip())
            for n, line, own in read
        )
    return Sweep(marker, walk, len(paths), tuple(lines), fenced)


def _is_marker(inner: str) -> bool:
    """Whether an escaped bracket's inner text names a marker."""
    return any(re.search(rf"\b{re.escape(name)}\b", inner) for name in NAMES)


def convention_documents(root: Path, directory: str = CONVENTIONS_DIR) -> list[Path]:
    """Return the documents `pattern_sites` reads — the pattern check's population (`W309`)."""
    return _population(root, directory)[0]


def pattern_sites(root: Path, directory: str = CONVENTIONS_DIR) -> list[PatternSite]:
    """Every marker pattern typed under `directory`: ruled, weak, or a control."""
    paths = convention_documents(root, directory)
    sites: list[PatternSite] = []
    for path in paths:
        relative = config.relative(path, root)
        block, fence = 0, False
        found: list[tuple[int, int | None, bool, str]] = []
        for number, line in enumerate((config.read_text(path) or "").splitlines(), start=1):
            if line.lstrip().startswith("```"):
                fence, block = not fence, block + (not fence)
                continue
            for match in _ESCAPED.finditer(line):
                if _is_marker(match.group(2)):
                    ruled = bool(match.group(1) and match.group(3))
                    found.append((number, block if fence else None, ruled, line.strip()))
        paired = {block for _n, block, ruled, _t in found if ruled and block is not None}
        for number, block, ruled, text in found:
            form = RULED if ruled else CONTROL if block in paired else WEAK
            sites.append(PatternSite(relative, number, form, text))
    return sites


def check_marker_patterns(root: Path) -> list[Finding]:
    """Report each weak marker pattern typed into a convention document."""
    return [
        Finding(
            site.document,
            site.number,
            RULE_PATTERN,
            "types the marker as a pattern without its backticks, so it counts every prose "
            f"mention as a finding (Ruling 65, Ruling 193). Name the command: `{COMMAND}`.",
        )
        for site in pattern_sites(root)
        if site.form == WEAK
    ]


def sweep_report(reading: Sweep, directory: str = HANDOFF_DIR) -> list[str]:
    """Format the reading as printed lines: the summary first, then every line."""
    summary = (
        f"marker sweep: {reading.marker} over {directory} ({reading.walk} walk) — "
        f"{reading.documents} documents read; {len(reading.lines)} lines hold the marker: "
        f"{reading.count(FINDING_LINE)} {FINDING_LINE}, {reading.count(IN_TEXT)} {IN_TEXT}; "
        f"{reading.fenced} more inside fences, not read{WALK_CAVEAT[reading.walk]}"
    )
    body = [f"{line.document}:{line.number}: {line.label}: {line.text}" for line in reading.lines]
    return [summary, *body]
