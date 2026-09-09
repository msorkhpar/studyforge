"""The one exception this package raises.

**What it does.** Names every way an address cannot be turned into a location,
so a caller catches one type rather than four.

**How you use it.** Catch `PlacementError`.

**Depends on.** Nothing.

⚠️ **`ValueError`, following SF-01's split**: every failure here is "you handed
me something I cannot place" — an unknown profile name, an origin that escapes
the source root, a title that slugifies to nothing. ⛔ None of them is a
*document* error, because this package reads no files at all (that is SF-04).
"""

from __future__ import annotations


class PlacementError(ValueError):
    """An address, origin or profile this build cannot turn into a location.

    ⛔ The message names the value and, where a closed set was expected, what
    the accepted values are — and never formats an exception object into
    itself, which would carry an absolute path into a log (R7).
    """
