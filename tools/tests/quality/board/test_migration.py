r"""Ruling 177: the split is validated over CONTENT, not over a line partition.

⛔ **This module exists because the first validation PASSED while text was
lost.** ⚠️ The claim was a line partition — *8,546 source lines went to 8,351 +
101 + 16 + 78 destinations, and the sum is exact* — ⭐ **and the sum was true.**
⛔ **What a line partition cannot see is a line that was SPLIT into pieces where
only some of the pieces were kept**, and that is exactly what happened: the 78
register lines were counted as consumed while only two of their five cells were
written anywhere.

| | |
|---|---|
| lost, and found by review rather than by the assertion | the **Owner** and
  **Status** columns, **28,262 bytes** |
| lost *and nowhere else in the tree* | ⛔ **three files** — `W38`, `W40`, `W53` |
| why those three | a pipe inside a code span, so a naive split tore the
  WRONG cell in mid-sentence |

⭐ **The claim is now simpler and checkable at the level of bytes: EVERY line of
`BOARD.md` at the base appears verbatim in one of the three destinations, and
`docs/tasks/rows/` is a live EXTRACT rather than a fourth destination.**

## ⛔ Why the base is read from git rather than pinned in a fixture

⭐ It is the same object the migration read, named by ref, so this cannot drift
into asserting a copy of the input against itself. ⚠️ **The test SKIPS rather
than passing when the base ref is unreachable** — ⛔ Ruling 155: a recorded
negative says which, and *"could not put the question"* is not *"the answer is
yes"*.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest

from tests.support import repository_root
from tools.quality.board.register import cells

_REGISTER_ROW = re.compile(r"^\|\s*(?:[⛔⭐✅⚠️ ]|\*\*)*`?(W\d+)`?\*{0,2}\s*\|")

#: ⛔ The ref the split was taken FROM, named rather than described.
BASE = "bfb8c8c"
SOURCE = "docs/tasks/BOARD.md"

#: ⛔ The ref the split produced, and **this module's subject is the OUTPUT, not
#: the working tree** (Ruling 180).
#:
#: ⚠️ **The first version read `docs/tasks/rows/` off disk, and the branch's own
#: contract then turned this suite RED on its first ordinary use:** `board.md`
#: tells the PO that re-scoping a live row means EDITING `rows/<ID>.md`, and
#: minting one means CREATING a new one. ⛔ **Both are correct actions, and both
#: failed a test shipped in the same commit** — ⭐ *the right property over the
#: wrong subject*, which is `CTO-45/1`'s own class recurring inside its fix.
#:
#: ⭐ **A migration is a claim about a pair of refs, and both halves of the pair
#: are now refs.** ⛔ **The live tree is not this module's business: the live
#: tree's shape is `check_board`'s, which runs on the floor and is
#: amendment-safe by construction.**
#:
#: ⚠️ It is a WHOLE sha rather than a short one, because a short sha is a
#: prefix and a prefix can become ambiguous in a repository that keeps growing.
OUTPUT = "5688dcd1a280aaaee27aa1d0763ce897389f2e3e"
ROWS = "docs/tasks/rows"

#: The three destinations, and the whole claim is that they cover the source.
ARCHIVE = "docs/tasks/BOARD-ARCHIVE.md"
CONVENTION = "docs/conventions/board.md"
BOARD = "docs/tasks/BOARD.md"

#: ⛔ Lines a partition may not be asked about, and both are structural rather
#: than content: markdown's own table separator, and blanks.
_STRUCTURAL = ("", "|---|---|", "---")

#: ⛔ The anchor `ARCH/4` re-addressed, and the ONLY text this migration
#: changed. ⚠️ **Two lines of 8,546**, both pointing at a heading that moved to
#: `docs/conventions/board.md` — ⭐ **accepted under Ruling 174 on the narrow
#: ground that Ruling 106's freeze attaches when material BECOMES a record, not
#: while it is being moved into one.** ⛔ *"A pointer is an address, not a
#: statement"* was REFUSED and is not the ground relied on here.
MOVED_ANCHOR = "#the-wave-checks-six-at-open-and-check-4-again-at-close"
RE_ADDRESSED = "../conventions/board.md#the-wave-checks-moved-whole-from-boardmd-2026-09-10"


def _at(ref: str, path: str) -> str:
    """The content of `path` at `ref`, or a SKIP naming which ref was missing.

    ⛔ Ruling 155: *"could not put the question"* is not *"the answer is yes"*,
    so an unreachable ref skips with the ref in the message rather than
    returning an empty string that would satisfy every assertion here.
    """
    root = repository_root()
    known = subprocess.run(
        ["git", "cat-file", "-e", f"{ref}^{{commit}}"], cwd=root, capture_output=True
    )
    if known.returncode != 0:
        pytest.skip(f"{ref} is not in this checkout, so the question cannot be put")
    shown = subprocess.run(
        ["git", "show", f"{ref}:{path}"], cwd=root, capture_output=True, text=True
    )
    assert shown.returncode == 0, shown.stderr
    return shown.stdout


def _base_lines() -> list[str]:
    return _at(BASE, SOURCE).split("\n")


def _output_row_files() -> dict[str, str]:
    """`{"W40": <text>}` for every row file the migration PRODUCED.

    ⭐ Read from `OUTPUT`, so an amendment, a mint or a close in the working
    tree changes nothing here — which is the whole of Ruling 180.
    """
    root = repository_root()
    known = subprocess.run(
        ["git", "cat-file", "-e", f"{OUTPUT}^{{commit}}"], cwd=root, capture_output=True
    )
    if known.returncode != 0:
        pytest.skip(f"{OUTPUT} is not in this checkout, so the question cannot be put")
    listed = subprocess.run(
        ["git", "ls-tree", "--name-only", f"{OUTPUT}:{ROWS}"],
        cwd=root,
        capture_output=True,
        text=True,
    )
    assert listed.returncode == 0, listed.stderr
    names = [n for n in listed.stdout.split("\n") if n.endswith(".md")]
    # ⛔ Ruling 48: an empty population satisfies every assertion below it.
    assert len(names) == 50, f"{OUTPUT}:{ROWS} holds {len(names)} files, expected 50"
    return {n.removesuffix(".md"): _at(OUTPUT, f"{ROWS}/{n}") for n in names}


def _consumed_register_lines() -> list[str]:
    """The 78 lines the split consumed — the last register row per `W` id."""
    latest: dict[str, str] = {}
    for line in _base_lines():
        match = _REGISTER_ROW.match(line)
        if match:
            latest[match.group(1)] = line
        elif line.startswith("| W17 **+ W19** |"):
            latest["W17+W19"] = line
    return list(latest.values())


#: The last line of every row file's frame. ⛔ Located by its text rather than
#: by an index, because `rows/W17.md` carries one extra frame block (the note
#: that `W19` rides with it) and an index would have silently skipped its
#: argument instead.
_FRAME_END = "not in two places.**"


def _argument_blocks(name: str, text: str) -> list[str]:
    """A row file's argument blocks — everything after its frame."""
    blocks = [b for b in text.split("\n\n") if b.strip()]
    for index, block in enumerate(blocks):
        if _FRAME_END in block:
            return [b.strip() for b in blocks[index + 1 :]]
    raise AssertionError(f"{name} has no frame; every row file states what it is")


def _unretargeted(block: str) -> str:
    """A row file's block with `ARCH/4`'s link rewrite undone.

    ⭐ The rewrite is the ONLY edit a row file's text carries, so undoing it is
    what lets the comparison below be `==` rather than a similarity.
    """
    return block.replace("](../BOARD-ARCHIVE.md#", "](#")


def _destination_text() -> str:
    root = repository_root()
    return "\n".join(
        (root / name).read_text(encoding="utf-8") for name in (ARCHIVE, CONVENTION, BOARD)
    )


def test_every_line_of_the_old_board_survives_verbatim() -> None:
    """⛔ The content-level assertion Ruling 177 requires, and it names its misses.

    ⭐ **Line by line, not by count**: a line that was split into pieces fails
    here even when every count still sums, which is precisely the reading the
    line partition could not take.
    """
    destination = _destination_text()
    source = _base_lines()
    missing = [
        (number, line)
        for number, line in enumerate(source, 1)
        if line.strip() not in _STRUCTURAL and line not in destination
    ]
    # ⛔ EXPECTED, written before the run: exactly 2 of 8,546, and both are
    # ARCH/4's re-addressed anchor. ⭐ Asserting "0 missing" would have been the
    # weaker claim — this one fails if a THIRD line ever changes.
    assert [line for _n, line in missing if MOVED_ANCHOR not in line] == [], (
        f"{len(missing)} of {len(source)} lines appear in no destination; first "
        f"unexplained is {missing[0][1][:120]!r}"
    )
    assert len(missing) == 2, [n for n, _l in missing]
    for _number, line in missing:
        assert line.replace(MOVED_ANCHOR, RE_ADDRESSED) in destination, line[:120]


def test_the_register_lines_carry_their_owner_and_status_columns() -> None:
    """⛔ `CTO-45/1` stated as a property, not as three filenames.

    ⚠️ **The residue that reached nothing was a COLUMN, not a file** — three
    files were merely where it became unrecoverable. ⭐ So the assertion is
    about the column: every register line is in the record whole, so every cell
    of it is.
    """
    archive = (repository_root() / ARCHIVE).read_text(encoding="utf-8")
    register_lines = _consumed_register_lines()
    assert len(register_lines) == 78, "Ruling 48: state the population, then reduce it"
    absent = [line for line in register_lines if line not in archive]
    assert absent == [], (
        f"{len(absent)} of {len(register_lines)} register lines are not in the record"
    )
    # ⭐ And the column that was lost, named as a number rather than as three files.
    status_bytes = sum(
        len(cells(line)[3].encode()) for line in register_lines if len(cells(line)) >= 5
    )
    assert status_bytes > 20_000, status_bytes


def test_every_block_of_every_row_file_is_a_WHOLE_CELL_of_its_own_row() -> None:
    """⛔ The defect itself, asserted as an equality rather than a heuristic.

    ⚠️ **The first version of this test used a tell — *does the block start
    mid-sentence?* — and it was a PROXY**: it flagged `` `api` is a generic
    field name`` and *"round 22's mint block above"*, both of which are whole,
    correct cells. ⭐ **Ruling 143's shape: a reading from a proxy is not a
    property of the thing.**

    ⭐ **The property is exact and cheap**: a row file's argument is made of
    WHOLE CELLS of that row's own source line. ⛔ A fragment fails (it is not a
    cell), and text from a neighbouring row fails (it is not one of THIS row's
    cells) — which is both halves of `CTO-45/1` in one assertion.
    """
    by_id = {}
    for line in _consumed_register_lines():
        match = _REGISTER_ROW.match(line)
        by_id[match.group(1) if match else "W17"] = cells(line)
    produced = _output_row_files()
    offenders = []
    for name, text in sorted(produced.items()):
        columns = by_id.get(name)
        assert columns, f"{name}.md has no register line at {BASE}"
        for block in _argument_blocks(name, text):
            if _unretargeted(block) not in columns:
                offenders.append((name, _unretargeted(block)[:70]))
    assert offenders == [], f"{len(offenders)} of {len(produced)} row files: {offenders}"


def test_no_row_file_carries_the_status_column() -> None:
    """⛔ The column that reached no destination, asserted out of the live half.

    ⭐ A status lives on the board and in the record; a row file carries the
    ARGUMENT. ⚠️ **This is the assertion that would have failed on the three
    broken files even if their text had been whole**, because what was in them
    was the status column and it did not belong there whatever its shape.
    """
    statuses = {cells(line)[3] for line in _consumed_register_lines() if len(cells(line)) >= 5}
    offenders = [
        name
        for name, text in sorted(_output_row_files().items())
        for block in _argument_blocks(name, text)
        if _unretargeted(block) in statuses
    ]
    assert offenders == [], offenders


def test_the_row_files_are_an_extract_of_the_source_not_a_fourth_destination() -> None:
    """⭐ Every row file's argument came OUT of the board, and is still in it.

    ⛔ This is what makes `rows/` an extract rather than a move: the record
    keeps the original, so the row file may be freely amended without any byte
    ceasing to exist.

    ⭐ **EVERY block, not just the naming one.** ⚠️ The first version sliced
    `[:1]` so that amendment would survive it — ⛔ **a workaround for the wrong
    subject, and it is unnecessary now that the subject is a ref** (Ruling 180).
    """
    base = "\n".join(_base_lines())
    thin = [
        (name, block[:60])
        for name, text in sorted(_output_row_files().items())
        for block in _argument_blocks(name, text)
        if _unretargeted(block) not in base
    ]
    assert thin == [], f"blocks not in {SOURCE}@{BASE}: {thin}"


def test_an_unreachable_base_skips_rather_than_passing(monkeypatch: pytest.MonkeyPatch) -> None:
    """⛔ The IMPOSSIBLE reading, and it is the one that keeps the rest honest.

    ⚠️ **Every assertion above compares the tree against a ref.** ⛔ If that ref
    is not in the checkout, a walk over an empty source would satisfy all four
    of them — ⭐ **`0 = 0` wearing a migration.** ⚠️ Ruling 155: *"could not put
    the question"* is not *"the answer is yes"*, so this reads `Skipped`.
    """
    for name in ("BASE", "OUTPUT"):
        monkeypatch.setattr(f"{__name__}.{name}", "0" * 40)
    for reader in (_base_lines, _output_row_files):
        with pytest.raises(BaseException) as caught:
            reader()
        assert caught.typename == "Skipped", (reader.__name__, caught.typename)
        assert "cannot be put" in str(caught.value.msg)
