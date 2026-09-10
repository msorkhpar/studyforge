"""What reconnaissance found, and — the part that matters — what it could not tell.

**What it does.** Holds the shape of a reconnaissance report: measured
observations, and the questions the material did not answer.

**How you use it.** A pass yields `Observation(what, measured)` for anything it
counted and `Uncertainty(question, why, settles_it)` for anything it could not
decide. `Survey.of(...)` gathers both; `survey.lines()` is what a person reads.

**Depends on.** Nothing. ⛔ Deliberately: every other module in this package
imports this one.

## ⛔ Knowing when it does not know is this skill's hardest requirement

⚠️ **A confident wrong answer about a hierarchy costs an entire ingestion.**
*"These 19 files look flat, but files 12–19 reference a grouping I cannot see —
please confirm"* costs a question. So an `Uncertainty` is not a weaker
`Observation`: it is the deliverable, and a report with none from unfamiliar
material is a report that guessed (R6).

⭐ **Every `Uncertainty` carries what would settle it.** A question a reader
cannot act on is a question that gets skipped, and a skipped question becomes a
silent guess one layer down. `settles_it` names the thing a person could say,
or the file they could point at.

⭐ **Every `Observation` carries its number.** *"The corpus looks flat"* is an
opinion; *"41 files, 0 directories"* is a measurement somebody can check, and
the integration catalogue's own rule is that a count without its denominator is
not a measurement.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class Observation:
    """One thing that was counted, and the number."""

    what: str
    measured: str

    def line(self) -> str:
        """Render as one aligned line a person can scan."""
        return f"  {self.what:<44} {self.measured}"


@dataclass(frozen=True, slots=True)
class Uncertainty:
    """One thing the material did not settle, and what would.

    ⛔ `settles_it` is required, not optional. A question with no stated way to
    answer it is a question a reader skips, and a skipped question is a silent
    guess with extra steps.
    """

    question: str
    why: str
    settles_it: str

    def lines(self) -> list[str]:
        """Render as three lines: the question, the evidence, the way out."""
        return [
            f"  ? {self.question}",
            f"      seen:    {self.why}",
            f"      settle:  {self.settles_it}",
        ]


@dataclass
class Survey:
    """Everything one pass over a source measured, and everything it could not."""

    root: str
    observations: list[Observation] = field(default_factory=list)
    uncertainties: list[Uncertainty] = field(default_factory=list)
    proposal: dict | None = None

    @classmethod
    def of(cls, root: str, items: Iterable[Observation | Uncertainty]) -> Survey:
        """Drain every check into one survey, keeping the order they were found."""
        survey = cls(root=root)
        for item in items:
            if isinstance(item, Observation):
                survey.observations.append(item)
            else:
                survey.uncertainties.append(item)
        return survey

    @property
    def settled(self) -> bool:
        """Did the material answer every question? ⚠️ Rarely true, and that is fine."""
        return not self.uncertainties

    def lines(self) -> list[str]:
        """Render the whole report: what was measured, then what was not settled.

        ⛔ The uncertainties are **last and never omitted**, including when
        there are none — a section that disappears when it is empty cannot be
        told from one nobody wrote.
        """
        out = [f"reconnaissance: {self.root}", "", "measured"]
        out += [observation.line() for observation in self.observations]
        out += ["", f"not settled ({len(self.uncertainties)})"]
        if not self.uncertainties:
            out.append("  none — every question this pass asks was answered by the material")
        for uncertainty in self.uncertainties:
            out += uncertainty.lines()
        out += ["", self.verdict()]
        return out

    def verdict(self) -> str:
        """One line: whether a manifest is proposed, and how much is unanswered."""
        drafted = "a draft manifest is proposed" if self.proposal else "no manifest is proposed"
        return (
            f"{drafted}; {len(self.observations)} measurement(s), "
            f"{len(self.uncertainties)} open question(s)"
        )
