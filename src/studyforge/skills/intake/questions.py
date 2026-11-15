"""The question model: one intake question, and whether it applies on a track.

**What it does.** Defines `Question`, the record the bank is built from, `applies`, which
says whether a question is asked on a track given the answers so far, and `HEDGE`, the
pattern for answers that decide nothing.

**How you use it.**

    q = Question(id="practice.shape", group="practice", ask="...", why="...",
                 default="...", tracks=frozenset({"topic"}), tier="costly")
    applies(q, "topic", answers)

**Depends on.** The standard library. `applies` reads only `status` and `value` of each
answer, so any object with those two attributes will do.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from typing import TYPE_CHECKING

from . import TRACKS

if TYPE_CHECKING:  # pragma: no cover
    from .brief import Answer

KINDS: tuple[str, ...] = ("text", "boolean", "choice", "private_ref")

#: Phrases that postpone a decision instead of making it, matched as whole words.
HEDGE: re.Pattern[str] = re.compile(
    r"\b(?:where possible|tbd|to be decided|if time allows|maybe)\b", re.IGNORECASE
)


@dataclass(frozen=True)
class Question:
    id: str
    group: str
    ask: str
    why: str
    default: str
    tracks: frozenset[str]
    tier: str
    kind: str = "text"
    choices: tuple[str, ...] = ()
    depends_on: tuple[str, tuple[object, ...]] | None = None

    def __post_init__(self) -> None:
        if self.group != self.id.split(".", 1)[0]:
            raise ValueError(f"{self.id}: group {self.group!r} is not the id prefix")
        if self.kind not in KINDS:
            raise ValueError(f"{self.id}: kind {self.kind!r} is not one of {KINDS}")
        if not self.tracks <= set(TRACKS):
            raise ValueError(f"{self.id}: unknown track in {sorted(self.tracks)}")


def applies(question: Question, track: str, answers: Mapping[str, "Answer"]) -> bool:
    """True when the question is on this track and its gate, if any, holds."""
    if track not in question.tracks:
        return False
    if question.depends_on is None:
        return True
    gate_id, values = question.depends_on
    gate = answers.get(gate_id)
    return gate is not None and gate.status == "answered" and gate.value in values
