"""Mirror of `skills/exercises/tryit.py` (R12): the try-it file's skeleton, command and check."""

from __future__ import annotations

import pytest

from studyforge.skills.exercises import tryit

WS = "practice/p"


def test_the_scaffold_names_every_language_and_flags_a_file_not_finished():
    for lang, name in tryit.TRYIT_FILE.items():
        text = tryit.skeleton(lang, "solution", "Cart")
        assert "Cart" in text or lang in ("java", "kotlin")
        assert tryit.LOGGER_SWITCH[lang] in text
        assert "it still has a TODO" in tryit.problems(lang, text)
        done = text.replace("TODO", "done") + "\nprint(1) println(1) console.log(1)\n"
        assert tryit.problems(lang, done) == []
    assert tryit.run_command("python", WS) == ("python3", f"{WS}/try_it.py")
    assert tryit.run_command("kotlin", WS)[-1] == "tryIt"
    assert 'mainClass.set("TryItKt")' in tryit.gradle_task("kotlin")
    with pytest.raises(ValueError):
        tryit.skeleton("cobol")
