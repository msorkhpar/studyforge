"""Whether a corpus carries a diagram, so a build writes Mermaid's files for it and for no other.

**What it does.** Reads every unit's lesson documents and answers whether any holds a `code` block
whose language is `mermaid`, at any depth: in a quote, a disclosure or a list item too.

**How you use it.** `generate.site` calls `wanted(corpus)` and writes `render.page.diagram_files()`.

**Depends on.** The corpus model, the archive's JSON and the R7 gate, which every lesson document
passes before it is read. Nothing renders here.

⛔ **Every depth, not only the top level.** The figure renderer frames a `mermaid` fence as a
diagram wherever it sits, and `render.page.diagram.links` then links Mermaid: a corpus whose only
diagram is inside a list item must still write the files that page links.
"""

from __future__ import annotations

import json

from studyforge.archive.scrub import assert_clean
from studyforge.generate.exampleruns import LESSON_GLOB, LESSON_WHERE

#: The fence language a diagram is written in. ⚠️ The figure renderer's own word
#: (`render.page.blocks.figure.DIAGRAM_LANGUAGE`); this module's test builds a corpus and
#: holds the two in step by behaviour.
DIAGRAM_LANGUAGE = "mermaid"


def wanted(corpus) -> bool:
    """Answer whether any lesson document of the corpus holds a diagram."""
    for source in corpus.units:
        for path in sorted(source.directory.glob(LESSON_GLOB)):
            try:
                raw = path.read_text(encoding="utf-8")
                document = json.loads(raw)
            except OSError, ValueError:
                continue
            assert_clean(document, LESSON_WHERE)
            if DIAGRAM_LANGUAGE in raw and _has_diagram(document):
                return True
    return False


def _has_diagram(document: object) -> bool:
    stack = [document]
    while stack:
        node = stack.pop()
        if isinstance(node, dict):
            if node.get("type") == "code" and node.get("lang") == DIAGRAM_LANGUAGE:
                return True
            stack.extend(node.values())
        elif isinstance(node, list):
            stack.extend(node)
    return False
