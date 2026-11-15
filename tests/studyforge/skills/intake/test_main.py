"""Mirror of `studyforge.skills.intake.__main__`: check, render and questions."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from studyforge.skills.intake.__main__ import main

from tests.studyforge.skills.intake.briefs import clean_brief

SRC = Path(__file__).parents[4] / "src"


def _repo(tmp_path: Path, brief: dict | None = None, *, git: bool = True,
          ignore: bool = True) -> Path:
    if git:
        subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    if ignore:
        (tmp_path / ".gitignore").write_text(".private/\n", encoding="utf-8")
    folder = tmp_path / ".studyforge"
    folder.mkdir()
    path = folder / "brief.json"
    path.write_text(json.dumps(brief or clean_brief("topic")), encoding="utf-8")
    return path


def test_check_on_a_clean_brief_exits_0_and_prints_open_0(tmp_path, capsys):
    path = _repo(tmp_path)
    assert main(["check", str(path)]) == 0
    assert capsys.readouterr().out == "open: 0\n"


def test_check_on_an_open_brief_exits_1_and_lists_each(tmp_path, capsys):
    data = clean_brief("topic")
    del data["answers"]["writing.pilot"]
    data["outline"] = []
    path = _repo(tmp_path, data)
    assert main(["check", str(path)]) == 1
    lines = capsys.readouterr().out.splitlines()
    assert lines[-1] == f"open: {len(lines) - 1}" and len(lines) >= 3
    assert any("writing.pilot" in line for line in lines)


def test_check_outside_a_git_repository_exits_2_with_one_line(tmp_path, capsys):
    path = _repo(tmp_path, git=False, ignore=False)
    assert main(["check", str(path)]) == 2
    captured = capsys.readouterr()
    assert captured.out == "" and len(captured.err.strip().splitlines()) == 1


def test_check_on_a_missing_brief_exits_2(tmp_path, capsys, monkeypatch):
    assert main(["check", str(tmp_path / ".studyforge" / "brief.json")]) == 2
    err = capsys.readouterr().err
    assert len(err.strip().splitlines()) == 1 and "Traceback" not in err
    assert str(tmp_path) not in err
    monkeypatch.chdir(tmp_path)
    assert main(["check"]) == 2
    assert capsys.readouterr().err == (
        "no brief at .studyforge/brief.json; run the intake skill first\n")


def test_check_on_a_wrong_shape_brief_exits_2_without_echoing_values(tmp_path, capsys):
    path = _repo(tmp_path, {"brief_api": 1, "title": "Secret Title", "answers": []})
    assert main(["check", str(path)]) == 2
    err = capsys.readouterr().err
    assert len(err.strip().splitlines()) == 1 and "Secret Title" not in err


def test_a_private_folder_that_does_not_exist_and_is_not_ignored_is_reported(
        tmp_path, capsys):
    path = _repo(tmp_path, ignore=False)
    assert not (tmp_path / ".private").exists()
    assert main(["check", str(path)]) == 1
    out = capsys.readouterr().out
    assert ".private/ is not ignored by git" in out and out.endswith("open: 1\n")


def test_render_writes_brief_md_beside_the_brief(tmp_path, capsys, monkeypatch):
    path = _repo(tmp_path)
    monkeypatch.chdir(tmp_path)
    assert main(["render"]) == 0
    assert capsys.readouterr().out == str(Path(".studyforge") / "brief.md") + "\n"
    text = (path.parent / "brief.md").read_text(encoding="utf-8")
    assert text.startswith("# Graph Basics\n")


def test_questions_for_a_track_lists_its_additions_and_not_others(capsys):
    assert main(["questions", "--track", "interview"]) == 0
    out = capsys.readouterr().out
    assert "interview.mocks [costly]" in out
    assert "convert.repository" not in out
    assert "\n  why: " in out and "\n  default: " in out


def test_questions_print_each_kind_its_choices_and_its_gate(capsys):
    assert main(["questions", "--track", "topic"]) == 0
    out = capsys.readouterr().out
    blocks = out.split("\n")
    kinds = [line for line in blocks if line.startswith("  kind: ")]
    assert len(kinds) == sum(line.startswith("  why: ") for line in blocks)
    assert "  default: false\n  kind: boolean, recorded as JSON true or false\n" in out
    assert "  kind: choice, recorded as exactly one of: yes, no, after-release\n" in out
    assert "  kind: private_ref, recorded as env:NAME or private:FILE" in out
    assert "  depends on narration.wanted = yes, after-release\n" in out


def _commit_private_then_ignore(root: Path) -> None:
    git = ["git", "-C", str(root), "-c", "user.name=Example",
           "-c", "user.email=noreply@example.invalid"]
    (root / ".private").mkdir()
    (root / ".private" / "notes.md").write_text("private notes\n", encoding="utf-8")
    subprocess.run([*git, "add", ".private/notes.md"], check=True)
    subprocess.run([*git, "commit", "-q", "-m", "notes"], check=True)
    (root / ".gitignore").write_text(".private/\n", encoding="utf-8")


def test_a_private_folder_ignored_after_a_commit_still_reports_its_tracked_files(
        tmp_path, capsys):
    path = _repo(tmp_path, ignore=False)
    _commit_private_then_ignore(tmp_path)
    assert main(["check", str(path)]) == 1
    out = capsys.readouterr().out
    assert out == ".private/ holds files git tracks\nopen: 1\n"


def test_an_ignored_private_folder_with_untracked_files_is_fine(tmp_path, capsys):
    path = _repo(tmp_path)
    (tmp_path / ".private").mkdir()
    (tmp_path / ".private" / "notes.md").write_text("private notes\n", encoding="utf-8")
    assert main(["check", str(path)]) == 0
    assert capsys.readouterr().out == "open: 0\n"


def test_usage_errors_exit_2_with_one_line(capsys):
    for argv in ([], ["bogus"], ["questions", "--track", "nope"], ["check", "a", "b"]):
        assert main(argv) == 2
        assert len(capsys.readouterr().err.strip().splitlines()) == 1


def test_the_module_runs_as_a_subprocess():
    done = subprocess.run([sys.executable, "-m", "studyforge.skills.intake", "questions"],
                          capture_output=True, text=True, check=False,
                          env={**os.environ, "PYTHONPATH": str(SRC)})
    assert done.returncode == 0 and "writing.pilot" in done.stdout


def test_check_on_a_brief_holding_a_personal_value_exits_2_with_one_line(tmp_path, capsys):
    planted = "/" + "home" + "/alice/notes"
    data = clean_brief("topic")
    data["answers"]["sources.list"] = {"status": "answered", "decided_by": "author",
                                       "value": planted}
    path = _repo(tmp_path, data)
    assert main(["check", str(path)]) == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert len(captured.err.strip().splitlines()) == 1
    assert "answers.sources.list" in captured.err and planted not in captured.err
