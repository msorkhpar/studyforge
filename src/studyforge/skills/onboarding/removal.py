r"""Take one onboarding back out of a repository, and never a file somebody filled in.

**What it does.** Removes exactly the files one onboarding recorded, and refuses,
naming every one at once, when any generated file changed or the person's module
is no longer the stub the written manifest scaffolds.

**How you use it.** `uninstall(root)`, re-exported by the package as step 6 of
`SKILL.md`. Returns the paths removed, sorted.

**Depends on.** `record` for what was written and its digests, `skills.adapter`
to re-derive the stub, and `corpus.manifest` to read the written manifest.

## ⭐ Split out of `onboard` at the removal seam (`W313`)

`onboard` composes and writes; this module takes back out. The two share the
install record and nothing else, so the seam is where the file set is already
on disk and only its record is read.
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from studyforge.corpus.manifest import RAISES, parse
from studyforge.skills.adapter import plan_for, scaffold
from studyforge.skills.onboarding import artifacts, record
from studyforge.skills.onboarding.pin import RECORD_FILE
from studyforge.skills.onboarding.record import OnboardingRefused


def uninstall(root: Path | str) -> list[str]:
    """Remove exactly what one onboarding wrote, and refuse if any of it changed.

    ⛔ **A file somebody filled in is never silently destroyed.** The usual
    reason a clean uninstall refuses is the adapter's reading step, which is the
    one file that was a person's — and losing it to a tidy-up is the failure
    this check exists for. ⭐ The record carries no digest for that file
    (`INT-09/1`), so it is removed only while it is still the stub the written
    manifest scaffolds.
    """
    root = Path(root)
    entries = record.entries(root)
    changed = record.changed(root, entries)
    filled = _filled_in(root, entries, changed)
    if changed or filled:
        raise OnboardingRefused(_kept(changed, filled))
    removed = []
    for where in [*[entry["where"] for entry in entries], RECORD_FILE]:
        path = root / where
        if path.exists():
            path.unlink()
            removed.append(where)
    _prune(root, removed)
    return sorted(removed)


def _filled_in(root: Path, entries: Sequence[dict], changed: Sequence[str]) -> list[str]:
    """Every person's module on disk that is not the stub onboarding left there, sorted.

    ⚠️ The stub is re-derived from the written manifest, which the scaffold
    varies on and nothing else does. ⛔ If that manifest changed or cannot be
    read, no stub can be derived, and every such module counts as filled in.
    """
    yours = [e["where"] for e in entries if record.is_yours(e) and (root / e["where"]).exists()]
    stubs = {} if not yours or artifacts.MANIFEST in changed else _stubs(root)
    return sorted(where for where in yours if _text(root / where) != stubs.get(where))


def _stubs(root: Path) -> dict[str, str]:
    """Return the scaffold's hand-written stubs from the manifest on disk, or nothing."""
    try:
        made = scaffold(plan_for(parse((root / artifacts.MANIFEST).read_text(encoding="utf-8"))))
    except (OSError, ValueError, *RAISES):
        return {}
    return {item.where: item.text for item in made.files if not item.generated}


def _text(path: Path) -> str | None:
    """Return a file's text, or None when it is not UTF-8 (and so is not a stub)."""
    try:
        return path.read_text(encoding="utf-8")
    except ValueError:
        return None


def _kept(changed: Sequence[str], filled: Sequence[str]) -> str:
    """Name every file uninstall will not remove, and why, at once."""
    parts = []
    if changed:
        parts.append(
            f"{len(changed)} generated file(s) changed since onboarding wrote them: {changed}"
        )
    if filled:
        parts.append(f"{len(filled)} file(s) of yours are no longer the stub: {filled}")
    return f"{'; '.join(parts)}. Nothing was removed. Move what you want to keep, then run again"


def _prune(root: Path, removed: Sequence[str]) -> None:
    """Remove the directories this onboarding created, deepest first, if they are empty.

    ⛔ Only empty ones, and never `root` itself: a directory that still holds
    something holds something this skill did not write.
    """
    candidates = sorted(
        {(root / where).parent for where in removed},
        key=lambda path: len(path.parts),
        reverse=True,
    )
    for path in candidates:
        while path != root and path.is_dir() and not any(path.iterdir()):
            path.rmdir()
            path = path.parent
