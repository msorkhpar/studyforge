"""Shape: the manifest's required fields, a document's key order, a block's keys.

**What it does.** The checks that are about *form* rather than about agreement
between two places — is this manifest complete, is this document in canonical
key order and canonical bytes, is every block a type the vocabulary names with
exactly the fields it names.

**How you use it.** Each function yields `(rule_id, message)` and nothing else.
An empty generator means the input is clean.

**Depends on.** `vocabulary` and `corpus`.

⛔ **Key order is a rule, not a preference.** An unchanged document must
re-render to identical bytes (R10), and a `sort_keys=True` anywhere would make
that true by accident for as long as nobody added a key.
"""

from __future__ import annotations

from studyforge.validate import blocks as block_shapes
from tests.fixture_checks.corpus import rendered
from tests.fixture_checks.vocabulary import (
    CORPUS_APIS,
    DOCUMENT_KEYS,
    OPTIONAL_KEYS,
    RAW_API,
)


def check_manifest(manifest):
    """`corpus.json`: the version it declares and the fields it must carry."""
    if manifest.get("corpus_api") not in CORPUS_APIS:
        yield "corpus-api", f"corpus.json declares corpus_api {manifest.get('corpus_api')!r}"
    for key in ("source", "title", "levels", "variants", "placement"):
        if not manifest.get(key):
            yield "manifest-field", f"corpus.json has no {key!r}"
    if not isinstance(manifest.get("permitted_edits", []), list):
        yield "manifest-field", "corpus.json 'permitted_edits' is not a list"


def check_document_shape(path, document, where):
    """One archive document: its key order, its version, and its bytes."""
    keys = tuple(document)
    if keys[: len(DOCUMENT_KEYS)] != DOCUMENT_KEYS:
        yield "key-order", f"{where} key order is {list(keys)}"
        return
    tail = keys[len(DOCUMENT_KEYS) :]
    if list(tail) != [k for k in OPTIONAL_KEYS if k in tail]:
        yield "key-order", f"{where} optional keys out of order: {list(tail)}"
    if document["raw_api"] != RAW_API:
        yield "raw-api", f"{where} declares raw_api {document['raw_api']!r}"
    if path.read_text(encoding="utf-8") != rendered(document):
        yield "canonical-bytes", f"{where} is not its own canonical rendering"


def check_blocks(document, where):
    """Every block is a named type with its fields, then only the optional keys it names.

    ⛔ **`W282`: read by `validate`'s own reader** (`validate.blocks.block_problems`), called
    through its module, so the fixture check and `validate` decide a block's type, its keys,
    a list's items and `start`, at every depth, through ONE function (`W263`).
    """
    for at, what in block_shapes.block_problems(document["blocks"]):
        yield "vocabulary", f"{where} {at} {what}"
