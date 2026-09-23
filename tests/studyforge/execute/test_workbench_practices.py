"""Mirror of `src/studyforge/execute/workbench.py`, `W446`: each practice owns its editor lock.

⛔ **The user's report**: a page with two practices answered one of them `409`,
and only the last-opened practice was editable. Both had one cause — every
practice opened ONE folder, so they shared ONE settings file, whose lock names
ONE file editable, written through ONE staging name.

⭐ **So each claim is asserted as a relation between two practices**, never as a
constant: the folders differ, opening one leaves the other's lock byte for byte
as it was, and two writes at once — two practices, or one practice twice — both
land. ⛔ **The concurrency is FORCED, not hoped for**: every settings write is
held at the moment before its `replace` until the other has reached the same
point, which is exactly the interleaving that refused the user's panel.
"""

from __future__ import annotations

import json
import os
import threading
from pathlib import Path

import pytest

from studyforge.execute import Editor, workbench
from studyforge.execute.workbench import (
    EVERYTHING,
    READONLY_EXCLUDE,
    READONLY_INCLUDE,
    SETTINGS_DIR,
    SETTINGS_FILE,
    practice_folder,
    write_settings,
)

#: The generated editor's two binds (`W445`): the sources and the practice
#: workspaces. ⚠️ Made-up container paths — the real one is a home (R7).
EDITOR = Editor(
    origin="http://127.0.0.1:8443",
    folder="/w/sources",
    base="src",
    others=(("practice", "/w/practice"),),
)

#: A flat practice, as `M7`'s are: its source and its test side by side.
FLAT = ("practice/bitmap/Bitmap.java", "practice/bitmap/BitmapTest.java")

#: An authored Maven practice, as the pilot's are, and its build file.
UNIT = "practice/fundamentals/prose/unit-15"
MAVEN = (
    f"{UNIT}/practice-1/src/main/java/com/example/Check.java",
    f"{UNIT}/practice-1/src/test/java/com/example/CheckTest.java",
)
MAVEN_TWO = (
    f"{UNIT}/practice-2/src/main/java/com/example/Recon.java",
    f"{UNIT}/practice-2/src/test/java/com/example/ReconTest.java",
)


def pom(number: int) -> str:
    return f"{UNIT}/practice-{number}/pom.xml"


def command(number: int) -> tuple[str, ...]:
    """The pilot's own shape of a test command: only `pom.xml` is a file."""
    return ("mvn", "-o", "-q", "-f", pom(number), "test")


@pytest.fixture
def root(tmp_path):
    for path in (*FLAT, *MAVEN, *MAVEN_TWO, pom(1), pom(2)):
        (tmp_path / path).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / path).write_text("x\n", encoding="utf-8")
    return tmp_path


def opened(root: Path, main: str, test: str | None, named=()) -> Editor:
    """The practice's folder, and its settings written — what the route does."""
    where = practice_folder(EDITOR, main, test, root=root, named=named)
    assert where is not None
    write_settings(root / where.base, where.inside(main), where.inside(test) if test else None)
    return where


def lock_of(root: Path, where: Editor) -> dict:
    target = root / where.base / SETTINGS_DIR / SETTINGS_FILE
    return json.loads(target.read_text(encoding="utf-8"))


def editable(root: Path, where: Editor, path: str) -> bool:
    """Whether the workbench would let the reader write `path` under this lock."""
    held = lock_of(root, where)
    assert held[READONLY_INCLUDE] == {EVERYTHING: True}
    return held[READONLY_EXCLUDE].get(where.inside(path), False) is True


# --- ⭐ the folder is the practice's own -------------------------------------


def test_a_flat_practice_opens_the_directory_it_sits_in(root):
    where = practice_folder(EDITOR, *FLAT, root=root)
    assert where == Editor(
        origin=EDITOR.origin, folder="/w/practice/bitmap", base="practice/bitmap"
    )
    assert where.inside(FLAT[0]) == "Bitmap.java"


def test_a_maven_practice_opens_the_directory_its_build_file_names(root):
    # ⭐ The build file weighs in, so the Java tooling sees a project and not
    # two loose source trees; `-f`, `mvn` and `test` are not files and do not.
    where = practice_folder(EDITOR, *MAVEN, root=root, named=command(1))
    assert where is not None and where.base == f"{UNIT}/practice-1"
    assert where.folder == "/w/practice/fundamentals/prose/unit-15/practice-1"


def test_without_a_named_file_the_folder_is_the_deepest_holding_both(root):
    where = practice_folder(EDITOR, *MAVEN, root=root)
    assert where is not None and where.base == f"{UNIT}/practice-1/src"


@pytest.mark.parametrize(
    "named",
    [("src/one.md",), ("practice/absent.xml",), ("../practice/x",), ("/etc/hostname",)],
    ids=["another bind's file", "no such file", "a climb", "an absolute path"],
)
def test_a_named_path_the_bind_does_not_hold_as_a_file_never_widens_the_folder(root, named):
    (root / "src").mkdir(exist_ok=True)
    (root / "src" / "one.md").write_text("x\n", encoding="utf-8")
    where = practice_folder(EDITOR, *FLAT, root=root, named=named)
    assert where is not None and where.base == "practice/bitmap"


def test_a_main_file_no_bind_holds_has_no_folder_at_all(root):
    assert practice_folder(EDITOR, "docs/Main.java", None, root=root) is None


def test_a_file_at_the_top_of_the_bind_opens_the_bind_itself(root):
    where = practice_folder(EDITOR, "practice/Main.java", None, root=root)
    assert where == Editor(origin=EDITOR.origin, folder="/w/practice", base="practice")


def test_two_practices_of_one_page_open_two_different_folders(root):
    one = practice_folder(EDITOR, *MAVEN, root=root, named=command(1))
    two = practice_folder(EDITOR, *MAVEN_TWO, root=root, named=command(2))
    assert one is not None and two is not None and one.folder != two.folder


# --- ⛔ opening a practice never changes another's lock ----------------------


@pytest.mark.parametrize("order", [(0, 1), (1, 0)], ids=["first then second", "second then first"])
def test_each_practice_keeps_its_own_main_editable_and_its_test_locked_in_any_order(root, order):
    practices = [(MAVEN, command(1)), (MAVEN_TWO, command(2))]
    opened_in = {}
    for index in order:
        (main, test), named = practices[index]
        opened_in[index] = opened(root, main, test, named)
    for index, ((main, test), _) in enumerate(practices):
        where = opened_in[index]
        assert editable(root, where, main), main
        assert not editable(root, where, test), test


def test_opening_another_practice_leaves_this_ones_lock_byte_for_byte(root):
    first = opened(root, *MAVEN, command(1))
    before = (root / first.base / SETTINGS_DIR / SETTINGS_FILE).read_bytes()
    opened(root, *MAVEN_TWO, command(2))
    opened(root, *FLAT)
    assert (root / first.base / SETTINGS_DIR / SETTINGS_FILE).read_bytes() == before


# --- ⛔ two writes at once never refuse each other ---------------------------


@pytest.fixture
def forced(monkeypatch):
    """Hold every settings `replace` until two writers have reached it."""
    meet, broken = threading.Barrier(2, timeout=5), []
    real = os.replace

    def replace(source, target, *args, **kwargs):
        if Path(target).name == SETTINGS_FILE:
            try:
                meet.wait()
            except threading.BrokenBarrierError:
                broken.append(target)
        return real(source, target, *args, **kwargs)

    monkeypatch.setattr(workbench.os, "replace", replace)
    return broken


def at_once(*writes) -> list[BaseException]:
    failures: list[BaseException] = []

    def attempt(write):
        try:
            write()
        except BaseException as error:  # noqa: BLE001 — every failure is the reading
            failures.append(error)

    threads = [threading.Thread(target=attempt, args=(write,)) for write in writes]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(15)
    return failures


def test_the_same_practice_asked_twice_at_once_is_written_twice(root, forced):
    # ⛔ The plant this file exists for: with ONE staging name, both writes
    # stage into the same file, the first `replace` moves it away, and the
    # second is refused — the user's `409`.
    where = practice_folder(EDITOR, *FLAT, root=root)
    folder, main, test = root / where.base, where.inside(FLAT[0]), where.inside(FLAT[1])
    assert at_once(*[lambda: write_settings(folder, main, test)] * 2) == []
    assert editable(root, where, FLAT[0]) and not editable(root, where, FLAT[1])
    assert list((folder / SETTINGS_DIR / workbench.STAGING_DIR).iterdir()) == []
    assert forced == [], "the two writes never met: this reading forced nothing"


def test_two_practices_asked_at_once_both_land_each_with_its_own_lock(root, forced):
    one = practice_folder(EDITOR, *MAVEN, root=root, named=command(1))
    two = practice_folder(EDITOR, *MAVEN_TWO, root=root, named=command(2))
    failures = at_once(
        lambda: write_settings(root / one.base, one.inside(MAVEN[0]), one.inside(MAVEN[1])),
        lambda: write_settings(root / two.base, two.inside(MAVEN_TWO[0]), two.inside(MAVEN_TWO[1])),
    )
    assert failures == [] and forced == []
    assert editable(root, one, MAVEN[0]) and not editable(root, one, MAVEN[1])
    assert editable(root, two, MAVEN_TWO[0]) and not editable(root, two, MAVEN_TWO[1])
