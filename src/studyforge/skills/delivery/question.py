r"""Questions, which are a first-class output beside findings — and decay like one.

**What it does.** Holds the shape of a question an integration asks the
framework: numbered, routed at a task, naming what it blocks, and carrying
**how to re-run it**. And it holds the answer, stamped with the ref it was
taken at, so that acting on a stale answer is a refusal rather than a habit.

**How you use it.**

    from studyforge.skills.delivery import Question, Questions

    q = Question(1, "does placement re-read its own output?",
                 routed_at="AB-31", blocks=("C-02",),
                 rerun="python3 -m pytest tests/studyforge/cli/plan")
    q = q.settled("no, since W28", at="8146bdb")
    q.is_current("8146bdb")     # True — safe to act on

**Depends on.** `dataclasses`. ⛔ Nothing else.

## ⛔ A question is not a soft finding, and no skill defined one until this
one

⚠️ **Named by the filing side as the highest-value item on their branch**, and
it had no home: a finding says *the framework could not do X*, and a question
says *I could not tell whether it can*. ⛔ Routing the second as the first
produces a framework task for something that was already true, and routing it
as prose produces nothing at all.

## ⭐ The re-run is the field that makes it a question rather than a doubt

⛔ **A question with no stated way to re-run it is refused**, for the same
reason reconnaissance refuses an `Uncertainty` with no `settles_it`: a
question a reader cannot act on is a question that gets skipped, and a skipped
question is a silent guess one layer down.

## ⚠️ And it decays against a framework that moves, not against the material

⛔ **Measured on the filing side: three of twelve open questions closed
between two rounds a day apart, one of them because a merged schema
changed** — with nothing having moved in the material. ⭐ **So an answer
carries the ref it was taken at**, and `is_current` is what a reader checks
before acting. ⚠️ A question answered against a ref that is no longer current
is an answer about a framework that no longer exists.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

#: The shortest re-run that can name anything a second reader could type.
MIN_RERUN_CHARS = 8


class QuestionRefused(Exception):
    """Raised when a question could not be acted on by the person receiving it."""


@dataclass(frozen=True, slots=True)
class Answer:
    """What the framework said, and the ref it said it at."""

    said: str
    at: str

    def __post_init__(self) -> None:
        """Refuse an answer that cannot be told from a stale one."""
        if not self.said.strip():
            raise QuestionRefused("an answer with no text answers nothing")
        if not self.at.strip():
            raise QuestionRefused(
                "an answer carries no ref. ⛔ An answer with no ref cannot be told "
                "from a stale one, which is the whole failure mode"
            )


@dataclass(frozen=True, slots=True)
class Question:
    """One thing an integration could not settle for itself."""

    number: int
    asks: str
    routed_at: str
    blocks: tuple[str, ...]
    rerun: str
    answer: Answer | None = None

    def __post_init__(self) -> None:
        """Refuse a question the person receiving it could not act on."""
        if self.number < 1:
            raise QuestionRefused("questions are numbered from 1")
        if not self.asks.strip():
            raise QuestionRefused("a question with no text is not a question")
        if not self.routed_at.strip():
            raise QuestionRefused(
                f"Q{self.number}: routed at nobody. ⛔ A question addressed to the "
                "project is a question addressed to whoever feels like it"
            )
        if not self.blocks:
            raise QuestionRefused(
                f"Q{self.number}: blocks nothing named. ⚠️ If it blocks nothing it is "
                "not a question, it is curiosity — and curiosity is not routed"
            )
        if len(self.rerun.strip()) < MIN_RERUN_CHARS:
            raise QuestionRefused(
                f"Q{self.number}: `rerun` is under {MIN_RERUN_CHARS} characters and does "
                "not say how to re-run it. ⛔ A question nobody can re-run is answered "
                "once and believed forever"
            )

    def settled(self, said: str, *, at: str) -> Question:
        """Attach an answer, stamped with the ref it was taken at."""
        return replace(self, answer=Answer(said, at))

    @property
    def open(self) -> bool:
        """True while nothing has answered it."""
        return self.answer is None

    def is_current(self, ref: str) -> bool:
        """⛔ False for an open question **and** for one answered elsewhere."""
        return self.answer is not None and self.answer.at == ref

    def act_on(self, ref: str) -> str:
        """Give back the answer, or refuse and name what to re-run.

        ⭐ This is the whole mechanism: a stale answer does not come back with
        a warning attached, it does not come back.
        """
        if self.answer is None:
            raise QuestionRefused(f"Q{self.number} is open — re-run: {self.rerun.strip()}")
        if self.answer.at != ref:
            raise QuestionRefused(
                f"Q{self.number} was answered at {self.answer.at}, and you are at {ref}. "
                f"⛔ Re-run before acting: {self.rerun.strip()}"
            )
        return self.answer.said

    def lines(self) -> list[str]:
        """Render as the four lines a reader needs to act or to re-run."""
        blocks = ", ".join(f"`{name}`" for name in self.blocks)
        state = (
            f"answered at {self.answer.at}: {self.answer.said}"
            if self.answer is not None
            else "⛔ OPEN"
        )
        return [
            f"  Q{self.number} {self.asks.strip()}",
            f"      routed at: {self.routed_at.strip()}",
            f"      blocks:    {blocks}",
            f"      re-run:    {self.rerun.strip()}",
            f"      state:     {state}",
        ]


def numbered(questions: tuple[Question, ...]) -> tuple[Question, ...]:
    """Refuse a set whose numbers repeat or skip, and return it in order.

    ⛔ **A question's number is how it is cited across two repositories**, so
    two questions numbered 4 is a citation that resolves to either. And a gap
    is a question somebody deleted rather than answered, which is exactly the
    thing this output exists to stop.
    """
    numbers = sorted(question.number for question in questions)
    if numbers != list(range(1, len(numbers) + 1)):
        raise QuestionRefused(
            f"questions are numbered 1..n with no repeats and no gaps — these are {numbers}"
        )
    return tuple(sorted(questions, key=lambda question: question.number))
