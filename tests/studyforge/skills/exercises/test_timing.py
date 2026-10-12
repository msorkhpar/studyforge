"""Mirror of `src/studyforge/skills/exercises/timing.py` (R12)."""

from __future__ import annotations

import pytest

from studyforge.skills.exercises.timing import FLOOR_MS, main, scan_text, scan_tree


@pytest.mark.parametrize(
    ("name", "line", "ms"),
    [
        ("A.java", "Thread.sleep(200);", 200),
        ("A.java", "latch.await(500, TimeUnit.MILLISECONDS);", 500),
        ("A.java", "assertTrue(done.await(1, TimeUnit.MICROSECONDS));", 0.001),
        ("A.java", "Duration.ofMillis(50)", 50),
        ("A.kt", "delay(100)", 100),
        ("A.kt", "withTimeout(250) { }", 250),
        ("A.kt", "val t = 300.milliseconds", 300),
        ("a.py", "time.sleep(0.5)", 500),
        ("a.py", "asyncio.sleep(0.01)", 10),
        ("a.js", "setTimeout(() => done(), 20)", 20),
        ("a.ts", "await sleep(100)", 100),
        ("a.js", "{ timeout: 300 }", 300),
    ],
)
def test_a_wait_below_a_second_is_flagged(name, line, ms):
    found = scan_text(line, name)
    assert [one.wait_ms for one in found] == [pytest.approx(ms)]


@pytest.mark.parametrize(
    ("name", "line"),
    [
        ("A.java", "Thread.sleep(1000);"),
        ("A.java", "latch.await(30, TimeUnit.SECONDS);"),
        ("A.java", "Thread.sleep(0);"),
        ("A.kt", "withTimeout(5000) { }"),
        ("a.py", "time.sleep(2)"),
        ("a.py", "time.sleep(1)"),
        ("a.js", "setTimeout(done, 5000)"),
        ("A.java", "items.get(3, other)"),
        ("A.java", "Thread.sleep(200); // timing: ok"),
    ],
)
def test_a_generous_or_unrelated_or_excused_wait_is_not(name, line):
    assert scan_text(line, name) == []


def test_the_floor_is_one_second():
    assert FLOOR_MS == 1000


def test_a_tree_is_read_in_path_order_and_the_command_only_warns_unless_strict(tmp_path, capsys):
    (tmp_path / "b.java").write_text("x\nThread.sleep(10);\n", encoding="utf-8")
    (tmp_path / "a.kt").write_text("delay(20)\n", encoding="utf-8")
    (tmp_path / "notes.txt").write_text("Thread.sleep(10)\n", encoding="utf-8")
    found = scan_tree(tmp_path)
    assert [(one.file.rsplit("/", 1)[1], one.line) for one in found] == [("a.kt", 1), ("b.java", 2)]
    assert main([str(tmp_path)]) == 0
    assert "2 short wait(s)" in capsys.readouterr().out
    assert main(["--strict", str(tmp_path)]) == 1
