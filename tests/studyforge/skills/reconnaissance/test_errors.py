"""Mirror of `src/studyforge/skills/reconnaissance/errors.py` (R12).

⛔ The behaviour of `inside_root` against a real poisoned tree is asserted in
`test_record.py`, beside the pass that calls it. What is asserted here is what
the family IS: one base a caller can catch, and one spelling of "name the value
without reproducing it" rather than a fifth.
"""

from __future__ import annotations

import pytest

from studyforge.describe import describe as the_one_spelling
from studyforge.skills.reconnaissance import ReconnaissanceRefused
from studyforge.skills.reconnaissance.errors import describe, inside_root


def test_the_refusal_is_a_value_error_so_code_that_handles_bad_input_handles_it():
    # ⚠️ A value a caller passed, not a document that could not
    # be read.
    assert issubclass(ReconnaissanceRefused, ValueError)


def test_describe_is_re_exported_and_never_re_implemented():
    # ⛔ R7: "describe a value without reproducing it" has ONE
    # home. Copies of it drift apart, about integers first.
    assert describe is the_one_spelling


def test_a_document_inside_the_root_is_not_refused(tmp_path):
    (tmp_path / "src").mkdir()
    inside_root(tmp_path / "src" / "unit.md", tmp_path)
    inside_root(tmp_path / "unit.md", tmp_path)


def test_a_document_beside_the_root_is_refused(tmp_path):
    root = tmp_path / "corpus"
    root.mkdir()
    with pytest.raises(ReconnaissanceRefused):
        inside_root(tmp_path / "unit.md", root)


def test_the_refusal_names_the_types_and_reproduces_neither_path(tmp_path):
    # ⛔ R7. The check is on the two values the caller actually handed over,
    # whatever they are named — a substring of either is a leak.
    root = tmp_path / "corpus"
    root.mkdir()
    document = tmp_path / "Jane-Doe" / "unit.md"
    with pytest.raises(ReconnaissanceRefused) as refused:
        inside_root(document, root)
    message = str(refused.value)
    assert str(document) not in message
    assert str(root) not in message
    assert "Jane-Doe" not in message
    # ⭐ What it says instead: the type, through the one spelling.
    assert the_one_spelling(document) in message


def test_the_refusal_says_why_it_is_silent_so_the_next_author_does_not_undo_it(tmp_path):
    # ⭐ The one way this discipline gets reversed is
    # a reader taking the vagueness for an oversight and putting the value back.
    root = tmp_path / "corpus"
    with pytest.raises(ReconnaissanceRefused) as refused:
        inside_root(tmp_path / "elsewhere" / "unit.md", root)
    assert "R7" in str(refused.value)
