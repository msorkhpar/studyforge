"""The skill's one door onto `studyforge.progress`: read a record, read an archived one, merge.

**What it does.** Reads a corpus's progress through `Progress.read`. Reads an archived
progress document through that same reader, staged under a temporary root, so the
store's own validation and R7 gate judge it before anything is written. Merges an
archive's practices into a corpus's store by recording runs through
`Progress.record_run`, the store's one public locked write.

**How you use it.**

    record.store_path(root)            # the store's directory, which the export leaves out
    record.owned(root, depth)          # this corpus's progress document
    practices = record.staged(text, depth)["practices"]
    refused = record.merge_into(root, depth, practices, say)

**Depends on.** `studyforge.progress`'s public surface only, and this package's `merge`
and `layout`. ⛔ Never `Progress`'s private methods, and never the record's file.

## ⛔ The corpus's record is written by `record_run`, and nothing else

`PROGRESS_FILENAME` and `store_dir` appear here for two reasons only. One names the
store's directory, so that material never includes it. The other stages an ARCHIVED
document under a temporary root, so the public reader can read it. `test_record.py`
wraps `record_run` and asserts that every change to the corpus's record happened
inside one of its calls.

⚠️ **A merge is many locked writes, not one**. A crash part-way leaves
some practices merged. The merge rule is a join, so running the import again
finishes it and changes nothing already merged.
"""

from __future__ import annotations

import tempfile
from collections.abc import Callable
from pathlib import Path

from studyforge.progress import (
    PROGRESS_FILENAME,
    RAISES,
    Progress,
    parse_practice_key,
    store_dir,
)
from studyforge.skills.personalarchive.layout import REFUSALS as LAYOUT_REFUSALS
from studyforge.skills.personalarchive.layout import ArchiveError
from studyforge.skills.personalarchive.merge import REFUSED, merged

#: Every refusal an export or an import reports rather than crashes on.
REFUSALS: tuple[type[Exception], ...] = (*LAYOUT_REFUSALS, *RAISES)


def store_path(root: Path | str) -> str:
    """Return the store's directory relative to the corpus root, as a POSIX path."""
    return store_dir(root).relative_to(Path(root)).as_posix()


def owned(root: Path | str, depth: int) -> dict:
    """Return this corpus's whole progress document, read through the store."""
    return Progress(root, depth).read()


def staged(text: str, depth: int) -> dict:
    """Return an archived progress document once the store's own reader has accepted it.

    ⭐ The text is placed where a store under a TEMPORARY root keeps its record, and
    `Progress.read` judges it there. The version, the shape, the key depth and the R7
    gate are all the store's, so none of them is re-implemented here.
    """
    with tempfile.TemporaryDirectory() as scratch:
        placed = store_dir(scratch) / PROGRESS_FILENAME
        placed.parent.mkdir(parents=True)
        placed.write_text(text, encoding="utf-8", newline="\n")
        return Progress(scratch, depth).read()


def merge_into(root: Path | str, depth: int, practices: dict, say: Callable[[str], None]) -> int:
    """Merge every archived practice into the corpus's store, report each, return the refused.

    ⛔ Every write is `Progress.record_run`. The entry read back afterwards must be the
    one the merge rule computed, or the import stops and says so (R6).
    """
    store = Progress(root, depth)
    refused = 0
    for key in sorted(practices):
        address, ordinal, section = parse_practice_key(key, depth)
        plan = merged(store.entry(address, ordinal, section), practices[key])
        for run in plan.runs:
            store.record_run(address, ordinal, section, **run.arguments())
        if store.entry(address, ordinal, section) != plan.entry:
            raise ArchiveError(
                f"practice {key} did not land as the merge rule says; the import stopped there"
            )
        refused += plan.outcome == REFUSED
        say(plan.line(key))
    return refused
