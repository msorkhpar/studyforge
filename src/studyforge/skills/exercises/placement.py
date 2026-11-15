r"""Where each practice stands on its page: beside the section it practises, or at the unit's end.

**What it does.** A practice helps most next to the part it exercises, while that part is still in
the reader's head, and it stays short because it practises one section. So a practice whose plan
draws on **one** section stands right after that section: its `<!-- practice N -->` marker sits
under that section's heading (or under one nested in it). A practice that **combines** several
sections is the exception a unit adds only when mixing them is the point; it stands after the last
of the sections it combines, which is usually the unit's end, and it may be a little longer. A
practice no marker places is drawn after the whole lesson, so a one-section practice without a
marker is reported too.

This module reads a page's lesson and its practice plan (`exercises/**/coverage.json`: each slot's
aspects, each aspect's `section:<heading>` basis) and returns what stands in the wrong place.

**How you use it.**

    from studyforge.skills.exercises.placement import misplaced, corpus_findings

    for problem in misplaced(lesson_text, plan):          # one page
        print(problem.slot, problem.message)

    python -m studyforge.skills.exercises.placement <corpus root>   # every page with a plan

The command prints one line per misplaced practice and exits 1 when there is any, 0 when none.

**Depends on.** The standard library only. The marker is the one `render/page/placed.py` draws
a practice at; slot `N` of a plan is practice `N` of its page.
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from studyforge.archive.scrub import assert_clean

#: The line a lesson places practice `N` with (the same spelling `render/page/placed.py` reads).
MARKER = re.compile(r"^\s*<!--\s*practice\s+(\d+)\s*-->\s*$")

#: A Markdown heading line, and a fence line that opens or closes a code block.
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
FENCE = re.compile(r"^\s*(```|~~~)")

#: The prefix a plan's basis gives a section of prose.
SECTION = "section:"


@dataclass(frozen=True, slots=True)
class Misplaced:
    """One practice that stands somewhere other than where its plan says it belongs."""

    slot: int
    message: str


@dataclass(frozen=True, slots=True)
class _Heading:
    line: int
    level: int
    text: str


def _read(text: str) -> tuple[list[_Heading], dict[int, int]]:
    """Return the page's headings and each marker's line, skipping fenced code."""
    headings: list[_Heading] = []
    markers: dict[int, int] = {}
    fenced = False
    for number, line in enumerate(text.splitlines()):
        if FENCE.match(line):
            fenced = not fenced
            continue
        if fenced:
            continue
        heading = HEADING.match(line)
        if heading:
            headings.append(_Heading(number, len(heading.group(1)), heading.group(2)))
            continue
        marker = MARKER.match(line)
        if marker:
            markers.setdefault(int(marker.group(1)), number)
    return headings, markers


def _under(headings: list[_Heading], line: int) -> list[_Heading]:
    """Return the chain of headings a line stands under, outermost first."""
    chain: list[_Heading] = []
    for heading in headings:
        if heading.line > line:
            break
        while chain and chain[-1].level >= heading.level:
            chain.pop()
        chain.append(heading)
    return chain


def _sections(plan: dict) -> dict[int, list[str]]:
    """Return each slot's sections, in the order its aspects name them."""
    basis = {
        aspect.get("id"): [
            b[len(SECTION) :] for b in aspect.get("basis") or [] if b.startswith(SECTION)
        ]
        for aspect in plan.get("aspects") or []
    }
    found: dict[int, list[str]] = {}
    for exercise in plan.get("exercises") or []:
        slot = exercise.get("slot")
        if not isinstance(slot, int):
            continue
        names: list[str] = []
        for aspect in exercise.get("aspects") or []:
            for name in basis.get(aspect, []):
                if name not in names:
                    names.append(name)
        found[slot] = names
    return found


def misplaced(text: str, plan: dict) -> list[Misplaced]:
    """Return the practices of this page that do not stand where their plan says they belong."""
    headings, markers = _read(text)
    end = len(text.splitlines())
    known = {heading.text for heading in headings}
    problems: list[Misplaced] = []
    for slot, names in sorted(_sections(plan).items()):
        names = [name for name in names if name in known]
        if not names:
            continue
        where = markers.get(slot, end)
        placed = "its marker" if slot in markers else "no marker, so it is drawn after the lesson"
        chain = [heading.text for heading in _under(headings, where)]
        if len(names) == 1:
            if names[0] not in chain:
                stands = f"under '{chain[-1]}'" if chain else "before the first section"
                problems.append(Misplaced(slot, (
                    f"practice {slot} practises one section, '{names[0]}', but stands {stands} "
                    f"({placed}). Put `<!-- practice {slot} -->` right after that section, so it "
                    f"helps that part while it is fresh."
                )))
            continue
        last = max((h for h in headings if h.text in names), key=lambda h: h.line)
        if where < last.line:
            problems.append(Misplaced(slot, (
                f"practice {slot} combines {len(names)} sections ({', '.join(names)}), but stands "
                f"before '{last.text}', the last of them. A practice that combines sections "
                f"stands after all of them, at the unit's end."
            )))
    return problems


def corpus_findings(root: Path) -> list[tuple[str, Misplaced]]:
    """Return every misplaced practice of the corpus at `root`, by the page it is on."""
    found: list[tuple[str, Misplaced]] = []
    for coverage in sorted((root / "exercises").rglob("coverage.json")):
        document = json.loads(coverage.read_text(encoding="utf-8"))
        assert_clean(document, coverage.relative_to(root).as_posix())
        page, plan = document.get("page"), document.get("plan")
        if not isinstance(page, str) or not isinstance(plan, dict) or not (root / page).is_file():
            continue
        lesson = (root / page).read_text(encoding="utf-8")
        found.extend((page, problem) for problem in misplaced(lesson, plan))
    return found


def main(argv: list[str]) -> int:
    """Print every misplaced practice of the corpus at `argv[0]`; exit 1 when there is any."""
    if len(argv) != 1:
        print("usage: python -m studyforge.skills.exercises.placement <corpus root>")
        return 2
    found = corpus_findings(Path(argv[0]))
    for page, problem in found:
        print(f"{page}: {problem.message}")
    print(f"placement: {len(found)} practice(s) misplaced")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
