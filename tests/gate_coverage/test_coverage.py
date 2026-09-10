"""W7's claim and Ruling 67's bound: the assertions this gate exists to make.

⛔ Every reader under `SCAN_ROOT` calls the gate, `GATED_TREES` is total over
the repository, and both are watched passing without their mechanism.

⭐ **Ruling 153 (`W68`): the two *repository-scoped* assertions derive their
population from `git ls-files`, not from the disk.** They ask a question about
**this repository** — every reader in it, and only the trees it names — and
what this repository contains is what git tracks. ⛔ The walk itself is
untouched: `document_readers` still reads a directory, because the negative
controls below plant readers in a `tmp_path` that git has never heard of.
"""

import json
from pathlib import Path

import pytest

from tests.gate_coverage import GATED_TREES, HOME, SCAN_ROOT
from tests.gate_coverage.tell import GATE, _calls, decodes, document_readers
from tests.support import git, init_repository, repository_root, run


def tracked_python_modules(root: Path | None = None) -> list[Path]:
    """Every Python module **git tracks** in `root`, as absolute paths.

    ⛔ **The index, never the disk** (Ruling 153, and Ruling 86a before it for
    ruff's denominator). ⚠️ A `git status --porcelain` clean tree can still
    carry hundreds of ignored `.py` — an agent's own `.scratch/`, a virtualenv,
    a second checkout — and a disk walk reads every one of them as this
    repository's. It is not; it is somebody else's tree sitting inside ours.

    ⚠️ **What this is blind to, said rather than discovered later.** `git
    ls-files` reads the **index**, so a module written and not yet `git add`ed
    is invisible to it — `CTO-36/6`, and the reason a pre-commit R7 check may
    never be a `git grep`. ⭐ **That blindness is correct for the question these
    two tests ask and wrong for the question the *gate* asks.** They ask *"does
    every reader in this repository live in a named, gated tree"* — a claim
    about the repository, whose contents are its tracked contents, and which is
    still true of a file the moment it is added. ⛔ They do **not** ask *"does
    my working tree pass right now"*; that question is `tools.quality`'s, it is
    answered over `git check-ignore` precisely so that a brand-new unadded file
    is caught (`tools/quality/config.py:253`, `FND-06`), and it is a different
    instrument on purpose.

    ⚠️ **A tracked module absent from the working tree is refused, not
    skipped** — an unstaged deletion would otherwise narrow this population by
    one file in silence, and a gate that stops covering something fails
    silently.

    ⭐ **`root` defaults to this repository and is a parameter for one reason:
    Ruling 11.** The mechanism is watched working in a throwaway repository
    below, where a plant can be *tracked* or *ignored* on purpose; without the
    parameter that control could only be written against this repository, which
    means writing into the tree the gate is measuring.
    """
    root = repository_root() if root is None else root
    result = run([git(), "ls-files", "-z", "--", "*.py"], cwd=root)
    assert result.returncode == 0, (
        f"git ls-files could not answer, so this gate has no population: "
        f"{result.stdout + result.stderr}"
    )
    tracked = [root / name for name in result.stdout.split("\0") if name]
    # ⛔ The population guard, in the body and before any caller counts
    # anything: an instrument that cannot find its subject must raise, never
    # report that its subject is clean (`W61`'s reading 3, Ruling 128).
    assert tracked, "git tracks no Python module at all; the population is empty"
    absent = sorted(str(path.relative_to(root)) for path in tracked if not path.is_file())
    assert absent == [], (
        "these modules are tracked but missing from the working tree, so this gate "
        f"cannot read them; restore them or stage the deletion: {absent}"
    )
    return tracked


def tracked_readers(tree: str = "", root: Path | None = None) -> list[Path]:
    """`document_readers`' question, asked of the tracked set under `tree`.

    ⛔ **The fix is here, at the call site, and never inside `document_readers`**
    (Ruling 153, constraint 1). Widening the walk to skip a nested checkout is
    a gate learning to ignore a tree, and `tests/gate_coverage/` exists because
    a gate that stops covering something fails silently.
    """
    where = repository_root() if root is None else root
    within = where / tree
    return sorted(
        path
        for path in tracked_python_modules(where)
        if path.is_relative_to(within) and decodes(path.read_text(encoding="utf-8"))
    )


def test_every_document_reader_calls_the_gate():
    # ⛔ W7. The assertion that makes an ungated reader unrepresentable rather
    # than merely discouraged — and the reason the fix is not "add a call".
    #
    # ⚠️ **This one keeps the disk walk, and the asymmetry with the two
    # repository-scoped tests below is deliberate** (`W68`). It is scoped to
    # `SCAN_ROOT`, a tree this repository owns and where nothing ignored
    # legitimately lives; and for *this* question — "is there an ungated reader
    # here" — seeing a module that has been written and not yet added is the
    # answer arriving one commit earlier, not a contaminated population.
    root = repository_root() / SCAN_ROOT
    offenders = sorted(
        str(path.relative_to(repository_root()))
        for path in document_readers(root)
        if GATE not in _calls(path)
    )
    assert offenders == [], (
        f"these modules decode a document and never gate it (R7, W7): {offenders}"
    )


def test_the_reader_scan_is_not_vacuous():
    # ⭐ Both directions. A scanner that found no readers would pass the test
    # above forever, so this asserts it really does see the module W7 was
    # opened against.
    root = repository_root() / SCAN_ROOT
    found = {str(path.relative_to(root)) for path in document_readers(root)}
    assert "corpus/manifest/document.py" in found
    assert len(found) >= 5, found


def test_the_scan_root_is_the_one_tree_this_gate_covers():
    # ⛔ **Ruling 67, half one.** `SCAN_ROOT` was a literal repeated in three
    # test bodies and justified nowhere; now it is a row of `GATED_TREES`, and
    # it must be *the* row whose gate is the one this file looks for. ⭐ Swapping
    # the root to `tools` — the fix `W26/1` reads as if it wanted — is then not
    # a one-word edit that keeps the suite green: it contradicts this line.
    assert SCAN_ROOT in GATED_TREES
    assert GATED_TREES[SCAN_ROOT] is not None
    assert GATED_TREES[SCAN_ROOT].endswith(f".{GATE}")
    assert (repository_root() / SCAN_ROOT).is_dir()

    # ⛔ And the other two rows are named as *not* this test's to measure: one
    # gated elsewhere, one deliberately ungated.
    assert GATED_TREES["tools"] == "tools.quality.personal_data"
    assert GATED_TREES["tests"] is None
    assert sorted(GATED_TREES) == ["src/studyforge", "tests", "tools"]


def test_no_fourth_tree_of_readers_exists_unnamed():
    # ⛔ **Ruling 67, half two, and the half with teeth.** The bound is not
    # "`src/studyforge` is where we look"; it is "`src/studyforge` is one of
    # exactly three trees that decode anything, and the other two have their own
    # answer". ⚠️ That second clause is about the whole repository, so it is
    # measured over the whole repository — a new package or script directory
    # that decodes arrives as a failure naming itself, not as a silent hole.
    #
    # ⭐ **`CTO-20-2`: state the set — and Ruling 126: state the command that
    # derives it, because a bare count is the half that goes stale.**
    #
    #     tracked_readers()                                # the whole population
    #     {t: len(tracked_readers(t)) for t in GATED_TREES}          # per tree
    #
    # ⛔ **44 at `ad27ed2`, decomposing 11 `src/studyforge` + 3 `tools` + 30
    # `tests`** — ⚠️ ~~*37 at `ddddd05`: 8, 3, 26*~~ and ~~*26: 6, 2, 18*~~
    # before that, which is what this comment said from `W29` until `W40`
    # measured it. It was true at `4f2fbf8` and nobody re-ran it, which is the
    # exact failure Ruling 126 was minted over.
    # ⭐ The assertion below never read the number, so the drift was silent
    # rather than red — the decomposition is checked by
    # `test_every_named_tree_is_populated_so_the_bound_is_not_vacuous`, whose
    # bounds are floors (`>= 5`, `>= 2`) precisely so that growth is not a
    # failure and a *shrink* still is.
    #
    # ⛔ **`W68`: `tracked_readers()`, not `document_readers(repository_root())`.**
    # ⚠️ The disk walk read **88** here in a worktree carrying a second checkout
    # under `.scratch/`, and `git status --porcelain` printed nothing (Ruling
    # 153). ⭐ The two instruments agreed exactly — 44, and 11/3/30 — in a clean
    # checkout of `ad27ed2`, which is the measurement that says this swap
    # de-biased the population rather than narrowing it.
    #
    # ⛔ `W26/1`'s "three" was a count over a set it never stated (ungated
    # readers outside `src/studyforge` that are not test modules); the raw tell
    # finds 33 outside it at this ref, and both are true of different sets.
    root = repository_root()
    homeless = sorted(
        str(path.relative_to(root))
        for path in tracked_readers()
        if not any(path.relative_to(root).is_relative_to(tree) for tree in GATED_TREES)
    )
    assert homeless == [], (
        "these modules decode a document from a tree GATED_TREES does not name; "
        f"name the tree and its R7 gate rather than widening SCAN_ROOT (Ruling 67): {homeless}"
    )


def test_every_named_tree_is_populated_so_the_bound_is_not_vacuous():
    # ⭐ **The control on the control.** Total coverage is cheap if a row is
    # wrong — `""`, or a directory that does not exist, makes the test above
    # pass forever. So every row is a real directory that really holds readers,
    # and the counts are a **decomposition, never a total** (`W22`, Ruling 72).
    #
    # ⛔ **`W68`: over the tracked set, for the reason above the sibling test.**
    # ⚠️ This is the half that went red on the nested checkout — `assert 44 ==
    # 88`, because the *sum* was measured over three trees and the *total* over
    # a disk holding two repositories.
    root = repository_root()
    per_tree = {tree: len(tracked_readers(tree)) for tree in GATED_TREES}
    assert all((root / tree).is_dir() for tree in GATED_TREES), per_tree
    assert all(count > 0 for count in per_tree.values()), per_tree
    assert per_tree["src/studyforge"] >= 5, per_tree
    assert per_tree["tools"] >= 2, per_tree
    assert sum(per_tree.values()) == len(tracked_readers()), per_tree

    # ⛔ **And the population is a real population, both ends** (`W68`). A
    # derived set is only as good as the derivation, and a `tracked_readers`
    # that had quietly stopped filtering — or started filtering the other way —
    # keeps every assertion above true: the counts stay positive, the
    # decomposition still sums, and no tree becomes homeless because every
    # tracked `.py` in this repository already lives in a named tree.
    # ⭐ So: the module W7 was opened against is *in* the set, and the set is a
    # **strict** subset of what git tracks.
    readers = {str(path.relative_to(root)) for path in tracked_readers()}
    assert "src/studyforge/corpus/manifest/document.py" in readers, sorted(readers)
    assert len(readers) < len(tracked_python_modules()), len(readers)


def test_a_fourth_tree_is_caught_rather_than_scanned_past(tmp_path):
    # ⛔ **Ruling 11: watch it pass without the mechanism.** A reader planted in
    # a tree no row names is exactly the shape the bound exists to refuse, and
    # nothing in the real repository is in that shape — so the negative control
    # builds one rather than asserting the absence of one.
    named, unnamed = tmp_path / "src" / "studyforge", tmp_path / "scripts"
    named.mkdir(parents=True)
    unnamed.mkdir()
    source = "import json\n\n\ndef parse(text):\n    return json.loads(text)\n"
    (named / "reader.py").write_text(source, encoding="utf-8")

    def homeless(root: Path) -> list[str]:
        return sorted(
            str(path.relative_to(root))
            for path in document_readers(root)
            if not any(path.relative_to(root).is_relative_to(tree) for tree in GATED_TREES)
        )

    assert homeless(tmp_path) == []
    (unnamed / "reader.py").write_text(source, encoding="utf-8")
    assert homeless(tmp_path) == ["scripts/reader.py"]

    # ⛔ And the wrong remedy does not silence it: pointing `SCAN_ROOT` at the
    # new tree would move the scan, not name the gate. Only a row does that.
    assert "scripts" not in GATED_TREES


def test_the_tracked_population_ignores_a_nested_checkout_and_still_catches_a_plant(tmp_path):
    # ⛔ **`W68`'s mechanism, watched working — Ruling 11, and both halves of
    # Ruling 153 in miniature.** The subject is a throwaway repository, because
    # the alternative is writing into the tree this gate measures.
    #
    # ⭐ **Expected, before the assertions:** the disk sees all three readers;
    # the tracked set sees only the staged one; and the moment the plant in the
    # unnamed tree is **added**, the tracked set sees it and reports it
    # homeless. ⛔ **That last clause is the whole risk of this change** — an
    # instrument that had merely stopped seeing untracked files would read
    # green here while the gate was gone (Ruling 153, constraint 2).
    repository = init_repository(tmp_path / "repository")
    source = "import json\n\n\ndef parse(text):\n    return json.loads(text)\n"

    named = repository / "src" / "studyforge"
    named.mkdir(parents=True)
    (named / "reader.py").write_text(source, encoding="utf-8")
    (repository / ".gitignore").write_text(".scratch/\n", encoding="utf-8")

    # ⚠️ The shape that reproduced this: a second checkout of a repository,
    # under an agent's own ignored scratch directory. `git status --porcelain`
    # says nothing about it, and a disk walk counts it as ours.
    nested = repository / ".scratch" / "trial" / "src" / "studyforge" / "archive"
    nested.mkdir(parents=True)
    (nested / "document.py").write_text(source, encoding="utf-8")

    unnamed = repository / "scripts"
    unnamed.mkdir()
    (unnamed / "reader.py").write_text(source, encoding="utf-8")

    added = run([git(), "add", ".gitignore", "src"], cwd=repository)
    assert added.returncode == 0, added.stdout + added.stderr

    def relative(paths: list[Path]) -> list[str]:
        return sorted(str(path.relative_to(repository)) for path in paths)

    # ⛔ The disk reads three repositories' worth of readers as one.
    assert relative(document_readers(repository)) == [
        ".scratch/trial/src/studyforge/archive/document.py",
        "scripts/reader.py",
        "src/studyforge/reader.py",
    ]
    # ⭐ The tree reads exactly what this repository contains.
    assert relative(tracked_readers(root=repository)) == ["src/studyforge/reader.py"]
    assert relative(tracked_readers("src/studyforge", root=repository)) == [
        "src/studyforge/reader.py"
    ]

    # ⛔ **Constraint 2, in the suite.** Commit the plant into a tree no row
    # names and it must be caught — an untracked plant going quiet is correct,
    # a tracked one going quiet is the gate deleted.
    planted = run([git(), "add", "scripts/reader.py"], cwd=repository)
    assert planted.returncode == 0, planted.stdout + planted.stderr
    assert relative(tracked_readers(root=repository)) == [
        "scripts/reader.py",
        "src/studyforge/reader.py",
    ]
    homeless = [
        name
        for name in relative(tracked_readers(root=repository))
        if not any(Path(name).is_relative_to(tree) for tree in GATED_TREES)
    ]
    assert homeless == ["scripts/reader.py"]

    # ⚠️ And the blindness, asserted rather than described: a reader written
    # and not yet added is invisible here, on purpose, and that is the half a
    # working-tree question would need and this repository question does not.
    (unnamed / "later.py").write_text(source, encoding="utf-8")
    assert "scripts/later.py" not in relative(tracked_readers(root=repository))
    assert "scripts/later.py" in relative(document_readers(repository))


def test_the_reader_scan_catches_a_reader_that_gates_nothing(tmp_path):
    # ⛔ Ruling 11: watch it pass without the mechanism. This is `corpus.json`
    # as it was until W7 — a real reader, correct in every other way.
    ungated = tmp_path / "reader.py"
    ungated.write_text(
        "import json\n\n\ndef parse(text):\n    return json.loads(text)\n",
        encoding="utf-8",
    )
    assert document_readers(tmp_path) == [ungated]
    assert GATE not in _calls(ungated)

    ungated.write_text(
        "import json\n\nfrom studyforge.archive.scrub import assert_clean\n\n\n"
        "def parse(text):\n    document = json.loads(text)\n"
        "    assert_clean(document, 'a document')\n    return document\n",
        encoding="utf-8",
    )
    assert GATE in _calls(ungated)


def test_the_gate_is_seen_however_the_module_reaches_for_it(tmp_path):
    # ⛔ **Found by a mutant surviving, not by reading.** W13 leaves exactly one
    # `assert_clean` to reach for, and a module may reach for it by name or
    # through `scrub`. ⚠️ Every gated module in `src/` uses the bare name
    # today, so nothing in the tree exercises the other half: deleting it from
    # `_calls` kept the whole file green, and a gated reader spelling it
    # `scrub.assert_clean` would then have been filed as an offender.
    reader = tmp_path / "reader.py"
    reader.write_text(
        "import json\n\nfrom studyforge.archive import scrub\n\n\n"
        "def parse(text):\n    document = json.loads(text)\n"
        "    scrub.assert_clean(document, 'a document')\n    return document\n",
        encoding="utf-8",
    )
    assert document_readers(tmp_path) == [reader]
    assert GATE in _calls(reader)


def test_the_manifest_front_door_refuses_a_leak_end_to_end():
    # ⭐ W7's own defect, driven the way `studyforge validate` meets it: a
    # decoded `corpus.json` whose free authored `title` carries a home path.
    #
    # ⛔ **Ruling 58, W27: refused as a `PersonalDataLeak` and NOT as a
    # `ManifestError`.** This test asserted the opposite until W27, and the
    # assertion it made was the fail-open: `ManifestError` exists so a caller
    # walking a corpus catches one type per file and continues, so an R7
    # refusal inside that family is logged as one more manifest that would not
    # read and the walk finishes green. ⭐ `not isinstance` is the load-bearing
    # line: without it this passes on the translating code, because
    # `PersonalDataLeak` and `ManifestError` would both satisfy a bare
    # `pytest.raises(Exception)`.
    from studyforge.archive.scrub import PersonalDataLeak
    from studyforge.corpus.manifest import ManifestError
    from studyforge.corpus.manifest.document import from_document

    manifest = json.loads(
        (repository_root() / "tests/fixtures/depth1/corpus.json").read_text(encoding="utf-8")
    )
    document = dict(manifest, title=f"Notes from {HOME}/corpus")
    with pytest.raises(PersonalDataLeak) as raised:
        from_document(document, "corpus.json")
    assert not isinstance(raised.value, ManifestError)
    assert "home path" in str(raised.value)
    assert "jane" not in str(raised.value)
