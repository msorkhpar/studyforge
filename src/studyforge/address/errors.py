"""The one exception this package raises.

**What it does.** Names every way an address, a slug, an identifier or a unit
ordinal can be wrong, so a caller catches one type rather than four.

**How you use it.** Catch `AddressError`. Every public function in this package
raises it and nothing else; none of them returns a sentinel, returns `None` for
bad input, or repairs a value quietly (R6).

**Depends on.** Nothing.

⚠️ **It subclasses `ValueError`, and that is a deliberate divergence from the
extraction source**, whose `LayoutError` and `RawDocError` subclass `Exception`
directly. Every failure here is one shape — *a caller passed a value this
package cannot accept* — which is what `ValueError` means, so code that already
handles bad input handles these too without importing anything from the
framework.

⚠️ That reasoning does **not** generalise to a document reader. "This file is
not an archive I can read" is not a bad argument; it is a bad file, and
`Exception` is right for it. Two different failure kinds, two different bases —
see `docs/tasks/handoffs/SF-01.md`, which proposes this split as a precedent
rather than assuming it.
"""

from __future__ import annotations


class AddressError(ValueError):
    """A value this package cannot accept as a slug, address or ordinal.

    ⛔ The message names the offending value with `!r` and says what was
    expected. It never says only "invalid": an address model that reports a
    problem without naming the string is one whose failures cost more to
    diagnose than to fix (R6).
    """
