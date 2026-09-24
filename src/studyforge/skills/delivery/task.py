r"""One task in a delivery plan: what it ends in, and who can check that it did.

**What it does.** Holds the two refusals that make a backlog worth reading —
a task that does not end in something a person can be **shown**, and an
acceptance clause the framework cannot **evaluate**.

**How you use it.**

    from studyforge.skills.delivery import Acceptance, Task

    Task(
        id="C-03",
        title="One unit opens in a browser",
        demonstrable="the reader opens unit 1 and it renders",
        acceptance=(Acceptance("the archive validates", runs="python3 -m pytest tests"),),
        owns=("ingest/read.py",),
    )

**Depends on.** `dataclasses`. ⛔ Nothing else — a task is data, and the thing
that judges a *set* of them lives next door in `backlog`.

## ⛔ Each task ends in something demonstrable, never in a layer

⚠️ This is inherited from this repository's own ordering principle and it has
already been paid for once: *build every contract, then every renderer, then
every service* hides all integration risk until the end, and integration risk
is the kind that **reorders plans**. ⛔ A task whose deliverable is *"the
parser is written"* is not a task; one whose deliverable is *"one unit of this
material opens in a browser"* is.

## ⭐ A task may own nothing, and that is the shape to expect

⛔ **The template that assumes the integrator *writes* things describes a
framework whose generators do not work.** As the skills improve, more of a
plan becomes *evidence about generated output* — a measurement, a diff, a
re-run that changes nothing. ⚠️ So `owns` may be empty; what may **not** be
empty is the answer to *what does this task produce that somebody can look
at*, which is `evidence`.

## ⛔ Acceptance the framework can evaluate, never acceptance by opinion

⭐ *"The pages look right"* is a task nobody can close and everybody can argue
about. Every clause therefore carries an instrument, and there are exactly
two legal forms:

- **`runs`** — a command whose exit code decides it;
- **`looked_at_by` + `at`** — a named person and the thing they look at, for
  the genuinely visual judgement, ⛔ **stated rather than smuggled in**.

⚠️ **Both at once is refused too.** A clause with a command *and* a reviewer
is a clause where nobody knows which one decides, and the answer under
pressure is always the reviewer.
"""

from __future__ import annotations

from dataclasses import dataclass, field

#: The shortest deliverable that can still name something. ⛔ Not a quality
#: bar — it only stops `demonstrable="done"` from being a way through.
MIN_DEMONSTRABLE_CHARS = 12


class PlanRefused(Exception):
    """Raised when a plan states something nobody could check."""


@dataclass(frozen=True, slots=True)
class Acceptance:
    """One clause, and the instrument that decides it."""

    clause: str
    runs: str = ""
    looked_at_by: str = ""
    at: str = ""

    def __post_init__(self) -> None:
        """Refuse a clause that no single instrument decides."""
        if not self.clause.strip():
            raise PlanRefused("an acceptance clause with no text accepts everything")
        looks = bool(self.looked_at_by.strip())
        if looks and not self.at.strip():
            raise PlanRefused(
                "an acceptance clause names a reviewer and no `at` — ⛔ a reviewer "
                "with no subject is an opinion with a name on it"
            )
        if bool(self.runs.strip()) == looks:
            raise PlanRefused(
                "an acceptance clause names exactly one instrument — a command that "
                "exits non-zero, or who looks and at what. This one names "
                f"{'both' if looks else 'neither'}"
            )

    @property
    def instrument(self) -> str:
        """What decides this clause, rendered for a reader."""
        if self.runs.strip():
            return f"`{self.runs.strip()}`"
        return f"{self.looked_at_by.strip()} looks at {self.at.strip()}"

    def line(self) -> str:
        """Render as one line of the task's acceptance list."""
        return f"  - {self.clause.strip()} — {self.instrument}"


@dataclass(frozen=True, slots=True)
class Task:
    """One unit of a delivery plan.

    ⛔ Every refusal here is raised at construction, so an unplannable task
    cannot reach a document. A planner that emitted the bad task and warned
    about it would be a planner whose warnings get filtered.
    """

    id: str
    title: str
    demonstrable: str
    acceptance: tuple[Acceptance, ...]
    owns: tuple[str, ...] = ()
    evidence: str = ""
    depends_on: tuple[str, ...] = ()
    effort: int = 1
    notes: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        """Refuse a task nobody could be shown the end of, or close."""
        if not self.id.strip() or not self.title.strip():
            raise PlanRefused("a task needs an id and a title")
        if len(self.demonstrable.strip()) < MIN_DEMONSTRABLE_CHARS:
            raise PlanRefused(
                "a task's `demonstrable` does not name something a person can be shown. "
                "A task that ends in a layer hides integration risk until the end"
            )
        if not self.acceptance:
            raise PlanRefused("a task with no acceptance, so nobody can close it")
        if not self.owns and not self.evidence.strip():
            raise PlanRefused(
                "a task owns nothing and states no evidence. ⭐ A task MAY own "
                "nothing — its deliverable is then evidence about generated output, "
                "and that has to be written down"
            )
        if self.effort < 1:
            raise PlanRefused(f"a task's effort is {self.effort}, which is not work anybody does")

    @property
    def owns_nothing(self) -> bool:
        """⭐ True for the shape a working generator produces."""
        return not self.owns

    def framework_dependencies(self, known: frozenset[str]) -> tuple[str, ...]:
        """Those of this task's dependencies that reach outside the plan.

        ⭐ `depends_on` is allowed to reach outside the corpus, and this is
        what makes the reach visible. `known` is every id outside the plan a
        task may name — the installed framework's capabilities and the plan's
        findings — passed in, because this module knows neither.
        """
        return tuple(name for name in self.depends_on if name in known)

    def corpus_dependencies(self, known: frozenset[str]) -> tuple[str, ...]:
        """Give back the rest: tasks inside the corpus's own plan."""
        return tuple(name for name in self.depends_on if name not in known)

    def lines(self) -> list[str]:
        """Render the task as a reader sees it in the backlog document."""
        owns = ", ".join(f"`{name}`" for name in self.owns) or "⭐ nothing"
        waits = ", ".join(f"`{name}`" for name in self.depends_on) or "—"
        out = [
            f"### {self.id} — {self.title.strip()}",
            "",
            f"**Owns** {owns} · **Depends on** {waits} · **Effort** {self.effort}",
            "",
            f"**Shown at the end of it.** {self.demonstrable.strip()}",
        ]
        if self.evidence.strip():
            out += ["", f"**Evidence it produces.** {self.evidence.strip()}"]
        out += ["", "**Acceptance.**", *(clause.line() for clause in self.acceptance)]
        out += ["", *(f"⚠️ {note}" for note in self.notes)] if self.notes else []
        return out
