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
from studyforge.corpus.container.document import KNOWN_CONTAINER_API

#: ⭐ Declared because most of what this module offers is now **re-exported**
#: rather than defined: the block vocabulary and the document's key order are
#: the framework's, and this package hands them on so no check has to know
#: which of the two places it came from.
__all__ = [
    "ARCHIVE_FILE",
    "BLOCK_FIELDS",
    "BLOCK_TYPES",
    "CONTAINER_APIS",
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

#: The corpora that must violate nothing. ⭐ `depth1` is not a reduced
#: `depth2` — it is the reading floor (spec §11.0) in its complete form.
#:
#: ⭐ **`shared-origin` is the third, and it is here for one property the other
#: two cannot carry: two units declaring the same `origin.path`** (`W95`, and
#: `Q23`'s answer in `docs/tasks/E04-narration.md`). ⛔ It is **not** a coverage
#: corpus — see `REQUIRED_TYPES` — and the README says what it is for. ⚠️ It is
#: also the set's only `container_api: 2` map, which is why the version check
#: below reads a set: a whole-file `origin` and a region `origin` are two code
#: paths and each needs an input, exactly as SF-10's two overlay shapes do.
VALID = ("depth1", "depth2", "shared-origin")

#: ⛔ **Imported, never restated.** The archive document's key order, its
#: optional keys, the eleven block types with their fields, the count keys and
#: the container types are `studyforge.archive`'s — one definition, and a test
#: in `tests/studyforge/archive/test_blocks.py` fails if a second list appears.
#: ⚠️ `CONTAINER_TYPES` is the framework's spelling of what this package called
#: `CONTAINER_BLOCKS`; the published name won.
#: Every block type each corpus is required to exercise. `depth1` carries no
#: video; every other type appears in both of the two coverage corpora.
#:
#: ⚠️ `rule`, `quote`, `html` and `disclosure` are required at **M1**, not
#: deferred. The spec's C3 says 18 ISO files contain raw HTML; a recount with
#: code fences stripped found **0 of 38** — the matches were XML inside fenced
#: blocks. The real drivers are elsewhere and are no weaker: the disclosure is
#: a SPARQL requirement (6 of 19 lessons, every one of them hiding an exercise
#: answer), thematic breaks and blockquotes are the Java corpus's. SF-07 needs
#: all of them either way.
#:
#: ⛔ **`shared-origin` is required to exercise three types and no more, and
#: that is a decision rather than a gap.** It exists for one property — two
#: units on one `origin.path` — and a corpus that also had to carry eleven
#: block types would be a second coverage corpus maintained for a reason that
#: is not its own. ⚠️ `code` is not optional among the three: the
#: fenced-markup check below is parametrized over `VALID`.
REQUIRED_TYPES = {
    "depth1": tuple(t for t in BLOCK_FIELDS if t != "video"),
    "depth2": tuple(BLOCK_FIELDS),
    "shared-origin": ("heading", "para", "code"),
}

#: A `<tag>`-shaped run — what a parser scanning for raw HTML without tracking
#: fences would match. Every valid corpus is required to carry one INSIDE a code
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
#: SF-06 collected what SF-06 owns. Routed as a finding rather than swept up in
#: a diff about blocks. ⚠️ It is the version **these fixtures** declare, which
#: is not the version the framework writes today — `studyforge`'s `CORPUS_API`
#: is 2 — and that gap is a finding rather than this file's to close.
CORPUS_API = 1

#: ⛔ **The container-map versions a fixture may declare — a set, imported.**
#: It was `CONTAINER_API = 1` while the framework's own constant moved to 2, so
#: a fixture that used Ruling 92's region `origin` was refused by this checker
#: for declaring the version that shape requires. ⭐ The set is the framework's
#: (`KNOWN_CONTAINER_API`), read rather than restated: the fixtures deliberately
#: carry **both** versions now, so the question this check asks is *is this a
#: version this build reads*, not *is this the newest one*.
#: ⚠️ Which fixture is at which version is pinned by
#: `tests/test_fixture_shared_origin.py`, so a silent downgrade reds there.
CONTAINER_APIS = KNOWN_CONTAINER_API

UNIT_DIR = re.compile(r"^unit-(\d{2})$")
ARCHIVE_FILE = re.compile(r"^(lesson|practice)-(\d+)\.json$")
