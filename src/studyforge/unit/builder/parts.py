r"""One served section, and the two fields on it that are never an author's.

**What it does.** Builds a section record in key order, deriving the `video` and
the `workspace` from the archive rather than accepting them from anywhere.

**How you use it.** `section(key=..., kind=..., heading=..., document=...)`.

**Depends on.** `archive.document` for what a video record is, `exercise` for
what a workspace is.

## ⛔ Both derived fields are refused in an authored overlay, and this is why

⚠️ `unit.content.DERIVED_FIELDS` names them and refuses them there; this is
where they come from instead.

- **`workspace`** — the backend runs those commands, so the only hand that may
  write them is the one that also wrote the file they address.
- **`video`** — the archive is the only record of what was downloaded and where
  it was filed, and it is *carried* byte for byte rather than re-derived.

## ⭐ `video` is always written, `null` when there is none

⛔ **A key that disappears when it is empty cannot be told from one nobody
wrote**, and the two answers are different: *the archive had no video* and
*this build could not see it* must not render the same. ⚠️ The same argument
`unit.trust` makes for a defaulted `trust`, one document along.
"""

from __future__ import annotations

from studyforge.archive.document import VIDEO_KEYS
from studyforge.exercise import of as exercise_of
from studyforge.exercise import to_document as exercise_document

#: A served section's keys, in the order they are written (R10).
SECTION_KEYS = ("key", "kind", "heading", "blocks", "video", "workspace")


def section(*, key: str, kind: str, heading: str, blocks: list, document: dict) -> dict:
    """One served section: somebody's heading and blocks, and the archive's two fields.

    ⚠️ **`blocks` is passed in rather than read from `document`**, and the
    distinction is the two shapes: a derived section's blocks *are* the
    archive's, and an authored section's are the **author's**. ⛔ The only
    things this build adds either way are `video` and `workspace`, which is the
    exact promise `unit.content.DERIVED_FIELDS` makes from the other side.
    """
    return {
        "key": key,
        "kind": kind,
        "heading": heading,
        "blocks": list(blocks or []),
        "video": video_of(document),
        "workspace": workspace_of(document, key),
    }


def video_of(document: dict) -> dict | None:
    """Carry the archive's own video record through — ⛔ never re-derive it."""
    record = document.get("video")
    if record is None:
        return None
    return {name: record.get(name) for name in VIDEO_KEYS if name in record}


def workspace_of(document: dict, where: str) -> dict | None:
    """Return the exercise record a practice carries, or `None` for anything else.

    ⚠️ Read through `exercise.of`, which owns R5's rule by way of `unit.trust`.
    ⛔ No provenance or trust logic is spelled here; a second spelling of that
    rule is the defect this package refuses.
    """
    exercise = exercise_of(document, where)
    return None if exercise is None else exercise_document(exercise)
