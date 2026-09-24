r"""The backlog document: milestones that declare their gate, and a critical path.

**What it does.** Gathers tasks into milestones, **checks the plan against the
capability index** rather than against the planner's memory, and renders the
durable artifact an integration works from.

**How you use it.**

    from studyforge.skills.delivery import Backlog, Milestone

    plan = Backlog(
        corpus="a repository of teaching material",
        milestones=(Milestone("C1", "one unit reads", gated_by="M4", tasks=(...,)),),
        terminal=terminal,
    ).checked(index)
    print("\n".join(plan.lines()))

**Depends on.** `dataclasses` and this package's `capability`, `task`,
`terminal`, `question`, `finding` and `refusal`. ⛔ Not the filesystem, and not
any source.

## ⛔ A corpus milestone DECLARES the framework milestone that gates it

⚠️ **Today a corpus milestone is silently gated on framework work and nothing
in the plan says so.** A plan that slips because a framework milestone slipped
is a plan that slipped for a reason nobody wrote down, and the integration
finds out by trying.

⭐ **So `gated_by` is a field, a task's `depends_on` may name a framework task
id, and the check is against the index**: a milestone whose tasks reach a
capability the index places *later* than the declared gate is refused, with
the capability named. ⛔ Never a warning — a warning about a plan is a warning
nobody reads until the plan has already been agreed.

## ⭐ The critical path is derived, never asserted

⚠️ A plan whose author *says* which chain is critical has stated a belief. The
chain is a property of the dependency graph and the efforts, so it is
computed — and the same walk is what refuses a cycle.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace

from studyforge.skills.delivery.capability import Index
from studyforge.skills.delivery.finding import Finding
from studyforge.skills.delivery.question import Question, numbered
from studyforge.skills.delivery.refusal import one_or_all
from studyforge.skills.delivery.task import PlanRefused, Task
from studyforge.skills.delivery.terminal import Terminal


@dataclass(frozen=True, slots=True)
class Milestone:
    """A group of tasks that lands together, and what it waits on."""

    id: str
    name: str
    tasks: tuple[Task, ...]
    gated_by: str | None = None

    def __post_init__(self) -> None:
        """Refuse a milestone that lands nothing, or names a task twice."""
        if not self.id.strip() or not self.name.strip():
            raise PlanRefused("a milestone needs an id and a name")
        if not self.tasks:
            raise PlanRefused("a milestone with no tasks lands nothing")
        ids = [task.id for task in self.tasks]
        repeated = {name for name in ids if ids.count(name) > 1}
        if repeated:
            raise PlanRefused(f"two tasks share an id — {len(repeated)} of them")

    @property
    def effort(self) -> int:
        """What this milestone costs."""
        return sum(task.effort for task in self.tasks)

    def lines(self) -> list[str]:
        """Render the milestone's header. Its tasks render themselves."""
        gate = f"`{self.gated_by}`" if self.gated_by else "⭐ nothing — this corpus alone"
        return [
            f"## {self.id} — {self.name.strip()}",
            "",
            f"**Gated by (framework)** {gate} · **Tasks** {len(self.tasks)} · "
            f"**Effort** {self.effort}",
        ]


@dataclass(frozen=True, slots=True)
class Backlog:
    """A whole delivery plan, and the checks that make it worth agreeing to."""

    corpus: str
    milestones: tuple[Milestone, ...]
    terminal: Terminal
    questions: tuple[Question, ...] = field(default_factory=tuple)
    findings: tuple[Finding, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        """Refuse a plan whose ids, questions or findings collide."""
        if not self.milestones:
            raise PlanRefused("a backlog with no milestones delivers nothing")
        ids = [task.id for task in self.tasks]
        repeated = {name for name in ids if ids.count(name) > 1}
        if repeated:
            raise PlanRefused(f"a task id is used twice — {len(repeated)} of them")
        numbered(self.questions)
        found = [item.id for item in self.findings]
        twice = {name for name in found if found.count(name) > 1}
        if twice:
            raise PlanRefused(f"a finding id is used twice — {len(twice)} of them")

    @property
    def tasks(self) -> tuple[Task, ...]:
        """Every task, in milestone order."""
        return tuple(task for milestone in self.milestones for task in milestone.tasks)

    @property
    def effort(self) -> int:
        """What the whole plan costs."""
        return sum(milestone.effort for milestone in self.milestones)

    @property
    def open_questions(self) -> tuple[Question, ...]:
        """The ones still blocking somebody."""
        return tuple(question for question in self.questions if question.open)

    def _milestone_of(self, task: str) -> str:
        """Which of this plan's milestones carries `task`."""
        for milestone in self.milestones:
            if any(item.id == task for item in milestone.tasks):
                return milestone.id
        raise PlanRefused("no such task in this plan")

    def checked(self, index: Index) -> Backlog:
        """Refuse a plan the index contradicts, ⛔ naming EVERYTHING that contradicts it.

        ⛔ **Every reason is named** (R6). The two checks below give back their reasons
        rather than raising, because the loop that drives them is here: a check
        that raised would refuse on the first offending task of the first
        offending milestone, and the reader would learn how many more there are
        only by fixing that one and running the whole plan again.

        ⭐ Returns a plan carrying the CHECKED terminal statement, which is
        where the capabilities that are not this framework's to deliver come
        back from the index. ⛔ Dropping the return would render a
        statement that had been checked and then thrown away.
        """
        terminal = self.terminal.checked(index)
        known = frozenset(capability.id for capability in index.capabilities)
        order = {milestone.id: position for position, milestone in enumerate(self.milestones)}
        refusals: list[str] = []
        for milestone in self.milestones:
            for task in milestone.tasks:
                refusals += self._check_framework(index, milestone, task, known)
                refusals += self._check_corpus(order, milestone, task, known)
        if refusals:
            raise PlanRefused(one_or_all(refusals))
        self.critical_path()
        return replace(self, terminal=terminal)

    def _check_framework(
        self, index: Index, milestone: Milestone, task: Task, known: frozenset[str]
    ) -> list[str]:
        """⛔ Every capability this milestone reaches later than its declared gate."""
        reaches = task.framework_dependencies(known)
        if not reaches:
            return []
        if milestone.gated_by is None:
            return [
                f"a milestone declares no framework gate and one of its tasks waits on "
                f"{', '.join(reaches)}. ⛔ A corpus milestone silently gated on "
                "framework work is a plan that slips for an unwritten reason"
            ]
        found: list[str] = []
        for name in reaches:
            lands = index.milestone_of(name)
            # ⛔ In the index's declared sequence, never by id: `M5` lands after
            # `M8` in a plan whose order is not the order its ids sort to.
            if index.later(lands, than=milestone.gated_by):
                found.append(
                    f"a milestone is gated by {milestone.gated_by}, but one of its "
                    f"tasks waits on {name}, which lands at {lands}"
                )
        return found

    def _check_corpus(
        self, order: dict[str, int], milestone: Milestone, task: Task, known: frozenset[str]
    ) -> list[str]:
        """⛔ Every dependency this plan does not carry, or carries later."""
        found: list[str] = []
        for name in task.corpus_dependencies(known):
            try:
                where = self._milestone_of(name)
            except PlanRefused:
                found.append(
                    "a task waits on something that is neither in this plan nor a "
                    "capability the index carries"
                )
                continue
            if order[where] > order[milestone.id]:
                found.append("a task waits on a task in a later milestone of this same plan")
        return found

    def _cyclic(self) -> tuple[str, ...]:
        """Every task that reaches itself through this plan's own tasks.

        ⭐ Derived by closing each task's dependencies over the plan until
        nothing grows, so the answer is the WHOLE population rather than
        whichever cycle a depth-first walk happened to enter first.
        """
        by_id = {task.id: task for task in self.tasks}
        reach = {
            name: {waits_on for waits_on in task.depends_on if waits_on in by_id}
            for name, task in by_id.items()
        }
        grew = True
        while grew:
            grew = False
            for name, seen in reach.items():
                wider = seen.union(*(reach[waits_on] for waits_on in seen)) if seen else seen
                if wider != seen:
                    reach[name] = wider
                    grew = True
        return tuple(sorted(name for name in by_id if name in reach[name]))

    def critical_path(self) -> tuple[str, ...]:
        """Derive the heaviest chain of this plan's own tasks, ⛔ refusing every cycle.

        ⛔ **The cycles are refused before the walk, all of them at once**
        (R6): a guard inside the walk raises on the first cycle
        it enters and says nothing about the rest. ⭐ The walk below is
        therefore over a graph already known to be acyclic, which is why it
        carries no cycle guard of its own.
        """
        cyclic = self._cyclic()
        if cyclic:
            several = len(cyclic) > 1
            raise PlanRefused(
                f"{f'{len(cyclic)} tasks depend' if several else 'a task depends'} on "
                f"{'themselves' if several else 'itself'}, through this plan's own tasks"
            )
        by_id = {task.id: task for task in self.tasks}
        depth: dict[str, tuple[int, tuple[str, ...]]] = {}

        def walk(name: str) -> tuple[int, tuple[str, ...]]:
            if name in depth:
                return depth[name]
            task = by_id[name]
            best: tuple[int, tuple[str, ...]] = (0, ())
            for waits_on in task.depends_on:
                if waits_on in by_id:
                    best = max(best, walk(waits_on))
            depth[name] = (best[0] + task.effort, (*best[1], name))
            return depth[name]

        longest: tuple[int, tuple[str, ...]] = (0, ())
        for name in by_id:
            longest = max(longest, walk(name))
        return longest[1]

    def lines(self) -> list[str]:
        """Render the backlog document, as a reader of the plan sees it."""
        path = self.critical_path()
        out = [
            f"# Delivery plan — {self.corpus.strip()}",
            "",
            f"**{len(self.tasks)} tasks · {len(self.milestones)} milestones · "
            f"{self.effort} units of effort · {len(self.open_questions)} open questions.**",
            "",
            "⛔ **Every task below ends in something a person can be shown, and every "
            "acceptance clause names the instrument that decides it.**",
            "",
            f"**Critical path.** {' → '.join(path) if path else '—'}",
            "",
            *self.terminal.lines(),
            "",
        ]
        for milestone in self.milestones:
            out += [*milestone.lines(), ""]
            for task in milestone.tasks:
                out += [*task.lines(), ""]
        if self.questions:
            out += ["## Questions", ""]
            for question in self.questions:
                out += [*question.lines(), ""]
        if self.findings:
            out += ["## Findings", ""]
            for item in self.findings:
                out += [*item.lines(), ""]
        return out
