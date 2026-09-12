"""Mirror of `src/studyforge/generate/writing.py` (R12)."""

from __future__ import annotations

from pathlib import PurePosixPath

import pytest

from studyforge.generate import Written
from studyforge.generate.writing import place

A = PurePosixPath("one/a.html")
B = PurePosixPath("two/b.html")


# --------------------------------------------------------------------------
# ⛔ place — R3 by refusing, not by remembering
# --------------------------------------------------------------------------


def test_a_path_that_does_not_exist_is_written_and_its_directories_minted(tmp_path):
    written, refused = [], []

    place(tmp_path, A, b"body", written, refused)

    assert (tmp_path / A).read_bytes() == b"body"
    assert (written, refused) == ([A], [])


def test_a_path_that_exists_is_named_and_never_opened_for_writing(tmp_path):
    (tmp_path / A).parent.mkdir(parents=True)
    (tmp_path / A).write_bytes(b"a reader's own file")
    written, refused = [], []

    place(tmp_path, A, b"body", written, refused)

    assert (tmp_path / A).read_bytes() == b"a reader's own file"
    assert (written, refused) == ([], [A])


def test_an_existing_directory_at_the_target_is_refused_rather_than_crashed_into(tmp_path):
    """⚠️ A directory `exists()` too, and the refusal is the same one."""
    (tmp_path / A).mkdir(parents=True)
    written, refused = [], []

    place(tmp_path, A, b"body", written, refused)

    assert (written, refused) == ([], [A])
    assert (tmp_path / A).is_dir()


def test_only_the_directories_a_target_needs_are_minted(tmp_path):
    written, refused = [], []

    place(tmp_path, A, b"body", written, refused)

    assert sorted(path.name for path in tmp_path.iterdir()) == ["one"]


# --------------------------------------------------------------------------
# ⭐ Written — two passes' records, added
# --------------------------------------------------------------------------


def test_two_records_add_in_the_order_the_passes_ran():
    first = Written(pages=(A,), refused=(B,))
    second = Written(pages=(B,), assets=(A,))

    both = first + second

    assert both.pages == (A, B)
    assert both.assets == (A,)
    assert both.refused == (B,)


def test_paths_is_every_file_written_and_never_a_refusal():
    record = Written(pages=(A,), assets=(B,), refused=(PurePosixPath("c.html"),))

    assert record.paths == (A, B)


def test_an_empty_record_is_the_identity_of_the_sum():
    record = Written(pages=(A,), assets=(B,), refused=(A,))

    assert record + Written() == record


def test_adding_something_that_is_not_a_record_is_refused():
    with pytest.raises(TypeError):
        Written() + object()


def test_an_output_root_that_does_not_exist_is_refused_and_never_minted(tmp_path):
    """⛔ Measured: `tests/emission` calls this with `Path('alpha')`.

    ⭐ A writer that minted its own root created `alpha/alpha` **in the
    repository** on every full test run, silently, because a relative root
    resolves against the process's working directory. ⛔ The refusal names
    neither the root nor the target (R7).
    """
    from studyforge.generate import BuildError

    missing = tmp_path / "nowhere"
    written, refused = [], []

    with pytest.raises(BuildError) as raised:
        place(missing, A, b"body", written, refused)

    assert not missing.exists()
    assert (written, refused) == ([], [])
    assert str(tmp_path) not in str(raised.value)


def test_a_file_where_the_output_root_should_be_is_refused_too(tmp_path):
    from studyforge.generate import BuildError

    (tmp_path / "root").write_bytes(b"not a directory")

    with pytest.raises(BuildError):
        place(tmp_path / "root", A, b"body", [], [])
