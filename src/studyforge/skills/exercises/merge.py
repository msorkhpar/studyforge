r"""One pass's ledger merged into the committed one: what it did not re-read is KEPT.

**What it does.** Takes the ledger document a pass just accounted for — which
covers only the files that pass read — and the ledger already committed, and
returns the document to commit and a `Delta` naming, row by row, what was
kept, added, changed and dropped.

**How you use it.**

    document, delta = merged(root, prior, fresh, "the ledger")
    delta.kept, delta.added, delta.changed, delta.dropped   # row keys, sorted

`prior` is the committed document (or `None`), `fresh` is
`accounting.ledger_document` over the files this pass read.

**Depends on.** `accounting` for the document's version, `ledger` for the two
entry kinds and its refusal, `studyforge.sourcepath` for what a committed
row's path may be, and `studyforge.describe` for R7. Standard library only.

## ⛔ ONE FILE FOR THE WHOLE CORPUS, SO A PASS OVER PART OF IT MUST NOT OWN ALL OF IT

⚠️ `exercises/ledger.json` is one file per corpus, so a pass over one container
must not write it with that container's entries alone. ⭐ **A pass OWNS
exactly the files it read** — its material and its graders — and nothing else:
every committed row for a file outside that set is carried over as the dict it
was decoded into, so it re-encodes to the same bytes whatever order the passes
ran in.

## ⛔ A ROW LEAVES ONLY WHEN ITS FILE IS GONE

⭐ **`dropped` is exactly the rows whose file the corpus no longer carries.** A
row for a file this pass did not read and that is still on disk is `kept`,
never dropped. ⚠️ A file this pass DID read owns its rows outright: a fence it
no longer carries is reported under `changed` — the page changed; it is not
gone — so a reader of the delta never sees a page's example leave under the
word reserved for a page that left.

## ⭐ A ROW'S KEY IS `ledger.key_of`'s SPELLING, AND A FILE'S IS `source:<path>`

⛔ **One spelling of an entry's identity**: `row_key` reads a decoded row the
way `key_of` reads an `Entry`, so a reason, a delta and a `validate` finding
name one entry one way. A file row carries no fence, so a prose page with no
example still shows in the delta.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from studyforge.skills.exercises.accounting import LEDGER_API
from studyforge.skills.exercises.ledger import EXAMPLE, TESTS, LedgerError
from studyforge.sourcepath import source_path_fault
from studyforge.version import check as check_version

#: The key a file row is reported under. ⛔ Not an entry kind: a file is what
#: the ledger READ, and an entry is what that file carries.
SOURCE = "source"


@dataclass(frozen=True, slots=True)
class Delta:
    """What one pass did to the committed ledger, row key by row key, each tuple sorted."""

    kept: tuple[str, ...] = ()
    added: tuple[str, ...] = ()
    changed: tuple[str, ...] = ()
    dropped: tuple[str, ...] = ()


def row_key(row: dict) -> str:
    """Return a decoded entry row's key — ⭐ `ledger.key_of`'s spelling, read off a dict."""
    if row.get("kind") == TESTS:
        return f"{TESTS}:{row.get('path')}"
    return f"{EXAMPLE}:{row.get('path')}:{row.get('ordinal')}"


def source_key(row: dict) -> str:
    """Return a decoded file row's key."""
    return f"{SOURCE}:{row.get('path')}"


def merged(root: Path, prior: dict | None, fresh: dict, where: str) -> tuple[dict, Delta]:
    """Merge a pass's ledger into the committed one, keeping every row it did not re-read.

    ⛔ **The files this pass read are `fresh`'s sources, and only those are
    replaced.** A committed row for any other file is kept verbatim while the
    file is on disk and dropped only when it is not.
    """
    read = {row["path"] for row in fresh["sources"]}
    before = ledger_rows(prior, where)
    sources = [row for row in before["sources"] if _carried(root, row, read)]
    entries = [row for row in before["entries"] if _carried(root, row, read)]
    document = {
        "ledger_api": LEDGER_API,
        "sources": sorted([*sources, *fresh["sources"]], key=lambda row: row["path"]),
        "entries": sorted([*entries, *fresh["entries"]], key=_order),
    }
    return document, _delta(root, before, document)


def _carried(root: Path, row: dict, read: set[str]) -> bool:
    """Is this committed row one the pass keeps? ⛔ Not re-read, and its file still there."""
    return row["path"] not in read and (root / row["path"]).is_file()


def _order(row: dict) -> tuple[str, int, str]:
    """`ledger._order`, read off a decoded row: by file, by position, the test entry first."""
    return (row["path"], row["ordinal"], row["kind"])


def _keyed(document: dict) -> dict[str, dict]:
    """Every row of a document by its key, file rows and entry rows alike."""
    keyed = {source_key(row): row for row in document["sources"]}
    keyed.update({row_key(row): row for row in document["entries"]})
    return keyed


def _delta(root: Path, before: dict, after: dict) -> Delta:
    """Name what happened to every row: ⛔ `dropped` only where the file is gone."""
    old, new = _keyed(before), _keyed(after)
    gone = sorted(key for key in old if key not in new)
    dropped = tuple(key for key in gone if not (root / old[key]["path"]).is_file())
    # ⭐ A row that left while its file is still there is one this pass re-read:
    # `_carried` keeps every other such row, so the file changed and is not gone.
    vanished = tuple(key for key in gone if key not in dropped)
    return Delta(
        kept=tuple(sorted(key for key in new if old.get(key) == new[key])),
        added=tuple(sorted(key for key in new if key not in old)),
        changed=tuple(sorted([*(k for k in new if k in old and old[k] != new[k]), *vanished])),
        dropped=dropped,
    )


def ledger_rows(prior: object, where: str) -> dict:
    """Return the committed document's two row lists, refusing one this build cannot read.

    ⭐ **The one reader of a committed ledger**: the merge keeps rows through
    it and `validate.ledger` checks them through it, so the two cannot disagree
    about which ledger is readable.
    """
    if prior is None:
        return {"sources": [], "entries": []}
    if not isinstance(prior, dict):
        raise LedgerError(f"{where}: the committed ledger is not an object. Nothing was written.")
    try:
        check_version(
            "ledger_api",
            prior.get("ledger_api"),
            (LEDGER_API,),
            where=f"{where}: the committed ledger",
            error=LedgerError,
        )
    except LedgerError as refused:
        raise LedgerError(
            f"{refused} It cannot say which of its rows to keep, so nothing was written."
        ) from None
    rows = {}
    for field in ("sources", "entries"):
        value = prior.get(field)
        if not isinstance(value, list) or not all(_row_ok(row, field) for row in value):
            raise LedgerError(
                f"{where}: the committed ledger's '{field}' is not a list of rows this "
                f"build wrote, so it cannot say which of them to keep. Nothing was written."
            )
        rows[field] = value
    return rows


def _row_ok(row: object, field: str) -> bool:
    """Is this a row the merge can key and order? ⛔ A source path; an entry's kind, ordinal.

    ⛔ **The path is checked before anything is opened with it**: a committed
    row is a document somebody could have edited, and a path that escapes the
    root would make `is_file` a question about the machine.
    """
    if not isinstance(row, dict) or not isinstance(row.get("path"), str):
        return False
    if source_path_fault(row["path"]) is not None:
        return False
    if field == "sources":
        return True
    return row.get("kind") in (EXAMPLE, TESTS) and isinstance(row.get("ordinal"), int)
