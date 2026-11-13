r"""Whether a bare dotted number is a release, read from the word right before it.

**What it does.** Says whether the text in front of a bare number ends in a
word that names a version, so `unit.mentions` leaves `PuLP 3.3.2` a number
even when `3.3.2` is also a unit's label.

**How you use it.** `follows_version_word(before)`, with `before` the text up
to the number.

**Depends on.** `re` only.

## ⛔ Narrow on purpose

⭐ **The word names a version when it is `version` or `v`, in any case, or a
product's name spelled with a capital after its first letter** (`PuLP`,
`HiGHS`, `CUDA`, `OR-Tools`, `OpenAPI`). It must touch the number across
spaces alone, so `lesson 6.2.1`, `as 6.2.1 showed`, `(6.2.1)`, `PuLP, 6.2.1`
and a list of labels still name their units.

⚠️ **A name with one capital (`Gurobi 13.0.0`) or none (`highspy 1.14.0`) is
not read as one**: `Lesson 6.2.1`, `See 6.2.1` and `from 6.2.1` look the same.
A corpus writes such a version in a code span, where nothing is rewritten.

⚠️ A dot inside the word is kept (`ASP.NET`); a dot that ends it is a
sentence's stop, and ends the name with it.
"""

from __future__ import annotations

import re

#: The word that ends right before a bare number, across spaces alone.
_BEFORE = re.compile(r"(?<![\w.-])(?P<word>[A-Za-z](?:[\w+-]|\.(?=\w))*)[ \t ]+\Z")

#: The words that name a version on their own, in any case.
VERSION_WORDS = frozenset({"version", "v"})

#: How much of the text before a number is read. ⚠️ A word is short, and a
#: unit's prose can be long.
_TAIL = 64


def follows_version_word(before: str) -> bool:
    """Whether `before` ends in a word that names a version, then spaces alone."""
    found = _BEFORE.search(before[-_TAIL:])
    if found is None:
        return False
    word = found.group("word")
    return word.lower() in VERSION_WORDS or any(letter.isupper() for letter in word[1:])
