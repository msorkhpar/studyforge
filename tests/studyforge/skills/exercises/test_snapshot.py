"""Mirror of `skills.exercises.snapshot` (R12): a snapshot's files by role, and its test ids."""

from __future__ import annotations

import pytest

from studyforge.skills.exercises import AuthoringError
from studyforge.skills.exercises.snapshot import DEFAULT_BUILD, read_snapshot, declared_tests
from tests.studyforge.skills.exercises.project_sample import SAMPLE


def test_every_file_of_the_sample_lands_in_one_role():
    after = read_snapshot(SAMPLE / "steps" / "01")
    assert set(after.sources) == {
        "main.py", "seedcrate/__init__.py", "seedcrate/data.py", "seedcrate/model.py",
        "seedcrate/report.py", "seedcrate/solve.py"}
    assert set(after.tests) == {"tests/test_data.py", "tests/test_model.py", "tests/test_report.py"}
    fixed = {"data/lots.csv", "expected/report.txt", "tests/fixtures/must.csv"}
    assert fixed <= set(after.read_only)
    assert set(after.build) == {"pytest.ini"}


def test_a_cache_and_a_dot_file_are_not_part_of_a_snapshot_and_a_missing_build_is_given(tmp_path):
    (tmp_path / "tests" / "__pycache__").mkdir(parents=True)
    (tmp_path / "tests" / "__pycache__" / "x.pyc").write_bytes(b"\x00\xff")
    (tmp_path / ".hidden").write_text("x", encoding="utf-8")
    (tmp_path / "tests" / "conftest.py").write_text("", encoding="utf-8")
    found = read_snapshot(tmp_path)
    assert found.read_only == {"tests/conftest.py": ""} and found.sources == {}
    assert found.build == {"pytest.ini": DEFAULT_BUILD}


def test_a_binary_file_and_a_missing_tests_folder_are_refused(tmp_path):
    with pytest.raises(AuthoringError, match="no tests folder"):
        read_snapshot(tmp_path)
    (tmp_path / "tests").mkdir()
    (tmp_path / "blob.bin").write_bytes(b"\xff\xfe\x00")
    with pytest.raises(AuthoringError, match="not UTF-8"):
        read_snapshot(tmp_path)


def test_test_ids_are_node_ids_with_their_docstrings_and_a_parametrised_test_is_set_apart(tmp_path):
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_a.py").write_text(
        "import pytest\n\n\ndef test_one():\n    \"\"\"One holds.\"\"\"\n\n\n"
        "class TestTwo:\n    def test_two(self):\n        pass\n\n\n"
        "@pytest.mark.parametrize('x', [1, 2])\ndef test_many(x):\n    pass\n",
        encoding="utf-8",
    )
    ids = declared_tests(read_snapshot(tmp_path))
    assert list(ids.declared) == ["tests/test_a.py::test_one", "tests/test_a.py::TestTwo::test_two"]
    assert ids.declared["tests/test_a.py::test_one"].summary == "One holds"
    assert ids.declared["tests/test_a.py::TestTwo::test_two"].summary == "two"
    assert ids.parametrised == ("tests/test_a.py::test_many",)
