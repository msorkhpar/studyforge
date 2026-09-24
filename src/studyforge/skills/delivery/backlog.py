r"""The backlog document: milestones, the framework they use, and a critical path.

**What it does.** Gathers tasks into milestones, **checks the plan against what
the installed framework offers** rather than against the planner's memory, and
renders the durable artifact an integration works from.

**How you use it.**

    from studyforge.skills.delivery import Backlog, Milestone, Offer

    plan = Backlog(
        corpus="a repository of teaching material",
        milestones=(Milestone("C1", "one unit reads", tasks=(...,)),),
        terminal=terminal,
    ).checked(Offer.installed())
    print("\n".join(plan.lines()))

**Depends on.** `dataclasses` and this package's `offer`, `task`, `terminal`,
`question`, `finding` and `refusal`. ⛔ Not the filesystem, and not any source.

## ⛔ A task names the framework capability it uses, and the offer checks it

⭐ A task's `depends_on` may name a task of this plan, a capability the
installed framework offers, or a finding this plan files. ⛔ Anything else is
refused: a task that waits on a capability nobody offers is a plan that will
slip for a reason nobody wrote down.

⭐ **A capability the framework lacks is filed as a finding, and the task waits
on the finding.** The plan then says, in its header, how many of its tasks are
waiting on the framework, which is the progress a reader needs before
agreeing to it.

## ⭐ The critical path is derived, never asserted

⚠️ A plan whose author *says* which chain is critical has stated a belief. The
chain is a property of the dependency graph and the efforts, so it is
computed — and the same walk is what refuses a cycle.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from studyforge.skills.delivery.finding import Finding
from studyforge.skills.delivery.offer import Offer
from studyforge.skills.delivery.question import Question, numbered
from studyforge.skills.delivery.refusal import one_or_all
from studyforge.skills.delivery.task import PlanRefused, Task
from studyforge.skills.delivery.terminal import Terminal, TerminalRefused


@dataclass(frozen=True, slots=True)
class Milestone:
    """A group of tasks that lands together."""

    id: str
    name: str
    tasks: tuple[Task, ...]

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
        return [
            f"## {self.id} — {self.name.strip()}",
            "",
            f"**Tasks** {len(self.tasks)} · **Effort** {self.effort}",
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

    @property
    def filed(self) -> frozenset[str]:
        """The ids of the findings this plan files, which a task may wait on."""
        return frozenset(item.id for item in self.findings)

    @property
    def waiting(self) -> tuple[Task, ...]:
        """⭐ The tasks that wait on a finding: the plan's work the framework holds up."""
        return tuple(task for task in self.tasks if set(task.depends_on) & self.filed)

    def used(self, offer: Offer) -> frozenset[str]:
        """Every offered capability a task of this plan names."""
        return frozenset(name for task in self.tasks for name in task.depends_on) & offer.ids

    def checked(self, offer: Offer) -> Backlog:
        """Refuse a plan the offer contradicts, ⛔ naming EVERYTHING that contradicts it.

        ⛔ **Every reason is named.** The check below gives back its reasons
        rather than raising, because the loop that drives it is here: a check
        that raised would refuse on the first offending task, and the reader
        would learn how many more there are only by fixing that one and
        running the whole plan again.

        ⭐ The terminal statement is checked against the same offer and against
        what this plan's tasks use, so the never-used table and the tasks can
        never disagree.
        """
        refusals: list[str] = []
        try:
            self.terminal.checked(offer, used=self.used(offer))
        except TerminalRefused as refused:
            refusals.append(str(refused))
        order = {milestone.id: position for position, milestone in enumerate(self.milestones)}
        outside = offer.ids | self.filed
        for milestone in self.milestones:
            for task in milestone.tasks:
                refusals += self._check_dependencies(order, milestone, task, outside)
        if refusals:
            raise PlanRefused(one_or_all(refusals))
        self.critical_path()
        return self

    def _check_dependencies(
        self, order: dict[str, int], milestone: Milestone, task: Task, outside: frozenset[str]
    ) -> list[str]:
        """⛔ Every dependency nobody offers, and every one this plan carries later.

        ⚠️ No dependency is quoted: `depends_on` is caller text.
        """
        found: list[str] = []
        for name in task.corpus_dependencies(outside):
            try:
                where = self._milestone_of(name)
            except PlanRefused:
                found.append(
                    "a task waits on something that is neither a task of this plan, nor a "
                    "capability the installed framework offers, nor a finding this plan "
                    "files. ⛔ A capability the framework lacks is filed as a finding, and "
                    "the task waits on the finding"
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
            f"{self.effort} units of effort · {len(self.open_questions)} open questions · "
            f"{len(self.waiting)} tasks waiting on a finding against the framework.**",
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
