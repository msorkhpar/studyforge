"""Mirror of `tools/quality/board/crossrepo.py` (R12): `W403`, asserted in BOTH directions.

⛔ **The subject is a SYNTHESISED workspace** — a repository from `conftest.py` and a sibling
component built beside it in `tmp_path` — and that is Ruling 191(b) rather than convenience:
⚠️ **the live workspace is shared state another office's gate may be reading, and a test that
moved it would be measuring the host** (Ruling 225, and the register's standing rule).

| clause | ⛔ the expectation, written before the run |
|---|---|
| a task naming a sibling declares BOTH halves | a row declaring one is REFUTED, naming which |
| the sibling half is read AT THE PIN | reachable from `HEAD`, not from the pin: REFUTED |
| the half on no committed ref | REFUTED — ⭐ `TC-05`'s own shape, replayed with its tree |
| the component absent | ⚠️ NOT ANSWERABLE, exit `2`, ⛔ never a pass |
| the block absent | ⚠️ NOT ANSWERABLE; a DECLARED and EMPTY block is the real answer |
| this repository | ⭐ DECLARES the block, and every entry declares both halves |

⭐ **The `HEAD`-versus-pin pair is the PLANT this row turns on:** both readings are taken over
the SAME sibling, and they DIFFER — ⛔ so a version of this instrument that read the working
tree (which is what read `TC-05`'s deliverable as present while it was on no ref) is refuted
by a measurement rather than by an argument.
"""

from __future__ import annotations

import json
from pathlib import Path

from tests.support import repository_root
from tools.quality.board.corroborate import (
    CORROBORATED,
    NOT_AUTHORITATIVE,
    REFUTED,
    corroborate,
)
from tools.quality.board.crossrepo import (
    ABSENT,
    CROSSREPO,
    CROSSREPO_CLOSE,
    CROSSREPO_OPEN,
    DECLARED,
    ROLES,
    UNREADABLE,
    declared,
    judge,
    read,
    read_declaration,
)
from tools.quality.board.verdict import Answer
from tools.workspace import PIN_FILENAME, git

from .conftest import CROSSREPO_HEADER, MISSING_OBJECT, RELEASE, commit, write_board

#: The component every synthetic declaration names. ⛔ Never a real sibling: this suite must
#: not depend on, and can never move, the components another office is reading.
SIDECAR = "sidecar"


def _block(rows: str, header: str = CROSSREPO_HEADER) -> str:
    return f"\n{CROSSREPO_OPEN}\n{header}{rows}{CROSSREPO_CLOSE}\n"


def _row(task: str, component: str, framework: str, sibling: str) -> str:
    return f"| `{task}` | `{component}` | `{framework}` | `{sibling}` |\n"


def _sibling(tmp_path: Path, name: str = SIDECAR) -> Path:
    """One committed sibling component beside the repository, on `main`."""
    where = tmp_path / name
    where.mkdir()
    assert git(where, "init", "-q", "-b", "main").returncode == 0
    commit(where, "first.txt")
    return where


def _at(where: Path, ref: str = "HEAD") -> str:
    """The full commit id `ref` names in `where`."""
    result = git(where, "rev-parse", ref)
    assert result.returncode == 0
    return result.stdout.strip()


def _pin(root: Path, rows: list[dict]) -> None:
    """Write `workspace.json` — ⛔ the pin file's own shape, refused by `tools.workspace` if not."""
    (root / PIN_FILENAME).write_text(
        json.dumps({"workspace_api": 1, "components": rows}, indent=2) + "\n", encoding="utf-8"
    )


def _pinned(root: Path, where: Path, at: str, name: str = SIDECAR) -> None:
    """Pin this repository and one sibling, the sibling at the commit `at`."""
    _pin(
        root,
        [
            {"name": "studyforge", "where": "self", "status": "present", "commit": _at(root)},
            {"name": name, "where": "sibling", "status": "present", "commit": at},
        ],
    )
    assert where.is_dir()


def _board(root: Path, rows: str | None, header: str = CROSSREPO_HEADER) -> None:
    """An empty, declared observation table, with the declaration file written by hand."""
    write_board(root, "", crossrepo=None)
    if rows is not None:
        (root / CROSSREPO).write_text(f"# halves\n{_block(rows, header)}", encoding="utf-8")


def _judged(root: Path, tmp_path: Path) -> tuple[Answer, str]:
    verdict = judge(root, read_declaration(root), RELEASE, tmp_path)
    return verdict.answer, "\n".join(verdict.lines)


# --------------------------------------------------------------------------
# The parser — what the board DECLARES, including that it did not read
# --------------------------------------------------------------------------


def test_no_block_at_all_reads_ABSENT() -> None:
    """⛔ ABSENT, and `read` never invents an empty declaration to stand in for one."""
    declaration = read("# Board\n\nno block here.\n")
    assert declaration.state == ABSENT
    assert declaration.entries == ()


def test_a_MENTION_of_the_marker_in_prose_declares_nothing() -> None:
    """⭐ The marker is matched as the WHOLE LINE, as every other block's is."""
    assert read(f"the block is spelled {CROSSREPO_OPEN} and closed by {CROSSREPO_CLOSE}.\n").state
    assert read(f"prose naming {CROSSREPO_OPEN} inline.\n").state == ABSENT


def test_a_DECLARED_and_EMPTY_block_is_DECLARED_and_carries_no_entry() -> None:
    """⭐ *This board has no cross-repo task* is a REAL answer (Ruling 191(a))."""
    declaration = read(_block(""))
    assert declaration.state == DECLARED
    assert declaration.entries == ()


def test_a_block_whose_header_declares_no_roles_reads_UNREADABLE_at_its_line() -> None:
    """⛔ A DECLARED block that did not read is *I could not answer*, never an empty one."""
    declaration = read(_block("| x | y |\n", header="| One | Two |\n|---|---|\n"))
    assert declaration.state == UNREADABLE
    assert declaration.line == 2


def test_a_header_missing_ONE_role_is_UNREADABLE_and_the_four_are_read_from_the_header() -> None:
    """⛔ All four roles or nothing — ⭐ and renaming a column does not hide it."""
    three = "| Task | Component | Framework half |\n|---|---|---|\n"
    assert read(_block("| `T` | `c` | `f` |\n", header=three)).state == UNREADABLE
    renamed = "| Sibling half | Framework half | The component | The task |\n|---|---|---|---|\n"
    entry = read(_block("| `s1` | `f1` | `c1` | `T1` |\n", header=renamed)).entries[0]
    assert (entry.task, entry.component, entry.framework, entry.sibling) == ("T1", "c1", "f1", "s1")
    assert set(ROLES) == {"task", "component", "framework", "sibling"}


def test_an_UNCLOSED_block_is_judged_at_end_of_file_and_does_not_vanish() -> None:
    """⚠️ A missing close marker must not make a declared block disappear."""
    assert read(f"{CROSSREPO_OPEN}\n").state == UNREADABLE
    text = f"{CROSSREPO_OPEN}\n{CROSSREPO_HEADER}{_row('T', 'c', 'f', 's')}"
    assert read(text).state == DECLARED


def test_the_separator_row_is_not_an_entry_and_the_entries_keep_their_order() -> None:
    """⛔ `|---|` is a table's punctuation, not a task."""
    entries = read(_block(_row("T1", "c", "f1", "s1") + _row("T2", "c", "f2", "s2"))).entries
    assert [entry.task for entry in entries] == ["T1", "T2"]
    assert entries[0].line == 5, "⭐ the first DATA row, and the separator is line 4"


def test_declared_reads_a_code_span_and_a_cell_that_declares_NOTHING() -> None:
    """⭐ The code span is the board's idiom; ⛔ `none` and a dash are the ABSENT vocabulary."""
    assert declared("`5c32726a`") == "5c32726a"
    assert declared("**`a3aee75`**, the tip") == "a3aee75"
    assert declared("") == ""
    assert declared(" — ") == ""
    assert declared("none") == ""
    assert declared("not yet") == ""
    assert declared("a3aee75") == "a3aee75"


# --------------------------------------------------------------------------
# Reading 1 — BOTH HALVES, and the plant is the pin against the working tree
# --------------------------------------------------------------------------


def test_both_halves_landed_is_CORROBORATED(repository: Path, tmp_path: Path) -> None:
    """⭐ The POSITIVE row (Ruling 191(c)): the reading is taken over a real pair of repos."""
    where = _sibling(tmp_path)
    commit(where, "consuming.json", "{}\n")
    _pinned(repository, where, _at(where))
    _board(repository, _row("TC-x", SIDECAR, RELEASE, _at(where)))
    answer, printed = _judged(repository, tmp_path)
    assert answer is Answer.CORROBORATED, printed
    assert "CORROBORATED: TC-x" in printed


def test_planted_the_sibling_half_is_REACHED_BY_HEAD_and_NOT_BY_THE_PIN(
    repository: Path, tmp_path: Path
) -> None:
    """⛔ **THE PLANT**: the pin and the working tree give DIFFERENT answers, and the pin wins.

    ⚠️ **This is `TC-05`'s defect in its general form.** The component's `HEAD` reaches the
    declared half, so an instrument reading the checkout — which is what read that task's
    deliverable as present — would print a green. ⭐ **The pin does not reach it, and the
    control below advances the pin over the SAME tree and turns the same row green**, so the
    two readings are measured against each other rather than asserted apart.
    """
    where = _sibling(tmp_path)
    pinned = _at(where)
    commit(where, "consuming.json", "{}\n")
    half = _at(where)
    _pinned(repository, where, pinned)
    _board(repository, _row("TC-x", SIDECAR, RELEASE, half))

    answer, printed = _judged(repository, tmp_path)
    assert answer is Answer.REFUTED, printed
    assert "SIBLING half" in printed and "UNLANDED" in printed and SIDECAR in printed
    assert _at(where, "HEAD") == half, "⭐ the working tree DOES reach it — that is the point"

    # ⭐ The CONTROL, over the same tree: advance only the pin and the reading flips.
    _pinned(repository, where, half)
    corroborated, control = _judged(repository, tmp_path)
    assert corroborated is Answer.CORROBORATED, control
    assert control != printed


def test_planted_the_sibling_half_is_ON_NO_COMMITTED_REF_with_TC_05s_own_tree(
    repository: Path, tmp_path: Path
) -> None:
    """⛔ `TC-05` REPLAYED: the deliverable is in the tree, staged, and on no ref at all.

    ⚠️ **Measured by the register 2026-09-20**: the sibling's `main` sat in an abandoned
    conflicted merge, so `consuming.json` — that task's whole deliverable — existed on no
    committed ref while the framework read it as present. ⭐ **Here the file is written and
    STAGED and the declared ref names a branch nobody committed**, and the answer is a
    refusal naming the half and the component.
    """
    where = _sibling(tmp_path)
    _pinned(repository, where, _at(where))
    (where / "consuming.json").write_text("{}\n", encoding="utf-8")
    assert git(where, "add", "consuming.json").returncode == 0
    _board(repository, _row("TC-05", SIDECAR, RELEASE, "task/TC-05-compose-and-mount"))
    answer, printed = _judged(repository, tmp_path)
    assert answer is Answer.REFUTED, printed
    assert "NO COMMITTED REF" in printed and SIDECAR in printed
    assert (where / "consuming.json").is_file(), "⭐ present in the TREE, and still refused"


def test_planted_the_FRAMEWORK_half_is_UNLANDED_and_the_refusal_names_that_half(
    repository: Path, tmp_path: Path
) -> None:
    """⛔ Both halves, and the near half is not exempt: `feat/held` is ahead and unmerged."""
    where = _sibling(tmp_path)
    _pinned(repository, where, _at(where))
    _board(repository, _row("TC-x", SIDECAR, "feat/held", _at(where)))
    answer, printed = _judged(repository, tmp_path)
    assert answer is Answer.REFUTED, printed
    assert "FRAMEWORK half" in printed and "UNLANDED" in printed


def test_planted_a_FRAMEWORK_half_git_cannot_resolve_is_REFUTED_as_on_no_ref(
    repository: Path, tmp_path: Path
) -> None:
    """⚠️ A well-formed sha no object carries is not a landed half."""
    where = _sibling(tmp_path)
    _pinned(repository, where, _at(where))
    _board(repository, _row("TC-x", SIDECAR, MISSING_OBJECT, _at(where)))
    answer, printed = _judged(repository, tmp_path)
    assert answer is Answer.REFUTED, printed
    assert "FRAMEWORK half" in printed and "NO COMMITTED REF" in printed


def test_planted_a_row_declaring_ONE_HALF_is_REFUSED_before_any_git_reading(
    repository: Path, tmp_path: Path
) -> None:
    """⛔ *A task naming a sibling DECLARES BOTH HALVES* — the clause, as an instrument.

    ⭐ **This is the arm that closes the defect rather than reporting it:** the half nobody
    wrote down is the half nobody can read, and the board cannot now declare a cross-repo
    task while leaving it out.
    """
    where = _sibling(tmp_path)
    _pinned(repository, where, _at(where))
    for row in (
        f"| `TC-x` | `{SIDECAR}` | `{RELEASE}` | — |\n",
        f"| `TC-x` | `{SIDECAR}` | none | `{_at(where)}` |\n",
        f"| `TC-x` |  | `{RELEASE}` | `{_at(where)}` |\n",
    ):
        _board(repository, row)
        answer, printed = _judged(repository, tmp_path)
        assert answer is Answer.REFUTED, printed
        assert "DECLARES BOTH HALVES" in printed


def test_planted_a_component_the_pin_file_does_not_carry_is_REFUTED(
    repository: Path, tmp_path: Path
) -> None:
    """⛔ REFUTED and NOT unanswerable: ⭐ the pin file is TRACKED, so its silence is a fact
    about the declaration and not about this host."""
    where = _sibling(tmp_path)
    _pinned(repository, where, _at(where))
    _board(repository, _row("TC-x", "nowhere", RELEASE, _at(where)))
    answer, printed = _judged(repository, tmp_path)
    assert answer is Answer.REFUTED, printed
    assert "pins no component called nowhere" in printed


def test_planted_a_component_recorded_NOT_YET_CREATED_is_REFUTED(
    repository: Path, tmp_path: Path
) -> None:
    """⚠️ A half declared in a repository that does not exist yet is a declaration, not a half."""
    _pin(
        repository,
        [
            {"name": "studyforge", "where": "self", "status": "present", "commit": _at(repository)},
            {"name": SIDECAR, "where": "sibling", "status": "not-yet-created"},
        ],
    )
    _board(repository, _row("TC-x", SIDECAR, RELEASE, "main"))
    answer, printed = _judged(repository, tmp_path)
    assert answer is Answer.REFUTED, printed
    assert "not created yet" in printed


def test_planted_the_component_is_ABSENT_from_disk_and_that_is_NOT_ANSWERABLE(
    repository: Path, tmp_path: Path
) -> None:
    """⛔ **The third answer, and the reason this can be trusted at all.**

    ⚠️ An instrument that shelled into an absent sibling and answered *nothing is wrong*
    would return the PASS reading from an empty population (Ruling 191) — ⭐ **and that is
    not hypothetical: inside the pinned image exactly one directory is mounted (`FND-03`),
    so every sibling is absent there.**
    """
    where = _sibling(tmp_path)
    _pinned(repository, where, _at(where))
    _board(repository, _row("TC-x", SIDECAR, RELEASE, _at(where)))
    assert git(where, "rev-parse", "HEAD").returncode == 0
    for path in sorted(where.rglob("*"), key=lambda item: -len(item.parts)):
        path.unlink() if path.is_file() or path.is_symlink() else path.rmdir()
    where.rmdir()
    answer, printed = _judged(repository, tmp_path)
    assert answer is Answer.NOT_ANSWERABLE, printed
    assert "NOT ANSWERABLE" in printed and "not a pass" in printed.lower()


def test_NOT_ANSWERABLE_DOMINATES_a_refuted_row_in_the_same_declaration(
    repository: Path, tmp_path: Path
) -> None:
    """⛔ Ruling 216's fold: *could not read* is neither *right* nor *wrong*."""
    where = _sibling(tmp_path)
    _pinned(repository, where, _at(where))
    _board(
        repository,
        _row("TC-x", SIDECAR, "feat/held", _at(where)) + _row("TC-y", "gone", RELEASE, "main"),
    )
    refuted, _ = _judged(repository, tmp_path)
    assert refuted is Answer.REFUTED, "⭐ the control: both rows are refutable"
    _pin(
        repository,
        [
            {"name": "studyforge", "where": "self", "status": "present", "commit": _at(repository)},
            {"name": SIDECAR, "where": "sibling", "status": "present", "commit": _at(where)},
            {"name": "gone", "where": "sibling", "status": "present", "commit": _at(where)},
        ],
    )
    answer, printed = _judged(repository, tmp_path)
    assert answer is Answer.NOT_ANSWERABLE, printed


# --------------------------------------------------------------------------
# Reading 2 — the EXIT CODE, which is what a merge reads
# --------------------------------------------------------------------------


def test_the_declaration_ABSENT_makes_the_command_NOT_AUTHORITATIVE(
    repository: Path, tmp_path: Path
) -> None:
    """⛔ The block is this board's contract, so its absence is *I could not read*.

    ⭐ **And the pair is the whole point**: the same tree with a DECLARED and EMPTY block
    exits `0` and says *this repository has no cross-repo task*, which is a real answer.
    """
    write_board(repository, "", crossrepo=None)
    lines, code = corroborate(repository, RELEASE, tmp_path)
    assert code == NOT_AUTHORITATIVE
    assert any("ABSENT" in line and "NOT ANSWERABLE" in line for line in lines)

    write_board(repository, "")
    lines, code = corroborate(repository, RELEASE, tmp_path)
    assert code == CORROBORATED
    assert any("carrying no row" in line for line in lines)


def test_a_REFUTED_half_makes_the_command_exit_REFUTED(repository: Path, tmp_path: Path) -> None:
    """⛔ The exit code MOVES — a half nobody can read is not a disclosure, it is a refusal."""
    where = _sibling(tmp_path)
    _pinned(repository, where, _at(where))
    _board(repository, _row("TC-x", SIDECAR, "feat/held", _at(where)))
    lines, code = corroborate(repository, RELEASE, tmp_path)
    assert code == REFUTED
    assert any("FRAMEWORK half" in line for line in lines)


def test_an_UNANSWERABLE_half_makes_the_command_NOT_AUTHORITATIVE_with_its_OWN_sentence(
    repository: Path, tmp_path: Path
) -> None:
    """⛔ Its own sentence, so the row-side populations keep the four they are asserted on."""
    _pin(
        repository,
        [
            {"name": "studyforge", "where": "self", "status": "present", "commit": _at(repository)},
            {"name": SIDECAR, "where": "sibling", "status": "present", "commit": MISSING_OBJECT},
        ],
    )
    _board(repository, _row("TC-x", SIDECAR, RELEASE, "main"))
    lines, code = corroborate(repository, RELEASE, tmp_path)
    assert code == NOT_AUTHORITATIVE
    assert any("A DECLARED cross-repo half has NO reading at all" in line for line in lines)


def test_the_CONTAINER_is_named_as_the_reason_a_sibling_is_unreadable(
    repository: Path, tmp_path: Path, monkeypatch
) -> None:
    """⚠️ Ruling 248(a): the absence belongs to the CONTAINER MOUNT, never to the worktree.

    ⛔ **The pinned image mounts exactly one directory (`FND-03`)**, so a run in there can see
    no component at all — ⭐ and it says so, rather than printing a refusal about a sibling it
    was never able to look at.
    """
    monkeypatch.setenv("STUDYFORGE_DEV_CONTAINER", "1")
    where = _sibling(tmp_path)
    _pinned(repository, where, _at(where))
    _board(repository, _row("TC-x", SIDECAR, RELEASE, _at(where)))
    declaration = read_declaration(repository)
    inside = judge(repository, declaration, RELEASE)
    assert inside.answer is Answer.NOT_ANSWERABLE
    assert "PINNED IMAGE" in "\n".join(inside.lines)
    # ⭐ The control: the SAME tree, with the workspace named, is read to the end.
    assert judge(repository, declaration, RELEASE, tmp_path).answer is Answer.CORROBORATED


# --------------------------------------------------------------------------
# Reading 3 — THIS repository, which is the only place that knows the answer is yes
# --------------------------------------------------------------------------


def test_this_repository_DECLARES_the_block_and_every_entry_DECLARES_BOTH_HALVES() -> None:
    """⛔ The PRESENCE half, `test_bijection.py`'s precedent — ⭐ and it reads the FILE, not git.

    ⚠️ **A committed assertion may not take its population from the host** (Ruling 225), so
    this asserts the declaration's own bytes and never resolves a ref: whether those refs are
    LANDED is `corroborate`'s reading, taken where the components are visible.
    """
    declaration = read_declaration(repository_root())
    assert declaration.state == DECLARED
    assert declaration.entries, "⛔ born vacuous: this board has cross-repo tasks to declare"
    for entry in declaration.entries:
        assert len(entry.halves) == 2, f"{entry.task} declares {len(entry.halves)} half/halves"
        assert entry.component and entry.task
