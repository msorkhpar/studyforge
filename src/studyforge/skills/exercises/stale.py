r"""Every authored unit in a corpus that went stale, read from the corpus alone, and its removal.

**What it does.** Walks every committed coverage report and asks
`coverage.stale_of` whether it still describes its unit — from what the corpus
holds now: the page and test files the report names, digested as the ledger
digests them, and the plan the report's own aspects give under this build's
rules. ⭐ **It changes nothing.** `remove_stale` is the one write, and it is asked
for by name.

**How you use it.**

    found = stale_units(root)        # every Stale, in unit order
    stale_summary(found)             # the line the pass and the build say up front
    remove_stale(root, found)        # both folders of each, only when git can give them back

**Depends on.** This package's `coverage` for the answer, `ledger` for the
one digest of a file, `aspects` and `plan` to plan again from a report,
`archive.scrub` for R7, `exercise.bundle` for the bundles' root, and
`validate.source.restorable`, the one place a removal asks git. `json` and
`pathlib`; standard library only.

## ⚠️ WHAT THE CORPUS ALONE CAN SAY ABOUT A PLAN

⭐ **A page's aspects are the author's reading, and the corpus holds them only
in each report.** So this module plans again from the report's own aspects,
tier and exercise order: a plan that no longer comes out the same under this
build's rules has moved. ⛔ A plan the AUTHOR changed for an unchanged page —
a new aspect, a quiz named on a code page — is in no file yet: the pass sees
it when that page is handed to it, and refuses it up front the same way.

## ⛔ A REMOVAL IS ALWAYS RECOVERABLE, OR IT DOES NOT HAPPEN

⭐ **`remove_stale` deletes exactly the listed folders, and only when git could
restore every byte in them**: the corpus is a git work tree, nothing is
staged, and no file in those folders is untracked, ignored or modified.
⛔ Anything else, and an unanswered git, refuses before a file is touched.
The removal is then one `git restore` away from undone, and one commit away
from recorded.
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from pathlib import Path

from studyforge.archive.scrub import assert_clean
from studyforge.exercise.bundle import BUNDLES_DIRNAME
from studyforge.skills.exercises.aspects import Aspect
from studyforge.skills.exercises.coverage import (
    CONTRACT,
    COVERAGE_FILENAME,
    Stale,
    stale_of,
    untracked,
)
from studyforge.skills.exercises.drafts import AuthoringError
from studyforge.skills.exercises.ledger import LedgerError, file_digest, source_digest
from studyforge.skills.exercises.plan import plan_document, plan_for
from studyforge.validate.source import restorable


def stale_units(root: Path | str) -> tuple[Stale, ...]:
    """Return every authored unit under `root` whose report no longer describes it.

    ⭐ In unit order, read only. ⛔ A report that will not read is stale by its
    contract: nothing can say what it was authored from. ⛔ Each report is
    gated for personal data before a string of it is used (R7).
    """
    base = Path(root)
    found: list[Stale] = []
    for path in sorted(base.glob(f"{BUNDLES_DIRNAME}/**/{COVERAGE_FILENAME}")):
        unit = path.parent.relative_to(base).as_posix()
        recorded = _report(path)
        if recorded is None:
            found.append(Stale(unit, (CONTRACT,), "its coverage report will not read"))
            continue
        assert_clean(recorded, f"the coverage report of '{unit}'")
        written = recorded.get("digests")
        written = written if isinstance(written, dict) else {}
        now = {name: _digest(base, name, unit) for name in written}
        planned = {"plan": _replanned(recorded, unit)}
        tracked = recorded.get("sources")
        copied = (
            {name: _source(base, name, unit) for name in tracked}
            if isinstance(tracked, dict)
            else None
        )
        stale = stale_of(unit, recorded, recorded.get("page"), now, planned, copied)
        if stale is not None:
            found.append(stale)
    return tuple(found)


def untracked_units(root: Path | str) -> int:
    """Return how many code units were authored before the files they are copied from were tracked.

    ⭐ Read only. Their reports carry no `sources` key, so a changed try-it file cannot be
    seen for them; they are counted, never called stale, so a corpus authored before
    the tracking does not suddenly report everything stale.
    """
    base = Path(root)
    count = 0
    for path in sorted(base.glob(f"{BUNDLES_DIRNAME}/**/{COVERAGE_FILENAME}")):
        recorded = _report(path)
        if recorded is not None and untracked(recorded):
            count += 1
    return count


def remove_stale(root: Path | str, stale: Sequence[Stale]) -> tuple[str, ...]:
    """Remove each stale unit's folders, ⛔ only when git could restore them; return them.

    ⭐ The folders that exist, in unit order — a unit whose practice counterpart
    was never written has one.
    """
    base = Path(root)
    folders = [folder for one in stale for folder in one.folders if (base / folder).exists()]
    if not folders:
        return ()
    if restorable(base, folders) is not True:
        raise AuthoringError(
            f"removing {len(folders)} folder(s) of stale units, the first '{folders[0]}': "
            f"refused, and nothing was removed. A removal happens only when git could restore "
            f"it: the corpus is a git work tree, nothing is staged, and every file in those "
            f"folders is tracked and unmodified. Commit or stash first, or remove them by hand."
        )
    for folder in folders:
        try:
            _delete(base / folder)
        except OSError:
            raise AuthoringError(
                f"removing '{folder}': it could not be removed; every file git tracks in it "
                f"is restored by `git restore`."
            ) from None
    return tuple(folders)


def _delete(folder: Path) -> None:
    """Delete one folder and everything in it, deepest first, never following a link."""
    if folder.is_symlink():
        folder.unlink()
        return
    for directory, folders, files in folder.walk(top_down=False):
        for name in files:
            (directory / name).unlink()
        for name in folders:
            inner = directory / name
            inner.unlink() if inner.is_symlink() else inner.rmdir()
    folder.rmdir()


def _report(path: Path) -> dict | None:
    """Read one coverage report, or `None` when it will not read as an object."""
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except OSError, UnicodeDecodeError, ValueError:
        return None
    return value if isinstance(value, dict) else None


def _digest(base: Path, path: object, unit: str) -> str | None:
    """Return what a recorded file digests to now, `None` when gone or not a source path."""
    try:
        return file_digest(base, path, f"the unit '{unit}'")  # type: ignore[arg-type]
    except LedgerError:
        return None


def _source(base: Path, path: object, unit: str) -> str | None:
    """Return what a recorded source file or folder digests to now, `None` when gone."""
    try:
        return source_digest(base, path, f"the unit '{unit}'")  # type: ignore[arg-type]
    except LedgerError:
        return None


def _replanned(recorded: dict, unit: str) -> dict | None:
    """Plan again from a report's own aspects, or `None` when they no longer plan.

    ⭐ Its exercises' recorded order is handed back as the order, so a plan
    that kept its teaching order plans the same; a quiz no exercise names
    is a plan that no longer holds (`loop.plan_page`'s rule).
    """
    where = f"the coverage report of '{unit}'"
    try:
        written = recorded["plan"]
        aspects = tuple(
            Aspect(one["id"], one["says"], tuple(one["basis"]), one["exercise"], one["reason"])
            for one in written["aspects"]
        )
        order = tuple(one["name"] for one in written["exercises"])
        plan = plan_for(aspects, written["tier"], where, written["nothing_checkable"], order)
    except KeyError, TypeError, ValueError:
        return None
    quiz = recorded.get("quiz")
    if quiz is not None and quiz not in order:
        return None
    return plan_document(plan)
