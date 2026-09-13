"""Mirror of `tools/quality/board/last_pointer.py` (R12), ⛔ over a SYNTHESISED repository.

⭐ **The base commit carries one record section of every shape the row separates:**

| section | pointed at, at `base`, by | what it is for |
|---|---|---|
| `#alpha` | `BOARD.md` alone | ⛔ the LAST pointer (clause 4, first arm) |
| `#beta` | `BOARD.md` and `rows/W1.md` | ⭐ one of TWO (clause 4, second arm) |
| `#gamma` | `BOARD.md` alone | a pointer MOVED, not removed |
| `#delta` | `BOARD.md`, and the archive cites itself | ⛔ `CTO-68/4`'s own shape |
| `handoffs/X.md#finding-one` | `BOARD.md` alone | a handoff is a record too |
| `#epsilon` | nothing | ⭐ an unreferenced heading is the denominator, never a finding |

⭐ **The identity the fixture commits with is a PLACEHOLDER** (R7).
"""

from __future__ import annotations

from pathlib import Path

import pytest

import tools.quality as quality
from tests.support import assert_package_contract
from tests.support import git as git_binary
from tools.quality.board import last_pointer
from tools.quality.board.last_pointer import (
    KEPT,
    ORPHANED,
    RECORD_ARCHIVE,
    UNREAD,
    Pointer,
    main,
    read,
    render,
    resolve,
)
from tools.workspace import git

AUTHOR = ("-c", "user.name=Example Author", "-c", "user.email=author@example.invalid")
BOARD = "docs/tasks/BOARD.md"
ROW = "docs/tasks/rows/W1.md"
HANDOFF = "docs/tasks/handoffs/X.md"
ARCHIVE = (
    "# Archive\n\n## Alpha\n\n## Beta\n\n## Gamma\n\n## Delta\n\n[itself](#delta)\n\n## Epsilon\n"
)
LINKS = {
    "alpha": "[a](BOARD-ARCHIVE.md#alpha)",
    "beta": "[b](BOARD-ARCHIVE.md#beta)",
    "gamma": "[g](BOARD-ARCHIVE.md#gamma)",
    "delta": "[d](BOARD-ARCHIVE.md#delta)",
    "finding": "[h](handoffs/X.md#finding-one)",
}


def board(*dropped: str) -> str:
    """The board with every link in `LINKS` except `dropped`, one per line."""
    return "# Board\n\n" + "".join(
        f"{link}\n" for name, link in LINKS.items() if name not in dropped
    )


def commit(root: Path, files: dict[str, str | None], message: str) -> str:
    """Write (or, for None, remove) `files`, commit them, and return the new sha."""
    for name, text in files.items():
        if text is None:
            assert git(root, "rm", "-q", name).returncode == 0
            continue
        (root / name).parent.mkdir(parents=True, exist_ok=True)
        (root / name).write_text(text, encoding="utf-8")
        assert git(root, "add", name).returncode == 0
    assert git(root, *AUTHOR, "commit", "-q", "-m", message).returncode == 0
    return git(root, "rev-parse", "HEAD").stdout.strip()


@pytest.fixture
def repository(tmp_path: Path) -> Path:
    """The base commit the module docstring tabulates, tagged `base`."""
    assert git_binary()
    root = tmp_path / "repo"
    root.mkdir()
    assert git(root, "init", "-q", "-b", "main").returncode == 0
    files = {RECORD_ARCHIVE: ARCHIVE, HANDOFF: "# X\n\n## Finding one\n", BOARD: board()}
    commit(root, {**files, ROW: "# W1\n\n[b](../BOARD-ARCHIVE.md#beta)\n"}, "base")
    assert git(root, "tag", "base").returncode == 0
    return root


# Clause 1 — the design decision: a command over two refs, never the floor.


def test_the_module_states_its_contract() -> None:
    """R17: what it does, how you use it, what it depends on."""
    assert_package_contract(last_pointer, "tools.quality.board.last_pointer")


def test_the_design_it_is_a_COMMAND_and_never_in_CHECKS_or_NOTICES() -> None:
    """⛔ A two-ref verdict on the floor would print two verdicts over one tree (Ruling 80)."""
    registered = [*quality.CHECKS, *quality.NOTICES]
    assert all(entry.__module__ != last_pointer.__name__ for entry in registered)


def test_the_exit_is_a_function_of_the_REFS_and_never_the_working_tree(repository: Path) -> None:
    """⭐ An uncommitted removal reads `KEPT` over `base..base`. Plant: read the disk → RED."""
    (repository / BOARD).write_text(board("alpha", "delta"), encoding="utf-8")
    (repository / RECORD_ARCHIVE).unlink()
    reading = read(repository, "base", "base")
    assert reading.exit == KEPT and reading.orphaned == []
    sha = commit(repository, {BOARD: board("alpha")}, "drop alpha")
    (repository / BOARD).write_text(board(), encoding="utf-8")
    assert read(repository, "base", sha).exit == ORPHANED


# Clause 2 — the predicate is LAST POINTER REMOVED, and the denominator is printed.


def test_an_UNREFERENCED_heading_is_the_denominator_and_never_a_finding(repository: Path) -> None:
    """⭐ `#epsilon` and both `# ` titles have no pointer, and `base..base` is `KEPT`."""
    reading = read(repository, "base", "base")
    assert reading.exit == KEPT
    printed = "\n".join(render(reading))
    assert (
        "2 record documents, 8 record headings, 3 with no pointer from a live document" in printed
    )


# Clause 4 — both directions (R12).


def test_removing_the_LAST_pointer_is_REPORTED_with_the_pointer_that_was_last(
    repository: Path,
) -> None:
    """⛔ Plant: an empty `orphaned` → RED."""
    reading = read(repository, "base", commit(repository, {BOARD: board("alpha")}, "trim"))
    assert reading.exit == ORPHANED
    assert reading.orphaned == [(RECORD_ARCHIVE, "alpha")]
    assert f"  ⛔ ORPHANED: {RECORD_ARCHIVE}#alpha -- its last pointer at " in "\n".join(
        render(reading)
    )
    assert any(line.endswith(f"{BOARD}:3") for line in render(reading))


def test_removing_ONE_OF_TWO_pointers_is_NOT_reported_and_is_counted(repository: Path) -> None:
    """⭐ The arm that decides usable or noise. Plant: `orphaned` = lost ANY pointer → RED."""
    reading = read(repository, "base", commit(repository, {BOARD: board("beta")}, "trim"))
    assert reading.exit == KEPT and reading.orphaned == []
    assert reading.thinned == [(RECORD_ARCHIVE, "beta")]
    assert "  sections that lost a pointer and are still reached: 1" in render(reading)


def test_a_record_CITING_ITSELF_does_not_keep_a_section_reached(repository: Path) -> None:
    """⛔ `CTO-68/4`'s shape: the archive's own `#delta`. Plant: count a record's pointers → RED."""
    reading = read(repository, "base", commit(repository, {BOARD: board("delta")}, "trim"))
    assert reading.orphaned == [(RECORD_ARCHIVE, "delta")]


def test_a_HANDOFF_section_is_a_record_section(repository: Path) -> None:
    """⚠️ The live witness range carried one. Plant: the archive alone is a record → RED."""
    reading = read(repository, "base", commit(repository, {BOARD: board("finding")}, "trim"))
    assert reading.orphaned == [(HANDOFF, "finding-one")]


def test_a_CODE_SPAN_mention_is_not_a_pointer_and_keeps_nothing_reached(repository: Path) -> None:
    """⭐ `markdown.pointers`' own grammar: a backticked link is a mention."""
    text = board("alpha") + "`[a](BOARD-ARCHIVE.md#alpha)`\n"
    reading = read(repository, "base", commit(repository, {BOARD: text}, "mention"))
    assert reading.orphaned == [(RECORD_ARCHIVE, "alpha")]


# The brief's third plant: a pointer MOVED, not removed, is ruled here.


@pytest.mark.parametrize(
    ("files", "why"),
    [
        (
            {
                BOARD: board("gamma"),
                ROW: "# W1\n\n[b](../BOARD-ARCHIVE.md#beta)\n[g](../BOARD-ARCHIVE.md#gamma)\n",
            },
            "moved to another LIVE document",
        ),
        (
            {BOARD: board("gamma"), RECORD_ARCHIVE: ARCHIVE + "\n## W1\n\n[g](#gamma)\n"},
            "moved INTO the archive at a close",
        ),
        (
            {BOARD: board("gamma") + "[g](./BOARD-ARCHIVE.md#GAMMA)\n"},
            "re-spelled on the same board",
        ),
    ],
)
def test_a_pointer_MOVED_is_not_REMOVED(repository: Path, files: dict[str, str], why: str) -> None:
    """⭐ Plants: `landed` returns `0`; reach counted per source document → RED."""
    reading = read(repository, "base", commit(repository, files, why))
    assert reading.exit == KEPT, why
    assert reading.orphaned == []


def test_a_section_whose_HEADING_is_gone_is_printed_apart_and_not_reported(
    repository: Path,
) -> None:
    """⚠️ A record edit is Ruling 106's and a dangling pointer is the floor's, never this row's."""
    archive = ARCHIVE.replace("## Alpha", "## Renamed")
    sha = commit(repository, {BOARD: board("alpha"), RECORD_ARCHIVE: archive}, "edit a record")
    reading = read(repository, "base", sha)
    assert reading.exit == KEPT and reading.vanished == [(RECORD_ARCHIVE, "alpha")]


# Ruling 191: nothing read is never the pass reading.


def test_a_ref_that_does_not_resolve_is_UNREAD(repository: Path) -> None:
    """⛔ git declining to answer is never a range with nothing lost."""
    reading = read(repository, "no-such-ref", "base")
    assert reading.exit == UNREAD and "does not resolve" in (reading.unread or "")


def test_no_RECORD_HEADING_at_until_is_UNREAD(repository: Path) -> None:
    """⛔ With no record there is nothing a pointer could reach. Plant: drop the refusal → RED."""
    sha = commit(repository, {RECORD_ARCHIVE: None, HANDOFF: None, BOARD: "# Board\n"}, "drop")
    reading = read(repository, "base", sha)
    assert reading.exit == UNREAD
    assert any("NOT READ" in line for line in render(reading))


@pytest.mark.parametrize(
    ("document", "target", "expected"),
    [
        (ROW, "../BOARD-ARCHIVE.md#a", RECORD_ARCHIVE),
        (RECORD_ARCHIVE, "#a", RECORD_ARCHIVE),
        (BOARD, "handoffs/X.md#b", HANDOFF),
        (BOARD, "/docs/tasks/BOARD-ARCHIVE.md#a", None),
        (BOARD, "../../../x.md#a", None),
    ],
)
def test_a_pointer_resolves_as_a_repository_path(document: str, target: str, expected) -> None:
    """⛔ A pointer that leaves the repository reaches no record."""
    assert resolve(document, Pointer(document, 1, target)) == expected


def test_the_command_line_prints_the_population_BEFORE_the_verdict(
    repository: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """⭐ The entry point the merging office runs, asserted rather than assumed (Ruling 128)."""
    sha = commit(repository, {BOARD: board("alpha")}, "trim")
    code = main(["--root", str(repository), "base", sha])
    printed = capsys.readouterr().out
    assert code == ORPHANED
    assert printed.index("population at") < printed.index("ORPHANED:") < printed.index("exit 1")
    assert str(repository) not in printed, "⛔ R7: no absolute path in a reading"
