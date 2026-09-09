"""Digests and counts: what a document says about itself, recomputed.

**What it does.** Recomputes `content_sha256`, `assets_sha256` and the eleven
`counts` from the blocks and assets they claim to cover, and reports each
disagreement.

**How you use it.** `check_digests(document, where)` yields
`(rule_id, message)`.

**Depends on.** `vocabulary` and `corpus`.

⛔ **Nothing here is maintained by hand.** `tests/fixtures/invalid/digest-mismatch/`
exists to prove this check fires, so a helper that "repaired" a digest while
walking the tree would silently make that fixture valid — which has been
avoided once already, when the count keys grew.

⚠️ **Nested blocks are not counted.** A quote's or a disclosure's inner blocks
are the container's content, not the document's top level; SF-25 counts
top-level blocks and recurses separately if it wants the total.
"""

from __future__ import annotations

import hashlib

from tests.fixture_checks.corpus import sha256_of
from tests.fixture_checks.vocabulary import COUNT_KEYS


def check_digests(document, where):
    """Recompute every digest and count the document records for itself."""
    if document["content_sha256"] != sha256_of(document["blocks"]):
        yield "digest", f"{where} content_sha256 does not cover its blocks"
    if "assets_sha256" in document and document["assets_sha256"] != sha256_of(document["assets"]):
        yield "digest", f"{where} assets_sha256 does not cover its assets"
    counts = {
        key: sum(1 for block in document["blocks"] if block.get("type") == kind)
        for key, kind in COUNT_KEYS.items()
    }
    if document["counts"] != counts:
        yield "counts", f"{where} counts disagree with its blocks"


def sha256_of_bytes(data):
    """The digest of raw bytes — what a media file's recorded `sha256` covers."""
    return hashlib.sha256(data).hexdigest()
