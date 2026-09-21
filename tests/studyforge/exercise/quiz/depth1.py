"""A quiz built from `depth1`'s own material — the corpus this shape exists for.

⭐ **`AX-05`'s Acceptance is taken on `FND-04`'s `depth1/`**, the 1-level,
zero-exercise prose fixture: a corpus whose subject is not code, which is what
the quiz shape is for. ⛔ **The fixture itself is NOT modified.** A quiz
practice is BUILT here, from the lesson document `depth1` already ships, and
read back through `archive.document` — so the reading is taken on that
corpus's material without touching a fixture other offices pin counts against.

⛔ **The question is DERIVED from the page, not pasted beside it.** Its
`origin` names the page the container map declares for unit 1 and the section
names that lesson's own heading, and `test_depth1.py` asserts the keyed
option's words are in the lesson's own prose. ⚠️ A quiz whose answer is
nowhere on the page is gate `Q1`'s failure, and a fixture that could not be
checked against the page would be the same failure in a test.

⚠️ **The origin path is a LITERAL here and is checked by containment against
the container map's bytes**, never by reading that map's `origin` key: `W109`
holds `origin` to one reader in `src/` and `tests/`, and a second site reading
it — even a test's — is what that instrument exists to refuse.

⛔ Mirrors no source module (R12 is one-way): it is material, not a test.
"""

from __future__ import annotations

import json
from pathlib import Path

from studyforge.archive.document import build, parse, render
from tests.support import repository_root

#: `depth1`, as `FND-04` shipped it.
FIXTURE = "tests/fixtures/depth1"

#: The container this corpus's one level holds.
ADDRESS = ("depth-one",)

#: The unit the quiz is attached to, and the lesson it is written from.
UNIT = 1
LESSON = "raw/prose/unit-01/lesson-1.json"

#: The page unit 1 came from, as `depth1`'s container map declares it.
#: ⛔ A literal, corroborated by containment — see the contract above.
PAGE = "depth-one/01-what-a-triple-is.md"


def fixture_root() -> Path:
    """Where `depth1` lives, found from this file rather than from the cwd."""
    return repository_root() / FIXTURE


def lesson() -> dict:
    """The lesson document the quiz is written from, read from the fixture."""
    path = fixture_root() / "archive" / ADDRESS[0] / LESSON
    return json.loads(path.read_text(encoding="utf-8"))


def container_text() -> str:
    """The container map's bytes, for the containment check on `PAGE`."""
    return (fixture_root() / "archive" / ADDRESS[0] / "container.json").read_text(encoding="utf-8")


def section() -> str:
    """The heading the quiz's passage is bounded by — the lesson's own first heading."""
    return next(block["text"] for block in lesson()["blocks"] if block["type"] == "heading")


def passage() -> str:
    """The lesson's prose, which is where the answer has to be."""
    return " ".join(block["text"] for block in lesson()["blocks"] if block["type"] == "para")


def question(**changes) -> dict:
    """The quiz's one question, with `changes` applied; a `None` value removes a key."""
    asked = {
        "id": "q-1",
        "stem": "What three things does a triple say?",
        "options": [
            {
                "id": "a",
                "text": "A subject, a predicate and an object",
                "correct": True,
                "says": "The page says a triple is those three, said in one breath.",
            },
            {
                "id": "b",
                "text": "A graph, a node and an edge",
                "correct": False,
                "says": "Those are words for drawing a graph, not for what a triple says.",
            },
            {
                "id": "c",
                "text": "A prefix, a namespace and a file",
                "correct": False,
                "says": "The page's prefix line is notation; it is not what a triple is.",
            },
        ],
        "origin": {"path": PAGE, "section": section()},
    }
    asked.update(changes)
    return {key: value for key, value in asked.items() if value is not None}


def record(**changes) -> dict:
    """The quiz record `depth1`'s practice carries, with `changes` applied."""
    out = {"kind": "quiz", "questions": [question()], **changes}
    return {key: value for key, value in out.items() if value is not None}


def practice_document(**changes) -> dict:
    """The whole practice document, built through `archive.document` and its gates."""
    return build(
        source=json.loads((fixture_root() / "corpus.json").read_text(encoding="utf-8"))["source"],
        address=list(ADDRESS),
        variant="prose",
        unit=UNIT,
        kind="practice",
        ordinal=1,
        ingested=lesson()["ingested"],
        title="Check yourself: what a triple is",
        blocks=[
            {"type": "heading", "level": 2, "text": "Check yourself"},
            {"type": "para", "text": "Three questions on what you have just read."},
        ],
        exercise=record(**changes),
    )


def on_disk(**changes) -> dict:
    """The same document, rendered to the bytes that reach disk and read back.

    ⭐ **The round trip a build actually takes**, so nothing here is read out
    of a dict that was never serialised.
    """
    return parse(render(practice_document(**changes)), "depth-one/unit-01/practice-1")
