"""The staging helpers every gated draft shares: bytes, citations and a staging root.

**What it does.** Encodes a document the one way this skill writes one, cites what each origin's
file digested to, encodes a gate record as it ships, and lays files under a staging root.
⛔ Nothing here writes into the corpus, and nothing here runs a gate: `gating` and `deckgating`
call it.
"""

from __future__ import annotations

import json
from pathlib import Path

from studyforge.exercise import Origin
from studyforge.exercise.gates import Cited, GateRecord, record_document, record_of
from studyforge.skills.exercises.ledger import Ledger


def json_bytes(document: object) -> bytes:
    """Encode a document the one way this skill writes one: indented, newline-ended (R10)."""
    return (json.dumps(document, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def cited(named: tuple[tuple[str, Origin], ...], ledger: Ledger) -> tuple[Cited, ...]:
    """Cite what each origin's file digested to when the ledger read it — ⛔ never `digests()`.

    ⚠️ **Read off the `Source` rows, deliberately not off the gate-facing
    mapping**, so the one thing the gates are handed is the one thing they are
    tested against. An origin the ledger never read is cited by nothing, and
    `G5`/`Q5` refuse it as a verdict.
    """
    read = {source.path: source.digest for source in ledger.sources}
    return tuple(
        Cited(role=role, path=origin.path, section=origin.section, digest=read[origin.path])
        for role, origin in named
        if origin.path in read
    )


def record_bytes(record: GateRecord, where: str) -> bytes:
    """Encode the gate record as it ships, re-read through `record_of` before it is believed."""
    written = record_document(record)
    record_of(written, where)
    return json_bytes(written)


def lay_down(root: Path, files: dict[str, bytes]) -> None:
    """Write every file under a staging root — ⛔ never the corpus."""
    for path, data in files.items():
        target = root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
