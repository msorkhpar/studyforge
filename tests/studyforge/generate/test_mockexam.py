"""Mirror of `src/studyforge/generate/mockexam.py` (R12): the two files are for a mock exam only.

**What it asserts.** A corpus with no mock exam builds to the files it always built (and the shared
bundle is the same bytes whether or not a mock exam exists); a corpus with one adds exactly the two
files and links them from the page that carries the exam and from no other; the question is asked of
the source documents.
"""

from __future__ import annotations

from studyforge.generate import read_corpus
from studyforge.generate.mockexam import wanted
from studyforge.render import pageassets
from studyforge.render.page import mock_files
from tests.studyforge.exercise.quiz.mock_corpus import built_files, mock_corpus
from tests.studyforge.exercise.quiz.depth1 import fixture_root

ADDED = [".studyforge/assets/mock-exam.css", ".studyforge/assets/mock-exam.js"]


def test_a_corpus_with_a_plain_quiz_and_one_with_none_want_no_mock_files(tmp_path):
    plain = mock_corpus(tmp_path / "plain", mock=False)
    assert wanted(read_corpus(plain)) is False
    assert wanted(read_corpus(fixture_root())) is False


def test_a_corpus_with_a_mock_exam_wants_them(tmp_path):
    root = mock_corpus(tmp_path / "mock")
    assert wanted(read_corpus(root)) is True


def test_a_mock_exam_adds_exactly_two_files_and_leaves_the_shared_bundle_as_it_was(tmp_path):
    plain = built_files(mock_corpus(tmp_path / "plain", mock=False))
    mocked = built_files(mock_corpus(tmp_path / "mock"))
    assert sorted(set(mocked) - set(plain)) == ADDED
    assert sorted(set(plain) - set(mocked)) == []
    for name in pageassets.written_files():
        assert mocked[f".studyforge/assets/{name}"] == plain[f".studyforge/assets/{name}"]


def test_only_the_page_with_the_exam_links_the_files(tmp_path):
    mocked = built_files(mock_corpus(tmp_path / "mock"))
    linking = sorted(
        path
        for path, body in mocked.items()
        if path.endswith((".html")) and b"mock-exam.js" in body
    )
    assert len(linking) == 1 and linking[0].endswith(".unit.html"), linking
    page = mocked[linking[0]].decode("utf-8")
    assert page.count("mock-exam.css") == 1 and page.count("mock-exam.js") == 1
    assert 'mock-exam.js" defer></script>' in page


def test_a_plain_quiz_builds_to_the_same_bytes_as_before_it_knew_about_mock_exams(tmp_path):
    # ⭐ The page of a quiz with no `mock` carries no word of the mock part.
    plain = built_files(mock_corpus(tmp_path / "plain", mock=False))
    joined = b"".join(plain.values())
    for word in (b"mock-exam", b"data-practice-mock", b"data-mock-"):
        assert word not in joined


def test_the_two_files_are_the_assets_the_framework_ships(tmp_path):
    mocked = built_files(mock_corpus(tmp_path / "mock"))
    for name, text in mock_files().items():
        assert mocked[f".studyforge/assets/{name}"] == text.encode("utf-8")
