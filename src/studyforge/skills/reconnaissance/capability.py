r"""Whether anything here is runnable, and whether a grader ships with it.

**What it does.** Answers the two questions that decide whether a corpus enters
the execution track at all — and answers *"no"* as a first-class result.

**How you use it.** `assess(inventory)` returns a `Capability`.

**Depends on.** `inventory` — for the walk as well as for the tree —
`report`, and `validate.source` for the directories a root never enters.

## ⭐ "No runnable code, no graders" is a complete answer, not a shortfall

⛔ **A corpus with no graders is complete at the reading floor, not short**
(spec §11.0, C5). The reading floor — narrated, navigable, offline pages — is a
*whole product* for prose material, and two of the four designed source shapes
have no build file of any kind.

⚠️ **So this module's job is to say "none" clearly**, with the evidence, rather
than to leave a section blank that a reader will mistake for "not looked at".
⛔ Two of the designed corpora have **no build file of any kind**; they are
finished at M4. `SKILL.md`, appendix **A4**, holds the counts.

## ⛔ Enumerate the legal, never the illegal

`BUILD_FILES` and `TEST_MARKERS` are **closed sets**. A build system this skill
does not recognise produces *"no build file found"* plus an `Uncertainty` — it
does not produce a guess, and it does not silently widen. ⚠️ A list of things
that are *not* build files would be an open set, and the unforeseen one would be
admitted without anybody deciding.

⭐ The cost of the closed set is exactly one question to a person, and the
question names what was looked for — which is also how the set grows.

## ⛔ The framework's own generated checks are not this corpus's graders

⚠️ **Counting the *generated* `tests/**/test_*.py` of a corpus this framework
has already onboarded as graders** would flip `graded` from false to true, drop
the *"no runnable code, no graders"* verdict, and draft `exercises: true` on a
corpus whose own onboarding report printed `graded practices  no`. ⛔ **A corpus
that is COMPLETE at the reading floor would then be presented to its reader as
unfinished** (C5).

⭐ So this pass asks `inventory` rather than the disk, and both of `inventory`'s
answers are instruments that already existed: `generated` is onboarding's own
record of what it wrote, and `enumerated` is `source_files`, which stops where
`validate` stops — outside the archive a build writes. ⛔ **There is no third
test here, and no test of this module's own**: not a name, not a suffix, not a
directory. A pass that recognised the framework's output by its spelling would
be a second rule to keep in step with the first.
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import PurePosixPath

from studyforge.skills.reconnaissance.inventory import Inventory, enters
from studyforge.skills.reconnaissance.report import Observation, Uncertainty
from studyforge.validate.source import SKIP_DIRS

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

    ⛔ **But never this framework's own output**: `inventory.generated`
    is onboarding's record of what it wrote, and a corpus's execution question
    is about the corpus.

    ⛔ **And it is `inventory`'s walk, not a second one**. This pass
    kept its own: it enumerated the tree itself and entered every directory
    `inventory.NOT_MATERIAL` names, so `__pycache__` supplied graders — and
    after a corpus had run the checks onboarding generated for it, the bytecode
    of those checks flipped `graded` on a corpus with none. ⚠️ It also counted
    the archive a build had written as the corpus's own source, which flipped
    `placement`. Both stop at `inventory.enumerated`.
    """
    found = Capability()
    for where in sorted(inventory.enumerated):
        parts = PurePosixPath(where).parts
        if parts[0] in SKIP_DIRS or not all(enters(part) for part in parts[:-1]):
            continue
        name = parts[-1]
        if name.startswith(".") or where in inventory.generated:
            continue
        suffix = PurePosixPath(where).suffix
        if name in BUILD_FILES:
            found.build_files.append(where)
        elif _is_test(where, name):
            found.test_files.append(where)
        elif suffix and suffix not in (".md", ".markdown", ".rst", ".txt"):
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
        # at", and the difference decides whether a corpus finishes at the
        # reading floor or enters the execution track.
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
