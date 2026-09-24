r"""The prime — one project per seeded build tool, out of the corpus's own build.

**What it does.** Finds, for each build tool the component seeds and the
corpus declares, the corpus's **own** build — its shallowest build file's
directory and every build file under it — and the smallest **real** source and
test inside that build, so an image can be warmed with a project that
actually compiles.

**How you use it.** `prime_for(root, runtimes, seeded=…)` returns a `Prime`;
`Prime.copies()` is every `(path in the prime, corpus-relative path)` pair a
generator copies.

**Depends on.** `pathlib`, `describe`, and the exercise layout's two directory
names. ⛔ It reads the corpus and writes nothing, and it names no source (R1):
every filename below belongs to a *build tool*, a *language* or the
*framework's own exercise layout*, never to any corpus.

## ⛔ THE PRIME IS THE COMPONENT'S LAYOUT, AND ITS NAMES ARE THE CONTRACT'S

⚠️ **Measured:** a prime holding the corpus's files at their
corpus-relative paths is REFUSED by the runner's build (exit 2), because the
component warms **one project directory per seeded tool** and nothing else at
the top. ⭐ **So each project is copied to `<tool>/…`, re-rooted at its own
build's directory**, and `<tool>` is a key of the contract's own
`runner.prime.seeds` map, which arrives here as `seeded`. ⛔ No tool name is
chosen here for the directory: a runtime the contract does not seed gets no
directory, and a seed key the contract renames renames the directory.

⭐ **Re-rooting keeps what a JVM build needs**: a specimen's path *below* its
build's directory is preserved, so a package directory still sits where the
build file expects it.

## ⛔ THE PRIME IS THE CORPUS'S OWN BUILD, NEVER THE SUM OF ITS EXERCISES'

⚠️ **An authored exercise carries a build role**: a `pom.xml` in its
bundle, and a copy of it laid into the reader's workspace. ⛔ **Neither is the
corpus's declared build**, and matching build files at any depth would sweep
every one into the prime. ⭐ So the bundle directory is never read from, and
neither is any workspace a bundle on disk owns — both named by the exercise
layout's own constants, never by a corpus.

## ⛔ AN EMPTY PRIME PRIMES NOTHING WHILE APPEARING TO SUCCEED

⚠️ **The failure this module exists to prevent, spelled out because it is
silent:** a `NO-SOURCE` compile task never resolves the compiler classpath. An
image warmed with an empty prime builds, tags, and reports success — and then a
reader's first offline build downloads the world, or fails with no network at
all. Nothing says anything is wrong until then.

⭐ **So a seeded tool with no build file, or a build with no source or no test
in it, is REFUSED by name.** That refusal is the step's whole point. ⚠️ A
corpus that declares no seeded tool gets an EMPTY prime and no refusal: the
component warms nothing for it, so there is nothing to prime.

## ⛔ NOTHING HERE IS AUTHORED, AND THAT IS R19 AND §8.1 AGREEING

⛔ **This module writes no build file, no dependency version and no test
framework.** §8.1 says the prime *copies the consuming repository's wrapper and
build files*; the corpus's own material is what supplies them, and its own
tests already use its own framework at its own version.

⚠️ **A version typed here is a version that disagrees with the corpus the day
the corpus moves**, and §8.1's own version guard would then fail a build over a
disagreement this skill created. ⭐ Selecting is the only honest operation: the
smallest real file the corpus already has cannot be wrong about the corpus.

## ⭐ WHICH RUNTIMES OWE A BUILD FILE IS THE CONTRACT'S ANSWER, NOT THIS MODULE'S

⚠️ `seeded` arrives from the component's own prime block, which maps a runtime
to the cache volume that runtime is seeded into. ⛔ **A runtime the contract
seeds and the corpus cannot build is refused; one it does not seed is not**, so
a corpus of plain scripts is never asked for a build file it has no reason to
own — and gets no project in the prime either.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from studyforge.corpus.placement import PRACTICE_DIRNAME
from studyforge.describe import describe
from studyforge.exercise.bundle import BUNDLE_FILENAME, BUNDLES_DIRNAME

#: A build tool's own files, by that tool's own names. ⛔ Names a *tool* chose,
#: never names a corpus chose (R1). A runtime absent here brings no build file.
BUILD_FILES: dict[str, tuple[str, ...]] = {
    "maven": ("pom.xml", ".mvn/wrapper/maven-wrapper.properties", "mvnw", "mvnw.cmd"),
    "gradle": (
        "build.gradle",
        "build.gradle.kts",
        "settings.gradle",
        "settings.gradle.kts",
        "gradle.properties",
        "gradlew",
        "gradlew.bat",
        "gradle/wrapper/gradle-wrapper.properties",
        "gradle/wrapper/gradle-wrapper.jar",
        "gradle/verification-metadata.xml",
        "gradle/libs.versions.toml",
    ),
    "node": ("package.json", "package-lock.json", "npm-shrinkwrap.json"),
    "python": ("pyproject.toml", "requirements.txt", "setup.cfg", "setup.py"),
}

#: The source suffixes a declared **runtime** writes, by that runtime's name.
#: ⛔ **Keyed on `corpus.json`'s `runtimes`, never on its `variants`** — and the
#: distinction is the defect §4 records: a single module-level map that answered
#: both *"can this be filed here?"* and *"can we run it?"* left eight SQL
#: courses unfileable. ⭐ `runtimes` is the declaration that IS about running
#: (§7), so a map keyed on it derives nothing from a filing key.
#:
#: ⚠️ **It is `SOURCE_SUFFIXES` and not `LANGUAGES` for that reason**, and
#: `tests/studyforge/corpus/manifest/test_document.py` holds the name: the
#: spelling it refuses is the spelling the original defect had.
SOURCE_SUFFIXES: dict[str, tuple[str, ...]] = {
    "java": (".java",),
    "kotlin": (".kt",),
    "node": (".js", ".mjs", ".cjs", ".ts"),
    "python": (".py",),
    "shell": (".sh", ".bash"),
    "sqlite": (".sql",),
}

#: Directory names a prime never selects out of: build output, caches and
#: version control. ⚠️ A specimen taken from `build/` is a copy of a copy, and
#: one taken from a dependency tree is not this corpus's code at all.
SKIPPED = (
    ".git",
    ".gradle",
    ".idea",
    ".mvn",
    ".studyforge",
    ".venv",
    "__pycache__",
    "bin",
    "build",
    "dist",
    "graphify-out",
    "node_modules",
    "out",
    "target",
    "venv",
)

#: How a path says it holds a test. ⭐ Two independent signals, because the two
#: conventions are genuinely different: a directory in the JVM and Go worlds, a
#: filename stem nearly everywhere else.
TEST_DIRECTORIES = ("test", "tests", "spec", "specs")

#: Stem shapes a test file takes. ⛔ Compared case-sensitively on the suffix
#: forms and case-insensitively on nothing: `Test` is a Java convention and
#: `test_` a Python one, and conflating them matches ordinary prose modules.
TEST_STEMS = ("Test", "Tests", "_test", ".test", "Spec", ".spec", "_spec")

#: The prefix a test stem may carry instead.
TEST_PREFIX = "test_"


class PrimeRefused(ValueError):
    """A prime that would prime nothing, and exactly what is missing from it."""


@dataclass(frozen=True, slots=True)
class Specimen:
    """One language's real source and real test, as corpus-relative paths."""

    language: str
    source: str
    test: str


@dataclass(frozen=True, slots=True)
class Project:
    """One seeded tool's project: the corpus's own build, and what it compiles."""

    #: The seed key, which is also the project's directory in the prime.
    tool: str
    #: The build's directory, corpus-relative; `""` when it is the corpus root.
    root: str
    build_files: tuple[str, ...]
    specimens: tuple[Specimen, ...]

    def copies(self) -> tuple[tuple[str, str], ...]:
        """`(path in the prime, corpus-relative path)` for every file, sorted.

        ⭐ Re-rooted at the build's directory and nothing more, because a
        package directory is part of a JVM source's identity and a specimen
        moved out of its package no longer compiles.
        """
        found = {*self.build_files}
        for specimen in self.specimens:
            found.update({specimen.source, specimen.test})
        cut = len(self.root) + 1 if self.root else 0
        return tuple(sorted((f"{self.tool}/{origin[cut:]}", origin) for origin in found))


@dataclass(frozen=True, slots=True)
class Prime:
    """Everything a warmed build needs: one project per seeded tool, or none."""

    projects: tuple[Project, ...]

    @property
    def build_files(self) -> tuple[str, ...]:
        """Every build file the prime carries, corpus-relative and sorted."""
        return tuple(sorted(one for project in self.projects for one in project.build_files))

    @property
    def specimens(self) -> tuple[Specimen, ...]:
        """Every project's specimens, in project order."""
        return tuple(one for project in self.projects for one in project.specimens)

    def copies(self) -> tuple[tuple[str, str], ...]:
        """`(path in the prime, corpus-relative path)` for every file, sorted."""
        return tuple(sorted(pair for project in self.projects for pair in project.copies()))

    def document(self) -> dict[str, object]:
        """Return the prime as data, for the selection document a corpus keeps."""
        return {
            "projects": [
                {
                    "tool": project.tool,
                    "root": project.root,
                    "build_files": list(project.build_files),
                    "specimens": [
                        {"language": one.language, "source": one.source, "test": one.test}
                        for one in project.specimens
                    ],
                }
                for project in self.projects
            ]
        }


def prime_for(root: Path, runtimes: Sequence[str], *, seeded: Sequence[str] = ()) -> Prime:
    """Select a prime for `runtimes` out of the corpus at `root`, or refuse."""
    if not isinstance(root, Path):
        raise PrimeRefused(f"the corpus root must be a path, got {describe(root)}")
    declared = tuple(sorted({name for name in runtimes if isinstance(name, str)}))
    held = _files(root)
    missing: list[str] = []
    found = [_project(tool, declared, held, missing) for tool in declared if tool in seeded]
    if missing:
        raise PrimeRefused(
            "this corpus cannot be primed for what it declared, and an empty prime "
            "primes nothing while appearing to succeed (§8.1): " + "; ".join(missing)
        )
    return Prime(projects=tuple(one for one in found if one is not None))


def is_a_test(where: str) -> bool:
    """Whether a corpus-relative path is a test, by directory or by stem."""
    parts = where.split("/")
    if any(part.lower() in TEST_DIRECTORIES for part in parts[:-1]):
        return True
    stem = parts[-1].rsplit(".", 1)[0]
    return stem.startswith(TEST_PREFIX) or any(stem.endswith(one) for one in TEST_STEMS)


def _files(root: Path) -> tuple[tuple[str, int], ...]:
    """Every file under `root` worth selecting from, as `(relative path, size)`.

    ⛔ Never an exercise's: not its bundle, and not a workspace a bundle owns.
    """
    found = []
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        if any(part in SKIPPED for part in relative.split("/")):
            continue
        if path.is_file() and not path.is_symlink():
            found.append((relative, path.stat().st_size))
    exercised = _exercise_material(where for where, _ in found)
    return tuple(one for one in found if not one[0].startswith(exercised))


def _exercise_material(held) -> tuple[str, ...]:
    """Return the prefixes exercise material occupies: the bundles, and their workspaces.

    ⭐ A workspace is found from its bundle, because the two roots share one
    tail (`exercise.bundle.Places`): `<bundles>/<tail>` and `<practice>/<tail>`.
    """
    prefixes = [f"{BUNDLES_DIRNAME}/"]
    for where in held:
        parts = where.split("/")
        if parts[0] == BUNDLES_DIRNAME and parts[-1] == BUNDLE_FILENAME and len(parts) > 2:
            prefixes.append("/".join([PRACTICE_DIRNAME, *parts[1:-1]]) + "/")
    return tuple(prefixes)


def _project(
    tool: str,
    declared: Sequence[str],
    held: Sequence[tuple[str, int]],
    missing: list[str],
) -> Project | None:
    """One seeded tool's project out of the corpus's own build, or a reason why not.

    ⚠️ **Rooted at the SHALLOWEST directory holding one of the tool's build
    files**, and every build file under it is kept, because a multi-module
    project keeps its build files beside each module. ⛔ Two builds at the same
    shallowest depth are two projects, and the component warms one per tool,
    so that is refused by name rather than one picked.
    """
    names = [where for where, _ in held]
    wanted = [where for where in names if _is_build_file(where, tool)]
    if not wanted:
        missing.append(
            f"{tool} is declared and its cache is seeded from a build, and this "
            f"corpus carries none of that tool's build files"
        )
        return None
    roots = {_directory_of(where, tool) for where in wanted}
    depth = min(_depth(one) for one in roots)
    shallowest = sorted(one for one in roots if _depth(one) == depth)
    if len(shallowest) > 1:
        missing.append(
            f"{tool} is declared and this corpus carries {len(shallowest)} separate builds "
            f"at the same depth ({', '.join(one or '.' for one in shallowest)}), and the "
            f"component warms one project per tool; keep one build and make the rest its "
            f"modules"
        )
        return None
    base = shallowest[0]
    inside = [(where, size) for where, size in held if _under(where, base)]
    return Project(
        tool=tool,
        root=base,
        build_files=tuple(sorted(where for where in wanted if _under(where, base))),
        specimens=_specimens(tool, base, declared, inside, missing),
    )


def _is_build_file(where: str, tool: str) -> bool:
    """Whether `where` is one of `tool`'s own build files, at any depth."""
    return any(where == one or where.endswith(f"/{one}") for one in BUILD_FILES.get(tool, ()))


def _directory_of(where: str, tool: str) -> str:
    """Return the build directory a build file belongs to: its path less the tool's name."""
    for one in BUILD_FILES.get(tool, ()):
        if where == one:
            return ""
        if where.endswith(f"/{one}"):
            return where[: -len(one) - 1]
    return where.rsplit("/", 1)[0] if "/" in where else ""


def _depth(directory: str) -> int:
    return len(directory.split("/")) if directory else 0


def _under(where: str, base: str) -> bool:
    return not base or where.startswith(f"{base}/")


def _specimens(
    tool: str,
    base: str,
    declared: Sequence[str],
    held: Sequence[tuple[str, int]],
    missing: list[str],
) -> tuple[Specimen, ...]:
    """One real source and one real test per declared language inside the build.

    ⚠️ A declared language with no file in this build is not this build's
    language and is passed over; one with a source and no test, or a test and
    no source, is refused; and a build with no pair at all is refused, because
    it would compile nothing.
    """
    found, before = [], len(missing)
    languages = [runtime for runtime in declared if SOURCE_SUFFIXES.get(runtime)]
    where = f"the {tool} build at {base or '.'}"
    for runtime in languages:
        suffixes = SOURCE_SUFFIXES[runtime]
        candidates = [(one, size) for one, size in held if one.endswith(suffixes) and size > 0]
        source = _smallest(one for one in candidates if not is_a_test(one[0]))
        test = _smallest(one for one in candidates if is_a_test(one[0]))
        if source is not None and test is not None:
            found.append(Specimen(language=runtime, source=source, test=test))
        elif source is not None:
            missing.append(f"{runtime} is declared and {where} carries no test for it")
        elif test is not None:
            missing.append(f"{runtime} is declared and {where} carries no source for it")
    if not found and len(missing) == before:
        missing.append(
            f"{where} carries no source and no test in any declared language "
            f"({', '.join(languages) or 'none declared'}), so it would compile nothing"
        )
    return tuple(found)


def _smallest(candidates) -> str | None:
    """Return the smallest candidate, ties broken by path so there is one answer."""
    ordered = sorted(candidates, key=lambda one: (one[1], one[0]))
    return ordered[0][0] if ordered else None
