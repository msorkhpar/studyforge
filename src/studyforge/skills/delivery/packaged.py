"""The capability index as the INSTALLED package ships it (`REL-06`).

**What it does.** Hands a planner the generated capability index from the
directory this module was loaded from, so the delivery skill's first step
reads the framework's plan with no checkout — and no plan documents — anywhere
on the disk. ⭐ The index is a **generated artifact that ships as package
data** beside this module, exactly as the skill's own procedure does.

**How you use it.** From a shell, the skill's first command:

    python3 -m studyforge.skills.delivery      the index, byte for byte

From code: `packaged_index()` is the index's text; `INDEX` is its `Path` in
this installation.

**Depends on.** `pathlib`, `sys` and `studyforge.exitcodes`, nothing else.
⛔ Not `importlib` in any form (`tests/harness/test_isolation.py`): the file is
found at `Path(__file__).parent`, the rule `studyforge.skills.documents` keeps.

## ⛔ The one module in this package that touches the filesystem, and why

Every other module here is handed text and gives back text, because a planner
that went looking for a plan's documents would be a module the next
repository has to be arranged around. ⭐ **This module goes looking for
nothing**: it reads the one file this package ships, from its own directory,
and never a path a caller names. The package's filesystem test excuses it by
name and for `pathlib` alone.

## ⛔ Generated, never hand-authored (R19)

The file is `capability_index(...)`'s output, regenerated whenever the
documents it is derived from change. ⛔ **A hand-edit to it is a finding
against the delivery skill, not a fix**, and the tests compare the shipped
bytes with a regeneration. ⛔ This module never regenerates it: the generator
is handed its documents by a caller, and this package does not know where any
plan lives.
"""

from __future__ import annotations

import sys
from pathlib import Path

from studyforge.exitcodes import UNUSABLE

#: The shipped index's file name, beside this module.
NAME = "capability-index.md"

#: The shipped index in THIS installation. ⛔ Never another package's `__file__`.
INDEX = Path(__file__).resolve().parent / NAME

#: How the command line is used, printed when it is used wrongly.
USAGE = "usage: python3 -m studyforge.skills.delivery"


def packaged_index() -> str:
    """Return the capability index this installation ships, as text."""
    return INDEX.read_text(encoding="utf-8")


def main(argv: list[str]) -> int:
    """Write the shipped index's BYTES to standard output unchanged; take no argument."""
    if argv:
        sys.stderr.write(f"{USAGE}\n")
        return UNUSABLE
    sys.stdout.flush()
    sys.stdout.buffer.write(INDEX.read_bytes())
    sys.stdout.buffer.flush()
    return 0
