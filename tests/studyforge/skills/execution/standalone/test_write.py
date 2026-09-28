"""Mirror of `src/studyforge/skills/execution/standalone/write.py` (R12).

⭐ End to end on the runnable fixture: a git checkout of it, with the two tags
its execution records, released against a synthetic toolchain that answers as
the real one does. ⛔ The manifest is read against the files actually on disk,
so a written file it forgot, or a listed file nobody wrote, turns it red.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from studyforge.skills.execution.standalone import closure, compose, split, write
from tests.studyforge.execute.runnable import fixture_copy
from tests.studyforge.skills.execution.standalone.test_vendor import (
    TAGS,
    answering,
    course,
    toolchain,
)

#: ⛔ A placeholder identity: the fixture's commit is nobody's.
GIT = ["git", "-c", "user.name=Example", "-c", "user.email=contact@example.com"]


def git(argv, cwd):
    """A real `run` for `git`: the caller's side of `split.Run`, as a person would write it."""
    done = subprocess.run(argv, cwd=cwd, stdin=subprocess.DEVNULL, capture_output=True, text=True)
    return done.returncode, done.stdout


def answered(tags=TAGS):
    """`git` answered for real, the toolchain's builds answered by the synthetic checkout."""
    fake = answering(tags)
    return lambda argv, cwd: git(argv, cwd) if argv[0] == "git" else fake(argv, cwd)


def checkout(tmp_path: Path) -> Path:
    """The runnable fixture as a one-commit git checkout recording the primed tags."""
    root = course(fixture_copy(tmp_path / "course"))
    subprocess.run([*GIT, "init", "-q"], cwd=root, check=True)
    subprocess.run([*GIT, "add", "-A"], cwd=root, check=True)
    subprocess.run([*GIT, "commit", "-q", "-m", "fixture"], cwd=root, check=True)
    return root


@pytest.fixture(scope="module")
def released(tmp_path_factory) -> tuple[Path, write.Released]:
    where = tmp_path_factory.mktemp("release")
    out = where / "learner"
    made = write.release(
        checkout(where),
        out,
        toolchain=toolchain(where / "tc"),
        platform="linux/amd64",
        run=answered(),
    )
    return out, made


def on_disk(out: Path) -> list[str]:
    return sorted(p.relative_to(out).as_posix() for p in out.rglob("*") if p.is_file())


def test_the_manifest_lists_exactly_the_files_the_tree_holds(released):
    out, made = released
    listed = json.loads((out / write.MANIFEST).read_text(encoding="utf-8"))["keeps"]
    assert listed == on_disk(out)
    assert write.kept_paths(made) == listed


def test_a_file_written_behind_the_manifest_s_back_would_be_seen(tmp_path, monkeypatch):
    real = write._ignore_env
    monkeypatch.setattr(write, "_ignore_env", lambda path: real(path) and False)
    out = tmp_path / "learner"
    write.release(
        checkout(tmp_path),
        out,
        toolchain=toolchain(tmp_path / "tc"),
        platform="linux/amd64",
        run=answered(),
    )
    listed = json.loads((out / write.MANIFEST).read_text(encoding="utf-8"))["keeps"]
    assert listed != on_disk(out)


def test_the_tree_carries_the_course_the_runtime_the_toolchain_and_both_compose_files(released):
    out, made = released
    for one in (
        "corpus.json",
        "compose.yaml",
        "compose.pull.yaml",
        "course.env",
        "README.md",
        ".dockerignore",
        f"{compose.TOOLCHAIN}/docker/minimal/Dockerfile",
        f"{compose.IMAGES}/serve/Dockerfile",
        f"{compose.IMAGES}/site/Dockerfile",
        f"{compose.IMAGES}/runner/Dockerfile",
        f"{compose.NO_PRIME}/README",
    ):
        assert (out / one).is_file(), one
    library = out / compose.IMAGES / "serve" / "library"
    assert (library / closure.PACKAGE / closure.STAMP).read_text(encoding="utf-8").strip()
    assert not (library / "studyforge" / "skills").exists()
    assert {v.path for v in made.verdicts if v.verdict == split.KEEP} >= {"corpus.json", "practice"}


def test_the_learner_s_gitignore_ignores_their_own_settings(released):
    out, _ = released
    assert ".env" in (out / ".gitignore").read_text(encoding="utf-8").splitlines()


def test_a_target_that_is_not_empty_is_refused(tmp_path):
    out = tmp_path / "out"
    out.mkdir()
    (out / "left.txt").write_text("x", encoding="utf-8")
    with pytest.raises(write.ReleaseRefused, match="not empty"):
        write.release(tmp_path, out, toolchain=tmp_path, platform="linux/amd64", run=answered())


def test_a_course_that_declares_no_runtime_is_refused(tmp_path):
    root = checkout(tmp_path)
    document = json.loads((root / "corpus.json").read_text(encoding="utf-8"))
    document["runtimes"] = []
    (root / "corpus.json").write_text(json.dumps(document), encoding="utf-8")
    with pytest.raises(write.ReleaseRefused, match="no runtime"):
        write.release(
            root,
            tmp_path / "out",
            toolchain=toolchain(tmp_path / "tc"),
            platform="linux/amd64",
            run=answered(),
        )
