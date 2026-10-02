"""The optional language an archive document may carry.

**What it does.** Says what a document's `lang` may be, once: an id, spelled as
a manifest spells the ids of the languages it declares. A lesson, a practice
and a quiz (a practice whose grader is a quiz) are all documents, so one key
tags them all.

**How you use it.** `require_lang(value, where)` returns the id or raises
`ArchiveError`; `archive.document` calls it on the way in (`build`) and on the
way out (`parse`).

**Depends on.** `archive.errors` and `describe`.

⛔ **Whether the id is a language the corpus declares is not asked here.** The
archive does not read the manifest; `validate.languages` reads both and names
a language the corpus does not declare. ⛔ **It names no language** (R1): an
id is data, and no line here branches on one.

⭐ **Absent means common to every reading.** A document without the key is
exactly what it was before the key existed, and it re-renders to the same
bytes: the key is written only when it has something to say, after the others.
⚠️ The id pattern is the manifest's, spelled again because the manifest reads
this package and this package may not read it back.
"""

from __future__ import annotations

import re

from studyforge.archive.errors import ArchiveError
from studyforge.describe import describe

#: An id: lowercase, starts with a letter or digit, then letters, digits, `-`, `_`.
LANG_ID = re.compile(r"[a-z0-9][a-z0-9_-]*")


def require_lang(value: object, where: str) -> str:
    """Return `value` when it is a language id, or raise saying so.

    ⛔ A value that is not id-shaped is never quoted: a field of a document an
    adapter wrote is where a leak would arrive (R7), so its type is named.
    """
    if not isinstance(value, str) or LANG_ID.fullmatch(value) is None:
        raise ArchiveError(
            f"{where} has an invalid 'lang', got {describe(value)}; it is an id of "
            f"lowercase letters, digits, '-' and '_'"
        )
    return value
