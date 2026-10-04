"""A quiz the lesson repeats is on the page once: the lesson says where, the practice holds it.

⭐ The corpus is `depth1` with a quiz practice, and its lesson ends with a section listing the same
six questions, as a lesson that copies its own quiz does. Read over `file://` on a page a real build
wrote: every stem is in the text once, and the lesson's section is the one pointer sentence.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from studyforge.archive.document import render
from studyforge.generate import write_site
from studyforge.render.page import POINTER
from tests.studyforge.exercise.quiz import mock_exam
from tests.studyforge.exercise.quiz.depth1 import (
    ADDRESS,
    LESSON,
    PAGE,
    fixture_root,
    practice_document,
    section,
)
from tests.studyforge.serve.routes.quizzing import PRACTICE_DOCUMENT, page_of
from tests.visual.page import OpenPage

ORIGIN = {"path": PAGE, "section": section()}

TEXT = "document.body.textContent"


@pytest.fixture(scope="module")
def page_url(tmp_path_factory: pytest.TempPathFactory) -> tuple[str, list[str]]:
    root = tmp_path_factory.mktemp("quiz-once") / "depth1"
    shutil.copytree(fixture_root(), root)
    plain = [
        {k: v for k, v in one.items() if k != "domain"} for one in mock_exam.questions(ORIGIN)
    ]
    document = practice_document(questions=plain)
    (root / PRACTICE_DOCUMENT).write_text(render(document), encoding="utf-8")
    lesson = root / "archive" / ADDRESS[0] / LESSON
    held = json.loads(lesson.read_text(encoding="utf-8"))
    stems = [one["stem"] for one in plain]
    held["blocks"] += [
        {"type": "heading", "level": 2, "text": "Check yourself"},
        {
            "type": "list", "ordered": True,
            "items": [[stem, {"type": "para", "text": "a"}] for stem in stems],
        },
        {"type": "disclosure", "summary": "Answer key", "open": False,
         "blocks": [{"type": "para", "text": "The key."}]},
    ]
    lesson.write_text(json.dumps(held, indent=2) + "\n", encoding="utf-8")
    manifest = root / "corpus.json"
    declared = json.loads(manifest.read_text(encoding="utf-8"))
    declared["exercises"] = True
    manifest.write_text(json.dumps(declared, indent=2) + "\n", encoding="utf-8")
    write_site(root, root)
    return "file://" + str(page_of(root)), stems


def test_every_repeated_stem_is_in_the_page_once_and_the_lesson_says_where(
    open_page: OpenPage, page_url: tuple[str, list[str]], capture_dir: Path
) -> None:
    url, stems = page_url
    open_page.resize(1280, 800)
    open_page.open(url)
    text = str(open_page.evaluate(TEXT))
    for stem in stems:
        assert text.count(stem) == 1, f"{stem!r} is on the page {text.count(stem)} times"
    assert POINTER in text and "Answer key" not in text
    open_page.evaluate(
        "(() => { const h = Array.from(document.querySelectorAll('h2'))"
        ".find((x) => x.textContent.trim() === 'Check yourself');"
        " h.scrollIntoView({block: 'start'}); return true; })()"
    )
    open_page.capture(capture_dir / "quiz-shown-once.png", whole=False)
