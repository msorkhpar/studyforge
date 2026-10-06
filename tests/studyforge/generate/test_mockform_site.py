"""The exam form's files are written for a mock that opts into it, and for no other.

**What it asserts.** A corpus with a plain mock exam builds exactly the files and the page bytes it
built before the exam form existed (the form's files are absent and its markup is not on the page);
a corpus whose mock opts in adds the form's four files, and its page links them and not the plain
exam's script; `form_wanted` reads the raw document; and the same twelve questions as a plain quiz
(no `mock` key) build as the plain quiz they were.
"""

from __future__ import annotations

from studyforge.generate import read_corpus
from studyforge.generate.mockexam import form_wanted, wanted
from tests.studyforge.exercise.quiz.mock_corpus import built_files, form_corpus, mock_corpus

FORM_FILES = [
    ".studyforge/assets/mock-form-core.js",
    ".studyforge/assets/mock-form-panels.js",
    ".studyforge/assets/mock-form.css",
    ".studyforge/assets/mock-form.js",
]


def unit_page(files: dict[str, bytes]) -> str:
    (page,) = [p for p in files if p.endswith(".unit.html") and b"data-practice-mock" in files[p]]
    return files[page].decode("utf-8")


def test_a_plain_mock_exam_does_not_want_the_exam_form(tmp_path):
    root = mock_corpus(tmp_path / "plain-mock")
    assert wanted(read_corpus(root)) is True and form_wanted(read_corpus(root)) is False
    files = built_files(root)
    assert not [p for p in files if "mock-form" in p]
    page = unit_page(files)
    assert "data-mock-form" not in page and "mock-form" not in page and "mock-exam.js" in page


def test_an_opted_in_mock_adds_exactly_the_forms_four_files(tmp_path):
    plain = built_files(mock_corpus(tmp_path / "plain-mock"))
    formed = built_files(form_corpus(tmp_path / "formed"))
    assert sorted(set(formed) - set(plain)) == FORM_FILES
    assert sorted(set(plain) - set(formed)) == []
    root = read_corpus(tmp_path / "formed" / "depth1")
    assert wanted(root) and form_wanted(root)


def test_the_opted_in_page_links_the_form_and_not_the_plain_exams_script(tmp_path):
    page = unit_page(built_files(form_corpus(tmp_path / "formed")))
    assert page.count("mock-form.js") == 1 and page.count("mock-form.css") == 1
    assert page.count("mock-form-core.js") == 1 and page.count("mock-form-panels.js") == 1
    assert "mock-exam.js" not in page and "mock-exam.css" not in page
    assert 'data-mock-form="exam"' in page and 'data-form-part="key"' in page
    assert 'type="checkbox"' in page and 'type="radio"' in page


def test_the_same_questions_with_no_mock_key_and_the_page_layout_build_a_plain_quiz(tmp_path):
    files = built_files(mock_corpus(tmp_path / "plain-quiz", mock=False, layout="page"))
    assert not [p for p in files if "mock-" in p]


def test_a_plain_quiz_is_drawn_one_question_at_a_time_by_default(tmp_path):
    # ⭐ The stepper is the default for a quiz: the exam form's four files are written and linked,
    # and the page is the form in its quiz kind, not the exam.
    files = built_files(mock_corpus(tmp_path / "stepped", mock=False))
    assert sorted(p for p in files if "mock-form" in p) == FORM_FILES
    page = unit_page(files)
    assert 'data-form-kind="quiz"' in page and 'data-mock-form="exam"' in page
    assert "mock-exam.js" not in page and "Mock exam" not in page
    assert 'data-practice-part="check"' not in page


def test_the_page_layout_is_the_opt_out_and_draws_every_question_on_one_page(tmp_path):
    files = built_files(mock_corpus(tmp_path / "paged", mock=False, layout="page"))
    pages = [body.decode("utf-8") for path, body in files.items() if path.endswith(".unit.html")]
    assert pages and all("mock-form" not in page for page in pages)
    assert any('data-practice-part="check"' in page for page in pages)


def test_a_multiple_response_question_alone_opts_in(tmp_path):
    from tests.studyforge.exercise.quiz import mock_form
    from tests.studyforge.exercise.quiz.mock_corpus import ORIGIN
    pool = mock_form.questions(ORIGIN)
    only = [q for q in pool if q["id"] in ("p9", "p7")]
    for question in only:
        question.pop("scenario", None)
        question.pop("difficulty", None)
    root = mock_corpus(
        tmp_path / "multi",
        questions=only,
        mock={"pass_mark": 50, "domains": [{"id": "AS1", "title": "Prompting"}]},
    )
    assert form_wanted(read_corpus(root))
