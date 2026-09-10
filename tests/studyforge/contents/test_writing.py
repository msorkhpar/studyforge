"""Mirror of `src/studyforge/contents/writing.py` (R12)."""

from __future__ import annotations

import pytest

from studyforge.contents.writing import WRITING_SUFFIX, write


def test_the_directory_is_created(tmp_path):
    target = tmp_path / "a" / "b" / "toc.json"
    write(target, "{}\n")
    assert target.read_text(encoding="utf-8") == "{}\n"


def test_no_staging_file_survives_a_successful_write(tmp_path):
    target = tmp_path / "toc.json"
    write(target, "{}\n")
    assert list(tmp_path.iterdir()) == [target]


def test_no_staging_file_survives_a_failed_write(tmp_path):
    # ⚠️ A torn `*.writing` file reads as absent, which is a rebuild; a file
    # half-overwritten in place reads as present and wrong.
    target = tmp_path / "toc.json"
    target.write_text("the version that was there\n", encoding="utf-8")
    with pytest.raises(TypeError):
        write(target, None)
    assert list(tmp_path.iterdir()) == [target]
    assert target.read_text(encoding="utf-8") == "the version that was there\n"


def test_the_staging_name_is_derived_from_the_target(tmp_path):
    # ⛔ Beside the target, so the move is on one filesystem and is atomic
    # where the platform makes it so.
    target = tmp_path / "toc.json"
    write(target, "{}\n")
    assert not (tmp_path / (target.name + WRITING_SUFFIX)).exists()


def test_writing_twice_leaves_the_second_document(tmp_path):
    target = tmp_path / "toc.json"
    write(target, "first\n")
    write(target, "second\n")
    assert target.read_text(encoding="utf-8") == "second\n"
