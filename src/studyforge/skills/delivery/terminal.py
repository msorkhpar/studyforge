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

## ⭐ A corpus with no graders is complete, not short

⛔ §7's three states and C5: `none` is an answer. This statement is how a
corpus **says** so, and the reason it is the planner's output rather than a
reviewer's impression is that the reviewer has no way to enumerate what was
skipped and the index does.
"""

from __future__ import annotations

from dataclasses import dataclass

from studyforge.skills.delivery.capability import Index

#: The shortest reason that can carry information. ⛔ `Unused("SF-22", "n/a")`
#: is the failure this floor exists to catch: a table filled in to pass.
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
    """The corpus's last milestone, the evidence for it, and the surface forgone."""

    milestone: str
    evidence: tuple[str, ...]
    unused: tuple[Unused, ...]

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
        """Refuse unless every later capability is accounted for, both ways.

        ⛔ **Coverage:** a capability the index places after `milestone` and
        this statement does not name is the one the planner forgot, and it is
        named in the refusal rather than counted.

        ⛔ **Subset:** a capability named here that the index does not place
        after `milestone` is a statement about something this corpus *does*
        use — or about nothing at all — and either way the table has stopped
        describing the framework.
        """
        forgone = {item.id for item in index.after(self.milestone)}
        missed = sorted(forgone - self.named)
        if missed:
            raise TerminalRefused(
                f"{self.milestone}: {len(missed)} capabilit"
                f"{'y is' if len(missed) == 1 else 'ies are'} unaccounted for — "
                f"{', '.join(missed)}"
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
        return self

    def lines(self) -> list[str]:
        """Render the statement as it appears in the backlog document."""
        return [
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
