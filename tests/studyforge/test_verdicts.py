"""Mirror of `src/studyforge/verdicts.py` (R12)."""

from __future__ import annotations

import os

import pytest

from studyforge.verdicts import (
    MAX_FILE_BYTES,
    REFUSED,
    Store,
    VerdictError,
    main,
    pending,
    preflight,
)


def test_only_the_verdict_and_small_result_files_are_kept(tmp_path):
    store = Store(tmp_path / "v")
    entry = store.record(
        "unit-a",
        "d1",
        "pass",
        {
            "report.json": "{}",
            "build/classes/Main.class": "x",
            "huge.txt": "x" * (MAX_FILE_BYTES + 1),
            "app.bin": "x",
        },
    )
    assert set(entry.files) == {"report.json"}
    assert set(store.lookup("unit-a", "d1").files) == {"report.json"}


def test_a_changed_digest_is_never_answered_from_an_older_verdict(tmp_path):
    store = Store(tmp_path)
    store.record("unit-a", "d1", "pass")
    assert store.lookup("unit-a", "d1").verdict == "pass"
    assert store.lookup("unit-a", "d2") is None


def test_a_rerun_resumes_from_recorded_verdicts(tmp_path):
    store = Store(tmp_path)
    digests = {"a": "1", "b": "2", "c": "3"}
    assert pending(store, digests) == ["a", "b", "c"]
    store.record("a", "1", "pass")
    store.record("b", "old", "fail")
    assert pending(store, digests) == ["b", "c"]


def test_the_size_report_counts_entries_and_bytes_largest_first(tmp_path):
    store = Store(tmp_path)
    store.record("small", "d", "pass")
    store.record("big", "d", "pass", {"r.txt": "x" * 5000})
    report = store.report()
    assert report.entries == 2
    assert report.largest[0][0] == "big"
    assert report.total_bytes == sum(size for _, size in report.largest)
    assert report.lines()[0].startswith("verdict store: 2 entries")


def test_compact_drops_files_a_judgement_does_not_read(tmp_path):
    store = Store(tmp_path)
    store.record("a", "d", "pass", {"r.json": "{}"})
    path = tmp_path / "a.verdict.json"
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace('"r.json": "{}"', '"r.json": "{}", "t/x.class": "z"'), encoding="utf-8")
    assert store.compact() == 1
    assert set(store.lookup("a", "d").files) == {"r.json"}
    assert store.compact() == 0


def test_prune_drops_unknown_units_then_the_oldest_to_a_cap(tmp_path):
    store = Store(tmp_path)
    for index, key in enumerate(("old", "mid", "new", "gone")):
        store.record(key, "d", "pass", {"r.txt": "x" * 1000})
        os.utime(tmp_path / f"{key}.verdict.json", (index, index))
    assert store.prune(keep=["old", "mid", "new"]) == ["gone"]
    size = (tmp_path / "new.verdict.json").stat().st_size
    assert store.prune(max_bytes=size + 1) == ["old", "mid"]
    assert [e.key for e in store.entries()] == ["new"]


def test_preflight_refuses_below_the_floor_and_passes_above(tmp_path):
    assert preflight(tmp_path / "not-yet", 1) > 0
    with pytest.raises(VerdictError, match="floor"):
        preflight(tmp_path, 1 << 62)
    assert main(["preflight", "--dir", str(tmp_path), "--floor-mb", str(1 << 40)]) == REFUSED
    assert main(["preflight", "--dir", str(tmp_path), "--floor-mb", "0"]) == 0


def test_a_key_with_a_separator_or_an_unknown_verdict_is_refused(tmp_path):
    store = Store(tmp_path)
    with pytest.raises(VerdictError):
        store.record("a/b", "d", "pass")
    with pytest.raises(VerdictError):
        store.record("a", "d", "maybe")


def test_the_command_line_reports_compacts_and_prunes(tmp_path, capsys):
    Store(tmp_path).record("a", "d", "pass")
    assert main(["report", "--dir", str(tmp_path)]) == 0
    assert "1 entries" in capsys.readouterr().out
    assert main(["compact", "--dir", str(tmp_path)]) == 0
    keep = tmp_path / "keep.lst"
    keep.write_text("other\n", encoding="utf-8")
    assert main(["prune", "--dir", str(tmp_path), "--keep-file", str(keep)]) == 0
    assert "pruned 1" in capsys.readouterr().out
