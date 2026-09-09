"""The thin wrapper that makes the main suite fail when the quality floor does.

⛔ **Thin on purpose.** It calls `tools.quality` and asserts the result. It does
not re-implement a rule, does not carry its own idea of 400, and does not keep
a second exclusion list — so the ceiling has exactly one definition, in
`tools/quality/config.py`, and there is no second place to update when it
moves.

Why it exists at all: `tools/quality/` is developer tooling that lives outside
`src/` and is tested at `tools/tests/`. Without this file, running the floor
would be a separate command a contributor has to remember and a reviewer has
to notice was never run. With it, `pytest` is sufficient.
"""

from __future__ import annotations

from tests.support import repository_root
from tools.quality import format_findings, run_all
from tools.quality.config import SCAN_ROOTS, python_files, relative


def test_the_quality_floor_is_clean():
    findings = run_all(repository_root())
    assert not findings, "\n" + format_findings(findings)


def test_the_checker_checks_itself():
    # ⭐ A checker exempt from what it checks is a checker nobody has tested.
    # `tools/` is a scan root, so the floor's own modules are held to their own
    # ceiling, their own mirror and their own contract rule — and the assertion
    # above is what proves they pass it.
    assert "tools" in SCAN_ROOTS
    root = repository_root()
    scanned = {relative(path, root) for path in python_files(root)}
    assert "tools/quality/size.py" in scanned
    assert "tools/tests/quality/test_size.py" in scanned
