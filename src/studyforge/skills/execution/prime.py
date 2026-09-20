r"""The prime project — the corpus's own build files, source and test, selected.

**What it does.** Finds, per declared runtime, the build and wrapper files a
build needs and the smallest **real** source and test the corpus already
carries, so an image can be warmed with a project that actually compiles.

**How you use it.** `prime_for(root, runtimes, seeded=…)` returns a `Prime`;
`Prime.copies()` is every corpus-relative path a generator copies.

**Depends on.** `pathlib` and `describe`. ⛔ It reads the corpus and writes
nothing, and it names no source (R1): every filename below belongs to a *build
tool* or a *language*, never to any corpus.

## ⛔ AN EMPTY PRIME PRIMES NOTHING WHILE APPEARING TO SUCCEED

⚠️ **The failure this module exists to prevent, spelled out because it is
silent:** a `NO-SOURCE` compile task never resolves the compiler classpath. An
image warmed with an empty prime builds, tags, and reports success — and then a
reader's first offline build downloads the world, or fails with no network at
all. Nothing says anything is wrong until then.

⭐ **So a declared runtime with no source, or no test, or no build file is
REFUSED by name.** That refusal is the step's whole point.

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
own.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from studyforge.describe import describe

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
class Prime:
    """Everything a warmed build needs, as paths into the corpus."""

    build_files: tuple[str, ...]
    specimens: tuple[Specimen, ...]

    def copies(self) -> tuple[str, ...]:
        """Every corpus-relative path a generator copies into the prime, sorted.

        ⭐ The relative path is preserved on the way in, because a package
        directory is part of a JVM source's identity and a specimen moved out
        of its package no longer compiles.
        """
        found = {*self.build_files}
        for specimen in self.specimens:
            found.update({specimen.source, specimen.test})
        return tuple(sorted(found))

    def document(self) -> dict[str, object]:
        """Return the prime as data, for the selection document a corpus keeps."""
        return {
            "build_files": list(self.build_files),
            "specimens": [
                {"language": one.language, "source": one.source, "test": one.test}
                for one in self.specimens
            ],
        }


def prime_for(root: Path, runtimes: Sequence[str], *, seeded: Sequence[str] = ()) -> Prime:
    """Select a prime for `runtimes` out of the corpus at `root`, or refuse."""
    if not isinstance(root, Path):
        raise PrimeRefused(f"the corpus root must be a path, got {describe(root)}")
    declared = tuple(sorted({name for name in runtimes if isinstance(name, str)}))
    held = _files(root)
    missing: list[str] = []
    build = _build_files(declared, seeded, held, missing)
    specimens = _specimens(declared, held, missing)
    if missing:
        raise PrimeRefused(
            "this corpus cannot be primed for what it declared, and an empty prime "
            "primes nothing while appearing to succeed (§8.1): " + "; ".join(missing)
        )
    return Prime(build_files=build, specimens=specimens)


def is_a_test(where: str) -> bool:
    """Whether a corpus-relative path is a test, by directory or by stem."""
    parts = where.split("/")
    if any(part.lower() in TEST_DIRECTORIES for part in parts[:-1]):
        return True
    stem = parts[-1].rsplit(".", 1)[0]
    return stem.startswith(TEST_PREFIX) or any(stem.endswith(one) for one in TEST_STEMS)


def _files(root: Path) -> tuple[tuple[str, int], ...]:
    """Every file under `root` worth selecting from, as `(relative path, size)`."""
    found = []
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        if any(part in SKIPPED for part in relative.split("/")):
            continue
        if path.is_file() and not path.is_symlink():
            found.append((relative, path.stat().st_size))
    return tuple(found)


def _build_files(
    declared: Sequence[str],
    seeded: Sequence[str],
    held: Sequence[tuple[str, int]],
    missing: list[str],
) -> tuple[str, ...]:
    """Every declared tool's build files, refusing a seeded tool that has none.

    ⚠️ **Matched by the tool's own file name at any depth**, because a
    multi-module project keeps its build files beside each module and a corpus
    that declares one is not obliged to be single-module.
    """
    names = [where for where, _ in held]
    found: set[str] = set()
    for runtime in declared:
        wanted = {
            where
            for where in names
            for one in BUILD_FILES.get(runtime, ())
            if where == one or where.endswith(f"/{one}")
        }
        found |= wanted
        if runtime in seeded and not wanted:
            missing.append(
                f"{runtime} is declared and its cache is seeded from a build, and this "
                f"corpus carries none of that tool's build files"
            )
    return tuple(sorted(found))


def _specimens(
    declared: Sequence[str], held: Sequence[tuple[str, int]], missing: list[str]
) -> tuple[Specimen, ...]:
    """One real source and one real test per declared language, or a reason."""
    found = []
    for runtime in declared:
        suffixes = SOURCE_SUFFIXES.get(runtime)
        if not suffixes:
            continue
        candidates = [
            (where, size) for where, size in held if where.endswith(suffixes) and size > 0
        ]
        source = _smallest(one for one in candidates if not is_a_test(one[0]))
        test = _smallest(one for one in candidates if is_a_test(one[0]))
        if source is None:
            missing.append(f"{runtime} is declared and this corpus carries no source for it")
        if test is None:
            missing.append(f"{runtime} is declared and this corpus carries no test for it")
        if source is not None and test is not None:
            found.append(Specimen(language=runtime, source=source, test=test))
    return tuple(found)


def _smallest(candidates) -> str | None:
    """Return the smallest candidate, ties broken by path so there is one answer."""
    ordered = sorted(candidates, key=lambda one: (one[1], one[0]))
    return ordered[0][0] if ordered else None
