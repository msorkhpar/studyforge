"""Mirror of `validate.projects` (R12): a project's workspace holds every file its record names."""

from __future__ import annotations

from types import SimpleNamespace

from studyforge.validate.projects import RULE_PROJECT_FILES, check_project_files

WS = "practice/p"
RECORD = {
    "main_path": f"{WS}/pkg/model.py",
    "test_path": f"{WS}/tests/test_expected_output.py",
    "run_command": ["python3", f"{WS}/main.py"],
    "test_command": ["python3", "-m", "pytest", f"{WS}/tests"],
    "provenance": "generated",
    "files": [f"{WS}/main.py"],
    "read_only": [f"{WS}/tests/test_model.py"],
}
FILES = ("pkg/model.py", "main.py", "tests/test_expected_output.py", "tests/test_model.py")


def _walk(root, record):
    unit = SimpleNamespace(where="u1", document={"kind": "practice", "exercise": record})
    return SimpleNamespace(root=root, units=[unit])


def _workspace(root, *names):
    for name in names:
        (root / WS / name).parent.mkdir(parents=True, exist_ok=True)
        (root / WS / name).write_text("x\n", encoding="utf-8")


def test_a_workspace_holding_exactly_the_record_s_files_is_clean(tmp_path):
    tools = ("target/report.xml", ".vscode/settings.json", "pkg/__pycache__/a.pyc")
    _workspace(tmp_path, *FILES, *tools)
    assert list(check_project_files(_walk(tmp_path, RECORD))) == []


def test_a_missing_file_and_a_stray_one_are_each_named(tmp_path):
    _workspace(tmp_path, *FILES[1:], "notes.txt")
    found = list(check_project_files(_walk(tmp_path, RECORD)))
    assert [finding.rule for finding in found] == [RULE_PROJECT_FILES, RULE_PROJECT_FILES]
    assert "pkg/model.py" in found[0].message and "does not hold" in found[0].message
    assert "notes.txt" in found[1].message and "never sees it" in found[1].message


def test_a_practice_that_is_not_a_project_is_not_judged(tmp_path):
    plain = {key: value for key, value in RECORD.items() if key != "read_only"}
    _workspace(tmp_path, "notes.txt")
    assert list(check_project_files(_walk(tmp_path, plain))) == []
