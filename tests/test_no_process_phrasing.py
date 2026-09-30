"""A tracked file states the product, not who decided it or how the work was run.

Mirrors no source module. `tests/test_no_roadmap.py` keeps work-item ids out of
the tree; this module keeps out the phrasing that goes with them, so a stranger
who reads a file meets the decision and its reason and nothing about a ruling
made by somebody, on some day, in some round of the work. This module holds
two things:

- **No process phrasing in any tracked file.** A file does not say a "register"
  ruled or directed something, that something was ruled on a date, or that the
  user or the owner said, asked or reversed something. A design rule of the
  specification may still be called a ruling: the ban is on who made it and when.
- **No work-item id spelled in lower case.** `test_no_roadmap` reads capitals; a
  task id typed as a name, in `w123` or `sf12` form, is caught here.

What is read is what `test_no_roadmap` reads: test code by its docstrings and
comments, every other file whole.

Standard library only, plus `git`.
"""

from __future__ import annotations

import re
from pathlib import Path

from tests.support import repository_root
from tests.test_decisions import scratch_repository
from tests.test_no_roadmap import NOT_READ as ROADMAP_NOT_READ
from tests.test_no_roadmap import _prose, _skipped, _text
from tests.test_prose_stands_alone import tracked

#: Who decided, and when, in the words of the work's own process.
PHRASING = re.compile(
    r"(?i)\bregister(?:'s)?\s+(?:ruling|rulings|direction|decision|decisions|reading)\b"
    r"|\bthe\s+register\b"
    r"|\b(?:user|owner|po|cto)(?:'s)?\s+(?:ruling|direction)\b"
    r"|\b(?:by|under)\s+(?:a\s+|an\s+|the\s+)?(?:later\s+|earlier\s+|same\s+)?rulings?\b"
    r"|\brulings?\s+of\s+20[0-9]{2}"
    r"|\bruled\s+(?:by|on\s+20)"
    r"|\b(?:the\s+)?(?:user|owner)\s+(?:said|ruled|reversed|directed)\b"
)

#: A work-item id typed as a name: `w` or `sf` and two or three digits, and a skill task's `SK08-A`.
LOWER_ID = re.compile(r"(?i)\b(?:w|sf)[0-9]{2,3}\b|\bSK[0-9]{2}-[A-Z]\b")

#: Paths this sweep does not read, each with its reason: the ones `test_no_roadmap` skips, and
#: this module, which spells every pattern it looks for.
NOT_READ = {
    **ROADMAP_NOT_READ,
    "tests/test_no_process_phrasing.py": "this module spells every pattern it looks for",
}


def phrasing(root: Path) -> dict[str, list[str]]:
    """Each tracked file that carries process phrasing or a lower-case id, with the matches."""
    found: dict[str, list[str]] = {}
    for name in tracked(root):
        if _skipped(name) or name in NOT_READ:
            continue
        text = _text(root / name)
        if text is None:
            continue
        read = _prose(name, text)
        matches = (m for p in (PHRASING, LOWER_ID) for m in p.finditer(read))
        hits = sorted({" ".join(m.group(0).split()) for m in matches})
        if hits:
            found[name] = hits
    return found


def test_no_tracked_file_says_who_ruled_or_when():
    root = repository_root()
    assert len(tracked(root)) > 500, "the sweep read too few files to mean anything"
    assert phrasing(root) == {}, "state the decision and its reason, not who made it or when"


def test_planted_process_phrasing_is_read_wherever_the_sweep_reads(tmp_path):
    # Each spelled by concatenation, so this module's own text carries none.
    planted = {
        "README.md": "By " + "register" + " ruling, it is so.\n",
        "docs/decisions.md": "A " + "register" + " direction (2026-09-25).\n",
        "src/pkg/data.json": '{"note": "the ' + "user" + ' said so"}\n',
        "pyproject.toml": "# ruled " + "by" + " the board\n",
        "tests/test_x.py": '"""The ' + "register" + '\'s ruling."""\n',
        "src/pkg/mod.py": "# see " + "w" + "436-thing\n",
        "docs/other.md": "Under a " + "ruling" + " of 2026-09-26.\n",
    }
    found = phrasing(scratch_repository(tmp_path, planted))
    assert sorted(found) == sorted(planted), f"a planted phrase went unread: {sorted(found)}"


def test_a_spec_rule_called_a_ruling_and_a_register_in_code_are_not_flagged(tmp_path):
    planted = {
        "docs/spec.md": "These rulings are rules, and R7 is one.\n",
        "src/pkg/mod.py": '"""Registers each verb; the registered table is checked."""\n',
        "tests/test_data.py": '"""A test."""\nPLANT = "' + "w" + '44"\n',
    }
    assert phrasing(scratch_repository(tmp_path, planted)) == {}
