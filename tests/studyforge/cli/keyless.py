"""Shared by the keyless-serving readings: a corpus-shaped root, its paths, every needle.

⭐ **The layout is ISO's**: the quiz corpus is built INTO its own root (`build . --out .`),
so the archive's `practice-1.json` sits under the served root; the exercise bundle's
`tests/quiz.json` is written where an authored bundle keeps it; a corpus document quotes
one sentence, hard-wrapped; and an editor's backup of the bundle (`quiz.json~`, a type the
static mount does not know) sits beside it. ⭐ The runnable corpus is its sibling, so one
root serves a quiz and code practices together.

⛔ **The needles are read off the quiz record** (`quizzing.QUESTIONS`), never typed, and
they are spelled HERE rather than imported from `serve.withheld`: a reading that shared the
product's pattern would go blind exactly when the product did.

⛔ **The population is every file under the served root**, walked, plus every endpoint
of every namespace — never a chosen few paths.
"""

from __future__ import annotations

import html
import json
import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote

from studyforge.generate import read_corpus
from tests.studyforge.serve.routes.quizzing import (
    PRACTICE_DOCUMENT,
    QUESTIONS,
    practice_of,
    quiz_corpus,
    sentences,
    source_of,
)
from tests.studyforge.serve.routes.running import served_copy
from tests.studyforge.serve.serving import fetch

#: Where an authored bundle keeps a quiz's key, as the ISO corpus does.
BUNDLE = Path("exercises/depth-one/prose/unit-01/practice-1/tests/quiz.json")

#: An editor's backup of it: a suffix the static mount has no type for.
BACKUP = BUNDLE.with_name("quiz.json~")

#: A corpus document that quotes one sentence, wrapped across two lines.
NOTES = Path("docs/notes.md")

#: The key, structurally: a JSON pair, or an option attribute a page built without
#: server grading carries — read as the key only beside one of the served quiz's
#: question ids.
KEY = re.compile(r'"correct"\s*:\s*(?:true|false)|data-[a-z-]*-correct\b')
QUESTION_IDS = tuple(f'"{question["id"]}"' for question in QUESTIONS)


@dataclass(frozen=True)
class Layout:
    """The served root, the quiz corpus built into it, and the runnable corpus beside it."""

    root: Path
    quiz: Path
    runnable: Path


def layout(where: Path) -> Layout:
    """Build the corpus-shaped root under `where`."""
    quiz = quiz_corpus(where)
    for path in (BUNDLE, BACKUP):
        (quiz / path).parent.mkdir(parents=True, exist_ok=True)
        (quiz / path).write_text(json.dumps({"questions": QUESTIONS}, indent=2), "utf-8")
    words = QUESTIONS[0]["options"][1]["says"].split()
    wrapped = " ".join(words[:4]) + "\n" + " ".join(words[4:])
    (quiz / NOTES).parent.mkdir(parents=True, exist_ok=True)
    (quiz / NOTES).write_text(f"# Notes\n\nWhy b is wrong:\n{wrapped}\n", "utf-8")
    return Layout(where, quiz, served_copy(where))


def carried(body: bytes) -> list[str]:
    """Every needle `body` holds: the key's structure, and each sentence in any spelling."""
    text = " ".join(body.decode("utf-8", errors="replace").split())
    keyed = KEY.search(text) and any(one in text for one in QUESTION_IDS)
    found = ["key"] if keyed else []
    for sentence in sentences():
        forms = {sentence, json.dumps(sentence)[1:-1], html.escape(sentence)}
        if any(" ".join(form.split()) in text for form in forms):
            found.append(sentence)
    return found


def files_under(served: Path) -> list[str]:
    """Every file under the served root, as the URL path the static mount answers it at."""
    return sorted(
        "/" + "/".join(quote(part) for part in path.relative_to(served).parts)
        for path in served.rglob("*")
        if path.is_file()
    )


def endpoints(layout: Layout, qualified: bool) -> list[str]:
    """Every `GET` endpoint of every namespace, over every unit of both corpora."""
    found = ["/api", "/api/v1", "/api/v1/content/toc", "/api/v1/state/", "/api/v1/run/"]
    found += ["/api/v1/run/client.js", "/api/v1/quiz/"]
    for root in (layout.quiz, layout.runnable) if qualified else (layout.quiz,):
        corpus = read_corpus(root)
        source = corpus.manifest.source
        prefix = f"{source}/" if qualified else ""
        found.append(f"/api/v1/state/{source}")
        for unit in corpus.units:
            found.append(f"/api/v1/content/units/{prefix}{unit.key}")
            found.append(f"/api/v1/state/{source}/units/{unit.key}")
    return found


def acts(layout: Layout) -> list[str]:
    """Every `POST` a page can make about the quiz practice, except grading it."""
    source, practice = source_of(layout.quiz), practice_of(layout.quiz)
    return [f"/api/v1/run/{source}/{mode}/{practice}" for mode in ("run", "test", "editor")]


def leaks(server, paths: list[str], posts: list[str] = ()) -> list[str]:
    """Every response to `paths` (`GET`) and `posts` (`POST`) that carries a needle."""
    origin = {"Origin": f"http://127.0.0.1:{server.server_address[1]}"}
    found = []
    for method, path in [("GET", p) for p in paths] + [("POST", p) for p in posts]:
        status, _, body = fetch(server, path, origin if method == "POST" else None, method)
        held = carried(body)
        if held:
            found.append(f"{method} {path} -> {status} carries {held}")
    return found


def quiz_files(served: Path, quiz: Path) -> list[str]:
    """The URL paths of the four files that carry the quiz, under whichever root is served."""
    return [
        "/" + (quiz / path).relative_to(served).as_posix()
        for path in (PRACTICE_DOCUMENT, BUNDLE, BACKUP, NOTES)
    ]
