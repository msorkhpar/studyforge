"""Mirror of `skills/exercises/staging.py` (R12): the helpers every gated draft shares."""

from __future__ import annotations

import json

from studyforge.exercise import Origin
from studyforge.skills.exercises.staging import cited, json_bytes, lay_down
from studyforge.skills.exercises.ledger import Ledger


def test_a_document_is_written_indented_and_newline_ended_and_reads_back():
    data = json_bytes({"b": 1, "a": ["é"]})
    assert data.endswith(b"\n") and b"\n  " in data and "é".encode() in data
    assert json.loads(data) == {"b": 1, "a": ["é"]}


def test_files_are_laid_under_the_root_and_nowhere_else(tmp_path):
    lay_down(tmp_path / "stage", {"a/b/c.txt": b"x", "d.txt": b"y"})
    assert (tmp_path / "stage" / "a" / "b" / "c.txt").read_bytes() == b"x"
    assert sorted(p.name for p in tmp_path.rglob("*") if p.is_file()) == ["c.txt", "d.txt"]


def test_an_origin_the_ledger_never_read_is_cited_by_nothing():
    empty = Ledger(sources=(), entries=())
    assert cited((("role", Origin("notes/none.md", "A section")),), empty) == ()
