r"""What every earlier course learned — ⛔ read before a course is built, added to after.

**What it does.** Locates the integration catalogue this installation ships
(`SKILL.md` beside this module) and names the exact text read with a short
digest, so a findings log can record *which* catalogue its run started from.

**How you use it.**

    python3 -m studyforge.skills.catalogue          # the catalogue, then the line to record

    from studyforge.skills.catalogue import digest, read_line
    read_line()      # 'Read first: the integration catalogue at 3f2a…' (64 hex)

**Depends on.** `hashlib` and `pathlib`. ⛔ Not `importlib`: the directory is
`Path(__file__).parent`, the rule `studyforge.skills.documents` keeps.

## ⛔ Why the read is recorded, and why a digest

⚠️ Two courses were built and published with this catalogue in the framework
repository, and neither read it, because nothing a course runs pointed at it
and an installed `studyforge` did not carry it. ⭐ It now ships as a skill
document, and the findings log a run writes carries the line `read_line()`
returns: the catalogue the run started from, by content. ⛔ A log without it is
refused by `closing`, so a run cannot close without having said what it read.

⭐ A digest, not a version: the catalogue changes between releases of the
framework only by entries added, and the digest names the exact text, so the
sort at the end of the run can see which entries arrived after it started.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

#: ⭐ The catalogue itself: the skill document this sub-package ships.
DOCUMENT = Path(__file__).parent / "SKILL.md"

#: How a findings log records the catalogue its run read, before the digest.
READ_PREFIX = "Read first: the integration catalogue at "

#: The digest's length in hex: the whole SHA-256. ⛔ Never cut short here: one module
#: in the framework shortens a digest, into a clip's name, and this is not it.
DIGEST_HEX = 64


def text() -> str:
    """The catalogue this installation ships."""
    return DOCUMENT.read_text("utf-8")


def digest(catalogue: str | None = None) -> str:
    """The SHA-256 of the catalogue's text, in hex."""
    body = text() if catalogue is None else catalogue
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def read_line(catalogue: str | None = None) -> str:
    """The line a findings log carries to say which catalogue its run read first."""
    return READ_PREFIX + digest(catalogue)


__all__ = ["DIGEST_HEX", "DOCUMENT", "READ_PREFIX", "digest", "read_line", "text"]
