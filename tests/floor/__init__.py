"""The product floor: the rules that keep the product honest, run by the product itself.

**What it does.** Reads the tree and reports every place the PRODUCT falls below the floor its
own rules set — R7 (no personal data reaches a tracked file), R11 (the size ceiling), R12 (every
module has its mirrored test), R17 (every module states its contract), R1 (framework source
names no corpus), the producer half of a package's surface (a name one package takes from
another is on the owner's `__all__`), the rejected palettes (spec §8.4: no shipped theme is an
rejected identity), and the standard-library style layer. Exit code, not
advice: `python3 -m tests.floor` returns 1 when anything is found.

**How you use it.**

    python3 -m tests.floor              # from the repository root
    python3 -m tests.floor --root PATH  # any other tree

or `run_all(Path("."))` from Python. `tests/floor/test_init.py` runs it over the repository, so
`pytest` alone fails on a finding and there is no second command to remember.

**Depends on.** The standard library, and nothing else, ever — the floor must run on a clean
checkout with no network and no install.

⛔ **Why it lives under `tests/` and not under `src/studyforge/`.** The framework ships what the
spec enumerates package by package, and a lint tool is not on that list: under `src/` the
ceiling check would become importable, versioned API (R9) that consumers depend on. Under
`tests/` it travels with the product's suite, is never packaged, and still runs on every
checkout, with nothing beside it.

⚠️ **Every check here is about the PRODUCT's tree.** A check about how the work
was organised has no place in the product's floor.
"""

from __future__ import annotations

from pathlib import Path

from tests.floor.config import (
    LINE_LENGTH,
    MIN_JUSTIFICATION_CHARS,
    SIZE_EXCEPTION_MARKER,
    SOURCE_LINE_CEILING,
    TEST_LINE_CEILING,
)
from tests.floor.docstrings import check_docstrings
from tests.floor.mirror import check_mirrors
from tests.floor.palettes import check_rejected_palettes, palette_census
from tests.floor.personal_data import check_personal_data, identity_notice
from tests.floor.report import Finding, format_findings
from tests.floor.size import check_sizes
from tests.floor.source_names import check_source_names
from tests.floor.style import check_style
from tests.floor.surfaces import check_producer_half, surface_census
from tests.floor.vacuity import vacuity_notice

#: Every product check, in the order the tooling registers the same checks. ⛔ Adding one means
#: answering, in `vacuity.py`, for the run where it compared nothing; `test_vacuity.py` fails
#: until that is done.
CHECKS = (
    check_sizes,
    check_mirrors,
    check_docstrings,
    check_style,
    check_personal_data,
    check_source_names,
    check_producer_half,
    check_rejected_palettes,
)

#: Lines printed on every run that never affect the exit code: the populations a green run
#: would otherwise swallow. ⚠️ `identity_notice` prints which R7 identifier arms had a value to
#: compare, by label and never by value; `vacuity_notice` speaks only when a check read nothing.
NOTICES = (
    surface_census,
    palette_census,
    vacuity_notice,
    identity_notice,
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
    "format_findings",
    "run_all",
    "run_notices",
]


def run_all(root: Path) -> list[Finding]:
    """Every product finding in the tree at `root`, sorted, so any machine prints the same."""
    findings: list[Finding] = []
    for check in CHECKS:
        findings.extend(check(root))
    return sorted(findings)


def run_notices(root: Path) -> list[str]:
    """Every non-failing line the product floor prints, in order."""
    lines: list[str] = []
    for notice in NOTICES:
        lines.extend(notice(root))
    return lines
