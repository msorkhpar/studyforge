"""Which toolchain image profile a corpus's runner and editor are built on — the `profile` key.

**What it does.** Models `corpus.json`'s optional `profile` key: the name of an image profile the
toolchain carries, layered on the base of the corpus's declared runtimes, that the export builds
the course's runner and editor layers on instead of the plain bases.

**How you use it.** `parse_profile(document, where)` returns the name, or `None` for an absent key,
which is every corpus before the key existed.

**Depends on.** `errors` and `describe`. ⛔ Nothing source-specific (R1): the name is the corpus's
own declaration, and whether the toolchain has a profile of that name is the toolchain's answer,
asked when a course is exported. ⭐ The key needs `runtimes`, because a profile is built on their
base, and it is gated at `corpus_api` 8 by `document.KEY_VERSIONS`, with no bump.
"""

from __future__ import annotations

import re

from studyforge.corpus.manifest.errors import ManifestError
from studyforge.describe import describe

#: What a profile's name may be: lower-case words joined by single hyphens, as the toolchain names
#: its profiles. ⛔ Only the shape is read here.
PROFILE_NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def parse_profile(document: dict, where: str) -> str | None:
    """Return the declared image profile, or `None`; it needs runtimes, built on their base."""
    if "profile" not in document:
        return None
    value = document["profile"]
    if not isinstance(value, str) or not PROFILE_NAME.match(value):
        raise ManifestError(
            f"{where} 'profile' must be a profile name of lower-case words joined by "
            f"hyphens, got {describe(value)}"
        )
    if not document.get("runtimes"):
        raise ManifestError(
            f"{where} declares a 'profile' and no 'runtimes'; a profile is built on the "
            "base of the runtimes a corpus declares"
        )
    return value
