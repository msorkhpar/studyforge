r"""The one form every refusal in this package takes when it found more than one thing.

**What it does.** Renders a gathered list of reasons as a single refusal
message: one reason reads as that reason alone, and
several are **all** named.

**How you use it.**

    from studyforge.skills.delivery.refusal import one_or_all

    if refusals:
        raise PlanRefused(one_or_all(refusals))

**Depends on.** `collections.abc`. ⛔ Nothing else — it takes strings the
caller has already made safe to quote and gives one back.

## ⛔ A refusal names its whole population, never its first witness

⚠️ **R6.** A gate that stops at the first thing it finds makes the
number of runs it takes to fix the input **unknowable**: the reader fixes
what was named, re-runs, and is told about the next one. ⭐ Each round is a
full run, so the cost is paid in wall-clock time by somebody who cannot size
the work before starting it.

⛔ **So the loop gathers and the refusal is raised once, after it** — and the
gathering is what the caller writes; this module is only the sentence that
comes out the other end.

## ⭐ One reason reads as itself, and that is deliberate

⚠️ **A count and a preamble over a single reason add nothing a reader needs**
and would make every one-reason refusal read differently from its reason. ⛔ So the
singular case is the identity: `one_or_all(("x",)) == "x"`.

⚠️ **This module adds no vocabulary of its own to a reason.** A reason arrives
already written by the check that found it, and R7 binds it there: a path or a
value that the message did not already carry does not enter one here.
"""

from __future__ import annotations

from collections.abc import Sequence

#: What separates one gathered reason from the next. ⛔ A semicolon rather
#: than a newline: these messages are read out of exception text in a shell,
#: a log line and a test's assertion message, and only one of the three keeps
#: a newline readable.
SEPARATOR = "; "

#: The preamble the plural form opens with, and it leads with the COUNT so a
#: reader knows how much work there is before reading any of it — which is the
#: whole cost a first-witness refusal hides (R6).
PREAMBLE = "{count} refusals, and every one of them is named"


def one_or_all(reasons: Sequence[str]) -> str:
    """Render `reasons` as one refusal message that hides none of them.

    ⛔ Refuses an empty sequence rather than rendering `0 refusals`: a caller
    that reached here with nothing to say was about to raise a refusal over an
    empty population: zero over nothing prints exactly like zero over everything.
    """
    if not reasons:
        raise ValueError("a refusal over no reasons refuses nothing")
    if len(reasons) == 1:
        return reasons[0]
    return f"{PREAMBLE.format(count=len(reasons))} — {SEPARATOR.join(reasons)}"
