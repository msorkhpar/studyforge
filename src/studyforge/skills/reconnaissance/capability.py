r"""Whether anything here is runnable, and whether a grader ships with it.

**What it does.** Answers the two questions that decide whether a corpus enters
the execution track at all — and answers *"no"* as a first-class result.

**How you use it.** `assess(inventory)` returns a `Capability`.

**Depends on.** `inventory`, `report`.

## ⭐ "No runnable code, no graders" is a complete answer, not a shortfall

⛔ **A corpus with no graders is complete at the reading floor, not short**
(spec §11.0, C5). The reading floor — narrated, navigable, offline pages — is a
*whole product* for prose material, and two of the four designed source shapes
have no build file of any kind.

⚠️ **So this module's job is to say "none" clearly**, with the evidence, rather
than to leave a section blank that a reader will mistake for "not looked at".
⛔ Measured (ISO-8583): **0 build files of any kind**, and its whole vocabulary
is five block types. That corpus is finished at M4.

## ⛔ Enumerate the legal, never the illegal

`BUILD_FILES` and `TEST_MARKERS` are **closed sets**. A build system this skill
does not recognise produces *"no build file found"* plus an `Uncertainty` — it
does not produce a guess, and it does not silently widen. ⚠️ A list of things
that are *not* build files would be an open set, and the unforeseen one would be
admitted without anybody deciding.

⭐ The cost of the closed set is exactly one question to a person, and the
question names what was looked for — which is also how the set grows.
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, field

from studyforge.skills.reconnaissance.inventory import Inventory
from studyforge.skills.reconnaissance.report import Observation, Uncertainty

#: Files that declare a build. ⛔ Closed; widened by a decision.
BUILD_FILES = (
    "pom.xml",
    "build.gradle",
    "build.gradle.kts",
    "settings.gradle",
    "package.json",
    "Cargo.toml",
    "go.mod",
    "pyproject.toml",
    "setup.py",
    "Makefile",
    "CMakeLists.txt",
    "build.sbt",
    "mix.exs",
    "Gemfile",
)

#: Path fragments that mean "a test lives here". ⚠️ Fragments rather than
#: filenames, because every ecosystem spells the directory differently and all
#: of them spell it recognisably.
TEST_MARKERS = ("src/test/", "tests/", "test/", "spec/", "__tests__/")

#: Filename shapes that mean "this file is a test".
TEST_NAMES = ("test_", "_test.", "Test.java", "Tests.java", ".test.", ".spec.")


@dataclass
class Capability:
    """What a corpus can do beyond being read."""

    build_files: list[str] = field(default_factory=list)
    test_files: list[str] = field(default_factory=list)
    source_files: list[str] = field(default_factory=list)

    @property
    def runnable(self) -> bool:
        """Whether there is a build the framework could invoke."""
        return bool(self.build_files)

    @property
    def graded(self) -> bool:
        """Whether a grader ships with the material."""
        return bool(self.test_files)


def assess(inventory: Inventory) -> Capability:
    """Walk the whole tree — not only the material — for build and test evidence.

    ⚠️ **Not only the material**, deliberately: a build file is not teaching
    material and `inventory.material` will never contain one. This is the one
    question that has to look at the files reconnaissance otherwise ignores.
    """
    found = Capability()
    for path in sorted(inventory.root.rglob("*")):
        parts = path.relative_to(inventory.root).parts
        if any(part.startswith(".") for part in parts):
            continue
        if not path.is_file():
            continue
        where = path.relative_to(inventory.root).as_posix()
        if path.name in BUILD_FILES:
            found.build_files.append(where)
        elif _is_test(where, path.name):
            found.test_files.append(where)
        elif path.suffix and path.suffix not in (".md", ".markdown", ".rst", ".txt"):
            found.source_files.append(where)
    return found


def _is_test(where: str, name: str) -> bool:
    """Say whether this path is a test, by where it sits or what it is called."""
    return any(marker in where for marker in TEST_MARKERS) or any(
        shape in name for shape in TEST_NAMES
    )


def observe(capability: Capability) -> Iterator[Observation | Uncertainty]:
    """Report both answers, including — especially — when both are "none"."""
    yield Observation("build files", f"{len(capability.build_files)} {capability.build_files[:3]}")
    yield Observation("files that look like graders", str(len(capability.test_files)))
    yield Observation("other source files", str(len(capability.source_files)))
    if not capability.runnable and not capability.graded:
        # ⭐ Stated as a finished answer. A blank section reads as "not looked
        # at", and the difference decides whether a corpus is planned to M4 or
        # to M8.
        yield Observation("verdict", "no runnable code, no graders — complete at the reading floor")
        if capability.source_files:
            yield Uncertainty(
                question="is any of this meant to be run?",
                why=(
                    f"{len(capability.source_files)} non-prose file(s) are present but "
                    f"no build file this skill knows: {list(BUILD_FILES[:4])}…"
                ),
                settles_it=(
                    "name the build file and the command that runs it, or "
                    "confirm the code is illustrative and is never executed"
                ),
            )
        return
    if capability.runnable and not capability.graded:
        yield Uncertainty(
            question="are there graders this skill did not recognise?",
            why=(
                f"{len(capability.build_files)} build file(s) but nothing matching "
                f"{list(TEST_MARKERS)} or {list(TEST_NAMES[:3])}"
            ),
            settles_it=(
                "point at one test, or confirm the corpus is ungraded — ⭐ an "
                "ungraded exercise is a first-class state (§7), not a gap"
            ),
        )
