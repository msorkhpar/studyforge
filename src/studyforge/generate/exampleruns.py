"""Which corpora have examples that name their code, so the Run strip's two files are written.

**What it does.** `wanted(corpus)` is true when any lesson document of any unit holds an example
block with a tab that names a `code` file. `generate.site` then writes `example-run.css` and
`example-run.js` beside the shared assets; every other corpus builds the files it always did.

`needed(corpus)` is every corpus-relative path the examples' Run needs in a release: the
files their tabs name as `code` and the `support` paths their blocks declare (a folder the
example imports, such as a shared harness). The standalone split keeps these in the learner tree.

**Depends on.** `generate.declarations`, `archive.blocks`, `archive.scrub`. ⛔ It reads a
document's tabs and decides nothing about a path: `render.page.examplerun` is the rule.
"""

from __future__ import annotations

import json
from collections.abc import Iterator

from studyforge.archive.blocks import walk as walk_blocks
from studyforge.archive.scrub import assert_clean
from studyforge.generate.declarations import Corpus

#: Where a unit's lesson documents sit, relative to the unit's archive directory.
LESSON_GLOB = "lesson-*.json"

#: What a refusal names in place of a path (R7): a lesson document, never where it sits.
LESSON_WHERE = "a unit's lesson document"


def wanted(corpus: Corpus) -> bool:
    """Does any unit carry an example whose tab names the file its code is?"""
    return any(code for code, _support in _declared(corpus))


def needed(corpus: Corpus) -> tuple[str, ...]:
    """Every path an example's Run needs: each tab's `code` file and each block's `support`."""
    found: set[str] = set()
    for code, support in _declared(corpus):
        found.update(code)
        found.update(support)
    return tuple(sorted(found))


def _declared(corpus: Corpus) -> Iterator[tuple[list[str], list[str]]]:
    """Yield `(code paths, support paths)` of every example block of every unit's lessons."""
    for source in corpus.units:
        for path in sorted(source.directory.glob(LESSON_GLOB)):
            try:
                document = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                continue
            assert_clean(document, LESSON_WHERE)
            blocks = document.get("blocks") if isinstance(document, dict) else None
            for block in walk_blocks(blocks if isinstance(blocks, list) else []):
                if isinstance(block, dict) and block.get("type") == "example":
                    yield _paths(block)


def _paths(block: dict) -> tuple[list[str], list[str]]:
    """The strings an example block names as `code` (per tab) and as `support`."""
    tabs = block.get("tabs")
    code = [
        tab["code"]
        for tab in (tabs if isinstance(tabs, list) else ())
        if isinstance(tab, dict) and isinstance(tab.get("code"), str)
    ]
    support = block.get("support")
    named = support if isinstance(support, list) else ()
    return code, [one for one in named if isinstance(one, str)]
