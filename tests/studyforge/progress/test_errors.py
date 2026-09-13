"""Mirror of `src/studyforge/progress/errors.py` (R12)."""

from __future__ import annotations

from studyforge.progress.errors import ProgressError, ProgressFormatError


def test_a_malformed_file_is_a_kind_of_refusal():
    # One catch of `ProgressError` must also catch a malformed record.
    assert issubclass(ProgressFormatError, ProgressError)
    assert not issubclass(ProgressError, ProgressFormatError)
