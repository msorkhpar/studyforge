"""Shared by the quiz's tests: the prose fixture with a quiz in it, built and served.

⭐ **The corpus is the fixture `depth1/` — the prose fixture, the corpus the quiz
shape exists for — COPIED, with one practice document added**. ⛔ The
fixture itself is never touched; the quiz record is the one `depth1.py` builds
through `archive.document`, so the bytes on disk are the bytes a build reads.

⭐ **Two questions**, because one cannot tell *every question answered correctly*
from *this question answered correctly* — which is the whole of the completion
rule (`exercise.quiz.completes`).

⭐ **`served` is the REAL instance** — `serve.instance.instance_of` over a real
discovery, every namespace wired the way `studyforge serve` wires them — so a
test reads the route through the same guards a reader's page does.

⭐ **Every needle a leak test looks for is read off the record, never typed**:
`sentences()` and `KEYED` come out of `QUESTIONS`, which is what reaches disk.
"""

from __future__ import annotations

import contextlib
import json
import re
import shutil
import threading
from collections.abc import Iterator
from pathlib import Path

from studyforge.address import parse_unit_key
from studyforge.archive.document import build, render
from studyforge.generate import read_corpus, write_site
from studyforge.progress import practice_key
from studyforge.serve.app import ServingServer
from studyforge.serve.discovery import discover
from studyforge.serve.instance import instance_of
from studyforge.serve.routes.content import CorpusContent
from studyforge.unit import served
from tests.studyforge.execute.runnable import RAW, fixture_copy
from tests.studyforge.exercise.quiz.depth1 import fixture_root, practice_document, question

#: The unit the quiz is attached to, as the content namespace keys it.
UNIT = "depth-one/unit-01"

#: Where the copy's practice document is written, beside the lesson it is built from.
PRACTICE_DOCUMENT = Path("archive/depth-one/raw/prose/unit-01/practice-1.json")

#: The quiz's two questions. ⭐ The first is `depth1.py`'s own; the second is
#: written from the same passage of the same page.
QUESTIONS = [
    question(),
    question(
        id="q-2",
        stem="What is everything else in this corpus built from?",
        options=[
            {
                "id": "a",
                "text": "That one shape",
                "correct": True,
                "says": "The page ends on it: everything is built from the triple.",
            },
            {
                "id": "b",
                "text": "A table of rows",
                "correct": False,
                "says": "Rows are a spreadsheet's shape; this page never mentions one.",
            },
        ],
    ),
]

#: `{question id: the keyed option's id}` — the answers that complete the quiz.
KEYED = {
    one["id"]: next(option["id"] for option in one["options"] if option["correct"])
    for one in QUESTIONS
}

#: `{question id: a wrong option's id}`.
WRONG = {
    one["id"]: next(option["id"] for option in one["options"] if not option["correct"])
    for one in QUESTIONS
}


def says(question_id: str, option_id: str) -> str:
    """The sentence the record gives one option — what the server must answer for it."""
    asked = next(one for one in QUESTIONS if one["id"] == question_id)
    return next(option["says"] for option in asked["options"] if option["id"] == option_id)


def sentences() -> list[str]:
    """Every per-option sentence the quiz carries, keyed and not."""
    return [option["says"] for one in QUESTIONS for option in one["options"]]


def quiz_corpus(where: Path, layout: str | None = "page") -> Path:
    """Copy `depth1` under `where`, add the quiz, declare exercises, build it; return its root.

    ⭐ The quiz is the all-on-one-page layout unless `layout` says otherwise: the readings built
    on this corpus are about that layout, and `layout=None` is the default, one question at a time.
    """
    root = where / "depth1"
    shutil.copytree(fixture_root(), root)
    extra = {"layout": layout} if layout else {}
    document = practice_document(questions=QUESTIONS, **extra)
    (root / PRACTICE_DOCUMENT).write_text(render(document), encoding="utf-8")
    manifest = root / "corpus.json"
    declared = json.loads(manifest.read_text(encoding="utf-8"))
    declared["exercises"] = True
    manifest.write_text(json.dumps(declared, indent=2) + "\n", encoding="utf-8")
    write_site(root, root)
    return root


def source_of(root: Path) -> str:
    """The corpus's `source`, read from its own manifest."""
    return read_corpus(root).manifest.source


def practice_of(root: Path) -> str:
    """The quiz's practice key, read off the unit's generated document — never typed.

    ⭐ The same string the page carries in `data-practice-quiz`: both are
    `progress.practice_key` of the section the unit builder named.
    """
    document = served.parse(CorpusContent(read_corpus(root)).unit(UNIT) or "", "unit.json")
    section = next(part for part in document["sections"] if part.get("kind") == "practice")
    address, ordinal = parse_unit_key(UNIT, len(document["address"]))
    return practice_key(address, ordinal, section["key"])


def page_of(root: Path) -> Path:
    """The built unit page the quiz is rendered on."""
    pages = sorted((root / ".studyforge" / "depth-one" / "units" / "unit-01").glob("*.unit.html"))
    assert len(pages) == 1, pages
    return pages[0]


def built_texts(root: Path) -> dict[str, str]:
    """Every page and asset the build wrote, as text, keyed by its path under the root.

    ⛔ **The whole generated tree plus the root index, never a chosen few**: a key
    that leaked into a script, a stylesheet or a JSON island would be missed by a
    reading of the one page.
    """
    found = sorted((root / ".studyforge").rglob("*")) + [root / "index.html"]
    return {
        path.relative_to(root).as_posix(): path.read_text(encoding="utf-8", errors="replace")
        for path in found
        if path.is_file()
    }


#: What an attribute carrying an option's correctness looks like in any spelling.
KEY_ATTRIBUTE = re.compile(r"data-[a-z-]*correct", re.I)


@contextlib.contextmanager
def served_instance(root: Path) -> Iterator[ServingServer]:
    """`studyforge serve`'s own instance over the corpus's parent, on a free loopback port."""
    server = instance_of(discover(root.parent), port=0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield server
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


# ⭐ One unit carrying a code practice AND a quiz — the runnable fixture's
# first unit, whose code practice runs on the host, with a quiz added after it.

#: The unit the quiz joins, and where its document is written in the copy.
MIXED_UNIT = "kata/unit-01"
MIXED_DOCUMENT = RAW / "unit-01" / "practice-2.json"

#: The quiz's one question, written from the unit's own page.
MIXED_QUESTION = {
    "id": "q-1",
    "stem": "What does the page's grader say about the file as shipped?",
    "options": [
        {"id": "a", "text": "Its test passes", "correct": True, "says": "The lesson says so."},
        {"id": "b", "text": "Its test fails", "correct": False, "says": "That is unit 2."},
    ],
    "origin": {"path": "kata/01-greeting.md", "section": "Lesson: A test that passes"},
}


def mixed_corpus(where: Path) -> Path:
    """Copy the runnable fixture, give unit 1 a quiz after its code practice, build it."""
    root = fixture_copy(where)
    container = root / "archive" / "kata" / "container.json"
    declared = json.loads(container.read_text(encoding="utf-8"))
    declared["units"][0]["practices"] = 2
    container.write_text(json.dumps(declared, indent=2) + "\n", encoding="utf-8")
    code = json.loads((root / RAW / "unit-01" / "practice-1.json").read_text(encoding="utf-8"))
    document = build(
        source=code["source"],
        address=code["address"],
        variant=code["variant"],
        unit=1,
        kind="practice",
        ordinal=2,
        ingested=code["ingested"],
        title="Check yourself: greeting",
        blocks=[
            {"type": "heading", "level": 2, "text": "Check yourself"},
            {"type": "para", "text": "One question on what this page has just taught."},
        ],
        exercise={"kind": "quiz", "questions": [MIXED_QUESTION]},
    )
    (root / MIXED_DOCUMENT).write_text(render(document), encoding="utf-8")
    write_site(root, root)
    return root


def practices_of(root: Path, unit: str) -> dict[str, str]:
    """`{'code' | 'quiz': practice key}` for one unit, read off its generated document."""
    document = served.parse(CorpusContent(read_corpus(root)).unit(unit) or "", "unit.json")
    address, ordinal = parse_unit_key(unit, len(document["address"]))
    return {
        "quiz" if part["workspace"].get("kind") == "quiz" else "code": practice_key(
            address, ordinal, part["key"]
        )
        for part in document["sections"]
        if part.get("kind") == "practice"
    }
