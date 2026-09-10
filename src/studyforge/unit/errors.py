"""The one exception the unit package raises for an authored overlay.

**What it does.** Names every way a `content.json` can be unacceptable, so a
caller catches one type rather than five.

**How you use it.** Catch `ContentError`; `describe(value)` when a refusal
needs to say what arrived without reproducing it.

**Depends on.** `studyforge.describe`, and nothing else.

⭐ **`describe` is re-exported, not re-implemented** (Ruling 10). This module
wrote the third copy of "name the type, not the value", and the three had
already drifted about integers. The rule now has one home at
`studyforge.describe`; the name stays importable from here because that is
where this package's callers already reach for it, and because a re-export
cannot disagree with what it re-exports.

⚠️ **`ValueError`, following SF-01's split and `corpus.manifest`'s reading of
it:** an overlay is a *value read from a document*, so both halves fail the
same way and one base is enough.

⛔ **Loud and specific, because this is the only file in the whole contract a
person edits by hand.** A typo must name itself rather than produce a page that
is quietly wrong — and the failures that matter each write a *plausible* page if
they are not caught: a unit filed under the wrong address, a section keyed on a
variant the corpus does not have, and a unit with no blocks at all.
"""

from __future__ import annotations

from studyforge.describe import SAFE_TO_QUOTE, describe

__all__ = ["SAFE_TO_QUOTE", "ContentError", "describe"]


class ContentError(ValueError):
    """An authored overlay this build will not accept.

    ⛔ The message names the file, the section index and the field — and never
    the offending *value* where that value is a path (R7), nor an exception
    object, which formats itself with an absolute path.
    """
