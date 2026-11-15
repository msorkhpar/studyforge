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


def test_check_on_a_missing_brief_exits_2(tmp_path, capsys):
    assert main(["check", str(tmp_path / ".studyforge" / "brief.json")]) == 2
    err = capsys.readouterr().err
    assert len(err.strip().splitlines()) == 1 and "Traceback" not in err


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
