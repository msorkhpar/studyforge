r"""The one command that runs a test file in the copy of a corpus's code.

**What it does.** `argv_for(files, test, module, runtimes)` answers the argv a runner starts to
run ONE test file, chosen by the test's suffix and the build file its module holds, or `None`
where no command is known; `workdir_for(test)` answers the directory that argv starts in.
`execute.codepair` pairs files and asks this for both.

**Depends on.** `codetree` for where the copy is. ⛔ Reads the corpus and writes nothing, and
names no corpus (R1): every name below is a tool's or a language's.

## ⭐ One command per kind of test

- `.py` (corpus declares `python`): `python3 -m pytest -q -p no:cacheprovider <test>`, started
  in the copy's ROOT (see below);
- `.ts`, `.js`, `.mjs`, `.cjs` (declares `node`): `node --test <test>`;
- a JVM test, by the build file its module holds, Maven first: a `pom.xml` gives Maven's
  command (the reactor, `-pl <module> -am`, one class) exactly as it always has; otherwise,
  with `gradle` declared, a `build.gradle(.kts)` or `settings.gradle(.kts)` gives
  `gradle --offline -q -p <build> [:<dir>:]cleanTest [:<dir>:]test --tests <package.Class>`,
  the class named by the package its file declares.

## ⭐ A Python test starts in the copy's root, so the corpus root is its import root

⚠️ **Measured:** an example whose program imports a package at the corpus root (`from harness
import ...`, a folder its block declares as `support`) failed its Run with `No module named
'harness'`: started in the runner's `/work`, pytest put only the test's own folder on the path.
⭐ So a `.py` test runs with the copy's root (`CODE_COPY`) as its working directory and its path
relative to it: `python3 -m` puts the working directory first on the import path, so a folder
named from the corpus root imports exactly as it does when the corpus is run from its root.
Every other command starts in the runner's root (`ROOT_DIR`), as it always has.

⚠️ A Gradle subproject is addressed by its directory path, which is its name unless the
settings file renames it; a directory name Gradle would not take unchanged gets no command
rather than a wrong one. ⛔ A corpus declaring a language but no tool for it gets none, and
the page then offers no Run.
"""

from __future__ import annotations

import re
from pathlib import Path, PurePosixPath

from studyforge.execute.codetree import CODE_COPY, in_copy
from studyforge.execute.commands import ROOT_DIR

MAVEN = "maven"
POM = "pom.xml"
GRADLE = "gradle"
PYTHON = "python"
NODE = "node"

#: The suffixes whose test a script runner runs; a JVM test's build file decides, not its suffix.
PYTHON_SUFFIXES = (".py",)
NODE_SUFFIXES = (".cjs", ".js", ".mjs", ".ts")

#: A Gradle build's own files: a module with one is a Gradle project, and a settings file
#: marks the build's root.
GRADLE_SETTINGS = ("settings.gradle", "settings.gradle.kts")
GRADLE_PROJECT_FILES = ("build.gradle", "build.gradle.kts", *GRADLE_SETTINGS)

#: A directory name Gradle takes as a project name unchanged.
PROJECT_NAME = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_.-]*")

#: What a source file's `package` line says, and the most of a file read for it.
PACKAGE = re.compile(
    r"^\s*package\s+([A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*)\s*;?\s*$", re.M
)
PACKAGE_HEAD = 16 * 1024


def argv_for(
    files: dict[str, Path], test: str, module: str, runtimes: tuple[str, ...] | list[str]
) -> list[str] | None:
    """Return the argv that runs `test` (in build module `module`) among `files`, or `None`."""
    suffix = PurePosixPath(test).suffix
    if suffix in PYTHON_SUFFIXES:
        return _pytest(test) if PYTHON in runtimes else None
    if suffix in NODE_SUFFIXES:
        return _node(test) if NODE in runtimes else None
    if MAVEN in runtimes and _in(module, POM) in files:
        return _maven(files, test, module)
    if GRADLE in runtimes:
        return _gradle(files, test, module)
    return None


def workdir_for(test: str) -> str:
    """Return the directory, relative to the runner's root, that `test`'s command starts in.

    ⭐ The copy's root for a Python test, so the corpus root is on its import path; the
    runner's root for every other test, whose command names the copy itself.
    """
    return CODE_COPY if PurePosixPath(test).suffix in PYTHON_SUFFIXES else ROOT_DIR


def _pytest(test: str) -> list[str]:
    """Return the argv that runs one pytest file from the copy's root, leaving no cache behind."""
    return ["python3", "-m", "pytest", "-q", "-p", "no:cacheprovider", test]


def _node(test: str) -> list[str]:
    """Return the argv that runs one test file under Node's own runner."""
    return ["node", "--test", in_copy(test)]


def _maven(files: dict[str, Path], test: str, module: str) -> list[str]:
    """Return the Maven argv that runs `test`: its module built from the topmost reactor."""
    reactor = module
    while reactor and _in(_parent(reactor), POM) in files:
        reactor = _parent(reactor)
    argv = ["mvn", "-B", "-o", "-f", in_copy(_in(reactor, POM))]
    if module != reactor:
        cut = len(reactor) + 1 if reactor else 0
        argv += ["-pl", module[cut:], "-am"]
    stem = PurePosixPath(test).stem
    return [*argv, "test", f"-Dtest={stem}", "-Dsurefire.failIfNoSpecifiedTests=false"]


def _gradle(files: dict[str, Path], test: str, module: str) -> list[str] | None:
    """Return the Gradle argv that runs `test`'s class, or `None` where the module has no build.

    ⭐ The build is the module's nearest ancestor holding a settings file (the module itself
    where none does); a module below it is addressed as `:a:b:`.
    """
    if not any(_in(module, one) in files for one in GRADLE_PROJECT_FILES):
        return None
    build = module
    while build and not any(_in(build, one) in files for one in GRADLE_SETTINGS):
        build = _parent(build)
    if not any(_in(build, one) in files for one in GRADLE_SETTINGS):
        build = module
    names = module[len(build) :].strip("/").split("/") if module != build else []
    if any(not PROJECT_NAME.fullmatch(name) for name in names):
        return None
    prefix = "".join(f":{name}" for name in names)
    tasks = [f"{prefix}:cleanTest", f"{prefix}:test"] if prefix else ["cleanTest", "test"]
    where = in_copy(build) if build else CODE_COPY
    return ["gradle", "--offline", "-q", "-p", where, *tasks, "--tests", _class(files, test)]


def _class(files: dict[str, Path], test: str) -> str:
    """Return the class a JVM test file declares: its package, a dot, its stem."""
    try:
        with files[test].open(encoding="utf-8", errors="replace") as handle:
            declared = PACKAGE.search(handle.read(PACKAGE_HEAD))
    except OSError:
        declared = None
    stem = PurePosixPath(test).stem
    return f"{declared.group(1)}.{stem}" if declared else stem


def _in(directory: str, name: str) -> str:
    return f"{directory}/{name}" if directory else name


def _parent(directory: str) -> str:
    return directory.rpartition("/")[0]
