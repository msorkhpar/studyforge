"""A quiz the lesson repeats is on the page once: the interactive quiz stands where the copy was.

⭐ The corpus is `depth1` with a quiz practice, and its lesson ends with a section listing the same
six questions, as a lesson that copies its own quiz does. Read over `file://` on a page a real build
wrote: every stem is in the text once, and the lesson's section holds the interactive quiz.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from studyforge.archive.document import render
from studyforge.generate import write_site
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


def _built(root: Path, head: list[dict]) -> tuple[str, list[str]]:
    """Build `depth1` with a quiz practice; the lesson gets `head` first and the questions last."""
    shutil.copytree(fixture_root(), root)
    plain = [
        {k: v for k, v in one.items() if k != "domain"} for one in mock_exam.questions(ORIGIN)
    ]
    document = practice_document(questions=plain)
    (root / PRACTICE_DOCUMENT).write_text(render(document), encoding="utf-8")
    lesson = root / "archive" / ADDRESS[0] / LESSON
    held = json.loads(lesson.read_text(encoding="utf-8"))
    stems = [one["stem"] for one in plain]
    held["blocks"] = head + held["blocks"] + [
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


@pytest.fixture(scope="module")
def page_url(tmp_path_factory: pytest.TempPathFactory) -> tuple[str, list[str]]:
    return _built(tmp_path_factory.mktemp("quiz-once") / "depth1", [])


#: Paragraphs of a lesson ingested as ONE section under its title, the way a page whose title is
#: its only top-level heading arrives: the title's range is the whole lesson, quiz included.
WHOLE = ["LESSONTEXT one, before any heading.", "LESSONTEXT two, still the opening."]


@pytest.fixture(scope="module")
def whole_url(tmp_path_factory: pytest.TempPathFactory) -> tuple[str, list[str]]:
    head = [
        {"type": "heading", "level": 1, "text": "The whole lesson"},
        *({"type": "para", "text": text} for text in WHOLE),
    ]
    return _built(tmp_path_factory.mktemp("quiz-whole") / "depth1", head)


def test_every_repeated_stem_is_in_the_page_once_and_the_quiz_stands_in_place(
    open_page: OpenPage, page_url: tuple[str, list[str]], capture_dir: Path
) -> None:
    url, stems = page_url
    open_page.resize(1280, 800)
    open_page.open(url)
    text = str(open_page.evaluate(TEXT))
    for stem in stems:
        assert text.count(stem) == 1, f"{stem!r} is on the page {text.count(stem)} times"
    assert "Answer key" not in text
    inside = open_page.evaluate(
        "document.querySelectorAll('section[data-kind=\"lesson\"] section[data-practice-quiz],"
        " section[data-practice-quiz]').length"
    )
    assert inside == 1, "the quiz is not drawn exactly once"
    assert open_page.evaluate("document.querySelectorAll('[data-practice-card]').length") == 0
    open_page.evaluate(
        "(() => { const h = document.querySelector('section[data-practice-quiz]');"
        " h.scrollIntoView({block: 'start'}); return true; })()"
    )
    open_page.capture(capture_dir / "quiz-shown-once.png", whole=False)


def test_a_lesson_that_is_one_section_keeps_its_prose_visible_beside_the_quiz(
    open_page: OpenPage, whole_url: tuple[str, list[str]], capture_dir: Path
) -> None:
    url, stems = whole_url
    open_page.resize(1280, 800)
    open_page.open(url)
    shown = open_page.evaluate(
        "Array.from(document.querySelectorAll('p')).filter(p =>"
        " p.textContent.includes('LESSONTEXT') && p.getClientRects().length > 0"
        " && getComputedStyle(p).visibility !== 'hidden').map(p => p.textContent.trim())"
    )
    for text in WHOLE:
        assert any(text in one for one in shown), f"{text!r} is not visible after load"
    text = str(open_page.evaluate(TEXT))
    assert "Answer key" not in text and "These questions are in" not in text
    for stem in stems:
        assert text.count(stem) == 1, f"{stem!r} is on the page {text.count(stem)} times"
    quizzes = "document.querySelectorAll('section[data-practice-quiz]').length"
    assert open_page.evaluate(quizzes) == 1
    open_page.capture(capture_dir / "quiz-whole-lesson.png", whole=False)
