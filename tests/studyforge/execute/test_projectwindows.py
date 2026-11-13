"""Mirror of `execute.projectwindows` (R12): a project's read-only windows, in record order."""

from __future__ import annotations

from studyforge.execute.editor import Editor
from studyforge.execute.projectwindows import read_only_windows
from studyforge.execute.workbench import open_url, prepared

EDITOR = Editor(origin="http://127.0.0.1:8443", folder="/w/sources", base="practice")


def test_each_read_only_file_gets_a_window_and_a_missing_one_a_hole(tmp_path):
    for name in ("p/tests/test_a.py", "p/data.csv"):
        (tmp_path / "practice" / name).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / "practice" / name).write_text("x\n", encoding="utf-8")
    paths = ["practice/p/tests/test_a.py", "practice/p/gone.csv", "practice/p/data.csv"]
    answer = read_only_windows(EDITOR, tmp_path, paths, open_url)["read_only"]
    assert [one and one["path"] for one in answer] == [
        "p/tests/test_a.py", None, "p/data.csv"]
    assert answer[0]["url"] == open_url(EDITOR, paths[0])


def test_a_practice_with_no_read_only_file_answers_nothing():
    assert read_only_windows(EDITOR, ".", (), open_url) == {}


def test_the_read_only_files_stay_locked_in_the_settings_the_practice_gets(tmp_path):
    for name in ("p/a.py", "p/t.py", "p/data.csv"):
        (tmp_path / "practice" / name).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / "practice" / name).write_text("x\n", encoding="utf-8")
    answer = prepared(
        EDITOR, tmp_path, "practice/p/a.py", "practice/p/t.py", read_only=["practice/p/data.csv"])
    assert answer["read_only"][0]["path"] == "p/data.csv"
    written = (tmp_path / "practice" / ".vscode" / "settings.json").read_text(encoding="utf-8")
    assert "data.csv" not in written, "a read-only file was excluded from the lock"
