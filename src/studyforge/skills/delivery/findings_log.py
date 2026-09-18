r"""The findings log a conversion writes — ⛔ a run that writes none is not done.

**What it does.** Renders the log a conversion run leaves in the corpus it
converted, one block per `Finding`, each carrying a **disposition slot** that
asks the question the integration catalogue's admission rule turns on —
*could a skill have generated this?* — and reads a log back at the end of the run, refusing one
that is absent, empty or missing a slot rather than letting the run close green.

**How you use it.**

    from studyforge.skills.delivery import Disposition, Entry, FindingsLog, closing

    log = FindingsLog(run="the first conversion", entries=(
        Entry(finding),                                   # the slot starts open
        Entry(other, Disposition("yes", "the onboarding skill's pin check")),
    ))
    text = "\n".join(log.lines()) + "\n"   # the caller writes it at `LOG`
    print("\n".join(closing(text)))        # ⛔ `closing(None)` refuses

**Depends on.** `dataclasses`, `re`, and this package's `finding` and
`refusal`. ⛔ Not on the filesystem: the caller names the file, the same rule
every module here keeps.

## ⛔ Why a skill obliges this, and why it is not a message

⚠️ **`W346`, measured:** the first conversion obliged no log, so its milestone's
whole deliverable was produced by hand a milestone later, by an office reading
commit bodies — and two of its seven numbered findings existed only in a
hand-back message and were found in no ref at all. ⭐ **A finding written into
the corpus, at a place the skill names, survives the message that announced
it.** The place is `.studyforge/`, which the validator already skips as this
tool's directory, so writing the log never makes the corpus it describes invalid.

## ⭐ The slot is the sort, started early

The catalogue's `QA-04` sort asked one question of every finding: *could a
skill have generated this?* **`yes`** is a hole in a skill (R19) and names
where it goes; **`no`** is a candidate entry and says why no generator could
write it; **`open`** is the question not yet asked. ⛔ `open` is allowed — the
conversion may not be the office that sorts — but `closing` counts it aloud,
so an unsorted log is reported as unsorted rather than read as done.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from studyforge.skills.delivery.finding import Finding
from studyforge.skills.delivery.refusal import one_or_all

#: ⭐ Where the log lives, relative to the corpus root: inside the tool's own
#: directory, which `validate` skips, so the log is never read as material.
LOG = ".studyforge/findings.md"

#: The question the catalogue's R19 refusal turns on, in the `QA-04` sort's words.
QUESTION = "could a skill have generated this?"

#: ⛔ Closed. `yes` is a hole in a skill, `no` a catalogue candidate, `open` unasked.
ANSWERS = ("yes", "no", "open")

#: The log's first line, which is how `closing` knows the text is a log at all.
TITLE = "# Findings log"

_HEADING = re.compile(r"^### (\S+) `\[(\w+)\]` — ", re.M)
_SLOT = re.compile(r"^  - \*" + re.escape(QUESTION) + r"\* \*\*(\w+)\*\*(?: — (\S.*))?$", re.M)


class LogRefused(Exception):
    """Raised when a findings log could not be written, or a run closes without one."""


@dataclass(frozen=True, slots=True)
class Disposition:
    """One answer to `QUESTION`, with the reason it carries."""

    answer: str = "open"
    why: str = ""

    def __post_init__(self) -> None:
        """Refuse an answer outside the three, or a settled answer with no reason."""
        if self.answer not in ANSWERS:
            raise LogRefused(f"a disposition answers {QUESTION!r} with one of {', '.join(ANSWERS)}")
        if (self.answer == "open") == bool(self.why.strip()):
            raise LogRefused(
                "an `open` disposition carries no reason, and a settled one carries "
                "the skill it is a hole in (`yes`) or why no generator could write it (`no`)"
            )

    def line(self) -> str:
        """Render as the slot line under a finding."""
        tail = f" — {self.why.strip()}" if self.why.strip() else ""
        return f"  - *{QUESTION}* **{self.answer}**{tail}"


@dataclass(frozen=True, slots=True)
class Entry:
    """A finding in the log, and its slot."""

    finding: Finding
    disposition: Disposition = field(default_factory=Disposition)

    def lines(self) -> list[str]:
        """Render the finding's own block, then its slot — ⛔ a `none` carries no slot."""
        if self.finding.marker == "none":
            return self.finding.lines()
        return [*self.finding.lines(), self.disposition.line()]


@dataclass(frozen=True, slots=True)
class FindingsLog:
    """Every finding one conversion run produced, each with its slot."""

    run: str
    entries: tuple[Entry, ...]

    def __post_init__(self) -> None:
        """Refuse a log that cannot be read back — every reason named at once."""
        reasons: list[str] = []
        if not self.run.strip():
            reasons.append("a findings log names its run")
        ids = [entry.finding.id for entry in self.entries]
        if not ids:
            reasons.append(
                "a findings log with no entry. ⛔ Zero is written as one `none` "
                "finding, never as an empty log"
            )
        repeated = sorted({one for one in ids if ids.count(one) > 1})
        if repeated:
            reasons.append(f"a finding id appears twice: {', '.join(repeated)}")
        if len(ids) > 1 and any(entry.finding.marker == "none" for entry in self.entries):
            reasons.append("a `none` finding stands beside a real one, and it writes zero")
        if reasons:
            raise LogRefused(one_or_all(reasons))

    def lines(self) -> list[str]:
        """Render the whole log, which `closing` reads back."""
        body: list[str] = [f"{TITLE} — {self.run.strip()}", ""]
        body.append(
            "⛔ Written by the conversion before the run is declared done. "
            f"Every finding asks: *{QUESTION}*"
        )
        for entry in self.entries:
            body += ["", *entry.lines()]
        return body


def _gaps(text: str) -> tuple[list[str], dict[str, str], list[str]]:
    """Read every finding and its slot; return what is missing, the answers, the markers."""
    headings = list(_HEADING.finditer(text))
    reasons: list[str] = []
    answers: dict[str, str] = {}
    markers = [heading.group(2) for heading in headings]
    ends = [heading.start() for heading in headings[1:]] + [len(text)] * bool(headings)
    for heading, end in zip(headings, ends, strict=True):
        found, marker = heading.group(1), heading.group(2)
        slots = list(_SLOT.finditer(text, heading.end(), end))
        if marker == "none":
            continue
        if len(slots) != 1:
            reasons.append(f"{found} carries {len(slots) or 'no'} disposition slot(s), not one")
        elif slots[0].group(1) not in ANSWERS:
            reasons.append(f"{found} answers {slots[0].group(1)!r}, outside {', '.join(ANSWERS)}")
        elif (slots[0].group(1) == "open") == bool(slots[0].group(2)):
            reasons.append(f"{found}'s `{slots[0].group(1)}` does not match its reason")
        else:
            answers[found] = slots[0].group(1)
    return reasons, answers, markers


def closing(text: str | None) -> list[str]:
    """Read the log at the end of a run; ⛔ refuse, never pass, one that is not there.

    `text` is the log's text, or `None` when nothing is at `LOG`. Returns the
    report a run closes on — every finding and its answer, and how many are
    still `open`. ⛔ Refuses, naming every gap at once, an absent log, text
    that is not a log, a log with no finding, and a finding with no slot.
    """
    if text is None:
        raise LogRefused(
            f"no findings log at {LOG}. ⛔ A run that writes none is not done, and "
            "what it found survives only in a message"
        )
    reasons: list[str] = []
    if not text.startswith(TITLE):
        reasons.append(f"the text at {LOG} does not open with {TITLE!r}")
    gaps, answers, markers = _gaps(text)
    if not markers:
        reasons.append("the log carries no finding; zero is written as one `none` finding")
    if "none" in markers and len(markers) > 1:
        reasons.append("a `none` finding stands beside a real one, and it writes zero")
    reasons += gaps
    if reasons:
        raise LogRefused(one_or_all(reasons))
    report = [f"{found}  {answer}" for found, answer in answers.items()]
    unsorted = sum(answer == "open" for answer in answers.values())
    if not answers:
        report.append("none: the run recorded that it found nothing")
    report.append(
        f"open: {unsorted} — the sort is not done" if unsorted else "open: 0 — every finding sorted"
    )
    return report
