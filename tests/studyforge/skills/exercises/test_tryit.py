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


def _ran_java(tmp_path, body: str) -> str:
    import shutil
    import subprocess

    if shutil.which("java") is None:
        pytest.skip("no JDK on this machine")
    text = tryit.skeleton("java", "solution", "Cart")
    start = text.index("            // TODO")
    end = text.index("        } catch (RuntimeException stopped)")
    source = tmp_path / "TryIt.java"
    source.write_text(text[:start] + body + "\n" + text[end:], encoding="utf-8")
    ran = subprocess.run(["java", str(source)], capture_output=True, text=True, timeout=120)
    assert ran.returncode == 0, ran.stderr
    return ran.stdout + ran.stderr


def test_a_java_run_shows_each_log_line_of_the_readers_code_once(tmp_path):
    # ⚠️ Measured: the skeleton added its handler beside the JDK's own console handler, so every
    # line at INFO or above was printed twice.
    out = _ran_java(tmp_path, '            java.util.logging.Logger.getLogger("shop").info("basket saved");')
    assert out.count("basket saved") == 1, out


def test_a_java_run_keeps_the_jdks_own_log_lines_out(tmp_path):
    # ⚠️ Measured: with the root logger at ALL, deserialization, the HTTP server and the security
    # providers printed their FINER lines into a reader's Run.
    out = _ran_java(
        tmp_path,
        '            java.util.logging.Logger.getLogger("jdk.event.security").fine("certificate noise");\n'
        '            java.util.logging.Logger.getLogger("sun.net.www").finer("socket noise");\n'
        '            java.util.logging.Logger.getLogger("shop").fine("reader detail");',
    )
    assert "noise" not in out, out
    assert "FINE reader detail" in out, out


def test_the_kotlin_skeleton_quiets_the_same_two_sources_of_noise():
    text = tryit.skeleton("kotlin", "solution", "Cart")
    assert "removeHandler" in text and tryit.JDK_LOGGERS.replace("\\", "\\\\") in text


def test_the_java_skeleton_imports_no_name_a_practice_may_use_for_its_own_type():
    # ⚠️ Measured: practices in the senior-Java course declare their own `Handler`; an import of
    # java.util.logging.Handler would shadow it in a try-it file in the same package.
    text = tryit.skeleton("java", "solution", "Cart")
    assert "import java.util.logging.Handler;" not in text
    assert "java.util.logging.Handler before" in text
