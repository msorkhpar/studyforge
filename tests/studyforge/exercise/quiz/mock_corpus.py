"""A built corpus with a mock exam in it: `depth1`, copied, one practice added, built.

⭐ The same construction as `tests/studyforge/serve/routes/quizzing.py`, with the mock exam's six
questions in place of its two, so a browser and a site test read a page a build really wrote.
⛔ The fixture `depth1` is never touched. Mirrors no source module (R12): material, not a test.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from studyforge.archive.document import render
from studyforge.generate import write_site
from tests.studyforge.exercise.quiz import mock_exam, mock_form
from tests.studyforge.exercise.quiz.depth1 import PAGE, fixture_root, practice_document, section
from tests.studyforge.serve.routes.quizzing import PRACTICE_DOCUMENT

ORIGIN = {"path": PAGE, "section": section()}


def mock_corpus(where: Path, *, mock: bool = True, form: bool = False, **changes) -> Path:
    """Copy `depth1`, add the practice, declare exercises, build it; return the corpus root.

    `mock=False` writes the same six questions as a plain quiz (no domain, no `mock` key), which is
    the quiz a corpus carried before mock exams existed.
    """
    root = where / "depth1"
    shutil.copytree(fixture_root(), root)
    questions = mock_form.questions(ORIGIN) if form else mock_exam.questions(ORIGIN)
    declared = mock_form.mock() if form else mock_exam.mock()
    if not mock:
        questions = [{k: v for k, v in one.items() if k != "domain"} for one in questions]
    parts = {"questions": questions, **({"mock": declared} if mock else {}), **changes}
    document = practice_document(**parts)
    (root / PRACTICE_DOCUMENT).write_text(render(document), encoding="utf-8")
    manifest = root / "corpus.json"
    declared = json.loads(manifest.read_text(encoding="utf-8"))
    declared["exercises"] = True
    manifest.write_text(json.dumps(declared, indent=2) + "\n", encoding="utf-8")
    write_site(root, root)
    return root


def built_files(root: Path) -> dict[str, bytes]:
    """Every file the build wrote, by path under the root."""
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted((root / ".studyforge").rglob("*"))
        if path.is_file()
    } | {"index.html": (root / "index.html").read_bytes()}


def form_corpus(where: Path, **changes) -> Path:
    """The same corpus with the exam-form mock (the course shape's twelve-question pool) in it."""
    return mock_corpus(where, form=True, **changes)
