"""Hand-built authored corpora for the staleness readings, recorded as the pass records a unit.

⭐ **No pass is run to build one**: each unit is a page, a test file, a coverage
report whose digests are the ledger's own reading of those files, and its two
folders. A real pass over the same shape is `test_corpus`'s; here what is under
test is only what a report says against what the corpus holds now.

⛔ Nothing here asserts: a helper that asserted would be an instrument nobody
names.
"""

from __future__ import annotations

import json
from pathlib import Path

from studyforge.skills.exercises.ledger import source_digest
from studyforge.skills.exercises import (
    CORE,
    COVERAGE_API,
    COVERAGE_FILENAME,
    Aspect,
    file_digest,
    plan_document,
    plan_for,
)

#: ⛔ A home path planted in a report, spelled in two halves so this file carries none.
LEAK = "/" + "home/someone/notes"

#: What every fixture page teaches, checked by one exercise.
ASPECTS = (
    Aspect("greets", "a greeting names who it greets", ("section:Greeting",), exercise="greet"),
)


def unit_of(number: int) -> str:
    """The bundles' folder of fixture unit `number`."""
    return f"exercises/kata/python/unit-{number:02d}"


def practice_of(number: int) -> str:
    """The practice counterpart of fixture unit `number`."""
    return f"practice/kata/python/unit-{number:02d}"


def page_of(number: int) -> str:
    """The page fixture unit `number` was authored from."""
    return f"lessons/page-{number:02d}.md"


def grader_of(number: int) -> str:
    """The test file fixture unit `number` was authored from."""
    return f"tests/test_page_{number:02d}.py"


def tryit_of(number: int) -> str:
    """The try-it file fixture unit `number`'s practice was copied from."""
    return f"source/unit-{number:02d}/practice-1/python/tryit/try_it.py"


def plan_of(aspects: tuple[Aspect, ...] = ASPECTS) -> dict:
    """The plan document the pass records for `aspects`."""
    return plan_document(plan_for(aspects, CORE, "the fixture"))


def authored(root: Path, number: int = 1) -> str:
    """Write fixture unit `number` as a pass leaves it, and return its bundles' folder."""
    unit, page, tests = unit_of(number), page_of(number), grader_of(number)
    write(root, page, f"# Page {number}\n\n## Greeting\n\nSay hello.\n")
    write(root, tests, "def test_greets():\n    assert True\n")
    tryit = tryit_of(number)
    write(root, tryit, "print('try it')\n")
    report = {
        "coverage_api": COVERAGE_API,
        "page": page,
        "kind": "code",
        "quiz": None,
        "case": "code-and-tests",
        "digests": {path: file_digest(root, path, "the fixture") for path in (page, tests)},
        "sources": {tryit: source_digest(root, tryit, "the fixture")},
        "plan": plan_of(),
        "shipped": [f"{unit}/practice-1"],
        "accounts": [],
        "shortfalls": [],
    }
    write(root, f"{unit}/{COVERAGE_FILENAME}", json.dumps(report, indent=2) + "\n")
    write(root, f"{unit}/practice-1/bundle.json", "{}\n")
    write(root, f"{practice_of(number)}/practice-1/greeting.py", "def greet():\n    pass\n")
    return unit


def edit_report(root: Path, number: int, change) -> None:
    """Rewrite fixture unit `number`'s coverage report through `change(document)`."""
    path = root / unit_of(number) / COVERAGE_FILENAME
    document = json.loads(path.read_text(encoding="utf-8"))
    change(document)
    path.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")


def write(root: Path, path: str, text: str) -> None:
    """Write `text` at `path` under `root`, creating its folders."""
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")


def snapshot(root: Path) -> dict[str, bytes]:
    """Every file under `root` and its bytes, so a test can say nothing changed."""
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file() and ".git" not in path.relative_to(root).parts
    }
