"""Whether a corpus has a mock exam, so that the files its page needs are written and no others.

**What it does.** Answers one question about a corpus: does any unit carry a practice whose
record declares `mock`. The site build writes `mock-exam.css` and `mock-exam.js` beside the
shared bundle only when it does.

**How you use it.** `wanted(corpus)`; `site.assets` asks it.

**Depends on.** `json` and the corpus's declarations (`generate.declarations`). It reads each
unit's practice documents once and parses nothing but their JSON.

## ⛔ Absent means today, byte for byte

⭐ A corpus with no mock exam writes exactly the files it always wrote: this answers `False`,
`site.assets` adds nothing, and no page links a file that is not there. ⚠️ **The question is
asked of the source documents and not of the rendered pages**, so it does not depend on the
order a build renders its units in and costs one read of each practice document.

⛔ An unreadable practice document answers nothing here: the page pass refuses it by name when
it renders that unit, and an asset question must not be the one to raise it. ⚠️ **Personal data is
not that case**: every document decoded here goes through the one gate (R7) and a leak raises, as it
does when the page pass reads the same document.
"""

from __future__ import annotations

import json

from studyforge.archive.scrub import assert_clean
from studyforge.generate.declarations import Corpus

#: Where a unit's practice documents sit, relative to the unit's archive directory.
PRACTICE_GLOB = "practice-*.json"

#: The exercise record's key that makes a quiz a mock exam. ⭐ A string here and not an import of
#: `exercise.quiz.MOCK`: this module reads a document's key and decides nothing about its value.
MOCK_KEY = "mock"

#: What a refusal names in place of a path (R7): a practice document, never where it sits.
MOCK_WHERE = "a unit's practice document"


def wanted(corpus: Corpus) -> bool:
    """Answer whether any unit of this corpus carries a mock exam."""
    return any(_has_mock(source.directory) for source in corpus.units)


#: What a mock's key may carry beyond the two it always had, and a question's keys that only the
#: exam form reads. ⭐ Read off the document and decided nowhere else: `page.mockform` is the rule.
FORM_MOCK_KEYS = ("minutes", "layout", "scenarios", "difficulties", "sittings", "scale")
FORM_QUESTION_KEYS = ("select",)


def form_wanted(corpus: Corpus) -> bool:
    """Answer whether any unit needs the exam form's files (`render.page.mockform`).

    ⭐ Two readers use them: a mock exam that opts into the form, and a plain quiz, which is drawn
    one question at a time unless its record says `layout: page`.
    """
    return any(
        _has_mock(source.directory, form=True) or _has_stepped_quiz(source.directory)
        for source in corpus.units
    )


#: The record keys that make a quiz something other than a plain one, and the layout that opts out.
OTHER_QUIZ_KEYS = (MOCK_KEY, "review")
PAGE_LAYOUT = "page"


def _has_stepped_quiz(directory) -> bool:
    """Answer whether a practice document here has a plain quiz not opted out of the stepper."""
    for path in sorted(directory.glob(PRACTICE_GLOB)):
        try:
            document = json.loads(path.read_text(encoding="utf-8"))
        except OSError, ValueError:
            continue
        assert_clean(document, MOCK_WHERE)
        record = document.get("exercise") if isinstance(document, dict) else None
        if (
            isinstance(record, dict)
            and record.get("kind") == "quiz"
            and not any(key in record for key in OTHER_QUIZ_KEYS)
            and record.get("layout") != PAGE_LAYOUT
        ):
            return True
    return False


def _opts_in(record: dict) -> bool:
    mock = record.get(MOCK_KEY)
    if not isinstance(mock, dict):
        return False
    if any(key in mock for key in FORM_MOCK_KEYS):
        return True
    if any(isinstance(d, dict) and "weight" in d for d in mock.get("domains") or ()):
        return True
    return any(
        isinstance(q, dict) and any(key in q for key in FORM_QUESTION_KEYS)
        for q in record.get("questions") or ()
    )


def _has_mock(directory, form: bool = False) -> bool:
    """Answer whether any practice document in this unit's directory declares `mock`."""
    for path in sorted(directory.glob(PRACTICE_GLOB)):
        try:
            document = json.loads(path.read_text(encoding="utf-8"))
        except OSError, ValueError:
            continue
        assert_clean(document, MOCK_WHERE)
        record = document.get("exercise") if isinstance(document, dict) else None
        if isinstance(record, dict) and MOCK_KEY in record and (not form or _opts_in(record)):
            return True
    return False
