"""What a fixture corpus is made of: keys, block types, versions, and the R7 shapes.

**What it does.** States the fixtures' own contract as data — the archive
document's key order, the eleven block types and their fields, the count keys,
the API versions, and the registry of invalid corpora — so every check reads
one definition rather than restating it.

**How you use it.** `from tests.fixture_checks import vocabulary`, or take the
names re-exported from the package.

**Depends on.** `re`, `pathlib`, and — since SF-06 landed — the framework's
own vocabulary. ⭐ **The duplication is resolved in the framework's favour, as
this file said it would be.** `src/studyforge/` was empty when these fixtures
were written, so the contract was restated here on purpose and with a note
saying who would come to collect it. What is left below is what the *fixtures*
declare about themselves — which corpora are valid, what each must exercise,
and the file-naming shapes — never a second answer to what a block is.
"""

from __future__ import annotations

import re
from pathlib import Path

from studyforge.archive.blocks import (
    BLOCK_FIELDS,
    BLOCK_TYPES,
    CONTAINER_TYPES,
    COUNT_KEYS,
)
from studyforge.archive.document import DOCUMENT_KEYS, OPTIONAL_KEYS, RAW_API

#: ⭐ Declared because most of what this module offers is now **re-exported**
#: rather than defined: the block vocabulary and the document's key order are
#: the framework's, and this package hands them on so no check has to know
#: which of the two places it came from.
__all__ = [
    "ARCHIVE_FILE",
    "BLOCK_FIELDS",
    "BLOCK_TYPES",
    "CONTAINER_API",
    "CONTAINER_TYPES",
    "CORPUS_API",
    "COUNT_KEYS",
    "DOCUMENT_KEYS",
    "FIXTURES",
    "INVALID_CORPORA",
    "MARKUP_SHAPED",
    "OPTIONAL_KEYS",
    "RAW_API",
    "REQUIRED_TYPES",
    "UNIT_DIR",
    "VALID",
]

#: The fixture tree, found from this file rather than from the cwd.
FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"

#: The two corpora that must violate nothing. ⭐ `depth1` is not a reduced
#: `depth2` — it is the reading floor (spec §11.0) in its complete form.
VALID = ("depth1", "depth2")

#: ⛔ **Imported, never restated.** The archive document's key order, its
#: optional keys, the eleven block types with their fields, the count keys and
#: the container types are `studyforge.archive`'s — one definition, and a test
#: in `tests/studyforge/archive/test_blocks.py` fails if a second list appears.
#: ⚠️ `CONTAINER_TYPES` is the framework's spelling of what this package called
#: `CONTAINER_BLOCKS`; the published name won.
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
    "count-mismatch": "counts",
    "digest-mismatch": "digest",
    "ordinal-gap": "ordinal-gap",
    "personal-data": "personal-data",
    "user-authoritative": "exercise-trust",
}

#: ⚠️ Still declared here, and deliberately: `corpus_api` is SF-02's and
#: `container_api` is SF-11's, which has not landed. SF-06 collected what SF-06
#: owns. Routed as a finding rather than swept up in a diff about blocks.
CORPUS_API = 1
CONTAINER_API = 1

UNIT_DIR = re.compile(r"^unit-(\d{2})$")
ARCHIVE_FILE = re.compile(r"^(lesson|practice)-(\d+)\.json$")
