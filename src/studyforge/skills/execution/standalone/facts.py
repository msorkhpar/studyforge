r"""What a course holds, counted from its own files, for the learner's README to state.

**What it does.** Reads, from the tree `release` is writing, how many modules, units,
practices and quizzes the course has, which topic areas its modules sit in, and how
many code examples its pages carry. ⭐ A number it cannot read is `None`, and the
README does not print it: a wrong count is worse than none.

**How you use it.** `read(tree)` gives `Facts`; `tree` is a course's root (or a learner
tree), whose `archive/` holds the records and whose built pages sit beside them.

**Depends on.** `archive.document.KINDS` and `archive.layout.DOCUMENT_SUFFIX` for the
record names, `corpus.container.CONTAINER_FILENAME`, `corpus.placement` for the
archive's directory name. ⛔ It imports no reader that could refuse a course, and
starts no process.

## ⭐ A quiz is a practice with no starting code

⭐ The archive keeps a quiz as a practice record, and a code practice is the one that
carries `starting_code`. So `practices` counts every practice record, `quizzes` those
with none, and the code practices are the difference (`Facts.coded`).
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from pathlib import Path

from studyforge.archive.document import KINDS
from studyforge.archive.layout import DOCUMENT_SUFFIX
from studyforge.corpus.container import CONTAINER_FILENAME
from studyforge.corpus.placement.names import ARCHIVE_DIRNAME

#: The record kinds, by what they count.
LESSON, PRACTICE = KINDS

#: The attribute the build puts on a code example.
EXAMPLE = re.compile(r"<details data-code-example[ >]")

#: Directories a page count never enters: build files and the working copies.
SKIPPED = frozenset({".git", "images", "execution", "exercises", "practice", "node_modules"})


@dataclass(frozen=True, slots=True)
class Facts:
    """The counts a README states; each is None where it could not be read."""

    modules: int | None = None
    units: int | None = None
    practices: int | None = None
    quizzes: int | None = None
    examples: int | None = None
    areas: tuple[str, ...] = ()

    @property
    def coded(self) -> int | None:
        """The practices that are code, graded by a runner."""
        if self.practices is None:
            return None
        return self.practices - (self.quizzes or 0)


def _json(path: Path) -> dict:
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except OSError, ValueError:
        return {}
    return document if isinstance(document, dict) else {}


def _count(count: int) -> int | None:
    return count or None


def _areas(titles: list[list[str]]) -> tuple[str, ...]:
    """Return the first title of every container filed under another: the topic areas."""
    seen: dict[str, None] = {}
    for one in titles:
        if len(one) >= 2 and one[0]:
            seen.setdefault(one[0])
    return tuple(seen)


def _examples(tree: Path) -> int:
    found = 0
    for where, folders, names in os.walk(tree):
        folders[:] = sorted(one for one in folders if one not in SKIPPED)
        for name in names:
            if name.endswith(".html"):
                with (Path(where) / name).open(encoding="utf-8", errors="replace") as handle:
                    found += len(EXAMPLE.findall(handle.read()))
    return found


def read(tree: Path) -> Facts:
    """Count what the course at `tree` holds."""
    archive = Path(tree) / ARCHIVE_DIRNAME
    if not archive.is_dir():
        return Facts()
    containers = [_json(one) for one in sorted(archive.rglob(CONTAINER_FILENAME))]
    lessons = sum(1 for _ in archive.rglob(f"{LESSON}-*{DOCUMENT_SUFFIX}"))
    records = [_json(one) for one in sorted(archive.rglob(f"{PRACTICE}-*{DOCUMENT_SUFFIX}"))]
    titles = [[str(t) for t in one.get("titles", ())] for one in containers]
    return Facts(
        modules=_count(len(containers)),
        units=_count(lessons),
        practices=_count(len(records)),
        quizzes=_count(sum(1 for one in records if not one.get("starting_code"))),
        examples=_count(_examples(Path(tree))),
        areas=_areas(titles),
    )
