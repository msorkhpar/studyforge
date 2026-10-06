"""Mirror of `src/studyforge/serve/versions.py` (R12): verdicts held against a file's version."""

from __future__ import annotations

import json
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import pytest

from studyforge.serve import versions
from studyforge.serve.versions import (
    MISSING,
    SETTLE_NS,
    UNHELD,
    Judged,
    Moved,
    Versions,
    build_digest,
    settled,
    version_of,
)

DIGEST = "ab" * 32


@pytest.fixture
def settle_now(monkeypatch):
    """Treat every file as settled, so a verdict is held the moment it is reached."""
    monkeypatch.setattr(versions, "SETTLE_NS", -(10**30))


def test_a_version_moves_with_the_file(tmp_path):
    path = tmp_path / "one.js"
    path.write_bytes(b"one")
    first = version_of(path.stat())
    path.write_bytes(b"three")
    assert version_of(path.stat()) != first


def test_a_file_is_settled_only_once_it_has_stood_for_the_window(tmp_path):
    path = tmp_path / "one.js"
    path.write_bytes(b"one")
    stat = path.stat()
    moved = max(stat.st_mtime_ns, stat.st_ctime_ns)
    assert not settled(stat, now=moved)
    assert settled(stat, now=moved + SETTLE_NS + 1)


def test_a_held_value_answers_only_its_own_version():
    memo = Versions()
    memo.put("/a", "gate", (1, 2, 3, 4, 5), (None, True))
    assert memo.get("/a", "gate", (1, 2, 3, 4, 5)) == (None, True)
    assert memo.get("/a", "gate", (1, 2, 3, 4, 6)) is MISSING
    assert memo.get("/a", "gzip", (1, 2, 3, 4, 5)) is MISSING


def test_the_memo_evicts_the_least_recently_used_by_count_and_by_bytes():
    memo = Versions(entries=2, budget=10)
    for name in ("a", "b", "c"):
        memo.put(name, "gate", (0,) * 5, (None, True))
    assert memo.get("a", "gate", (0,) * 5) is MISSING
    memo.put("big", "gzip", (0,) * 5, (None, b"x" * 8))
    memo.put("more", "gzip", (0,) * 5, (None, b"y" * 8))
    assert memo.get("big", "gzip", (0,) * 5) is MISSING
    assert memo.get("more", "gzip", (0,) * 5) == (None, b"y" * 8)


def test_the_default_memo_holds_nothing():
    UNHELD.put("/a", "gate", (0,) * 5, (None, True))
    assert UNHELD.get("/a", "gate", (0,) * 5) is MISSING


def test_a_settled_verdict_is_reached_once_per_version(tmp_path, settle_now):
    path = tmp_path / "index.js"
    path.write_bytes(b"clean")
    memo, calls = Versions(), []

    def judge(judged):
        calls.append(judged.bytes())
        return True

    for _ in range(3):
        judged = Judged(path, path.stat(), memo)
        assert judged.verdict("gate", lambda judged=judged: judge(judged))
    assert calls == [b"clean"]
    path.write_bytes(b"moved, and longer")
    judged = Judged(path, path.stat(), memo)
    judged.verdict("gate", lambda: judge(judged))
    assert calls == [b"clean", b"moved, and longer"]


def test_a_burst_of_requests_reaches_one_verdict_once(tmp_path, settle_now):
    path = tmp_path / "index.js"
    path.write_bytes(b"large")
    memo, calls, lock = Versions(), [], threading.Lock()

    def judge():
        with lock:
            calls.append(1)
        time.sleep(0.05)
        return True

    def ask(_):
        return Judged(path, path.stat(), memo).verdict("gate", judge)

    with ThreadPoolExecutor(8) as pool:
        assert all(pool.map(ask, range(8)))
    assert calls == [1]


def test_a_file_written_within_the_window_is_judged_every_time(tmp_path):
    path = tmp_path / "index.js"
    path.write_bytes(b"fresh")
    memo, calls = Versions(), []
    for _ in range(2):
        Judged(path, path.stat(), memo).verdict("gate", lambda: calls.append(1) or True)
    assert calls == [1, 1]


def test_a_verdict_reached_against_other_marks_is_judged_again(tmp_path, settle_now):
    path = tmp_path / "index.js"
    path.write_bytes(b"text")
    memo = Versions()
    judged = Judged(path, path.stat(), memo)
    assert judged.verdict("withheld", lambda: False, against="old") is False
    assert judged.verdict("withheld", lambda: True, against="old") is False
    assert judged.verdict("withheld", lambda: True, against="new") is True


def test_bytes_of_another_version_are_refused_as_moved(tmp_path):
    path = tmp_path / "index.js"
    path.write_bytes(b"before")
    judged = Judged(path, path.stat())
    path.write_bytes(b"after, longer")
    with pytest.raises(Moved):
        judged.bytes()
    assert not judged.read
    fresh = Judged(path, path.stat())
    assert fresh.bytes() == b"after, longer" and fresh.read


def a_record(directory, digest=DIGEST):
    record = directory / ".studyforge" / "site.json"
    record.parent.mkdir(parents=True, exist_ok=True)
    record.write_text(json.dumps({"site_api": 1, "scan_sha256": digest}), encoding="utf-8")


def test_the_build_digest_is_the_nearest_record_within_the_root(tmp_path):
    corpus = tmp_path / "root" / "course"
    asset = corpus / ".studyforge" / "assets" / "page.css"
    asset.parent.mkdir(parents=True)
    asset.write_text("a{}", encoding="utf-8")
    root = (tmp_path / "root").resolve()
    assert build_digest(root, asset.resolve()) is None
    a_record(corpus)
    assert build_digest(root, asset.resolve()) == DIGEST
    a_record(tmp_path, "cd" * 32)
    os.remove(corpus / ".studyforge" / "site.json")
    assert build_digest(root, asset.resolve()) is None


@pytest.mark.parametrize("digest", ['"quoted"', "a b", 7, None, "x" * 129])
def test_a_digest_that_is_not_plain_hex_is_not_folded_in(tmp_path, digest):
    a_record(tmp_path, digest)
    page = tmp_path / "index.html"
    page.write_text("<p>", encoding="utf-8")
    assert build_digest(tmp_path.resolve(), page.resolve()) is None
