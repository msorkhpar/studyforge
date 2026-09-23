r"""The install record: what one onboarding wrote, and which of it is a person's.

**What it does.** Renders `.studyforge/installed.json` from a file set, reads
one back through the personal-data gate, names every generated file whose
bytes no longer match what was written there, and refuses a regenerate that
would take a file it does not claim (`W353`).

**How you use it.**

    from studyforge.skills.onboarding import hand_edited

    hand_edited(corpus_root)    # [] when nothing generated was hand-edited

**Depends on.** `archive.scrub` for the gate, `skills.adapter.Written` for the
file set, and `pin` for where the record lives. ⛔ Nothing source-specific
(R1): which file is a person's is the scaffold's own `generated` flag, never a
name this module knows.

## ⛔ The one hand-written module is MARKED, and carries no digest (INT-09/1)

⚠️ **Measured at a corpus:** the record filed the adapter's reading step under
its stub's digest, and a regenerate re-recorded that digest. So the one
legitimate edit in a corpus read exactly like a hand-edit to a generated file,
and R19's *"a hand-edit to a generated artifact is a finding"* could not be
checked by anybody. ⭐ **The entry is now `{"where": …, "hand_written": true}`**:
a regenerate writes the same entry, which records nothing about the file's
bytes, and `hand_edited` never names it.

⚠️ **`installed_api` moved to `2` for that reason.** A build that reads `1`
expects a digest on every entry and would fail on the marked one rather than
refuse it by name. ⭐ This build still reads `1`: every entry there has a
digest, so reading it is not a migration.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Sequence
from pathlib import Path

from studyforge.archive.scrub import assert_clean
from studyforge.skills.adapter import Written
from studyforge.skills.onboarding.pin import RECORD_FILE

#: The version of the install record's own shape.
INSTALLED_API = 2

#: Every shape this build reads. ⭐ `1` put a digest on every entry, the
#: person's included, so it is read as it stands.
READS = (1, INSTALLED_API)

#: The key that marks the person's module. ⭐ The same word `Scaffold` uses.
HAND_WRITTEN = "hand_written"


class OnboardingRefused(ValueError):
    """An onboarding that will not be written or undone, and every reason at once.

    ⛔ Paths are root-relative, never absolute (R7): the first thing an
    integrator does with a refusal is paste it somewhere.
    """


def render(files: Sequence[Written]) -> str:
    """Return what uninstall undoes: every path, and the digest written there.

    ⛔ **The person's module is marked and carries no digest**, because what is
    in it is theirs and a regenerate must not re-record it. Which file that is
    comes from `Written.generated`, the scaffold's own declaration.

    ⚠️ The record does not list itself — it is removed last, unconditionally,
    because a record that had to verify its own digest could never be written.
    """
    return (
        json.dumps(
            {"installed_api": INSTALLED_API, "files": [_entry(item) for item in files]},
            indent=2,
        )
        + "\n"
    )


def is_yours(entry: dict) -> bool:
    """Whether a record entry is the person's module. ⛔ Only a literal `true` marks one."""
    return entry.get(HAND_WRITTEN) is True


def entries(root: Path) -> list[dict]:
    """Read the install record, gating it and refusing a shape this build does not speak.

    ⛔ **The personal-data gate runs over the whole decoded document** (R7, W7),
    before any field is read — the rule `corpus.json` was missing until W7, and
    this document is a *list of paths*, which is the shape a home directory
    arrives in. ⚠️ It is the one document this skill reads back rather than
    writes, so it is the only place the gate can be owed.
    """
    record = root / RECORD_FILE
    if not record.exists():
        raise OnboardingRefused(
            f"{RECORD_FILE} is not here, so there is no record of what onboarding wrote; "
            f"an uninstall that guessed would be deleting somebody's repository"
        )
    try:
        document = json.loads(record.read_text(encoding="utf-8"))
    except OSError, ValueError:
        raise OnboardingRefused(
            f"{RECORD_FILE} is not readable JSON, so nothing is removed"
        ) from None
    assert_clean(document, RECORD_FILE)
    if not isinstance(document, dict) or document.get("installed_api") not in READS:
        raise OnboardingRefused(
            f"{RECORD_FILE} declares an install record this build does not read; "
            f"this build writes installed_api {INSTALLED_API}"
        )
    listed = document.get("files")
    if not isinstance(listed, list):
        raise OnboardingRefused(f"{RECORD_FILE} lists no files, so there is nothing to remove")
    return [entry for entry in listed if isinstance(entry, dict) and "where" in entry]


def changed(root: Path, listed: Sequence[dict]) -> list[str]:
    """Every generated file on disk whose digest is not the one recorded, sorted.

    ⚠️ An absent file has no bytes to differ, so it is not named here. ⛔ A
    generated entry with no digest is named: nothing proves it was left alone.
    """
    return sorted(
        entry["where"]
        for entry in listed
        if not is_yours(entry)
        and (root / entry["where"]).exists()
        and _digest_of(root / entry["where"]) != entry.get("sha256")
    )


def hand_edited(root: Path | str) -> list[str]:
    """Name every generated file whose bytes differ from the record. Never the person's.

    ⭐ **R19, made checkable:** an empty list means nothing generated was edited
    by hand, whatever the person wrote in their own module.
    """
    root = Path(root)
    return changed(root, entries(root))


def refuse_unrecorded(root: Path, files: Sequence[Written]) -> None:
    """Refuse, by name, a regenerate that would overwrite a file the record does not claim.

    ⛔ **`W353`, generalising `W345`'s ignore-file guard to every generated
    path.** A regenerate gives an already-onboarded corpus whatever files a
    later framework added. A file already at one of those paths that the
    install record does not list as generated is not known to be the
    framework's, and rewriting it would be the edit R3 forbids — which the
    generated check could not then see, because the record would claim it
    from that write on.

    ⚠️ **A record that predates a path is refused, never adopted** (`W353`
    clause 2). The record lists every path its run wrote, so a path it does
    not list was put there by something else; adopting it would overwrite
    that file and record it in one silent step. ⭐ Moving one file aside is
    the whole cost of refusing. ⛔ No record at all claims nothing.

    ⭐ Not refused: the person's module (`write_files` never rewrites an
    existing one), the record itself (it never lists itself), and an absent
    path (there is nothing to lose).
    """
    present = (root / RECORD_FILE).exists()
    listed = entries(root) if present else []
    claimed = {entry["where"] for entry in listed if not is_yours(entry)}
    theirs = sorted(
        item.where
        for item in files
        if item.generated
        and item.where != RECORD_FILE
        and item.where not in claimed
        and (root / item.where).exists()
    )
    if theirs:
        raise OnboardingRefused(
            f"{len(theirs)} file(s) this regenerate would write are already here and "
            f"{RECORD_FILE} {'does not list them as generated' if present else 'is not here'}, "
            f"so they are not known to be the framework's: {theirs}. Nothing was written "
            f"(R3); move each aside, regenerate, then keep what was yours outside the "
            f"generated paths"
        )


def _digest(text: str) -> str:
    """Return the digest of what was written, so a hand-edit is visible rather than assumed."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _digest_of(path: Path) -> str:
    """Return the digest of what is on disk now."""
    return _digest(path.read_text(encoding="utf-8"))


def _entry(item: Written) -> dict:
    """One record entry: a digest for a generated file, a mark for the person's."""
    if not item.generated:
        return {"where": item.where, HAND_WRITTEN: True}
    return {"where": item.where, "sha256": _digest(item.text)}


def collision(blocked: Sequence[str]) -> str:
    """Name every path in the way at once, and say which flag would move it.

    ⚠️ An integrator told about one existing file, who moves it, runs again and
    is told about the next has been given a guessing game — `validate`'s rule,
    for `validate`'s reason. Only a first write collides.
    """
    return (
        f"{len(blocked)} path(s) already exist and generation is non-destructive "
        f"(R3): {sorted(blocked)}. Nothing was written; pass regenerate=True to "
        "rewrite the generated ones and keep the one that is yours"
    )
