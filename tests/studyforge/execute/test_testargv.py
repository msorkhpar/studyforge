"""Mirror of `src/studyforge/execute/testargv.py` (R12): the command that runs one test file.

⭐ Each case builds a small corpus on disk and asks `execute.test_command`, so the pairing and the
command are read together, the way a served page reads them.
"""

from __future__ import annotations

from pathlib import Path

from studyforge.execute import CODE_COPY, ROOT_DIR, pair
from studyforge.execute import test_command as command_for
from studyforge.execute import test_commands as allowlist
from studyforge.execute import test_runs as runs_of
from studyforge.execute import test_workdir as workdir_of
from studyforge.exercise import require_command
from tests.studyforge.execute.test_codepair import JAVA, MAIN, corpus

# ⭐ One command per kind of test: pytest, `node --test`, Maven's (unchanged) and Gradle's.
FOUR = ("gradle", "java", "kotlin", "node", "python")
EXAMPLES = {
    "py/bpe.py": "def encode(text):\n    return text.split()\n",
    "py/test_bpe.py": "from bpe import encode\n",
    "ts/bpe.ts": "export const encode = (text: string) => text.split(' ');\n",
    "ts/bpe.test.ts": "import { encode } from './bpe.ts';\n",
    "jv/settings.gradle": "rootProject.name = 'jv'\n",
    "jv/build.gradle": "plugins { id 'java' }\n",
    "jv/src/main/java/demo/Greeter.java": "package demo;\npublic class Greeter {}\n",
    "jv/src/test/java/demo/GreeterTest.java": "package demo;\nclass GreeterTest { Greeter g; }\n",
    "kt/settings.gradle.kts": 'rootProject.name = "kt"\n',
    "kt/build.gradle.kts": "// build\n",
    "kt/src/main/kotlin/demo/Counter.kt": "package demo\nclass Counter\n",
    "kt/src/test/kotlin/demo/CounterTest.kt": (
        "package demo\nclass CounterTest { val c: Counter? = null }\n"
    ),
}


def examples(root: Path, extra: dict[str, str] | None = None) -> Path:
    for where, text in {**EXAMPLES, **(extra or {})}.items():
        (root / where).parent.mkdir(parents=True, exist_ok=True)
        (root / where).write_text(text, encoding="utf-8")
    return root


def argv_of(root: Path, path: str, runtimes=FOUR) -> list[str] | None:
    return command_for(root, pair(root, path, runtimes), runtimes)


def test_every_language_of_the_four_pairs_and_names_one_command_in_the_copy(tmp_path):
    root = examples(tmp_path)
    # ⭐ A Python test names its file from the copy's root, which is where it starts.
    assert argv_of(root, "py/bpe.py") == [
        "python3",
        "-m",
        "pytest",
        "-q",
        "-p",
        "no:cacheprovider",
        "py/test_bpe.py",
    ]
    assert argv_of(root, "ts/bpe.ts") == ["node", "--test", f"{CODE_COPY}/ts/bpe.test.ts"]
    gradle = ["gradle", "--offline", "-q", "-p"]
    assert argv_of(root, "jv/src/main/java/demo/Greeter.java") == [
        *gradle,
        f"{CODE_COPY}/jv",
        "cleanTest",
        "test",
        "--tests",
        "demo.GreeterTest",
    ]
    assert argv_of(root, "kt/src/test/kotlin/demo/CounterTest.kt") == [
        *gradle,
        f"{CODE_COPY}/kt",
        "cleanTest",
        "test",
        "--tests",
        "demo.CounterTest",
    ]
    for where in ("py/bpe.py", "ts/bpe.ts", "jv/src/main/java/demo/Greeter.java"):
        assert pair(root, where, FOUR).test is not None
        argv = argv_of(root, where)
        assert require_command(argv, "test_command", "a code test") == tuple(argv)


def test_a_typescript_example_has_its_own_pair_and_a_run(tmp_path):
    # ⛔ A plant: `.ts` dropped from the pairing's suffixes leaves no Run.
    root = examples(tmp_path)
    found = pair(root, "ts/bpe.test.ts", FOUR)
    assert (found.source, found.test) == ("ts/bpe.ts", "ts/bpe.test.ts")
    assert argv_of(root, "ts/bpe.test.ts") is not None


def test_a_language_the_corpus_does_not_declare_is_no_code_and_has_no_command(tmp_path):
    root = examples(tmp_path)
    assert pair(root, "py/test_bpe.py", ("gradle", "java", "node")) is None
    assert pair(root, "ts/bpe.test.ts", ("gradle", "java", "python")) is None
    # ⛔ Gradle undeclared: a module holding only a Gradle build gets no command.
    only_java = ("java", "node", "python")
    assert argv_of(root, "jv/src/test/java/demo/GreeterTest.java", only_java) is None


def test_a_gradle_subproject_is_addressed_below_the_settings_file_that_names_it(tmp_path):
    extra = {
        "multi/settings.gradle.kts": 'include("app")\n',
        "multi/app/build.gradle.kts": "// build\n",
        "multi/app/src/main/kotlin/a/App.kt": "package a\nclass App\n",
        "multi/app/src/test/kotlin/a/AppTest.kt": (
            "package a\nclass AppTest { val a: App? = null }\n"
        ),
        "multi/odd name/build.gradle.kts": "// build\n",
        "multi/odd name/src/test/kotlin/AppTest.kt": "class AppTest\n",
    }
    root = examples(tmp_path, extra)
    argv = argv_of(root, "multi/app/src/main/kotlin/a/App.kt")
    assert argv == [
        "gradle",
        "--offline",
        "-q",
        "-p",
        f"{CODE_COPY}/multi",
        ":app:cleanTest",
        ":app:test",
        "--tests",
        "a.AppTest",
    ]
    assert require_command(argv, "test_command", "a code test") == tuple(argv)
    # ⛔ A directory whose name Gradle would not take unchanged gets no command, never a wrong one.
    assert argv_of(root, "multi/odd name/src/test/kotlin/AppTest.kt") is None


def test_a_test_with_no_package_names_its_class_alone(tmp_path):
    root = examples(tmp_path, {"jv/src/test/java/PlainTest.java": "class PlainTest {}\n"})
    assert argv_of(root, "jv/src/test/java/PlainTest.java")[-2:] == ["--tests", "PlainTest"]


def test_where_a_module_holds_a_pom_the_maven_command_is_chosen_even_beside_gradle(tmp_path):
    root = corpus(tmp_path)
    both = ("gradle", "java", "maven")
    path = f"{MAIN}/Types.java"
    assert command_for(root, pair(root, path, both), both)[:5] == [
        "mvn",
        "-B",
        "-o",
        "-f",
        f"{CODE_COPY}/pom.xml",
    ]
    found = command_for(root, pair(root, path, both), both)
    assert found == command_for(root, pair(root, path, JAVA), JAVA)


def test_the_allowlist_holds_the_command_of_each_test_of_the_four(tmp_path):
    root = examples(tmp_path)
    held = allowlist(root, FOUR)
    assert sorted(held[i][0] for i in range(len(held))) == ["gradle", "gradle", "node", "python3"]
    assert all(require_command(argv, "test_command", "a code test") for argv in held)


def test_a_python_test_starts_in_the_copys_root_and_every_other_in_the_runners(tmp_path):
    # ⚠️ Measured: started in the runner's root, an example importing a folder at the corpus
    # root (`from harness import ...`) failed with "No module named 'harness'". From the
    # copy's root, `python3 -m` puts that root first on the import path.
    root = examples(tmp_path)
    assert workdir_of(pair(root, "py/bpe.py", FOUR)) == CODE_COPY
    for where in (
        "ts/bpe.ts",
        "jv/src/main/java/demo/Greeter.java",
        "kt/src/test/kotlin/demo/CounterTest.kt",
    ):
        assert workdir_of(pair(root, where, FOUR)) == ROOT_DIR


def test_the_allowlist_pairs_each_command_with_the_directory_it_starts_in(tmp_path):
    root = examples(tmp_path)
    runs = runs_of(root, FOUR)
    assert [argv for _, argv in runs] == allowlist(root, FOUR)
    by_tool = {argv[0]: workdir for workdir, argv in runs}
    assert by_tool == {"python3": CODE_COPY, "node": ROOT_DIR, "gradle": ROOT_DIR}
    # ⭐ The Python test's path is corpus-relative: relative to the copy's root it starts in.
    [python] = [argv for workdir, argv in runs if argv[0] == "python3"]
    assert (root / python[-1]).is_file()
