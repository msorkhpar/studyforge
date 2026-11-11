"""Whether a corpus carries math, so a build writes KaTeX's files for it and for no other corpus.

**What it does.** Reads every unit's lesson documents and answers whether any holds a `math` code
block or an inline formula (a code span between dollar signs, kept in the text as "$`").

**How you use it.** `generate.site` calls `wanted(corpus)` and writes `render.page.math.files()`.

**Depends on.** The corpus model, the archive's JSON and the R7 gate, which every lesson document
passes before it is read. Nothing renders here.
"""

from __future__ import annotations

import json

from studyforge.archive.scrub import assert_clean
from studyforge.generate.exampleruns import LESSON_GLOB, LESSON_WHERE

INLINE = "$`"


def wanted(corpus) -> bool:
    """Answer whether any lesson document of the corpus holds a formula."""
    for source in corpus.units:
        for path in sorted(source.directory.glob(LESSON_GLOB)):
            try:
                raw = path.read_text(encoding="utf-8")
                document = json.loads(raw)
            except OSError, ValueError:
                continue
            assert_clean(document, LESSON_WHERE)
            if INLINE in raw or _has_math_block(document):
                return True
    return False


def _has_math_block(document: object) -> bool:
    stack = [document]
    while stack:
        node = stack.pop()
        if isinstance(node, dict):
            if node.get("type") == "code" and node.get("lang") == "math":
                return True
            stack.extend(node.values())
        elif isinstance(node, list):
            stack.extend(node)
    return False
