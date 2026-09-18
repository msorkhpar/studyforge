"""Media: every declared local file is on disk, at the size and digest recorded.

**What it does.** Walks a document's `assets` and `attachments` and checks each
entry against the file it names.

**How you use it.** `check_media(container_dir, document, where)` yields
`(rule_id, message)`.

**Depends on.** `digests` for the byte digest, and `addresses` for the one
question this module asks about geography: where a unit's own files sit.

⚠️ **`W214` first, then `W322`.** This module composed the directory from a
literal and a format string, which made it a second spelling of the one
`skills.adapter.Layout.unit_files` computes — and a fixture check that agreed
with itself about where media lives is the reading `validate` could not
contradict. `W214` replaced the literal with the two constants that own the
segments. ⛔ **It was still a join, and a join is a producer**: two of them
agree only for as long as nobody changes one. ⭐ `addresses.unit_files_in`
asks the layout for the shape, and this module asks `addresses` — so the
directory has one producer and this file is not it.
⭐ `studyforge validate` now asks the same question of any corpus
(`media-missing`); this half stays because these fixtures are checked without
it.

⭐ **`media_skipped` is a third state, not a missing one.** The marker exists
precisely so a capture that named its media and never fetched it can be told
from one whose unit simply had none — the same distinction C5 taught this
project about exercises, and the reason this check returns rather than
reporting.
"""

from __future__ import annotations

from tests.fixture_checks.addresses import unit_files_in
from tests.fixture_checks.digests import sha256_of_bytes


def check_media(container_dir, document, where):
    """Every declared local file is on disk with the digest recorded for it."""
    if document.get("media_skipped"):
        return
    unit_root = unit_files_in(container_dir, document["unit"])
    for entry in list(document["assets"]) + list(document["attachments"]):
        local = entry.get("local") or ""
        if not local:
            yield "media-present", f"{where} declares an entry naming no file"
            continue
        target = unit_root / local
        if not target.is_file():
            yield "media-present", f"{where} declares {local} and it is not on disk"
            continue
        data = target.read_bytes()
        if entry.get("sha256") != sha256_of_bytes(data):
            yield "digest", f"{where} recorded a sha256 that {local} does not match"
        if entry.get("bytes") != len(data):
            yield "digest", f"{where} recorded a byte count {local} does not match"
