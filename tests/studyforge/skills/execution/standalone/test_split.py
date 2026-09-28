"""Mirror of `src/studyforge/skills/execution/standalone/split.py` (R12).

⭐ The fixture is the runnable corpus, built in place, and the tracked files are
handed in: the course's own material around it is what a real course has, so
every rule is read against a path the rule names and one it does not.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from studyforge.generate import read_corpus, write_site
from studyforge.skills.execution.standalone import split
from tests.studyforge.execute.runnable import fixture_copy

#: What a built, onboarded course tracks around the fixture's own files.
AROUND = (
    "LICENSE",
    "README.md",
    "CLAUDE.md",
    ".claude/commands/new-module.md",
    ".gitignore",
    "exercises/kata/unit-01/practice-1/reference/main.py",
    "ingest/read.py",
    "tests/test_framework_pin.py",
    "docs/studyforge/ONBOARDING.md",
    "module-a/pom.xml",
    "module-a/src/Main.java",
    "somewhere-else/notes.txt",
    ".studyforge/pin.json",
    ".studyforge/installed.json",
    ".studyforge/skills/adapter.md",
    ".studyforge/narration.json",
    ".studyforge/narration-release/restore.sh",
    ".studyforge/.gitignore",
    ".studyforge/execution/compose.yaml",
    ".studyforge/execution/instance.env",
    ".studyforge/execution/runservice.pl",
    ".studyforge/execution/prime/maven/module-a/pom.xml",
    ".studyforge/execution/code/.gitignore",
    ".studyforge/execution/allowed/.gitignore",
)


@pytest.fixture(scope="module")
def course(tmp_path_factory) -> tuple[Path, tuple[str, ...], dict[str, split.Verdict]]:
    root = fixture_copy(tmp_path_factory.mktemp("course"))
    write_site(root, root)
    files = tuple(
        sorted({*(p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()), *AROUND})
    )
    verdicts = split.classify(root, files)
    return root, files, {one.path: one for one in verdicts}


def verdict(course, path: str) -> str:
    return course[2][path].verdict


@pytest.mark.parametrize(
    "path",
    [
        "corpus.json",
        "archive",
        "practice",
        "index.html",
        "kata",
        "module-a",
        "LICENSE",
        ".gitignore",
        ".studyforge/assets",
        ".studyforge/narration.json",
        ".studyforge/narration-release",
        ".studyforge/.gitignore",
        ".studyforge/execution/runservice.pl",
        ".studyforge/execution/prime",
        ".studyforge/execution/code",
        ".studyforge/execution/allowed",
    ],
)
def test_what_a_learner_needs_to_study_or_run_the_course_is_kept(course, path):
    assert verdict(course, path) == split.KEEP, course[2][path].why


@pytest.mark.parametrize(
    "path",
    [
        "exercises",
        "ingest",
        "tests",
        "docs",
        "README.md",
        "CLAUDE.md",
        ".claude",
        ".studyforge/pin.json",
        ".studyforge/installed.json",
        ".studyforge/skills",
        ".studyforge/execution/compose.yaml",
        ".studyforge/execution/instance.env",
    ],
)
def test_what_records_how_the_course_was_built_moves(course, path):
    assert verdict(course, path) == split.MOVE


def test_a_path_nothing_recognises_moves_and_says_so(course):
    assert verdict(course, "somewhere-else") == split.MOVE
    assert course[2]["somewhere-else"].why == split.UNKNOWN


def test_the_bundles_move_because_they_hold_every_answer(course):
    assert "answer" in course[2]["exercises"].why


def test_a_top_level_entry_the_prime_does_not_mirror_is_not_kept_as_code(course):
    root, files, _ = course
    unmirrored = tuple(one for one in files if not one.startswith(".studyforge/execution/prime/"))
    judged = {one.path: one.verdict for one in split.classify(root, unmirrored)}
    assert judged["module-a"] == split.MOVE


def test_every_entry_gets_exactly_one_verdict_with_a_sentence(course):
    paths = [one.path for one in course[2].values()]
    assert len(paths) == len(set(paths))
    assert all(one.why and one.verdict in (split.KEEP, split.MOVE) for one in course[2].values())


def test_kept_is_every_file_beneath_a_keep_and_nothing_beneath_a_move(course):
    root, files, verdicts = course
    kept = split.kept(verdicts.values(), files)
    assert "module-a/src/Main.java" in kept
    assert ".studyforge/execution/runservice.pl" in kept
    assert not [
        one for one in kept if one.startswith(("exercises/", "ingest/", ".studyforge/skills/"))
    ]
    assert ".studyforge/execution/compose.yaml" not in kept


def test_the_archive_is_kept_because_without_it_the_server_has_no_unit(tmp_path):
    root = fixture_copy(tmp_path)
    write_site(root, root)
    assert read_corpus(root).units
    shutil.rmtree(root / "archive")
    assert read_corpus(root).units == ()


def test_the_tracked_files_are_what_git_answers_through_the_callers_run(tmp_path):
    from tests.studyforge.skills.execution.standalone.test_write import checkout, git

    root = checkout(tmp_path)
    files = split.tracked(root, git)
    assert "corpus.json" in files and all("\\" not in one for one in files)
    assert list(files) == sorted(files)


def test_a_directory_git_does_not_track_is_refused(tmp_path):
    with pytest.raises(ValueError, match="not a git checkout"):
        split.tracked(tmp_path, lambda argv, cwd: (128, ""))


def test_the_table_prints_one_verdict_a_line(course):
    rows = split.table(course[2].values()).splitlines()
    assert len(rows) == len(course[2])
    assert "KEEP  corpus.json  " in "\n".join(rows)
    assert any(row.startswith("MOVE  ") for row in rows)
