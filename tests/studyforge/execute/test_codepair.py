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
