"""Where a build's files sit: which directory a build file roots, and which builds a prime may warm.

**What it does.** Answers, for the paths a corpus holds, whether one is a tool's own build file,
the directory it roots, how deep that is, and which of several builds the component can warm.

**How you use it.** `prime` calls `is_build_file`, `directory_of`, `depth`, `under` and
`warmable` while it chooses a build. Pure functions of strings; no file is read.

**Depends on.** `execute.BUILD_FILES`. Standard library otherwise.
"""

from __future__ import annotations

from studyforge.execute import BUILD_FILES

GRADLE_CHECKSUMS = "gradle/verification-metadata.xml"  # the component warms no build without it


def warmable(tool: str, roots: set[str], names: set[str]) -> set[str]:
    """Every build directory; for Gradle, only those with checksums where any has them.

    ⭐ A build without checksums beside one with them is never the prime, at any depth: the
    component would refuse it, so the two are not counted as rival builds (an example build
    beside the corpus's prime build at the same depth). Where every build or none has them,
    every build is a candidate, as before.
    """
    pinned = {one for one in roots if f"{one}/{GRADLE_CHECKSUMS}".lstrip("/") in names}
    return pinned if tool == "gradle" and pinned else roots


def is_build_file(where: str, tool: str) -> bool:
    """Whether `where` is one of `tool`'s own build files, at any depth."""
    return any(where == one or where.endswith(f"/{one}") for one in BUILD_FILES.get(tool, ()))


def directory_of(where: str, tool: str) -> str:
    """Return the build directory a build file belongs to: its path less the tool's name."""
    for one in BUILD_FILES.get(tool, ()):
        if where == one:
            return ""
        if where.endswith(f"/{one}"):
            return where[: -len(one) - 1]
    return where.rsplit("/", 1)[0] if "/" in where else ""


def depth(directory: str) -> int:
    return len(directory.split("/")) if directory else 0


def under(where: str, base: str) -> bool:
    return not base or where.startswith(f"{base}/")
