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
