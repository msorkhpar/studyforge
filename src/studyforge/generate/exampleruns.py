"""Which corpora have examples that name their code, so the Run strip's two files are written.

**What it does.** `wanted(corpus)` is true when any lesson document of any unit holds an example
block with a tab that names a `code` file. `generate.site` then writes `example-run.css` and
`example-run.js` beside the shared assets; every other corpus builds the files it always did.

**Depends on.** `generate.declarations`, `archive.blocks`, `archive.scrub`. ⛔ It reads a
document's tabs and decides nothing about a path: `render.page.examplerun` is the rule.
"""

from __future__ import annotations

import json

from studyforge.archive.blocks import walk as walk_blocks
from studyforge.archive.scrub import assert_clean
from studyforge.generate.declarations import Corpus

#: Where a unit's lesson documents sit, relative to the unit's archive directory.
LESSON_GLOB = "lesson-*.json"

#: What a refusal names in place of a path (R7): a lesson document, never where it sits.
LESSON_WHERE = "a unit's lesson document"


def wanted(corpus: Corpus) -> bool:
    """Does any unit carry an example whose tab names the file its code is?"""
    return any(_names_code(source.directory) for source in corpus.units)


def _names_code(directory) -> bool:
    """Does any lesson document in this unit's directory hold an example tab with `code`?"""
    for path in sorted(directory.glob(LESSON_GLOB)):
        try:
            document = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        assert_clean(document, LESSON_WHERE)
        blocks = document.get("blocks") if isinstance(document, dict) else None
        for block in walk_blocks(blocks if isinstance(blocks, list) else []):
            if isinstance(block, dict) and block.get("type") == "example":
                tabs = block.get("tabs")
                if any(isinstance(tab, dict) and "code" in tab for tab in tabs or ()):
                    return True
    return False
