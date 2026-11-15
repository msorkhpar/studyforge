"""The brief as Markdown: what `brief.md` shows a person.

**What it does.** Turns a parsed `Brief` into deterministic Markdown: the title and track,
one section per question group with each applicable answered question, what Claude decided,
what is deferred, what is still open, and the course outline. Output uses LF line endings and
ends with exactly one newline. Nothing in it depends on the date or on dict order beyond the
bank and outline order.

**How you use it.**

    from studyforge.skills.intake.render import render

    Path(".studyforge/brief.md").write_text(render(brief), encoding="utf-8")

The "Still open" section comes from `check(brief, private_ignored=True)`, so the line about
the private folder never appears: the renderer cannot see the repository. A `later` question
the checker skips still shows there, marked `(later)`, when its answer is only proposed: a
proposal nobody accepted is never hidden from the author.

**Depends on.** `BANK` and `applies` from the package, and `check` for the open lines.
"""

from __future__ import annotations

from .bank import BANK
from .brief import Answer, Brief
from .check import check
from .questions import applies


def _value(value: object) -> str:
    if isinstance(value, bool):
        return "yes" if value else "no"
    return "" if value is None else str(value)


def _bullet(head: str, value: str) -> list[str]:
    """A list item; extra lines of `value` stay indented under it."""
    first, *rest = value.split("\n") if value else [""]
    lines = [f"- {head} {first}".rstrip()]
    lines += [f"  {line}".rstrip() for line in rest]
    return lines


def _block(title: str, lines: list[str]) -> list[str]:
    return [f"## {title}", "", *(lines or ["None."]), ""]


def _applicable(brief: Brief):
    for question in BANK:
        if applies(question, brief.track, brief.answers):
            yield question, brief.answers.get(question.id)


def _groups(brief: Brief) -> list[str]:
    grouped: dict[str, list[str]] = {}
    for question, answer in _applicable(brief):
        if isinstance(answer, Answer) and answer.status == "answered":
            lines = _bullet(f"**{question.ask}**", _value(answer.value))
            grouped.setdefault(question.group, []).extend(lines)
    out: list[str] = []
    for group, lines in grouped.items():
        out += [f"## {group.capitalize()}", "", *lines, ""]
    return out


def _outline(brief: Brief) -> list[str]:
    lines: list[str] = []
    for section in brief.outline:
        lines += [f"### {section.title}", ""]
        for module in section.modules:
            lines.append(f"- {module.title}" + (" (pilot)" if module.pilot else ""))
            lines += [f"  - {lesson.title} [{lesson.depth}]" for lesson in module.lessons]
        lines.append("")
    return lines


def render(brief: Brief) -> str:
    """The brief as Markdown, LF only, ending in one newline."""
    decided: list[str] = []
    deferred: list[str] = []
    proposed: list[str] = []
    for question, answer in _applicable(brief):
        if answer is None:
            continue
        if answer.status == "answered" and answer.decided_by == "claude":
            decided += _bullet(f"`{question.id}`:", _value(answer.value))
        elif answer.status == "deferred":
            deferred += _bullet(f"`{question.id}`:", answer.reason or "")
        elif answer.status == "proposed" and question.tier == "later":
            proposed.append(f"- open: {question.id}: proposed, not yet accepted (later)")
    open_lines = [f"- {line}" for line in check(brief, private_ignored=True)] + proposed
    lines = [f"# {brief.title}", "", f"Track: {brief.track}", ""]
    lines += _groups(brief)
    lines += _block("Decided by Claude", decided)
    lines += _block("Deferred", deferred)
    lines += _block("Still open", open_lines)
    lines += ["## Outline", "", *(_outline(brief) or ["None."])]
    return "\n".join(lines).rstrip("\n") + "\n"
