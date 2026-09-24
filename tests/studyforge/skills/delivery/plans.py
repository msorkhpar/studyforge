"""Worked plans and the offer the delivery tests share.

Built here rather than in each module for the reason `corpora.py` exists next
door: a fixture retyped in nine files is nine fixtures that drift.

⚠️ **Every corpus here is invented, and so is the offer.** The framework names
no source (R1), and a test fixture that borrowed a real repository's plan would
teach the next reader that borrowing one is normal. The offer's ids are not the
installed framework's, so a test of the planner never depends on which verbs
or skills a release happens to carry.
"""

from __future__ import annotations

from studyforge.skills.delivery import (
    Acceptance,
    Backlog,
    Capability,
    Milestone,
    Offer,
    Task,
    Terminal,
    Unused,
)

#: Three capabilities: two a reading plan uses, one only a runnable corpus would.
READ = "tool read"
RENDER = "tool render"
RUN = "tool run"


def offer() -> Offer:
    """A small installed framework: it reads, it renders, it runs code."""
    return Offer(
        (
            Capability(READ, "read a corpus's material into an archive"),
            Capability(RENDER, "write the site from an archive"),
            Capability(RUN, "run a reader's code against a grader"),
        )
    )


def terminal() -> Terminal:
    """A corpus that finishes at the reading floor, accounting for what it never uses."""
    return Terminal(
        finishes="the reading floor",
        evidence=("0 runnable units", "0 graders anywhere in the repository"),
        unused=(Unused(RUN, "no unit asks the reader to run anything"),),
    )


def reading_task(name: str = "C-01", **overrides: object) -> Task:
    """A task that ends in something a person can be shown."""
    fields: dict[str, object] = {
        "id": name,
        "title": "One unit opens in a browser",
        "demonstrable": "the reader opens unit 1 and every block renders",
        "acceptance": (Acceptance("the archive validates", runs="python3 -m pytest tests"),),
        "owns": ("ingest/read.py",),
    }
    fields.update(overrides)
    return Task(**fields)  # type: ignore[arg-type]


def backlog(**overrides: object) -> Backlog:
    """A two-milestone plan that passes every check."""
    fields: dict[str, object] = {
        "corpus": "a repository of teaching prose",
        "milestones": (
            Milestone(
                id="C1",
                name="the material reads",
                tasks=(reading_task("C-01", depends_on=(READ,)),),
            ),
            Milestone(
                id="C2",
                name="the whole corpus reads",
                tasks=(
                    reading_task(
                        "C-02",
                        depends_on=("C-01", RENDER),
                        owns=(),
                        evidence="a re-run of the generator that changes no byte",
                        effort=4,
                    ),
                ),
            ),
        ),
        "terminal": terminal(),
    }
    fields.update(overrides)
    return Backlog(**fields)  # type: ignore[arg-type]
