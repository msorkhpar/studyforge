"""Mirror of `skills/exercises/tryit.py` (R12): the try-it file's skeleton, command and check."""

from __future__ import annotations

import pytest

from studyforge.skills.exercises import tryit

WS = "practice/p"


def test_the_scaffold_names_every_language_and_flags_a_file_not_finished():
    for lang, _name in tryit.TRYIT_FILE.items():
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


def test_a_maven_practice_runs_try_it_through_the_pinned_exec_plugin():
    assert tryit.run_command("java", WS, build="maven") == (
        "mvn", "-o", "-q", "-f", f"{WS}/pom.xml", "compile", "exec:java",
    )
    plugin = tryit.maven_plugin("java")
    assert f"<version>{tryit.EXEC_PLUGIN_VERSION}</version>" in plugin
    assert "<mainClass>TryIt</mainClass>" in plugin
    assert "<mainClass>TryItKt</mainClass>" in tryit.maven_plugin("kotlin")
    assert tryit.run_command("python", WS, build="maven") == ("python3", f"{WS}/try_it.py")
    primed = tryit.maven_prime_plugin()
    assert "<goal>help</goal>" in primed and "<phase>validate</phase>" in primed
    assert f"<version>{tryit.EXEC_PLUGIN_VERSION}</version>" in primed
    with pytest.raises(ValueError):
        tryit.run_command("java", WS, build="ant")
    with pytest.raises(ValueError):
        tryit.maven_plugin("python")


def test_a_finished_skeleton_has_no_todo_left_but_the_one_the_author_replaces():
    for lang in ("java", "kotlin"):
        text = tryit.skeleton(lang, "solution", "Cart")
        assert text.count("TODO") == 1, lang
        assert "java.lang.Runtime" in text
