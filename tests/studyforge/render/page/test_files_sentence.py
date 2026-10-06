"""Mirror of `page.practice.files_sentence` (R12): the sentence naming the file or files the reader
edits."""

from __future__ import annotations

from studyforge.exercise import of as exercise_of


def test_the_practice_page_names_every_edited_file(tmp_path):
    from studyforge.render.page import practice

    files_sentence = practice.files_sentence

    record = exercise_of(
        {
            "kind": "practice",
            "exercise": {
                "main_path": "practice/p/settings.json",
                "files": ["practice/p/docs/memory.md", "practice/p/hooks/guard.sh"],
                "run_command": ["true"],
            },
        },
        "w",
    )
    sentence = files_sentence(record)
    assert sentence.count("<code>") == 3
    assert "settings.json</code>, <code>practice/p/docs/memory.md</code> and <code>" in sentence
    one = exercise_of(
        {"kind": "practice", "exercise": {"main_path": "practice/p/a.py", "run_command": ["true"]}},
        "w",
    )
    assert files_sentence(one) == (
        '<p data-practice-part="file">Your file for this practice is '
        "<code>practice/p/a.py</code>.</p>"
    )


def test_the_page_says_what_run_executes_only_where_there_is_a_try_file():
    from studyforge.exercise import from_document, of
    from studyforge.render.page import practice

    WS = "practice/p"
    WITH = {
        "main_path": f"{WS}/solution.py",
        "test_path": f"{WS}/test_solution.py",
        "run_command": ["python3", f"{WS}/try_it.py"],
        "test_command": ["python3", "-m", "pytest", f"{WS}/test_solution.py"],
        "provenance": "bundled",
        "trust": "authoritative",
        "files": [f"{WS}/try_it.py"],
        "try_file": f"{WS}/try_it.py",
    }
    said = practice.files_sentence(of({"kind": "practice", "exercise": WITH}, "w"))
    assert 'data-practice-part="tryit"' in said
    assert "<code>practice/p/try_it.py</code>, your own calls" in said
    no_try = {**WITH}
    del no_try["try_file"]
    assert "tryit" not in practice.files_sentence(of({"kind": "practice", "exercise": no_try}, "w"))
    assert practice.controls(from_document(WITH, "w")).count("data-practice-act=") == 2
