"""An example's Run, read in a container with no network: Python, TypeScript, Java and Kotlin.

⭐ **The commands are the framework's own**: the corpus below is built on disk, the copy is made by
`execute.sync`, and every command run is one `execute.test_runs` offers for it (the list the
run service's allowlist is written from), in the directory it names. Each runs as `docker run
--network none`, a read-only root with a scratch tmpfs, the host user, and nothing mounted but
the corpus root. ⭐ The Python example imports a folder at the corpus root (`support`), as a
course's shared harness is imported.

⚠️ **Skipped unless told what to run in**, because the base runner has no wheelhouse, npm
cache or Gradle cache for a Kotlin build:

- `STUDYFORGE_EXAMPLE_IMAGE`: a runner image carrying `python3` with pytest, `node` and the warm
  Gradle cache the Kotlin and Java builds below resolve from (the `claude-sdks` profile's);
- `STUDYFORGE_EXAMPLE_STAGE`: an empty directory the engine can bind, never under the host's
  temporary directory.

⛔ A heavy job: run it through the heavy-job slot, one at a time.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import uuid
from pathlib import Path

import pytest

from studyforge.execute import CODE_COPY, sync
from studyforge.execute import ROOT_DIR
from studyforge.execute import test_runs as runs_of
from tests.harness import engine

IMAGE = os.environ.get("STUDYFORGE_EXAMPLE_IMAGE")
STAGE = os.environ.get("STUDYFORGE_EXAMPLE_STAGE")
RUNTIMES = ("gradle", "java", "kotlin", "node", "python")

QUIET_LOGGING = (
    'quiet { events("failed"); '
    "exceptionFormat = org.gradle.api.tasks.testing.logging.TestExceptionFormat.FULL }"
)
BUILD = """\
plugins { %s }
repositories { mavenCentral() }
%s
dependencies {
    %s
    testRuntimeOnly("org.junit.platform:junit-platform-launcher")
}
tasks.test {
    useJUnitPlatform()
    testLogging { %s }
}
"""

FILES = {
    "harness/__init__.py": "def hello(name):\n    return 'hello ' + name\n",
    "py/greeter.py": "from harness import hello\n\n\ndef greet(name):\n    return hello(name)\n",
    "py/test_greeter.py": (
        "from greeter import greet\n\n\ndef test_greets():\n    assert greet('a') == 'hello a'\n"
    ),
    "ts/greeter.ts": "export const greet = (name: string): string => 'hello ' + name;\n",
    "ts/greeter.test.ts": (
        "import { test } from 'node:test';\nimport assert from 'node:assert/strict';\n"
        "import { greet } from './greeter.ts';\n"
        "test('greets', () => { assert.equal(greet('a'), 'hello a'); });\n"
    ),
    "jv/settings.gradle.kts": 'rootProject.name = "jv"\n',
    "jv/build.gradle.kts": BUILD
    % (
        "java",
        "java { toolchain { languageVersion = JavaLanguageVersion.of(25) } }",
        'testImplementation("org.junit.jupiter:junit-jupiter:5.10.2")',
        QUIET_LOGGING,
    ),
    "jv/src/main/java/demo/Greeter.java": (
        "package demo;\npublic class Greeter {\n"
        '    public static String greet(String n) { return "hello " + n; }\n}\n'
    ),
    "jv/src/test/java/demo/GreeterTest.java": (
        "package demo;\nimport org.junit.jupiter.api.Test;\n"
        "import static org.junit.jupiter.api.Assertions.assertEquals;\n"
        "class GreeterTest {\n"
        '    @Test void greets() { assertEquals("hello a", Greeter.greet("a")); }\n}\n'
    ),
    "kt/settings.gradle.kts": 'rootProject.name = "kt"\n',
    "kt/build.gradle.kts": BUILD
    % (
        'kotlin("jvm") version "2.4.20"',
        "kotlin { jvmToolchain(25) }",
        'testImplementation(kotlin("test"))',
        QUIET_LOGGING,
    ),
    "kt/src/main/kotlin/demo/Counter.kt": (
        "package demo\nclass Counter { var n = 0; fun bump() = ++n }\n"
    ),
    "kt/src/test/kotlin/demo/CounterTest.kt": (
        "package demo\nimport kotlin.test.Test\nimport kotlin.test.assertEquals\n"
        "class CounterTest { @Test fun bumps() { assertEquals(1, Counter().bump()) } }\n"
    ),
}
PLANTS = {
    "py/test_greeter.py": ("== 'hello a'", "== 'goodbye a'"),
    "ts/greeter.test.ts": ("'hello a'", "'goodbye a'"),
    "jv/src/test/java/demo/GreeterTest.java": ('"hello a"', '"goodbye a"'),
    "kt/src/test/kotlin/demo/CounterTest.kt": ("assertEquals(1,", "assertEquals(2,"),
}
ASSERTION = ("AssertionError", "AssertionFailedError", "expected:", "assert ")

needs_image = pytest.mark.skipif(
    not (IMAGE and STAGE), reason="set STUDYFORGE_EXAMPLE_IMAGE and STUDYFORGE_EXAMPLE_STAGE"
)


def build(root: Path) -> None:
    for where, text in FILES.items():
        (root / where).parent.mkdir(parents=True, exist_ok=True)
        (root / where).write_text(text, encoding="utf-8")
    (root / CODE_COPY).mkdir(parents=True)  # execution onboarding writes it in a real corpus
    sync(root)


def in_container(root: Path, run: tuple[str, list[str]]) -> tuple[int, str]:
    """Run one allowlist entry in the directory it names, offline; its exit code and output."""
    workdir, argv = run
    where = "/w" if workdir == ROOT_DIR else f"/w/{workdir}"
    command = [
        "docker", "--context", "desktop-linux", "run", "--rm", "--network", "none",
        "--read-only", "--tmpfs", "/tmp:rw,size=2g", *engine.run_as(),
        "-e", "HOME=/tmp/home", "-e", "GRADLE_USER_HOME=/tmp/gradle-home",
        "-v", f"{engine.bindable(root)}:/w", "-w", where, "--entrypoint", argv[0], IMAGE, *argv[1:],
    ]
    done = subprocess.run(  # noqa: S603 - fixed argv, no shell
        command, capture_output=True, text=True, check=False, stdin=subprocess.DEVNULL
    )
    return done.returncode, done.stdout + done.stderr


def by_language(root: Path) -> dict[str, tuple[str, list[str]]]:
    held = {}
    for workdir, argv in runs_of(root, RUNTIMES):
        key = {"python3": "py", "node": "ts"}.get(argv[0])
        if key is None:
            key = "jv" if "/jv" in " ".join(argv) else "kt"
        held[key] = (workdir, argv)
    return held


@needs_image
def test_each_of_the_four_examples_runs_and_passes_with_no_network():
    root = Path(STAGE) / uuid.uuid4().hex
    root.mkdir(parents=True)
    try:
        build(root)
        commands = by_language(root)
        assert sorted(commands) == ["jv", "kt", "py", "ts"]
        for language, run in commands.items():
            code, output = in_container(root, run)
            assert code == 0, (language, run, output[-2000:])
        assert (root / CODE_COPY / "jv/build/test-results/test/TEST-demo.GreeterTest.xml").is_file()
        assert (root / CODE_COPY / "kt/build/test-results/test/TEST-demo.CounterTest.xml").is_file()
        for language, marker in {"py": "1 passed", "ts": "pass 1"}.items():
            assert marker in in_container(root, commands[language])[1], language
    finally:
        shutil.rmtree(root, ignore_errors=True)


@needs_image
def test_a_planted_wrong_example_fails_on_an_assertion_in_each_language():
    root = Path(STAGE) / uuid.uuid4().hex
    root.mkdir(parents=True)
    try:
        build(root)
        for where, (old, new) in PLANTS.items():
            copy = root / CODE_COPY / where
            text = copy.read_text(encoding="utf-8")
            assert old in text
            copy.write_text(text.replace(old, new), encoding="utf-8")
        for language, run in by_language(root).items():
            code, output = in_container(root, run)
            assert code != 0, language
            assert any(word in output for word in ASSERTION), (language, output[-6000:])
    finally:
        shutil.rmtree(root, ignore_errors=True)
