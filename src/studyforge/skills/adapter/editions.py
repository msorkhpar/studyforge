"""One practice in several languages: the edition id every language of one practice folder shares.

**What it does.** Answers the `edition` an adapter gives each language edition of one practice,
read off the folder of the adapter's own material the practice is written in, and the practice
document's fields as that edition (`render.page.editions` makes them one card).

**How you use it.** From `read.documents`, for each language of a practice:

    fields = as_edition(fields, folder="exercises/u2/practice-1", lang="kotlin", labels=["Kotlin"])

`skills.adapter.practices` re-exports all three. **Depends on.** `re` only.

⛔ **An id built from an ordinal differs by language**: each language is authored and numbered
as an exercise of its own, so such ids split one practice into a card per language. Here the
id is read off the folder alone, and no language, ordinal or count can enter it.
"""

from __future__ import annotations

import re
from collections.abc import Iterable


class EditionRefused(ValueError):
    """A folder no edition id can be read off. ⛔ Names no value (R7)."""


#: ⭐ What an edition id may hold: the archive's id shape (`archive.language`).
_NOT_ID = re.compile(r"[^a-z0-9]+")


def edition_id(folder: str) -> str:
    """Return the edition id of the practice written in `folder`, the same for every language.

    ⭐ `folder` is where the adapter's own material for the practice lives (corpus-relative),
    the folder that holds all its languages. The id is read off that folder alone, so no
    language, ordinal or count enters it. ⛔ A folder with no letter or digit is refused.
    """
    said = _NOT_ID.sub("-", str(folder).casefold()).strip("-")
    if not said:
        raise EditionRefused(
            "an edition id is read off the folder a practice is written in, and the folder "
            "given names no letter or digit"
        )
    return said


def untitled(title: str, labels: Iterable[str]) -> str:
    """Return `title` without a trailing parenthesis that names one of `labels`, in any case.

    ⭐ `Count by a key (Kotlin)` with labels `("kotlin", "Kotlin")` is `Count by a key`; a title
    naming no label, or nothing but the parenthesis, is returned as it came.
    """
    names = {str(one).strip().casefold() for one in labels if str(one).strip()}
    text = str(title).rstrip()
    if text.endswith(")") and " (" in text:
        cut = text.rindex(" (")
        if text[cut + 2 : -1].strip().casefold() in names and text[:cut].strip():
            return text[:cut].rstrip()
    return title


def as_edition(fields: dict, *, folder: str, lang: str, labels: Iterable[str] = ()) -> dict:
    """Return a practice document's fields as the `lang` edition of the practice in `folder`.

    ⭐ Sets `lang`, sets `edition` to `edition_id(folder)`, and drops a trailing language
    name from `title` (the language's id and each of `labels`), so the card and the panel
    carry one title and the switch names the language. ⛔ `fields` is not changed in place.
    """
    title = untitled(str(fields.get("title", "")), (lang, *labels))
    return {**fields, "lang": lang, "edition": edition_id(folder), "title": title}
