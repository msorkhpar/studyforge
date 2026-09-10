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

from tools.quality.config import (
    LINE_LENGTH,
    MIN_JUSTIFICATION_CHARS,
    SIZE_EXCEPTION_MARKER,
    SOURCE_LINE_CEILING,
    TEST_LINE_CEILING,
)
from tools.quality.docstrings import check_docstrings
from tools.quality.knowledge_index import check_knowledge_index, notices
from tools.quality.mirror import check_mirrors
from tools.quality.personal_data import check_personal_data
from tools.quality.report import Finding, format_findings
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
CHECKS = (
    check_sizes,
    check_mirrors,
    check_docstrings,
    check_style,
    check_personal_data,
    check_source_names,
    check_knowledge_index,
)

#: ⛔ **The second channel, and it exists because one of the floor's answers is
#: not a failure.** `check_knowledge_index` must be able to say *"there is no
#: knowledge index here, and this is how you build one"* **without failing**: a
#: fresh clone legitimately has none, and a red suite on clone is hostile and
#: gets muted — which is how a check stops being read (FND-07).
#:
#: ⚠️ A notice never affects the exit code. Anything that should fail a build
#: is a `Finding`, and nothing here is a quieter way to report one.
NOTICES = (notices,)

__all__ = [
    "CHECKS",
    "NOTICES",
    "LINE_LENGTH",
    "MIN_JUSTIFICATION_CHARS",
    "SIZE_EXCEPTION_MARKER",
    "SOURCE_LINE_CEILING",
    "TEST_LINE_CEILING",
    "Finding",
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
