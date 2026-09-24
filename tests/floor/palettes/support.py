"""Shared machinery for the palette mirrors: a tree that carries the LIVE convention.

⛔ **Every plant is judged against the table the spec's §8.4 carries** (`UI_CONVENTION`),
copied into the temp tree, so a row somebody edits there is a row these tests
re-read rather than a fixture that quietly drifts from it.
"""

from __future__ import annotations

from pathlib import Path

from tests.floor.palettes import RULE_PALETTE, UI_CONVENTION, check_rejected_palettes
from tests.floor.palettes.shipped import STYLESHEET_DIR

#: The repository this file sits in. ⚠️ Derived here rather than imported from
#: `tests.support`: a module of the floor that is not a test imports the standard
#: library and the floor only (`tests/floor/test_init.py`).
REPOSITORY = Path(__file__).resolve().parents[3]

#: The identities the live table names, by the name a finding prints.
CREAM = "Warm cream and terracotta"
SLATE = "Cool slate with teal-green and amber"
SATURATED = "A saturated brand colour as the page ground"
GRADIENT = "A purple-to-blue gradient"

#: ⭐ The look the user ACCEPTED on 2026-09-19, as a stylesheet: cool slate
#: neutrals, ONE loud accent, no green. ⛔ It shares its ground band with the
#: rejected slate row, and that is exactly why it is here.
ACCEPTED = """
:root {
  --bg: #f1f5f9;
  --surface: #f8fafc;
  --fg: #22304a;
  --rule: #dbe3ec;
  --accent: #a64d07;
  --sign: #92400e;
  --focus: #0369a1;
}
:root[data-theme="dark"] {
  --bg: #0f172a;
  --fg: #d2dbe6;
  --accent: #ffc933;
  --sign: #ffc933;
  --focus: #38bdf8;
}
"""


def convention_text() -> str:
    """The live UI convention, as text."""
    return (REPOSITORY / UI_CONVENTION).read_text(encoding="utf-8")


def tree(tmp_path: Path, stylesheet: str, document: str | None = None) -> Path:
    """A tree carrying the LIVE convention (or `document`) and one shipped stylesheet."""
    root = tmp_path / "repo"
    (root / STYLESHEET_DIR).mkdir(parents=True)
    (root / UI_CONVENTION).parent.mkdir(parents=True, exist_ok=True)
    (root / UI_CONVENTION).write_text(
        convention_text() if document is None else document, encoding="utf-8"
    )
    (root / STYLESHEET_DIR / "palette.css").write_text(stylesheet, encoding="utf-8")
    return root


def named(root: Path) -> list[str]:
    """The identities the check reports over `root`, in report order."""
    found = []
    for finding in check_rejected_palettes(root):
        assert finding.rule == RULE_PALETTE
        found.append(finding.message.partition("is the identity '")[2].partition("'")[0])
    return found
