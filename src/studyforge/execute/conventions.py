r"""What a build tool and a language call their own files: build files, sources, tests.

**What it does.** Spells, once, the names a declared runtime's TOOLS chose —
each build tool's build files, each language's source suffixes, the
directories a build writes into, and how a path says it holds a test — and
answers the two questions every reader of them asks: `is_a_test(path)` and
`source_suffixes(runtimes)`.

**How you use it.** `skills.execution.prime` selects a corpus's build and its
smallest source and test with them; `execute.codetree` copies a corpus's code
and `execute.codepair` pairs a test with its source by them; `generate` hands
`source_suffixes(manifest.runtimes)` to a page, which marks a link to a code
file by it.

**Depends on.** `corpus.manifest.runtimes` for each runtime's source
suffixes, which are the runtime vocabulary's and are re-published here. ⛔ Pure
constants and pure functions: every name below belongs to a *build tool*, a
*language* or *version control*, never to any corpus (R1).

## ⭐ One spelling, because three readers ask the same question

⚠️ **The prime selects out of a corpus's build, the copy mirrors it and the
pair walks it**, and each asks *which files are the build's, which are code,
which are tests and which directories are output*. ⛔ Three spellings of one
answer drift the day one of them learns a tool the others do not, and a copy
that took `target/` for source would compile a build's output as the reader's
code. ⭐ So the answer lives here, where `execute` — which runs the builds — and
`skills` — which prepares them — can both reach it.

⭐ **`SOURCE_SUFFIXES` lives beside the runtime vocabulary it is keyed on**
(`corpus.manifest.runtimes`), because the static route serves a code file as
text by it and `serve` reaches the manifest, never `execute`.
"""

from __future__ import annotations

from studyforge.corpus.manifest import SOURCE_SUFFIXES, source_suffixes

__all__ = [
    "BUILD_FILES",
    "SKIPPED",
    "SOURCE_SUFFIXES",
    "TEST_DIRECTORIES",
    "TEST_PREFIX",
    "SHARED_MODULE_LANGUAGES",
    "TEST_STEMS",
    "is_a_test",
    "other_language_suffixes",
    "source_suffixes",
    "tested_stem",
]

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

#: Directory names that hold no corpus code: build output, caches and version
#: control. ⚠️ A file taken from `build/` is a copy of a copy, and one taken
#: from a dependency tree is not this corpus's code at all.
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


#: Languages one build module may hold side by side and compile together, so a test
#: written in one may test a source written in another (a Java test of a Kotlin class).
#: ⛔ A *toolchain* fact, never a corpus's: only these pair across suffixes, so a corpus
#: declaring Python beside Java still pairs a test with a source of its own suffix only.
SHARED_MODULE_LANGUAGES = ("java", "kotlin")


def other_language_suffixes(suffix: str, runtimes: tuple[str, ...] | list[str]) -> tuple[str, ...]:
    """Return the source suffixes of the OTHER shared-module languages the corpus declares.

    ⭐ Empty unless `suffix` is one a shared-module language writes and at least one other
    such language is declared, so a one-language corpus has nothing to fall back to.
    """
    declared = [name for name in SHARED_MODULE_LANGUAGES if name in runtimes]
    if not any(suffix in SOURCE_SUFFIXES[name] for name in declared):
        return ()
    return tuple(
        sorted(one for name in declared for one in SOURCE_SUFFIXES[name] if one != suffix)
    )


def is_a_test(where: str) -> bool:
    """Whether a corpus-relative path is a test, by directory or by stem."""
    parts = where.split("/")
    if any(part.lower() in TEST_DIRECTORIES for part in parts[:-1]):
        return True
    stem = parts[-1].rsplit(".", 1)[0]
    return stem.startswith(TEST_PREFIX) or any(stem.endswith(one) for one in TEST_STEMS)


def tested_stem(stem: str) -> str:
    """Return the stem a test's stem names once its test marking is taken off.

    ⭐ `PrimitiveTypesTest` → `PrimitiveTypes`, `test_parse` → `parse`; a stem
    carrying no marking comes back as it came.
    """
    if stem.startswith(TEST_PREFIX):
        return stem[len(TEST_PREFIX) :]
    for one in sorted(TEST_STEMS, key=len, reverse=True):
        if stem.endswith(one) and len(stem) > len(one):
            return stem[: -len(one)]
    return stem
