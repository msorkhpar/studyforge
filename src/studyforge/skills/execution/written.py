r"""The execution skill's own record: every file it wrote, and the digest it wrote there.

**What it does.** Keeps `.studyforge/execution/written.json`, one entry per
file `onboard.write` and `record` put on disk, and names, in a sentence a
person reads, each of those files whose bytes are no longer the ones written or
that is gone.

**How you use it.** `stamp(root, paths)` after every write, which `write`,
`record_runner` and `record_editor` already do; `hand_edited(root)` for the
report, which onboarding's own `hand_edited` includes, so ONE check answers for
both skills:

    from studyforge.skills.onboarding import hand_edited

    hand_edited(corpus_root)    # [] when nothing either skill generated was edited

**Depends on.** `archive.scrub` for R7's gate over what it reads back.
⛔ Nothing source-specific (R1), and nothing inside `skills.onboarding`: that
package reads this one, never the reverse.

## ⛔ WHY THE EXECUTION SKILL KEEPS A RECORD OF ITS OWN

⚠️ The execution skill's outputs are outside onboarding's install record, so
without a record of their own a wrong tag hand-written into `editor.env` would
leave onboarding's `hand_edited` at `[]`. R19 says a hand-edit to a generated
artifact is a finding. ⭐ So the skill that writes them records them, in the shape onboarding
records its own, and onboarding's check reads both records.

⛔ **Not added to onboarding's install record.** That record is rewritten by
every re-onboard and undone by `uninstall`, and neither of those is the
execution skill's to trigger. A record per writer keeps each one true.

## ⭐ A REGENERATE REWRITES NOTHING (R10)

Entries are sorted by path and carry no clock, so writing the same files again
writes the same record, byte for byte. ⭐ A stamp MERGES: `write` re-stamps its
files and leaves the two environment files' entries as the record step left
them, so a hand-edit to `editor.env` is still named after a regenerate that did
not re-run the record step.

⛔ **The record does not list itself**, for the reason onboarding's does not: a
file that had to hold its own digest could never be written.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable
from pathlib import Path, PurePosixPath

from studyforge.archive.scrub import assert_clean
from studyforge.version import check as check_version

#: Where the record lives. ⭐ Under the skill's own directory, so the glob the
#: skill already declares not-material covers it and no manifest changes.
RECORD = ".studyforge/execution/written.json"

#: The version of the record's own shape.
WRITTEN_API = 1

#: What a reader is told to do about a generated file that moved (R6).
REMEDY = (
    "A hand-edit to a generated file is a finding, not a fix: change corpus.json "
    "or the component's pin, then re-run the execution skill's write and record steps, "
    "which write it back"
)


class WrittenRefused(ValueError):
    """A record this build cannot read, and so cannot vouch for anything in it."""


def stamp(root: Path, paths: Iterable[str]) -> str:
    """Record the digest now on disk for each of `paths`, keep every other entry, and return where.

    ⭐ Called right after the files are written, so the digest is what the
    skill wrote. A path that is not a file is dropped rather than recorded.
    """
    listed = {entry["where"]: entry["sha256"] for entry in entries(root)}
    for where in paths:
        digest = _digest(root / where)
        if digest is not None and where != RECORD:
            listed[where] = digest
    document = {
        "written_api": WRITTEN_API,
        "files": [{"where": where, "sha256": listed[where]} for where in sorted(listed)],
    }
    target = root / RECORD
    target.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(document, indent=2) + "\n"
    if not target.is_file() or target.read_text(encoding="utf-8") != text:
        target.write_text(text, encoding="utf-8")
    return RECORD


def entries(root: Path) -> list[dict[str, str]]:
    """Read the record, gated (R7); an absent record lists nothing.

    ⛔ A record that is present and unreadable is REFUSED, never read as empty:
    an empty answer would say nothing was edited when nothing was checked.
    """
    record = root / RECORD
    if not record.exists():
        return []
    try:
        document = json.loads(record.read_text(encoding="utf-8"))
    except OSError, ValueError:
        raise WrittenRefused(
            f"{RECORD} is not readable JSON, so nothing the execution skill wrote can be "
            f"checked; re-run the execution skill's write and record steps"
        ) from None
    assert_clean(document, RECORD)
    if not isinstance(document, dict):
        document = {}
    check_version(
        "written_api",
        document.get("written_api"),
        (WRITTEN_API,),
        where=RECORD,
        error=WrittenRefused,
    )
    listed = document.get("files")
    if not isinstance(listed, list):
        raise WrittenRefused(f"{RECORD} lists no files, so nothing it records can be checked")
    return [
        {"where": entry["where"], "sha256": entry["sha256"]}
        for entry in listed
        if isinstance(entry, dict)
        and isinstance(entry.get("sha256"), str)
        and _inside(entry.get("where"))
    ]


def _inside(where: object) -> bool:
    """Whether a recorded path is a relative one that stays inside the corpus."""
    if not isinstance(where, str) or not where:
        return False
    path = PurePosixPath(where)
    return not path.is_absolute() and ".." not in path.parts


def hand_edited(root: Path | str) -> list[str]:
    """Say, one sentence per file, which of the skill's files were edited, then which are gone."""
    root = Path(root)
    listed = entries(root)
    edited = [
        f"{entry['where']} was edited by hand: {RECORD} holds the digest the execution "
        f"skill wrote there, and the bytes there now are not it. {REMEDY}"
        for entry in listed
        if (root / entry["where"]).is_file() and _digest(root / entry["where"]) != entry["sha256"]
    ]
    gone = [
        f"{entry['where']} is missing: {RECORD} records that the execution skill wrote it "
        f"there, and nothing is there now. {REMEDY}"
        for entry in listed
        if not (root / entry["where"]).is_file()
    ]
    return edited + gone


def _digest(path: Path) -> str | None:
    """Return the digest of a file's bytes, or `None` for one that is not a readable file."""
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return None
