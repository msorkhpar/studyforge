"""Course intake: the questions asked before a course is planned, and where answers live.

**What it does.** Intake collects the author's decisions about a course (its track, its
depth, its practices, its sources) into one brief before any lesson is written. The
question bank decides which questions exist for a given track; a question the track does
not need is never asked, and a question whose gate is unanswered waits.

**How you use it.**

    from studyforge.skills.intake import TRACKS, DEPTHS, BRIEF_PATH
    from studyforge.skills.intake.questions import Question, applies

    applies(question, "topic", answers)     # does this question belong on this track?

The brief lives at `.studyforge/brief.json` in the course repository (`BRIEF_PATH`) and is
rendered for reading to `.studyforge/brief.md`.

**Depends on.** Nothing outside the standard library.
"""

from __future__ import annotations

#: The kinds of course intake knows how to plan.
TRACKS: tuple[str, ...] = ("topic", "interview", "exam", "bridge", "convert")

#: The depth tags a lesson outline may carry.
DEPTHS: tuple[str, ...] = ("core", "deep", "survey", "prose")

#: Where the brief is stored, relative to the course repository root.
BRIEF_PATH = ".studyforge/brief.json"

# Re-exports come last: the submodules import the constants above from this package.
from .bank import BANK  # noqa: E402
from .brief import Brief, BriefError, load, parse  # noqa: E402
from .check import check  # noqa: E402
from .questions import Question  # noqa: E402
from .render import render  # noqa: E402

__all__ = ["BANK", "BRIEF_PATH", "Brief", "BriefError", "DEPTHS", "Question", "TRACKS",
           "check", "load", "parse", "render"]
