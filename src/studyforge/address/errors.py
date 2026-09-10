"""The one exception this package raises.

**What it does.** Names every way an address, a slug, an identifier or a unit
ordinal can be wrong, so a caller catches one type rather than four.

**How you use it.** Catch `AddressError`. Every public function in this package
raises it and nothing else; none of them returns a sentinel, returns `None` for
bad input, or repairs a value quietly (R6).

**Depends on.** Nothing.

⛔ **Read the class docstring before writing a message that formats a value.**
It carries the one rule this package's refusals have already got wrong once.

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

    ⛔ **The message never reproduces the offending value, and never says only
    "invalid" either.** Both halves are required and this sentence used to
    mandate the first of them: it said the message *"names the offending value
    with `!r`"*, which is how every address segment, identity field and unit
    ordinal in the framework came to inherit an R7 echo (Ruling 14, W1).

    ⚠️ **Fixing the code and leaving this sentence would have been worse than
    fixing neither.** The next author to touch `slug.py` would have read the
    module's own documented policy and put the echo back, correctly by the
    rules as written. ⭐ A commit that tightens a rule brings the whole tree
    into compliance in the same commit — and the tree includes the sentence
    that authorised the defect.

    ⭐ **What a refusal owes the reader instead** (R6, and it is more
    actionable than the value was): the **field** that was wrong — `what` —
    the **class** that was expected, and for a string the **position** at
    which it failed. `slug.slug_fault` and `studyforge.describe` are how this
    package says those things.
    """
