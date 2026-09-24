"""Mirror of `src/studyforge/skills/exercises/merge.py` (R12) — a pass keeps what it did not read.

**What it asserts.** The ledger's keep rule, first and third clauses, at the merge itself: a
committed row for a file the pass did not read is kept as it was, whatever the
pass carried; a row leaves only when its file is gone; a fence a re-read page
no longer carries is `changed`, never `dropped`; and a committed ledger this
build cannot read is refused rather than overwritten.

⭐ The documents here are what `accounting.ledger_document` writes, taken over
real files by `ledger.take` — never rows typed to look like one.
"""

from __future__ import annotations

import json

import pytest

from studyforge.skills.exercises import (
    LedgerError,
    account,
    json_bytes,
    ledger_document,
    ledger_rows,
    merged,
    take,
)

PAGES = {
    "one.md": "# One\n\n```python\nprint(1)\n```\n\n```python\nprint(11)\n```\n",
    "two.md": "# Two\n\n```python\nprint(2)\n```\n",
}


def _document(root, *paths):
    """The ledger a pass over `paths` accounts for, every entry excused."""
    ledger = take(root, sources=paths, tests=(), where="the ledger")
    reasons = {f"example:{e.path}:{e.ordinal}": "an aside" for e in ledger.entries}
    return ledger_document(ledger, account(ledger, {}, reasons, "the ledger"))


def _write(root, pages=PAGES):
    for path, text in pages.items():
        (root / path).write_text(text, encoding="utf-8")


def _rows_of(document, path):
    return [row for row in document["entries"] if row["path"] == path]


def test_a_row_for_a_file_the_pass_did_not_read_is_kept_byte_identical(tmp_path):
    _write(tmp_path)
    prior, _ = merged(tmp_path, None, _document(tmp_path, "one.md"), "the ledger")
    before = [json_bytes(row) for row in _rows_of(prior, "one.md")]
    document, delta = merged(tmp_path, prior, _document(tmp_path, "two.md"), "the ledger")
    assert [json_bytes(row) for row in _rows_of(document, "one.md")] == before
    assert delta.kept == ("example:one.md:1", "example:one.md:2", "source:one.md")
    assert delta.added == ("example:two.md:1", "source:two.md")
    assert delta.changed == () and delta.dropped == ()


def test_the_order_of_the_passes_does_not_change_a_byte(tmp_path):
    _write(tmp_path)
    one, two = _document(tmp_path, "one.md"), _document(tmp_path, "two.md")
    forward, _ = merged(tmp_path, merged(tmp_path, None, one, "l")[0], two, "l")
    backward, _ = merged(tmp_path, merged(tmp_path, None, two, "l")[0], one, "l")
    whole, _ = merged(tmp_path, None, _document(tmp_path, "one.md", "two.md"), "l")
    assert json_bytes(forward) == json_bytes(backward) == json_bytes(whole)


def test_a_row_is_dropped_only_when_its_file_is_gone(tmp_path):
    _write(tmp_path)
    prior, _ = merged(tmp_path, None, _document(tmp_path, "one.md", "two.md"), "l")
    (tmp_path / "one.md").unlink()
    assert not (tmp_path / "one.md").exists()
    document, delta = merged(tmp_path, prior, _document(tmp_path, "two.md"), "l")
    assert delta.dropped == ("example:one.md:1", "example:one.md:2", "source:one.md")
    assert _rows_of(document, "one.md") == []
    assert delta.kept == ("example:two.md:1", "source:two.md")


def test_a_fence_a_re_read_page_no_longer_carries_is_changed_and_not_dropped(tmp_path):
    _write(tmp_path)
    prior, _ = merged(tmp_path, None, _document(tmp_path, "one.md"), "l")
    _write(tmp_path, {"one.md": "# One\n\n```python\nprint(1)\n```\n"})
    _, delta = merged(tmp_path, prior, _document(tmp_path, "one.md"), "l")
    assert delta.dropped == (), "a page that is still there had a row dropped"
    assert delta.changed == ("example:one.md:2", "source:one.md")
    assert delta.kept == ("example:one.md:1",)


@pytest.mark.parametrize(
    ("prior", "says"),
    [
        ({"ledger_api": 2, "sources": [], "entries": []}, "ledger_api 2"),
        # ⛔ Both equal 1, and neither is a version: only `version.check` refuses them.
        ({"ledger_api": True, "sources": [], "entries": []}, "ledger_api as a bool"),
        ({"ledger_api": 1.0, "sources": [], "entries": []}, "ledger_api"),
        ({"ledger_api": 1, "sources": {}, "entries": []}, "'sources'"),
        ({"ledger_api": 1, "sources": [{"path": "../outside.md"}], "entries": []}, "'sources'"),
        ({"ledger_api": 1, "sources": [], "entries": [{"path": "a.md", "kind": "x"}]}, "'entries'"),
        (["not", "an", "object"], "not an object"),
    ],
)
def test_a_committed_ledger_this_build_cannot_read_is_refused_not_overwritten(
    tmp_path, prior, says
):
    _write(tmp_path)
    with pytest.raises(LedgerError, match=says):
        merged(tmp_path, prior, _document(tmp_path, "two.md"), "the ledger")


def test_ledger_rows_reads_what_the_merge_wrote(tmp_path):
    _write(tmp_path)
    document, _ = merged(tmp_path, None, _document(tmp_path, "one.md"), "l")
    decoded = json.loads(json_bytes(document))
    assert ledger_rows(decoded, "l") == {
        "sources": decoded["sources"],
        "entries": decoded["entries"],
    }
