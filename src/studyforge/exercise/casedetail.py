"""What a graded run's report says about each case beyond pass or fail.

**What it does.** Reads the same JUnit report `report.breakdown_of` folds and answers, per declared
case, the
failure message the test tool wrote (the assertion's own words, which carry the input, the expected
and the
actual value when the test says them), the lines the reader's code LOGGED while that case ran, and
what it PRINTED.
Lines no case owns are kept for the whole run. ⛔ It reads a file a run left behind and starts
nothing.

**How you use it.**

    detail = detail_of(exercise, source_root, where, started=started)   # `None` where there is no
    report
    for case in detail.cases: case.id, case.passed, case.message, case.log, case.out, case.err
    detail.log, detail.out, detail.err, detail.truncated

**Depends on.** `report` for the files, their freshness and the parse; `spelling` for which declared
case a
`<testcase>` is. ⛔ Not on `execute` or `serve`.

## ⭐ Two kinds of text, told apart by a marker, never by a guess

The reader's code logs through its language's own logger, and the test harness's handler writes each
line as
`[log] LEVEL name: message` (a line of the case's own `<system-out>`) or `[log:<test name>] LEVEL
name: message`
(a line of the suite's output, which names the test that was running, for a tool that records output
once per
suite). Every other line is what the code PRINTED. ⛔ **They are kept apart on purpose**: a practice
may grade
printed output, so the printed lines are never mixed into the log, and nothing here ever decides a
verdict.
pytest writes the sections `Captured Log`, `Captured Out` and `Captured Err` into a case's output;
those headers
decide a line's kind where they are present.

## ⛔ Bounded

All text kept for one run is at most `MAX_LINES` lines and `MAX_BYTES` bytes, and a message at most
`MAX_MESSAGE` characters; what does not fit is dropped from the FRONT of a stream's tail (the last
lines are the
ones a reader needs) and `truncated` says so. ⭐ A report that carries none of this (an older course)
gives
messages only, and a case with nothing to show has empty tuples.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from xml.etree import ElementTree

from studyforge.exercise.cases import Case
from studyforge.exercise.errors import ExerciseError
from studyforge.exercise.record import Exercise
from studyforge.exercise.report import _files, _identify, _parse, _passed, _require_fresh
from studyforge.exercise.spelling import file_level_failure, spells

#: The most lines and bytes of captured text kept for one run, over every case and the run.
MAX_LINES = 200
MAX_BYTES = 20 * 1024
#: The most characters kept of one case's failure message.
MAX_MESSAGE = 4000
#: The most lines of one kind kept for one case, so a noisy case cannot starve the ones after it.
CASE_LINES = 50

#: A logged line: `[log] text` in a case's own output, or `[log:<test>] text` in a suite's.
LOG_LINE = re.compile(r"^\[log(?::(.*?))?\] ?(.*)$")
#: The section headers pytest writes between the kinds of output it captured.
SECTION = re.compile(r"^-+ Captured (Log|Out|Err) -+$")

LOG, OUT, ERR = "log", "out", "err"
_SECTION_KIND = {"Log": LOG, "Out": OUT, "Err": ERR}


@dataclass(frozen=True, slots=True)
class CaseDetail:
    """One declared case: its verdict, its failure message and the text captured while it ran."""

    id: str
    passed: bool
    message: str = ""
    log: tuple[str, ...] = ()
    out: tuple[str, ...] = ()
    err: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class Detail:
    """A run's cases in the corpus's order, and the lines no case owns."""

    cases: tuple[CaseDetail, ...]
    log: tuple[str, ...] = ()
    out: tuple[str, ...] = ()
    err: tuple[str, ...] = ()
    #: True where some captured text was dropped to stay inside the bounds.
    truncated: bool = False
    #: True where printed text was recorded per case (the tool writes it per test).
    per_case_out: bool = False


@dataclass
class _Lines:
    log: list[str] = field(default_factory=list)
    out: list[str] = field(default_factory=list)
    err: list[str] = field(default_factory=list)

    def add(self, kind: str, line: str) -> None:
        getattr(self, kind).append(line)


def detail_of(exercise: Exercise, root: Path, where: str, *, started: float) -> Detail | None:
    """Return what the report says per case, or `None` where there is no report to read.

    ⭐ Refuses what `breakdown_of` refuses (a stale or unreadable report, a test no case names), so a
    reader is
    never shown text from a run that did not write it. `None` is also the answer for a record with
    no cases.
    """
    cases, report = exercise.cases, exercise.report
    if cases is None or report is None or not exercise.breaks_down:
        return None
    files = _files(root / report.path)
    if not files:
        return None
    _require_fresh(files, report.path, where, started=started)
    return _read(files, cases, report.path, where)


def _read(files: tuple[Path, ...], cases: tuple[Case, ...], declared: str, where: str) -> Detail:
    ids = tuple(case.id for case in cases)
    own: dict[str, _Lines] = {}
    passed: dict[str, bool] = {}
    messages: dict[str, str] = {}
    names: dict[str, str] = {}
    suite = _Lines()
    for path in files:
        root = _parse(path, declared, where)
        for element in root.iter("testcase"):
            if file_level_failure(element) and not any(spells(element, one) for one in ids):
                continue
            case_id = _identify(element, ids, declared, path, where)
            names[element.get("name", "")] = case_id
            passed[case_id] = _passed(element)
            messages[case_id] = _message(element)
            own.setdefault(case_id, _Lines())
            for child in element:
                if child.tag in ("system-out", "system-err"):
                    _classify(child, own[case_id])
        for holder in dict.fromkeys((root, *root.iter("testsuite"))):
            for child in holder:
                if child.tag in ("system-out", "system-err"):
                    _classify(child, suite, named=True)
    per_case_out = any(lines.out or lines.err for lines in own.values())
    _attribute(suite, own, names)
    return _bounded(cases, own, passed, messages, suite, per_case_out)


def _message(element: ElementTree.Element) -> str:
    """The failure's own message, as the test tool wrote it; empty where the case passed."""
    for child in element:
        if child.tag in ("failure", "error"):
            text = child.get("message") or (child.text or "").strip()
            return text.strip()[:MAX_MESSAGE]
    return ""


def _classify(output: ElementTree.Element, into: _Lines, *, named: bool = False) -> None:
    """File each line of one `<system-out>` or `<system-err>` as log, printed or error text."""
    kind = ERR if output.tag == "system-err" else OUT
    for raw in (output.text or "").splitlines():
        header = SECTION.match(raw)
        if header:
            kind = _SECTION_KIND[header.group(1)]
            continue
        if not raw.strip() and kind != LOG:
            continue
        marked = LOG_LINE.match(raw)
        if marked:
            into.add(LOG, raw if named and marked.group(1) is not None else marked.group(2))
        else:
            into.add(kind, raw)


def _attribute(suite: _Lines, own: dict[str, _Lines], names: dict[str, str]) -> None:
    """Move the suite's `[log:<test>]` lines to their case; keep the rest as the run's."""
    kept: list[str] = []
    for line in suite.log:
        marked = LOG_LINE.match(line)
        owner = names.get(marked.group(1) or "") if marked else None
        if marked and owner is not None:
            own[owner].log.append(marked.group(2))
        elif marked and marked.group(1) is not None:
            kept.append(marked.group(2))
        else:
            kept.append(line)
    suite.log = kept


def _bounded(
    cases: tuple[Case, ...],
    own: dict[str, _Lines],
    passed: dict[str, bool],
    messages: dict[str, str],
    suite: _Lines,
    per_case_out: bool,
) -> Detail:
    """Keep each stream's last lines within the run's budget; say whether any were dropped."""
    budget = [MAX_LINES, MAX_BYTES]
    dropped = [False]

    def take(lines: list[str], limited: bool = True) -> tuple[str, ...]:
        kept: list[str] = []
        for line in reversed(lines[-CASE_LINES:] if limited else lines):
            size = len(line.encode("utf-8", "replace")) + 1
            if budget[0] < 1 or budget[1] < size:
                dropped[0] = True
                break
            budget[0] -= 1
            budget[1] -= size
            kept.append(line)
        if len(kept) < len(lines):
            dropped[0] = True
        return tuple(reversed(kept))

    found = []
    for case in cases:
        lines = own.get(case.id, _Lines())
        found.append(
            CaseDetail(
                case.id,
                passed.get(case.id, False),
                messages.get(case.id, ""),
                take(lines.log),
                take(lines.out),
                take(lines.err),
            )
        )
    return Detail(
        tuple(found),
        take(suite.log, False),
        take(suite.out, False),
        take(suite.err, False),
        dropped[0],
        per_case_out,
    )


__all__ = ["CaseDetail", "Detail", "ExerciseError", "detail_of"]
