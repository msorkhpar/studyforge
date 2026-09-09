"""What a fixture corpus is made of: keys, block types, versions, and the R7 shapes.

**What it does.** States the fixtures' own contract as data — the archive
document's key order, the eleven block types and their fields, the count keys,
the API versions, and the registry of invalid corpora — so every check reads
one definition rather than restating it.

**How you use it.** `from tests.fixture_checks import vocabulary`, or take the
names re-exported from the package.

**Depends on.** `re` and `pathlib`. ⛔ Nothing else, and deliberately no
`studyforge` module: `src/studyforge/` was empty when these fixtures were
written, and a fixture check that needed the framework could not run until the
framework did. SF-06 owns the framework's canonicalisation; when it lands the
duplication is resolved in its favour.
"""

from __future__ import annotations

import re
from pathlib import Path

#: The fixture tree, found from this file rather than from the cwd.
FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"

#: The two corpora that must violate nothing. ⭐ `depth1` is not a reduced
#: `depth2` — it is the reading floor (spec §11.0) in its complete form.
VALID = ("depth1", "depth2")

#: The archive document's key order, which is also what reaches disk: an
#: unchanged document must re-render to identical bytes (R10), so the order is
#: fixed rather than sorted.
DOCUMENT_KEYS = (
    "raw_api",
    "source",
    "address",
    "variant",
    "unit",
    "kind",
    "ordinal",
    "ingested",
    "title",
    "blocks",
    "video",
    "assets",
    "attachments",
    "counts",
    "content_sha256",
)

#: Written only when they have something to say, and always **after** the
#: digest, so appending one cannot disturb it.
OPTIONAL_KEYS = ("assets_sha256", "starting_code", "media_skipped")

#: `count key -> block type`. Always all of them, including the zeroes: a
#: count that disappears when it is zero cannot be told from a count nobody
#: wrote, and noticing a short ingest is the whole reason they are recorded.
COUNT_KEYS = {
    "headings": "heading",
    "paras": "para",
    "code": "code",
    "tables": "table",
    "lists": "list",
    "images": "image",
    "videos": "video",
    "rules": "rule",
    "quotes": "quote",
    "html": "html",
    "disclosures": "disclosure",
}

#: `block type -> its keys, in order`. The six CodeSignal proved, SF-07's
#: additions (`rule`, `quote`, `html`), `video` — which the Markdown reader
#: never produces but the archive vocabulary carries — and `disclosure`.
BLOCK_FIELDS = {
    "heading": ("type", "level", "text"),
    "para": ("type", "text"),
    "code": ("type", "lang", "text"),
    "list": ("type", "ordered", "items"),
    "table": ("type", "headers", "rows"),
    "image": ("type", "src", "alt", "width"),
    "video": ("type", "src", "title"),
    "rule": ("type",),
    "quote": ("type", "blocks"),
    "html": ("type", "text"),
    "disclosure": ("type", "summary", "open", "blocks"),
}

#: Block types that hold other blocks. ⭐ Two now, one shape: a quote and a
#: disclosure both wrap arbitrary content, so every walker in this package
#: recurses on this tuple rather than naming `quote` and then forgetting the
#: next one. `disclosure` is *present but withheld* — the third state between
#: shown and absent, which is C5's lesson landing in the block vocabulary.
#: The archive records that it is disclosed on demand and what its label is;
#: that the markup is `<details><summary>` is SF-12's decision, not this
#: document's (R13).
CONTAINER_BLOCKS = ("quote", "disclosure")

#: Every block type each corpus is required to exercise. `depth1` carries no
#: video; every other type appears in both.
#:
#: ⚠️ `rule`, `quote`, `html` and `disclosure` are required at **M1**, not
#: deferred. The spec's C3 says 18 ISO files contain raw HTML; a recount with
#: code fences stripped found **0 of 38** — the matches were XML inside fenced
#: blocks. The real drivers are elsewhere and are no weaker: the disclosure is
#: a SPARQL requirement (6 of 19 lessons, every one of them hiding an exercise
#: answer), thematic breaks and blockquotes are the Java corpus's. SF-07 needs
#: all of them either way.
REQUIRED_TYPES = {
    "depth1": tuple(t for t in BLOCK_FIELDS if t != "video"),
    "depth2": tuple(BLOCK_FIELDS),
}

#: A `<tag>`-shaped run — what a parser scanning for raw HTML without tracking
#: fences would match. Both corpora are required to carry one INSIDE a code
#: block, so that such a parser fails here rather than against real material.
MARKUP_SHAPED = re.compile(r"</?[A-Za-z][A-Za-z0-9]*(\s[^<>]*)?/?>")

#: Directory name -> the single rule id that corpus is allowed to violate.
INVALID_CORPORA = {
    "bad-corpus-api": "corpus-api",
    "address-directory-mismatch": "address-directory",
    "digest-mismatch": "digest",
    "ordinal-gap": "ordinal-gap",
    "personal-data": "personal-data",
}

CORPUS_API = 1
CONTAINER_API = 1
RAW_API = 1

UNIT_DIR = re.compile(r"^unit-(\d{2})$")
ARCHIVE_FILE = re.compile(r"^(lesson|practice)-(\d+)\.json$")
