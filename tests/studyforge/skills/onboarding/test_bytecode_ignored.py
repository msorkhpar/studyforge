"""End to end: the Python the skills generate ignores its own bytecode.

⭐ **Three clauses, each asserted both ways (R12):**

1. every directory the skills generate that holds Python carries its OWN ignore
   file — a new file inside it, never an edit to the root one (R3);
2. after the generated package is imported and its tests run, `git status`
   shows no bytecode under it — ⚠️ and with those files taken out it does, so
   the first half is not passing on a run that wrote none; and the files ignore
   nothing a person wrote, asked of git over every other file in the tree;
3. a corpus onboarded before them gains them on regeneration, and the generated
   non-destructive check stays green — while still catching a real edit in the
   same state, and a person's own ignore file at one of those paths is refused.

⚠️ The corpus is a fabricated one under pytest's `tmp_path`, driven through the
same steps `test_walkthrough` drives, including its bytecode environment.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path, PurePosixPath

import pytest

from studyforge.corpus.placement import GENERATED_IGNORE_HOME, SITE_CACHE_FILENAME
from studyforge.skills.adapter.scaffold import IGNORE_FILE, bytecode_ignore
from studyforge.skills.onboarding import record
from studyforge.skills.onboarding.nondestructive import EDITS_TEST
from studyforge.skills.onboarding.pin import RECORD_FILE
from studyforge.skills.onboarding.record import OnboardingRefused
from tests.studyforge.skills.onboarding import corpora
from tests.studyforge.skills.onboarding.test_walkthrough import _first_run, _run, _surveyed

#: Every directory whose generated Python leaves bytecode when it runs.
PYTHON_HOMES = ("ingest", "tests", "tests/ingest")


def _git(root: Path, *arguments: str, stdin: str | None = None) -> subprocess.CompletedProcess:
    """Run git in the corpus with no user config, reading rather than asserting."""
    return subprocess.run(
        [shutil.which("git"), "-C", str(root), *arguments],
        input=stdin,
        capture_output=True,
        text=True,
        env={"PATH": os.environ.get("PATH", ""), "HOME": str(root), **corpora.SYNTHETIC_GIT},
        check=False,
    )


def _untracked(root: Path) -> list[str]:
    """Every path `git status` offers, one per file, never collapsed to a directory."""
    status = _git(root, "status", "--porcelain", "--untracked-files=all")
    assert status.returncode == 0, status.stderr
    return [line[3:] for line in status.stdout.splitlines()]


def _bytecode(paths: list[str]) -> list[str]:
    return [where for where in paths if "__pycache__" in where or where.endswith(".pyc")]


def _ignores(made) -> list[str]:
    """Every bytecode ignore file. ⛔ Not the generated root's.

    ⚠️ A corpus carries a second ignore file, at `GENERATED_IGNORE_HOME`,
    written for a different reason by a different writer — it covers the
    discovery cache `studyforge serve` leaves behind. Counting it here would
    make this population wrong in both directions.
    """
    home = GENERATED_IGNORE_HOME.as_posix()
    named = [where for where in made.paths if PurePosixPath(where).name == IGNORE_FILE]
    return [where for where in named if where != home]


# --------------------------------------------------------------------------
# ⛔ Clause 1: one ignore file per generated directory holding Python
# --------------------------------------------------------------------------


def test_every_generated_directory_holding_python_carries_its_own_ignore_file(tmp_path):
    root, made = _first_run(tmp_path)
    homes = {str(PurePosixPath(w).parent) for w in made.paths if w.endswith(".py")}

    assert homes == set(PYTHON_HOMES)
    assert sorted(_ignores(made)) == [f"{home}/{IGNORE_FILE}" for home in sorted(homes)]
    for home in homes:
        text = (root / home / IGNORE_FILE).read_text(encoding="utf-8")
        assert text == bytecode_ignore(), home


def test_it_is_a_new_file_and_never_the_root_ignore_file(tmp_path):
    # ⭐ The other way: no directory without Python gets one, and the root one
    # is neither written nor claimed.
    root, made = _first_run(tmp_path)

    assert not (root / IGNORE_FILE).exists()
    assert IGNORE_FILE not in made.paths
    assert not (root / "src" / IGNORE_FILE).exists()
    # ⚠️ The generated root DOES carry one, for the discovery
    # cache and not for bytecode — so it is checked by what it says, not by
    # being absent, and the bytecode rules are not in it.
    generated = (root / GENERATED_IGNORE_HOME).read_text(encoding="utf-8")
    assert SITE_CACHE_FILENAME in generated.splitlines()
    assert generated != bytecode_ignore()


# --------------------------------------------------------------------------
# ⛔ Clause 2: no bytecode in `git status`, and nothing a person wrote ignored
# --------------------------------------------------------------------------


def test_after_the_package_is_imported_git_status_shows_no_bytecode(tmp_path):
    root, _ = _first_run(tmp_path)
    written = {str(p.relative_to(root).parent.parent) for p in root.rglob("__pycache__/*.pyc")}

    assert written == set(PYTHON_HOMES), "a directory wrote no bytecode, so this reads nothing"
    assert _bytecode(_untracked(root)) == []


def test_without_the_generated_ignore_files_the_same_bytecode_is_offered(tmp_path):
    # ⭐ The control: the run above did write bytecode, and only these files
    # keep it out of `git status`.
    root, made = _first_run(tmp_path)
    for where in _ignores(made):
        (root / where).unlink()

    offered = {str(PurePosixPath(w).parent.parent) for w in _bytecode(_untracked(root))}

    assert offered == set(PYTHON_HOMES)


def test_each_rule_comes_from_the_file_inside_its_own_directory(tmp_path):
    # ⭐ Catalogue entry 15's positive direction: the rule, from that file.
    root, _ = _first_run(tmp_path)
    for home in PYTHON_HOMES:
        cached = sorted((root / home / "__pycache__").glob("*.pyc"))[0]
        seen = _git(root, "check-ignore", "-v", cached.relative_to(root).as_posix())

        assert seen.returncode == 0, home
        assert seen.stdout.startswith(f"{home}/{IGNORE_FILE}:"), seen.stdout


def test_the_ignore_files_ignore_nothing_a_person_wrote(tmp_path):
    # ⛔ Catalogue entry 15's negative direction, over the whole tree: the
    # material, the hand-written module, every generated file, and files a
    # person adds beside the generated modules. `check-ignore` exits 1 when
    # none of what it is asked about is ignored. ⚠️ `.pytest_cache/` is left
    # out: pytest writes it with an ignore file of its own, and nobody wrote it.
    root, made = _first_run(tmp_path)
    (root / "tests/helper.py").write_text("HELPER = 1\n", encoding="utf-8")
    (root / "ingest/NOTES.md").write_text("# notes\n", encoding="utf-8")
    # ⛔ The generated root's file is left out and asked about separately below: it is the
    # framework's own, it hides itself on purpose, and nobody wrote it.
    written = [
        p.relative_to(root).as_posix()
        for p in root.rglob("*")
        if p.is_file() and not {".git", ".pytest_cache", "__pycache__"} & set(p.parts)
    ]
    written = [where for where in written if where != GENERATED_IGNORE_HOME.as_posix()]
    assert made.hand_written[0] in written and "src/01.md" in written

    asked = _git(root, "check-ignore", "--stdin", stdin="\n".join(written))

    assert asked.returncode == 1, f"ignored: {asked.stdout.split()}"
    # ⭐ The control, and the other direction: the one file left out above IS
    # ignored, so the clean answer is a measurement and not an empty question.
    covered = _git(root, "check-ignore", "-q", GENERATED_IGNORE_HOME.as_posix())
    assert covered.returncode == 0


# --------------------------------------------------------------------------
# ⛔ Clause 3: a corpus onboarded without them gains them on regeneration
# --------------------------------------------------------------------------


def _before_w345(tmp_path):
    """A corpus onboarded with no bytecode ignore files, committed.

    ⚠️ Its bytecode is deleted before the commit: committed bytecode is a
    different state, not this one.
    """
    root, made = _first_run(tmp_path)
    for where in _ignores(made):
        (root / where).unlink()
    for cache in list(root.rglob("__pycache__")):
        shutil.rmtree(cache)
    earlier = [item for item in made.files if item.where not in _ignores(made)]
    earlier = [item for item in earlier if item.where != RECORD_FILE]
    (root / RECORD_FILE).write_text(record.render(earlier), encoding="utf-8")
    corpora.git(root, "add", "-A")
    corpora.git(root, "commit", "-q", "-m", "a corpus onboarded without ignore files")
    return root


def _regenerate(root: Path):
    again = _surveyed(root, existing=(root / "corpus.json").read_text(encoding="utf-8"))
    again.write(root, regenerate=True)
    return again


def _generated_check(root: Path) -> subprocess.CompletedProcess:
    return _run(root, "-m", "pytest", EDITS_TEST, "-q", "-p", "no:cacheprovider")


def test_a_corpus_onboarded_before_gains_the_files_on_regeneration(tmp_path):
    root = _before_w345(tmp_path)
    assert not [home for home in PYTHON_HOMES if (root / home / IGNORE_FILE).exists()]
    manifest = (root / "corpus.json").read_bytes()

    again = _regenerate(root)

    assert (root / "corpus.json").read_bytes() == manifest, "the regenerate moved a glob"

    for home in PYTHON_HOMES:
        assert (root / home / IGNORE_FILE).read_text(encoding="utf-8") == bytecode_ignore()
    listed = {entry["where"] for entry in json.loads((root / RECORD_FILE).read_text())["files"]}
    assert set(_ignores(again)) <= listed
    assert _bytecode(_untracked(root)) == []


def test_and_the_generated_non_destructive_check_does_not_read_them_as_an_edit(tmp_path):
    root = _before_w345(tmp_path)
    _regenerate(root)

    unstaged = _generated_check(root)
    corpora.git(root, "add", "-A")
    staged = _generated_check(root)

    assert unstaged.returncode == 0, unstaged.stdout
    assert staged.returncode == 0, staged.stdout
    assert list((root / "tests/__pycache__").glob("*.pyc")), "the check wrote no bytecode"
    assert _bytecode(_untracked(root)) == []


def test_while_the_same_check_still_catches_a_real_edit_in_that_state(tmp_path):
    # ⭐ The control: the green above is not a check that reads nothing.
    root = _before_w345(tmp_path)
    _regenerate(root)
    (root / "src/01.md").write_text("# First\n\nRewritten.\n", encoding="utf-8")

    caught = _generated_check(root)

    assert caught.returncode != 0
    assert "src/01.md" in caught.stdout


def test_a_persons_ignore_file_at_one_of_those_paths_is_refused_and_nothing_written(tmp_path):
    root = _before_w345(tmp_path)
    (root / "tests" / IGNORE_FILE).write_text("scratch/\n", encoding="utf-8")
    before = {p: p.read_bytes() for p in root.rglob("*") if p.is_file() and ".git" not in p.parts}

    with pytest.raises(OnboardingRefused) as refused:
        _regenerate(root)

    assert f"['tests/{IGNORE_FILE}']" in str(refused.value)
    after = {p: p.read_bytes() for p in root.rglob("*") if p.is_file() and ".git" not in p.parts}
    assert after == before
