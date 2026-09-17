r"""Where a corpus **finishes**, with the evidence, and what it will never use.

**What it does.** Turns *"this corpus is complete at the reading floor"* from
an assertion into a checkable statement: a terminal milestone, the
measurements that decided it, and a table naming **every** framework
capability the corpus will never use, with a reason for each.

**How you use it.**

    from studyforge.skills.delivery import Terminal, Unused

    Terminal(
        milestone="M4",
        evidence=("0 build files", "0 graders", "0 runnable units"),
        unused=(Unused("SF-22", "no exercise asks the reader to run anything"),),
    ).checked(index)

**Depends on.** `dataclasses` and this package's `capability`. ⛔ Not the
filesystem, and not any source.

## ⛔ Two plans look identical, and only one of them is right

⚠️ **A plan for a corpus genuinely complete without the execution track and a
plan whose author forgot the execution track existed are the same document.**
Nothing else in a backlog asks where the corpus **ends**.

⭐ **What separates them is the table**, and the table is only worth anything
if it is **complete**: every capability the index places after the terminal
milestone is accounted for, one line each, with the reason. ⛔ A partial table
is worse than none, because it looks like the check was done.

⚠️ **`checked` is therefore a coverage test against the index and not a subset
test.** Naming ten capabilities that exist proves nothing; the claim is about
the ones that were *not* named.

## ⛔ But the population is NOT everything the index places later (`W92`)

⚠️ **It was, and that is what forced a false statement.** A capability
delivered inside a component pinned somewhere else is not this corpus's to
explain away, and *"why this corpus never reaches it"* is a question with no
true answer — the corpus may be the very thing that delivers it. ⛔ A row the
documents say nothing about is worse: a `why` for one of those is a claim
nothing supports.

⭐ **So the table covers exactly the capabilities the index says this
framework delivers**, and the other two are RENDERED rather than explained:
named, counted, with the reading that placed them there. ⛔ Writing a `why`
for one of them is refused, which is how the false sentence stops being
writable rather than merely discouraged.

## ⭐ A corpus with no graders is complete, not short

⛔ §7's three states and C5: `none` is an answer. This statement is how a
corpus **says** so, and the reason it is the planner's output rather than a
reviewer's impression is that the reviewer has no way to enumerate what was
skipped and the index does.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

from studyforge.skills.delivery.capability import Index
from studyforge.skills.delivery.components import ELSEWHERE, HERE, UNDECLARED

#: The shortest reason that can carry information. ⛔ `Unused("SF-22", "n/a")`
#: is the failure this floor exists to catch: a table filled in to pass.
MIN_REASON_CHARS = 12

#: What the statement says about a capability delivered somewhere else, and
#: about one no document places at all. ⛔ Neither carries a `why`.
NOT_OURS = (
    "⭐ **{count} more are NOT this framework's to deliver**, so this corpus states "
    "nothing about them: they are delivered inside a component this workspace pins "
    "somewhere else."
)
NOT_SAID = (
    "⚠️ **{count} more declare no path in any document**, so nothing says which side "
    "delivers them. ⛔ A `why` here would be a claim the documents do not support "
    "(`W92`); the remedy is a component in the row's own `Owns` cell."
)


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
    """The corpus's last milestone, the evidence for it, and the surface forgone."""

    milestone: str
    evidence: tuple[str, ...]
    unused: tuple[Unused, ...]
    #: ⛔ DERIVED by `checked`, never declared: the ids after this milestone
    #: that the index does not place on this side. A planner who typed them
    #: would be retyping the index, which is R19's own defect.
    elsewhere: tuple[str, ...] = ()
    undeclared: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        """Refuse a terminal statement with no reading behind it."""
        if not self.milestone.strip():
            raise TerminalRefused("a terminal statement with no milestone states nothing")
        if not self.evidence:
            raise TerminalRefused(
                f"{self.milestone}: no evidence. ⛔ Where a corpus finishes is a "
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

    def checked(self, index: Index) -> Terminal:
        """Refuse unless every later capability of THIS side is accounted for, both ways.

        ⛔ **Coverage:** a capability the index places after `milestone` on
        this side, which this statement does not name, is the one the planner
        forgot, and it is named in the refusal rather than counted.

        ⛔ **Subset:** a capability named here that the index does not place
        after `milestone` is a statement about something this corpus *does*
        use — or about nothing at all — and either way the table has stopped
        describing the framework.

        ⛔ **Side** (`W92`): a capability the index does not place on this side
        is refused as a `why`, and comes back on the returned statement as a
        row that is rendered instead of explained.
        """
        sides = index.sides
        forgone = {item.id for item in index.after(self.milestone)}
        ours = {name for name in forgone if sides[name] == HERE}
        missed = sorted(ours - self.named)
        if missed:
            raise TerminalRefused(
                f"{self.milestone}: {len(missed)} capabilit"
                f"{'y is' if len(missed) == 1 else 'ies are'} unaccounted for — "
                f"{', '.join(missed)}"
            )
        theirs = sorted(self.named & (forgone - ours))
        if theirs:
            raise TerminalRefused(
                f"{len(theirs)} capabilit{'y is' if len(theirs) == 1 else 'ies are'} not "
                f"this framework's to deliver, so saying this corpus never reaches "
                f"{'it' if len(theirs) == 1 else 'them'} states nothing about this corpus "
                f"— {', '.join(theirs)}. ⭐ They are rendered by side instead (W92). "
                "⚠️ The ids come from the index and are safe to quote; the `why` is "
                "caller text and is not"
            )
        stray = sorted(self.named - forgone)
        if stray:
            raise TerminalRefused(
                f"{len(stray)} named capabilit"
                f"{'y is' if len(stray) == 1 else 'ies are'} not delivered after this "
                "milestone at all, so calling them unused says nothing about this "
                "corpus. ⛔ Their names are withheld: `unused` is caller text, and a "
                "refusal that quoted it would put an unvetted value in a log (R7)"
            )
        return replace(
            self,
            elsewhere=tuple(sorted(name for name in forgone if sides[name] == ELSEWHERE)),
            undeclared=tuple(sorted(name for name in forgone if sides[name] == UNDECLARED)),
        )

    def lines(self) -> list[str]:
        """Render the statement as it appears in the backlog document."""
        out = [
            f"## This corpus finishes at {self.milestone}",
            "",
            "⭐ **A corpus with no graders is complete here, not short.**",
            "",
            "**The evidence.**",
            *(f"  - {item.strip()}" for item in self.evidence),
            "",
            f"**The {len(self.unused)} framework capabilities it will never use.**",
            "",
            "| capability | why this corpus never reaches it |",
            "|---|---|",
            *(item.row() for item in self.unused),
        ]
        for template, named in ((NOT_OURS, self.elsewhere), (NOT_SAID, self.undeclared)):
            if not named:
                continue
            out += [
                "",
                template.format(count=len(named)),
                "",
                *(f"  - `{name}`" for name in named),
            ]
        return out
