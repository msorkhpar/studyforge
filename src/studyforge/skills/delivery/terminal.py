r"""Where a corpus **finishes**, with the evidence, and what it will never use.

**What it does.** Turns *"this corpus is complete at the reading floor"* from
an assertion into a checkable statement: where the corpus finishes, the
measurements that decided it, and a table naming **every** capability the
installed framework offers that this corpus will never use, with a reason for
each.

**How you use it.**

    from studyforge.skills.delivery import Terminal, Unused

    Terminal(
        finishes="the reading floor",
        evidence=("0 build files", "0 graders", "0 runnable units"),
        unused=(Unused("studyforge check", "no unit asks the reader to run anything"),),
    ).checked(offer, used=frozenset({"studyforge validate", "studyforge build"}))

**Depends on.** `dataclasses` and this package's `offer` and `refusal`.
⛔ Not the filesystem, and not any source.

## ⛔ Two plans look identical, and only one of them is right

⚠️ **A plan for a corpus genuinely complete without the execution track and a
plan whose author forgot the execution track existed are the same document.**
Nothing else in a backlog asks where the corpus **ends**.

⭐ **What separates them is the table**, and the table is only worth anything
if it is **complete**: every capability the installed framework offers is
either reached by a task of the plan or named here, one line each, with the
reason. ⛔ A partial table is worse than none, because it looks like the check
was done.

⚠️ **`checked` is therefore a coverage test against the offer and not a subset
test.** Naming ten capabilities that exist proves nothing; the claim is about
the ones that were *not* named.

## ⛔ `used` is the plan's, never the planner's memory

What the plan uses is every offered capability a task's `depends_on` names,
and `Backlog.checked` derives it and hands it here. ⛔ A capability both used
by a task and named as never used is a table that has stopped describing the
plan, and it is refused.

## ⭐ A corpus with no graders is complete, not short

⛔ §7's three states and C5: `none` is an answer. This statement is how a
corpus **says** so, and the reason it is the planner's output rather than a
reviewer's impression is that the reviewer has no way to enumerate what was
skipped and the offer does.
"""

from __future__ import annotations

from dataclasses import dataclass

from studyforge.skills.delivery.offer import Offer
from studyforge.skills.delivery.refusal import one_or_all

#: The shortest reason that can carry information. ⛔ `Unused("x", "n/a")` is
#: the failure this floor exists to catch: a table filled in to pass.
MIN_REASON_CHARS = 12


class TerminalRefused(Exception):
    """Raised when a terminal statement cannot be believed, with what is missing."""


@dataclass(frozen=True, slots=True)
class Unused:
    """One capability this corpus will never use, and why."""

    capability: str
    why: str

    def __post_init__(self) -> None:
        """Refuse a row filled in to pass rather than to inform."""
        if not self.capability.strip():
            raise TerminalRefused("an unused capability with no name names nothing")
        if len(self.why.strip()) < MIN_REASON_CHARS:
            raise TerminalRefused(
                f"an unused capability's `why` is under {MIN_REASON_CHARS} characters, "
                "so it is not a reason. ⛔ A table filled in to pass is worse than none"
            )

    def row(self) -> str:
        """Render as one row of the never-used table."""
        return f"| `{self.capability}` | {self.why.strip()} |"


@dataclass(frozen=True, slots=True)
class Terminal:
    """Where the corpus finishes, the evidence for it, and the offer it forgoes."""

    finishes: str
    evidence: tuple[str, ...]
    unused: tuple[Unused, ...]

    def __post_init__(self) -> None:
        """Refuse a terminal statement with no reading behind it."""
        if not self.finishes.strip():
            raise TerminalRefused("a terminal statement that says nowhere states nothing")
        if not self.evidence:
            raise TerminalRefused(
                "a terminal statement with no evidence. ⛔ Where a corpus finishes is a "
                "measurement, and one with no reading behind it is a preference"
            )
        named = [item.capability for item in self.unused]
        duplicated = {name for name in named if named.count(name) > 1}
        if duplicated:
            raise TerminalRefused(
                f"{len(duplicated)} capabilit"
                f"{'y is' if len(duplicated) == 1 else 'ies are'} named twice in `unused`"
            )

    @property
    def named(self) -> frozenset[str]:
        """The capabilities this statement accounts for."""
        return frozenset(item.capability for item in self.unused)

    def checked(self, offer: Offer, *, used: frozenset[str]) -> Terminal:
        """Refuse unless every offered capability the plan does not use is accounted for.

        ⛔ **Coverage:** an offered capability that no task uses and this
        statement does not name is the one the planner forgot, and it is named
        in the refusal rather than counted. Its id comes from the offer, so it
        is safe to quote.

        ⛔ **Subset:** a capability named here that the plan uses, or that the
        framework does not offer, says nothing about what this corpus forgoes.
        ⚠️ Those names are withheld: `unused` is caller text, and a refusal that
        quoted it would put an unvetted value in a log.

        ⭐ **Every reason is named at once**, so a planner fixes the whole
        table in one pass.
        """
        forgone = offer.ids - used
        refusals: list[str] = []
        missed = sorted(forgone - self.named)
        if missed:
            refusals.append(
                f"{len(missed)} offered capabilit"
                f"{'y is' if len(missed) == 1 else 'ies are'} neither used by a task nor "
                f"accounted for — {', '.join(missed)}"
            )
        both = self.named & used
        if both:
            refusals.append(
                f"{len(both)} named capabilit{'y is' if len(both) == 1 else 'ies are'} "
                "used by a task of this plan, so calling them unused contradicts the plan"
            )
        stray = self.named - offer.ids
        if stray:
            refusals.append(
                f"{len(stray)} named capabilit{'y is' if len(stray) == 1 else 'ies are'} "
                "not offered by the installed framework, so calling them unused says "
                "nothing about this corpus"
            )
        if refusals:
            raise TerminalRefused(one_or_all(refusals))
        return self

    def lines(self) -> list[str]:
        """Render the statement as it appears in the backlog document."""
        return [
            f"## This corpus finishes at {self.finishes.strip()}",
            "",
            "⭐ **A corpus with no graders is complete here, not short.**",
            "",
            "**The evidence.**",
            *(f"  - {item.strip()}" for item in self.evidence),
            "",
            f"**The {len(self.unused)} framework capabilities it will never use.**",
            "",
            "| capability | why this corpus never uses it |",
            "|---|---|",
            *(item.row() for item in self.unused),
        ]
