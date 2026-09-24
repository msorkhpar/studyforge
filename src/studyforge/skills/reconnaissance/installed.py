r"""What the framework generated here, read from the corpus's own install record.

**What it does.** Answers one question for the whole skill: *which files under
this root did `studyforge` write?* — so no pass mistakes the framework's own
consuming half for the corpus's material.

**How you use it.** `generated(root)` returns the relative posix paths, or an
empty set when there is no readable record.

**Depends on.** `studyforge.skills.onboarding.RECORD_FILE` for where the record
lives and `studyforge.archive.scrub` for R7's gate. ⛔ Nothing source-specific
(R1): no file name is special here, and every path comes from the record.

## ⛔ One instrument, and it already existed

⚠️ **A skill that reads a corpus it has already onboarded reads its own output
back.** Unchecked, a re-survey counts the generated
`tests/**/test_*.py` as the corpus's graders, drops its *"no runnable code,
no graders"* verdict, and drafts `exercises: true` for a corpus whose own
onboarding report printed `graded practices  no` three lines above. ⛔ **A
COMPLETE corpus is then presented to its reader as unfinished** — the spec's own
C5 failure — and nothing raises.

⭐ **`.studyforge/installed.json` names every file of it**, one entry per
generated path, and onboarding writes it on the same run that writes the files.
⛔ **So there is no second way to recognise a generated file, and a pass that
invents one — a name, a suffix, a directory — is a defect against this module.**

## ⚠️ An unreadable record reads as no footprint

A corpus that was never onboarded has no record, and a first survey is
unchanged by everything above. ⛔ The record is a list of paths, so it is gated
by `assert_clean` before a field is read (R7), and a leak raises rather
than being swallowed with the rest.
"""

from __future__ import annotations

import json
from pathlib import Path

from studyforge.archive.scrub import assert_clean
from studyforge.skills.onboarding import RECORD_FILE

#: Where onboarding records what it wrote. ⭐ Re-exported so a reader of this
#: module does not have to know which skill owns the file.
INSTALL_RECORD = RECORD_FILE


def generated(root: Path | str) -> frozenset[str]:
    """Return every path onboarding's record says it wrote under `root`.

    ⭐ Relative, posix-spelled, exactly as the record states them — which is how
    every other pass in this skill spells a path. ⛔ An absent, unreadable or
    malformed record is *no footprint*, never a guess: a corpus nobody onboarded
    must survey exactly as if this module did not exist.
    """
    try:
        document = json.loads((Path(root) / INSTALL_RECORD).read_text(encoding="utf-8"))
    except OSError, ValueError:
        return frozenset()
    assert_clean(document, INSTALL_RECORD)
    files = document.get("files") if isinstance(document, dict) else None
    if not isinstance(files, list):
        return frozenset()
    return frozenset(
        entry["where"]
        for entry in files
        if isinstance(entry, dict) and isinstance(entry.get("where"), str)
    )
