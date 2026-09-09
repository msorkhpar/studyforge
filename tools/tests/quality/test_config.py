"""Mirror of `tools/quality/config.py` (R12)."""

from __future__ import annotations

import tomllib

from tests.support import repository_root
from tools.quality import config


def test_the_size_exception_marker_is_the_ruled_literal():
    # ⛔ Fixed by ruling, case included: the review rubric greps for exactly
    # this token, so a marker that drifts passes here and fails there.
    assert config.SIZE_EXCEPTION_MARKER == "Size exception:"


def test_ceilings_are_the_documented_ones():
    # docs/conventions/module-structure.md states 400 and 600. If these move,
    # that document moved first — this assertion is the tripwire.
    assert config.SOURCE_LINE_CEILING == 400
    assert config.TEST_LINE_CEILING == 600


def test_ruff_line_length_agrees_with_the_always_on_checker():
    # ⛔ Two tools disagreeing about the same file is worse than one tool.
    # `pyproject.toml`'s `[tool.ruff] line-length` and `config.LINE_LENGTH`
    # are the same number or this fails.
    pyproject = tomllib.loads((repository_root() / "pyproject.toml").read_text("utf-8"))
    assert pyproject["tool"]["ruff"]["line-length"] == config.LINE_LENGTH


def test_test_files_get_the_test_ceiling():
    assert config.ceiling_for("tests/studyforge/test_init.py") == config.TEST_LINE_CEILING
    assert config.ceiling_for("src/studyforge/serve/app.py") == config.SOURCE_LINE_CEILING
    assert config.ceiling_for("tools/quality/size.py") == config.SOURCE_LINE_CEILING
    # The tooling's tests live beside the tooling and are still tests.
    assert config.ceiling_for("tools/tests/quality/test_size.py") == config.TEST_LINE_CEILING


def test_a_path_merely_containing_tests_is_not_a_test_file():
    # `is_test_file` matches a root, not a substring: a source module named
    # `contests.py` must not inherit the looser ceiling.
    assert not config.is_test_file("src/studyforge/contests.py")
    assert not config.is_test_file("testsuite/thing.py")


def test_fixtures_are_never_read():
    # FND-04's fixtures are deliberately shaped wrong — an invalid corpus is
    # the point of half of them — so holding them to the repository's style
    # would be a category error.
    assert config.is_excluded("tests/fixtures/depth1/corpus.json")
    assert config.is_excluded("src/studyforge/__pycache__/x.py")
    assert not config.is_excluded("tests/studyforge/test_init.py")


def test_relative_is_repo_relative_with_forward_slashes():
    root = repository_root()
    assert config.relative(root / "tools" / "quality" / "config.py", root) == (
        "tools/quality/config.py"
    )


def test_python_files_finds_the_tree_and_is_sorted():
    files = config.python_files(repository_root())
    names = [config.relative(path, repository_root()) for path in files]
    assert "src/studyforge/__init__.py" in names
    assert "tools/quality/config.py" in names
    assert "tests/support.py" in names
    assert "tools/tests/quality/test_config.py" in names  # it checks itself
    assert names == sorted(names)
    assert not [name for name in names if "__pycache__" in name]
