"""Mirror of `src/studyforge/execute/codepair.py` (R12): a code file, its partner, its test's run.

⭐ The shapes are the Java course's own: a Maven reactor at the root, one module
per lesson group, a test named for its source — and, where the author named the
two differently, a test that names its source in its text.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from studyforge.execute import CODE_COPY, is_code, pair
from studyforge.execute import test_command as command_for
from studyforge.execute.codepair import pair_in, pairing
from studyforge.exercise import require_command

JAVA = ("java", "maven")
MAIN = "basics/src/main/java/p"
TESTS = "basics/src/test/java/p"


def corpus(root: Path, extra: dict[str, str] | None = None) -> Path:
    """A reactor with a shared module and a lesson module."""
    files = {
        "pom.xml": "<project/>\n",
        "base/pom.xml": "<project/>\n",
        "base/src/main/java/b/Util.java": "class Util {}\n",
        "basics/pom.xml": "<project/>\n",
        f"{MAIN}/Types.java": "class Types {}\n",
        f"{TESTS}/TypesTest.java": "class TypesTest { Types t; }\n",
        f"{MAIN}/WrapperVsPrimitive.java": "class WrapperVsPrimitive {}\n",
        f"{TESTS}/AutoboxingPerformanceTest.java": (
            "class AutoboxingPerformanceTest {"
            " WrapperVsPrimitive a; WrapperVsPrimitive b; Types c; }\n"
        ),
        f"{MAIN}/Vehicle.java": "class Vehicle {}\n",
        f"{MAIN}/Drivable.java": "interface Drivable {}\n",
        f"{TESTS}/AbstractionTest.java": "class AbstractionTest { Vehicle v; Drivable d; }\n",
        f"{MAIN}/Alone.java": "class Alone {}\n",
        "README_1.1.md": "# Types\n",
        **(extra or {}),
    }
    for where, text in files.items():
        (root / where).parent.mkdir(parents=True, exist_ok=True)
        (root / where).write_text(text, encoding="utf-8")
    return root


def test_a_test_named_for_its_source_reaches_it_and_back(tmp_path):
    root = corpus(tmp_path)
    found = pair(root, f"{TESTS}/TypesTest.java", JAVA)
    assert (found.source, found.test, found.module) == (
        f"{MAIN}/Types.java",
        f"{TESTS}/TypesTest.java",
        "basics",
    )
    back = pair(root, f"{MAIN}/Types.java", JAVA)
    assert (back.source, back.test) == (found.source, found.test)
    assert back.opened == f"{MAIN}/Types.java" and found.opened == f"{TESTS}/TypesTest.java"


def test_a_test_named_otherwise_reaches_the_source_its_text_names_most_and_back(tmp_path):
    root = corpus(tmp_path)
    found = pair(root, f"{TESTS}/AutoboxingPerformanceTest.java", JAVA)
    assert found.source == f"{MAIN}/WrapperVsPrimitive.java"
    back = pair(root, f"{MAIN}/WrapperVsPrimitive.java", JAVA)
    assert back.test == f"{TESTS}/AutoboxingPerformanceTest.java"


def test_a_tie_is_no_partner_never_a_guess(tmp_path):
    root = corpus(tmp_path)
    found = pair(root, f"{TESTS}/AbstractionTest.java", JAVA)
    assert found.source is None and found.test == f"{TESTS}/AbstractionTest.java"


def test_a_source_no_test_names_opens_alone(tmp_path):
    found = pair(corpus(tmp_path), f"{MAIN}/Alone.java", JAVA)
    assert (found.source, found.test) == (f"{MAIN}/Alone.java", None)


def test_a_partner_is_looked_for_inside_the_file_s_own_module(tmp_path):
    other = {"other/pom.xml": "<project/>\n", "other/src/main/java/p/Types.java": ""}
    root = corpus(tmp_path, other)
    assert pair(root, f"{TESTS}/TypesTest.java", JAVA).source == f"{MAIN}/Types.java"


@pytest.mark.parametrize(
    "path",
    ["README_1.1.md", "basics/pom.xml", "basics/src/main/java/p/Missing.java", "../x.java"],
)
def test_a_file_that_is_not_code_the_copy_holds_has_no_pair(tmp_path, path):
    assert pair(corpus(tmp_path), path, JAVA) is None


def test_code_is_what_a_declared_runtime_writes():
    assert is_code("a/B.java", JAVA) and not is_code("a/B.py", JAVA)
    assert not is_code("a/B.java", ("maven",))


def test_the_test_runs_in_the_copy_with_its_module_built_from_the_reactor(tmp_path):
    root = corpus(tmp_path)
    argv = command_for(root, pair(root, f"{MAIN}/Types.java", JAVA), JAVA)
    assert argv == [
        "mvn",
        "-B",
        "-o",
        "-f",
        f"{CODE_COPY}/pom.xml",
        "-pl",
        "basics",
        "-am",
        "test",
        "-Dtest=TypesTest",
        "-Dsurefire.failIfNoSpecifiedTests=false",
    ]
    # ⛔ The runner starts only what a record may carry.
    assert require_command(argv, "test_command", "a code test") == tuple(argv)


def test_a_module_that_is_its_own_build_names_no_module(tmp_path):
    root = tmp_path
    for where in ("pom.xml", "src/main/java/p/A.java", "src/test/java/p/ATest.java"):
        (root / where).parent.mkdir(parents=True, exist_ok=True)
        (root / where).write_text("x\n", encoding="utf-8")
    argv = command_for(root, pair(root, "src/test/java/p/ATest.java", JAVA), JAVA)
    assert argv[:5] == ["mvn", "-B", "-o", "-f", f"{CODE_COPY}/pom.xml"] and "-pl" not in argv


def test_no_test_or_no_known_tool_is_no_command(tmp_path):
    root = corpus(tmp_path)
    assert command_for(root, pair(root, f"{MAIN}/Alone.java", JAVA), JAVA) is None
    found = pair(root, f"{TESTS}/TypesTest.java", ("java", "gradle"))
    assert command_for(root, found, ("java", "gradle")) is None


def test_a_build_s_pairing_answers_as_pair_does_walking_the_code_once(tmp_path, monkeypatch):
    from studyforge.execute import codepair

    root = corpus(tmp_path)
    walks = []
    walked = codepair.code_files
    monkeypatch.setattr(codepair, "code_files", lambda where: walks.append(1) or walked(where))
    answer = pairing(root, JAVA)
    for path in (
        f"{TESTS}/AutoboxingPerformanceTest.java",
        f"{MAIN}/Types.java",
        f"{MAIN}/Alone.java",
    ):
        assert answer(path) == pair_in(walked(root), path, JAVA)
    assert answer("README_1.1.md") is None
    assert len(walks) == 1


def test_code_too_large_to_copy_pairs_nothing(tmp_path, monkeypatch):
    from studyforge.execute import codepair

    def refused(where):
        raise codepair.CodeRefused("too large")

    monkeypatch.setattr(codepair, "code_files", refused)
    assert pairing(corpus(tmp_path), JAVA)(f"{MAIN}/Types.java") is None


def test_a_kts_script_opens_in_the_editor_but_is_no_code_file_for_pairing(tmp_path):
    from studyforge.execute.codepair import opens_as_code

    extra = {"app/build.gradle.kts": "plugins {}\n", "app/Main.kt": "fun main() {}\n"}
    root = corpus(tmp_path, extra)
    runtimes = ("java", "kotlin")
    found = pair(root, "app/build.gradle.kts", runtimes)
    assert (found.source, found.test) == ("app/build.gradle.kts", None)
    assert pair(root, "app/build.gradle.kts", JAVA) is None
    assert opens_as_code("a/B.kts", runtimes) and not opens_as_code("a/B.kts", JAVA)
    assert not is_code("a/B.kts", runtimes), "still no source for a test to stand beside"
    assert pair(root, "app/Main.kt", runtimes).test is None


MIXED = ("gradle", "java", "kotlin")
KT = "interop/src/main/kotlin/p"
JV = "interop/src/main/java/p"
JT = "interop/src/test/java/p"
KTT = "interop/src/test/kotlin/p"


def mixed(root: Path, extra: dict[str, str] | None = None) -> Path:
    """A Gradle module holding a Kotlin class with a Java test, and a pair in each language."""
    files = {
        "interop/build.gradle.kts": "// build\n",
        f"{KT}/Greeter.kt": "class Greeter\n",
        f"{JT}/GreeterTest.java": "class GreeterTest { Greeter g; }\n",
        f"{KT}/Both.kt": "class Both\n",
        f"{JV}/Both.java": "class Both {}\n",
        f"{KTT}/BothTest.kt": "class BothTest { Both b }\n",
        f"{JT}/BothTest.java": "class BothTest { Both b; }\n",
        f"{JV}/OnlyJava.java": "class OnlyJava {}\n",
        f"{KTT}/OnlyJavaTest.kt": "class OnlyJavaTest { OnlyJava o }\n",
        f"{JV}/Lonely.java": "class Lonely {}\n",
        "other/build.gradle.kts": "// build\n",
        "other/src/test/java/p/GreeterTest.java": "class GreeterTest { Greeter g; }\n",
        **(extra or {}),
    }
    for where, text in files.items():
        (root / where).parent.mkdir(parents=True, exist_ok=True)
        (root / where).write_text(text, encoding="utf-8")
    return root


def test_a_java_test_pairs_a_kotlin_source_in_its_module_and_back(tmp_path):
    root = mixed(tmp_path)
    found = pair(root, f"{JT}/GreeterTest.java", MIXED)
    assert (found.source, found.test, found.module) == (
        f"{KT}/Greeter.kt",
        f"{JT}/GreeterTest.java",
        "interop",
    )
    back = pair(root, f"{KT}/Greeter.kt", MIXED)
    assert (back.source, back.test) == (found.source, found.test)


def test_a_source_of_the_other_language_in_another_module_is_no_partner(tmp_path):
    found = pair(mixed(tmp_path), "other/src/test/java/p/GreeterTest.java", MIXED)
    assert found.source is None


def test_the_same_suffix_pairs_first_where_it_exists(tmp_path):
    root = mixed(tmp_path)
    java = pair(root, f"{JT}/BothTest.java", MIXED)
    kotlin = pair(root, f"{KTT}/BothTest.kt", MIXED)
    assert java.source == f"{JV}/Both.java"
    assert kotlin.source == f"{KT}/Both.kt"
    assert pair(root, f"{JV}/Both.java", MIXED).test == f"{JT}/BothTest.java"
    assert pair(root, f"{KT}/Both.kt", MIXED).test == f"{KTT}/BothTest.kt"


def test_a_source_falls_back_to_the_other_language_test_and_a_lonely_one_stays_alone(tmp_path):
    root = mixed(tmp_path)
    assert pair(root, f"{JV}/OnlyJava.java", MIXED).test == f"{KTT}/OnlyJavaTest.kt"
    assert pair(root, f"{JV}/Lonely.java", MIXED).test is None


def test_a_one_language_declaration_never_crosses_suffixes(tmp_path):
    root = mixed(tmp_path)
    assert pair(root, f"{JT}/GreeterTest.java", ("gradle", "java")).source is None
    assert pair(root, f"{KT}/Greeter.kt", ("gradle", "kotlin")).test is None


def test_a_cross_language_tie_is_no_partner(tmp_path):
    root = mixed(
        tmp_path,
        {
            f"{KT}/Alpha.kt": "class Alpha\n",
            f"{KT}/Beta.kt": "class Beta\n",
            f"{JT}/MixTest.java": "class MixTest { Alpha a; Beta b; }\n",
        },
    )
    assert pair(root, f"{JT}/MixTest.java", MIXED).source is None
