"""`corpus.json` — the declaration that makes a directory a source.

**What it does.** Owns the manifest: its version, the corpus's identity, the
container levels that fix its depth, its variants, its placement profile, what
counts as its content, whether it commits its media, and the enumerated set of
existing files it may add to.

**How you use it.** `load(path)` or `parse(text)`; then ask the `Manifest`.

    from studyforge.corpus.manifest import load

    manifest = load("corpus.json")
    manifest.depth                       # 2 — len(levels)
    manifest.parse_key("basics/01-intro") # an Address, checked against that depth
    manifest.content.classify("src/whole-series.md")  # Classification.EXCLUDED
    manifest.media.commits               # True — 'auto' commits
    manifest.allows_edit_to("pom.xml")   # R3's declaration, asked not assumed

**Depends on.** `studyforge.address`, `studyforge.version` for the R9 gate,
and the standard library. ⛔ Nothing source-specific (R1), asserted over the
whole of `src/` rather than promised.

⭐ **This file is where a corpus's customisation lives** (SK-07). Everything
that differs between two sources and is not the source's own content is a
field here — which is what makes "every artifact is generated" and "every
corpus is different" both true at once. ⛔ If a corpus needs something this
file cannot express, **the manifest is missing a field**, and that is the
finding; it is never a hand-edit to generated output.

## What is in the package

| Module | Owns |
|---|---|
| `document` | `Manifest`, `parse`, `load` — the document and its version (R9) |
| `content` | `include` / `exclude` / `not_material`, and `classify` (C2) |
| `edits` | `permitted_edits`, the three targets R3 never permits, and the undo |
| `media` | the commit mode and its limits; an absent key is a **stated** default |
| `errors` | `ManifestError`, the only exception any of it raises |

⛔ **An unknown `corpus_api` is refused, never migrated at read time** (R9),
and the test itself is `studyforge.version`'s — this package owns the *set* of
versions it speaks, not the check (SF-33).
⛔ **A file matching none of `include`, `exclude` and `not_material` is
unclassified**, and that is a refusal at validate time, not a shrug — silence
is the failure C2 describes. ⚠️ **A file matching `include` *and*
`not_material` is refused too**, under its own rule, because a precedence
between them would decide by rule order what nobody declared.
"""

from __future__ import annotations

from studyforge.corpus.manifest.content import (
    MIN_WHY_CHARS,
    Classification,
    ContentPolicy,
    Exclusion,
    NotMaterial,
    parse_content,
)
from studyforge.corpus.manifest.document import (
    CORPUS_API,
    KNOWN_CORPUS_API,
    MANIFEST_FILENAME,
    MANIFEST_KEYS,
    PLACEMENT_PROFILES,
    REQUIRED_KEYS,
    Manifest,
    from_document,
    load,
    parse,
)
from studyforge.corpus.manifest.edits import (
    EDIT_KINDS,
    PermittedEdit,
    Reversal,
    parse_edits,
)
from studyforge.corpus.manifest.errors import ManifestError
from studyforge.corpus.manifest.media import (
    COMMIT_MODES,
    DEFAULT_MEDIA,
    MediaPolicy,
    parse_media,
)

#: ⛔ The package's whole public surface. A consumer that has to import
#: `studyforge.corpus.manifest.document` directly is a consumer this contract
#: failed.
__all__ = [
    "COMMIT_MODES",
    "CORPUS_API",
    "DEFAULT_MEDIA",
    "EDIT_KINDS",
    "KNOWN_CORPUS_API",
    "MANIFEST_FILENAME",
    "MANIFEST_KEYS",
    "MIN_WHY_CHARS",
    "PLACEMENT_PROFILES",
    "REQUIRED_KEYS",
    "Classification",
    "ContentPolicy",
    "Exclusion",
    "Manifest",
    "ManifestError",
    "MediaPolicy",
    "NotMaterial",
    "PermittedEdit",
    "Reversal",
    "from_document",
    "load",
    "parse",
    "parse_content",
    "parse_edits",
    "parse_media",
]
