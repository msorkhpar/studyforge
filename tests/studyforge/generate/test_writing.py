"""Mirror of `src/studyforge/generate/writing.py` (R12)."""

from __future__ import annotations

import os
from pathlib import Path, PurePosixPath

import pytest

from studyforge.generate import Written
from studyforge.generate.writing import copy, mint, place

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
# ⛔ copy — the same refusal, without the bytes going through memory
# --------------------------------------------------------------------------


def test_a_file_is_copied_byte_for_byte_and_its_directories_minted(tmp_path):
    source = tmp_path / "origin.bin"
    source.write_bytes(b"\x00\x01\x02")
    written, refused = [], []

    copy(tmp_path, A, source, written, refused)

    assert (tmp_path / A).read_bytes() == b"\x00\x01\x02"
    assert (written, refused) == ([A], [])


def test_a_file_already_at_the_target_is_named_and_never_opened_for_writing(tmp_path):
    source = tmp_path / "origin.bin"
    source.write_bytes(b"new")
    (tmp_path / A).parent.mkdir(parents=True)
    (tmp_path / A).write_bytes(b"a reader's own file")
    written, refused = [], []

    copy(tmp_path, A, source, written, refused)

    assert (tmp_path / A).read_bytes() == b"a reader's own file"
    assert (written, refused) == ([], [A])


def test_an_executable_bit_in_the_archive_does_not_reach_the_generated_tree(tmp_path):
    """⛔ Content only — see `copy`'s docstring.

    ⭐ **Found by planting**: `copy2` passed every other clause in this module,
    because the two spellings differ in exactly the field nothing was asserting.
    A material file that arrived executable would otherwise put an executable
    byte into a reader's repository.
    """
    source = tmp_path / "origin.bin"
    source.write_bytes(b"body")
    source.chmod(0o777)
    written, refused = [], []

    copy(tmp_path, A, source, written, refused)

    assert not os.access(tmp_path / A, os.X_OK)


def test_a_copy_into_an_output_root_that_does_not_exist_is_refused(tmp_path):
    from studyforge.generate import BuildError

    source = tmp_path / "origin.bin"
    source.write_bytes(b"body")
    missing = tmp_path / "nowhere"

    with pytest.raises(BuildError):
        copy(missing, A, source, [], [])

    assert not missing.exists()


# --------------------------------------------------------------------------
# ⛔ mint — a directory the plan declared
# --------------------------------------------------------------------------


def test_a_declared_directory_is_created_and_is_not_recorded_as_a_write(tmp_path):
    refused = []

    mint(tmp_path, PurePosixPath("one/images"), refused)

    assert (tmp_path / "one/images").is_dir()
    assert refused == []


def test_a_directory_that_is_already_there_is_simply_already_there(tmp_path):
    (tmp_path / "one/images").mkdir(parents=True)
    refused = []

    mint(tmp_path, PurePosixPath("one/images"), refused)

    assert refused == []


def test_every_writer_here_refuses_the_emission_census_own_filler(tmp_path, monkeypatch):
    """⛔ `SF-28/2`, closed for all three writers rather than for the first one.

    ⭐ **The census fills a `Path` parameter with `Path("alpha")`** — a *relative*
    path, resolved against whatever the process's working directory happens to
    be, which for a test run is the repository. ⚠️ A second path parameter is
    the shape that actually lands a file, so this asserts the guard from the
    caller's side: run from inside a checkout-shaped directory, with the census's
    own value, all three refuse and nothing appears.
    """
    from studyforge.generate import BuildError

    monkeypatch.chdir(tmp_path)
    source = tmp_path / "origin.bin"
    source.write_bytes(b"body")
    census = Path("alpha")

    for call in (
        lambda: place(census, A, b"body", [], []),
        lambda: copy(census, A, source, [], []),
        lambda: mint(census, PurePosixPath("alpha"), []),
    ):
        with pytest.raises(BuildError):
            call()

    assert sorted(path.name for path in tmp_path.iterdir()) == ["origin.bin"]


def test_a_readers_own_file_where_a_directory_belongs_is_named_and_left_alone(tmp_path):
    """⛔ R3: `mkdir(exist_ok=True)` still raises on a file, and a build must not."""
    (tmp_path / "one").mkdir()
    (tmp_path / "one/images").write_bytes(b"a reader's own file")
    refused = []

    mint(tmp_path, PurePosixPath("one/images"), refused)

    assert refused == [PurePosixPath("one/images")]
    assert (tmp_path / "one/images").read_bytes() == b"a reader's own file"


# --------------------------------------------------------------------------
# ⭐ Written — two passes' records, added
# --------------------------------------------------------------------------


def test_two_records_add_in_the_order_the_passes_ran():
    first = Written(pages=(A,), refused=(B,))
    second = Written(pages=(B,), assets=(A,), media=(A,), missing=(B,))

    both = first + second

    assert both.pages == (A, B)
    assert both.assets == (A,)
    assert both.media == (A,)
    assert both.refused == (B,)
    assert both.missing == (B,)


def test_paths_is_every_file_written_and_never_a_refusal_or_an_absence():
    record = Written(
        pages=(A,),
        assets=(B,),
        media=(PurePosixPath("three/c.svg"),),
        refused=(PurePosixPath("c.html"),),
        missing=(PurePosixPath("d.svg"),),
    )

    assert record.paths == (A, B, PurePosixPath("three/c.svg"))


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
