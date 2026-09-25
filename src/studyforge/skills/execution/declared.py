r"""Whether the corpus's manifest declares what this skill writes, before it writes.

**What it does.** `undeclared(root, paths)` names each path this skill would
write that the corpus's own `corpus.json` does not classify as not material;
`refuse_undeclared` refuses a write over them.

**How you use it.** `onboard.write` asks before its first byte.

**Depends on.** `corpus.manifest` for the manifest and its classification.
⛔ Nothing source-specific (R1). ⭐ Every path is asked, the ones under
`.studyforge/` too: onboarding declares that directory for every corpus, so
asking costs nothing and a manifest that dropped it is caught.

## ⛔ A FIRST WRITE LEAVES `validate` CLEAN, OR DOES NOT HAPPEN

⚠️ **Measured on a runnable corpus:** the first write put `EXECUTION.md` at the
root, the manifest declared nothing for it, and `validate` read RED at once.
⭐ **Onboarding declares these globs for a corpus that declares `runtimes`**
(`skills.onboarding.onboard`), because onboarding owns
`corpus.json` and records its digest: a second writer would read as a
hand-edit. ⛔ So a manifest written before that is refused here, by name, with
the remedy — re-run onboarding — rather than left for `validate` to find.
⭐ A corpus with no `corpus.json` on disk is not refused: there is nothing yet
for `validate` to read.
"""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from studyforge.corpus.manifest import MANIFEST_FILENAME, Classification, parse
from studyforge.skills.execution.binds import ExecutionRefused


def undeclared(root: Path, paths: Iterable[str]) -> tuple[str, ...]:
    """Each path that `corpus.json` does not declare not material, sorted."""
    manifest_file = root / MANIFEST_FILENAME
    if not manifest_file.is_file():
        return ()
    content = parse(manifest_file.read_text(encoding="utf-8")).content
    kept = Classification.NOT_MATERIAL
    found = {where for where in paths if content.classify(where) is not kept}
    return tuple(sorted(found))


def refuse_undeclared(root: Path, paths: Iterable[str]) -> None:
    """Refuse, naming each path and the remedy, a write `validate` would then read RED."""
    missing = undeclared(root, paths)
    if missing:
        raise ExecutionRefused(
            f"{MANIFEST_FILENAME} does not declare {', '.join(missing)} not material, so "
            "writing it would leave `studyforge validate` RED. Re-run onboarding, which "
            "declares this skill's files for a corpus that declares runtimes, then write again"
        )
