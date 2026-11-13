"""Mirror of `page.project` (R12): a project's file list on the page and its explorer."""

from __future__ import annotations

from studyforge.exercise import from_document
from studyforge.render.page import practice, project

WS = "practice/p"
RECORD = {
    "main_path": f"{WS}/pkg/model.py",
    "files": [f"{WS}/main.py"],
    "test_path": f"{WS}/tests/test_expected_output.py",
    "run_command": ["python3", f"{WS}/main.py"],
    "test_command": ["python3", "-m", "pytest", f"{WS}/tests"],
    "provenance": "generated",
    "trust": "advisory",
    "cases": [
        {"id": "a", "kind": "main", "says": "it works"},
        {"id": "b", "kind": "edge", "says": "the edge"},
        {"id": "c", "kind": "kept", "says": "the old part still works"},
    ],
    "report": {"format": "junit", "path": f"{WS}/target/report.xml"},
    "read_only": [f"{WS}/tests/fixtures/a.csv", f"{WS}/data.csv"],
}


def test_the_files_are_listed_folders_after_the_root_and_the_read_only_ones_say_so():
    exercise = from_document(RECORD, "w")
    assert project.is_project(exercise)
    assert [path for _, path, _ in project.entries(exercise)] == [
        "data.csv", "main.py", "pkg/model.py", "tests/test_expected_output.py",
        "tests/fixtures/a.csv"]
    listed = project.files_list(exercise)
    assert listed.startswith("<details") and "project of 5 files" in listed
    assert "<li><code>main.py</code></li>" in listed
    assert "<li><code>data.csv</code> <span data-practice-readonly>read-only</span></li>" in listed


def test_the_explorer_is_a_hidden_tablist_whose_buttons_are_named_for_their_windows():
    explorer = project.explorer(from_document(RECORD, "w"))
    assert explorer.startswith('<div data-practice-part="tabs" data-practice-explorer')
    assert " hidden>" in explorer.splitlines()[0]
    for window in ('"main"', '"file:0"', '"test"', '"ro:0"', '"ro:1"'):
        assert f"data-practice-tab={window}" in explorer
    assert '<p data-practice-folder aria-hidden="true">tests/fixtures/</p>' in explorer
    assert 'aria-label="pkg/model.py, yours to edit"' in explorer


def test_the_panel_draws_the_project_s_surfaces_and_a_plain_practice_keeps_its_own():
    exercise = from_document(RECORD, "w")
    assert project.files_part(exercise, practice.files_sentence) == project.files_list(exercise)
    assert project.tabs_part(exercise, practice.tabs) == project.explorer(exercise)
    plain = from_document({k: v for k, v in RECORD.items() if k != "read_only"}, "w")
    assert project.files_part(plain, practice.files_sentence) == practice.files_sentence(plain)
    assert project.tabs_part(plain, practice.tabs) == practice.tabs(plain)


def test_only_a_breakdown_with_kept_cases_carries_the_kept_words():
    assert "data-practice-kept=" in practice.breakdown(from_document(RECORD, "w"))
    cases = [case for case in RECORD["cases"] if case["kind"] != "kept"]
    plain = from_document({**RECORD, "cases": cases}, "w")
    assert "data-practice-kept" not in practice.breakdown(plain)
