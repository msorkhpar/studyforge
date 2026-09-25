"""Mirror of `src/studyforge/execute/codetree.py` (R12): the copy a lesson's code opens from.

⛔ **The author's tree is never written**, so every test here reads the author's
files back byte for byte after the copy moved.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

from studyforge.execute import codetree
from studyforge.execute.codetree import (
    CODE_COPY,
    IGNORE_TEXT,
    CodeRefused,
    code_files,
    in_copy,
    sync,
)

SOURCE = "m/src/main/java/p/Types.java"
TEST = "m/src/test/java/p/TypesTest.java"


def corpus(root: Path) -> Path:
    """A corpus with code, the framework's own directories, output and dot-files."""
    for where, text in {
        "pom.xml": "<project/>\n",
        "m/pom.xml": "<project/>\n",
        SOURCE: "class Types {}\n",
        TEST: "class TypesTest {}\n",
        "m/target/classes/Types.class": "compiled\n",
        "archive/m/raw/prose/unit-01/practice-1.json": '{"key": "the answer"}\n',
        "exercises/m/tests/quiz.json": '{"key": "the answer"}\n',
        "practice/m/Work.java": "class Work {}\n",
        ".env": "SECRET=1\n",
        ".git/config": "[core]\n",
        ".studyforge/site.json": "{}\n",
    }.items():
        (root / where).parent.mkdir(parents=True, exist_ok=True)
        (root / where).write_text(text, encoding="utf-8")
    (root / CODE_COPY).mkdir(parents=True)
    (root / CODE_COPY / ".gitignore").write_text(IGNORE_TEXT, encoding="utf-8")
    return root


def test_the_copy_mirrors_the_code_and_nothing_else(tmp_path):
    root = corpus(tmp_path)
    assert sorted(code_files(root)) == ["m/pom.xml", SOURCE, TEST, "pom.xml"]


@pytest.mark.parametrize(
    "never",
    [
        "archive/m/raw/prose/unit-01/practice-1.json",
        "exercises/m/tests/quiz.json",
        "practice/m/Work.java",
        "m/target/classes/Types.class",
        ".env",
        ".git/config",
        ".studyforge/site.json",
    ],
)
def test_no_key_no_output_no_dot_file_and_no_practice_is_ever_copied(tmp_path, never):
    root = corpus(tmp_path)
    copy = sync(root)
    assert not (copy / never).exists()


def test_a_sync_copies_every_file_and_leaves_the_author_s_bytes_alone(tmp_path):
    root = corpus(tmp_path)
    before = {where: path.read_bytes() for where, path in code_files(root).items()}
    copy = sync(root)
    for where, data in before.items():
        assert (copy / where).read_bytes() == data
        assert (root / where).read_bytes() == data
    assert in_copy(SOURCE) == f"{CODE_COPY}/{SOURCE}"


def test_a_reader_s_change_survives_until_the_author_changes_the_file(tmp_path):
    root = corpus(tmp_path)
    copy = sync(root)
    (copy / SOURCE).write_text("class Types { int mine; }\n", encoding="utf-8")
    future = (root / SOURCE).stat().st_mtime + 10
    os.utime(copy / SOURCE, (future, future))
    sync(root)
    assert "mine" in (copy / SOURCE).read_text(encoding="utf-8")
    (root / SOURCE).write_text("class Types { int author; }\n", encoding="utf-8")
    os.utime(root / SOURCE, (future + 10, future + 10))
    sync(root)
    assert "author" in (copy / SOURCE).read_text(encoding="utf-8")


def test_a_file_the_author_removed_leaves_the_copy_but_output_and_settings_stay(tmp_path):
    root = corpus(tmp_path)
    copy = sync(root)
    (copy / "m/target/surefire-reports").mkdir(parents=True)
    (copy / "m/target/surefire-reports/TEST-p.TypesTest.xml").write_text("<x/>\n")
    (copy / "m/.vscode").mkdir()
    (copy / "m/.vscode/settings.json").write_text("{}\n")
    (root / TEST).unlink()
    sync(root)
    assert not (copy / TEST).exists()
    assert (copy / "m/target/surefire-reports/TEST-p.TypesTest.xml").is_file()
    assert (copy / "m/.vscode/settings.json").is_file()
    assert (copy / ".gitignore").read_text(encoding="utf-8") == IGNORE_TEXT


def test_a_missing_copy_directory_is_refused_rather_than_made(tmp_path):
    root = corpus(tmp_path)
    (root / CODE_COPY / ".gitignore").unlink()
    (root / CODE_COPY).rmdir()
    with pytest.raises(CodeRefused, match="regenerate"):
        sync(root)
    assert not (root / CODE_COPY).exists()


def test_a_symlink_is_never_copied(tmp_path):
    root = corpus(tmp_path)
    (root / "m/Link.java").symlink_to(root / ".env")
    assert "m/Link.java" not in code_files(root)


def test_code_larger_than_a_copy_is_refused(tmp_path, monkeypatch):
    root = corpus(tmp_path)
    monkeypatch.setattr(codetree, "MAX_FILES", 2)
    with pytest.raises(CodeRefused, match="larger than a copy"):
        code_files(root)


def test_git_ignores_everything_in_the_copy_but_its_own_ignore_file(tmp_path):
    root = corpus(tmp_path)
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    sync(root)
    listed = subprocess.run(
        ["git", "-C", str(root), "status", "--porcelain", "--untracked-files=all", CODE_COPY],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    assert listed == [f"?? {CODE_COPY}/.gitignore"]
