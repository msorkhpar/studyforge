"""The brief checker: which costly questions are still open, and what is wrong with the outline.

**What it does.** Reads a `Brief` against the question bank and reports, one line per problem,
every costly question that applies and is not decided: missing, proposed but not accepted,
empty, of the wrong type, hedged, or carrying personal data. It also checks the outline (not
empty, a pilot module, and `writing.pilot` naming it) and scrubs every title for personal data.
A deferred answer that gives a reason is a decision and is not open. Questions of the `later`
tier never appear. A line names the shape of personal data found, never the matched text.

**How you use it.**

    from studyforge.skills.intake.check import check

    for line in check(brief, private_ignored=True):
        print(line)          # "open: goal.end_state: hedged"

`open_questions` and `outline_faults` give the two halves separately. An empty list means the
brief is ready to build from.

**Depends on.** The question bank, the brief record, and `studyforge.archive.scrub.findings`.
"""

from __future__ import annotations

import re

from studyforge.archive.scrub import findings

from .bank import BANK
from .brief import Answer, Brief
from .questions import HEDGE, Question, applies

_NAME = r"[A-Z][A-Z0-9_]*"
_FILE = r"(?!/)(?!(?:.*/)?\.\.(?:/|#|$))[^#\s]+"

#: `env:NAME` or `private:FILE`, each optionally followed by `#KEY`. The `[#]` keeps the
#: fragment sweep from reading the pattern as an anchor being composed.
PRIVATE_REF: re.Pattern[str] = re.compile(
    rf"(?:env:{_NAME}|private:{_FILE})(?:[#]{_NAME})?"
)


def _empty(value: object) -> bool:
    return value is None or (isinstance(value, str) and not value.strip())


def _shape(text: str) -> str | None:
    found = findings(text)
    return found[0][1] if found else None


def _problem(question: Question, answer: Answer | None) -> str | None:
    """The first reason this question is open, or None."""
    if answer is None:
        return "missing"
    if answer.status == "proposed":
        return "proposed, not yet accepted"
    if answer.status == "deferred":
        return None
    value = answer.value
    if _empty(value):
        return "empty"
    if question.kind == "boolean":
        return None if isinstance(value, bool) else "not a boolean"
    if not isinstance(value, str):
        return "not a boolean" if isinstance(value, bool) else "empty"
    if question.kind == "choice" and value not in question.choices:
        return f"not one of {', '.join(question.choices)}"
    if question.kind == "private_ref" and not PRIVATE_REF.fullmatch(value):
        return "not a variable name or a .private/ key"
    if HEDGE.search(value):
        return "hedged"
    shape = _shape(value)
    return f"carries {shape}" if shape else None


def open_questions(brief: Brief) -> list[str]:
    """One `open: <id>: <reason>` line per undecided costly question, in bank order."""
    lines: list[str] = []
    for question in BANK:
        if question.tier != "costly" or not applies(question, brief.track, brief.answers):
            continue
        reason = _problem(question, brief.answers.get(question.id))
        if reason:
            lines.append(f"open: {question.id}: {reason}")
    return lines


def outline_faults(brief: Brief) -> list[str]:
    """Problems with the outline as a whole: empty, no pilot, or a pilot that does not match."""
    modules = [m for section in brief.outline for m in section.modules]
    if not modules:
        return ["outline: empty"]
    pilots = {m.title for m in modules if m.pilot}
    faults: list[str] = []
    if not pilots:
        faults.append("outline: no module is marked pilot")
    named = brief.answers.get("writing.pilot")
    if named is not None and named.status == "answered" and named.value not in pilots:
        faults.append(f"outline: writing.pilot names {named.value}, which is not a pilot module")
    return faults


def _title_paths(brief: Brief) -> list[tuple[str, str]]:
    paths = [("title", brief.title)]
    for i, section in enumerate(brief.outline):
        paths.append((f"outline.{i}", section.title))
        for j, module in enumerate(section.modules):
            base = f"outline.{i}.modules.{j}"
            paths.append((base, module.title))
            for k, lesson in enumerate(module.lessons):
                paths.append((f"{base}.lessons.{k}", lesson.title))
    return paths


def _title_findings(brief: Brief) -> list[str]:
    lines: list[str] = []
    for path, title in _title_paths(brief):
        shape = _shape(title)
        if shape:
            lines.append(f"outline: {path} carries {shape}")
    return lines


def check(brief: Brief, private_ignored: bool) -> list[str]:
    """Every open question and outline fault, then the git-ignore finding if it applies."""
    lines = open_questions(brief) + outline_faults(brief) + _title_findings(brief)
    if not private_ignored:
        lines.append(".private/ is not ignored by git")
    return lines
