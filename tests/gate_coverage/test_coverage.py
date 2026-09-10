"""W7's claim and Ruling 67's bound: the assertions this gate exists to make.

⛔ Every reader under `SCAN_ROOT` calls the gate, `GATED_TREES` is total over
the repository, and both are watched passing without their mechanism.
"""

import json
from pathlib import Path

import pytest

from tests.gate_coverage import GATED_TREES, HOME, SCAN_ROOT
from tests.gate_coverage.tell import GATE, _calls, document_readers
from tests.support import repository_root


def test_every_document_reader_calls_the_gate():
    # ⛔ W7. The assertion that makes an ungated reader unrepresentable rather
    # than merely discouraged — and the reason the fix is not "add a call".
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
    #     document_readers(repository_root())            # the whole population
    #     {t: len(document_readers(root / t)) for t in GATED_TREES}   # per tree
    #
    # ⛔ **37 at `ddddd05`, decomposing 8 `src/studyforge` + 3 `tools` + 26
    # `tests`** — ⚠️ ~~*26: 6, 2, 18*~~, which is what this comment said from
    # `W29` until `W40` measured it. It was true at `4f2fbf8` and nobody
    # re-ran it, which is the exact failure Ruling 126 was minted over.
    # ⭐ The assertion below never read the number, so the drift was silent
    # rather than red — the decomposition is checked by
    # `test_every_named_tree_is_populated_so_the_bound_is_not_vacuous`, whose
    # bounds are floors (`>= 5`, `>= 2`) precisely so that growth is not a
    # failure and a *shrink* still is.
    #
    # ⛔ `W26/1`'s "three" was a count over a set it never stated (ungated
    # readers outside `src/studyforge` that are not test modules); the raw tell
    # finds 29 outside it at this ref, and both are true of different sets.
    root = repository_root()
    homeless = sorted(
        str(path.relative_to(root))
        for path in document_readers(root)
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
    root = repository_root()
    per_tree = {tree: len(document_readers(root / tree)) for tree in GATED_TREES}
    assert all((root / tree).is_dir() for tree in GATED_TREES), per_tree
    assert all(count > 0 for count in per_tree.values()), per_tree
    assert per_tree["src/studyforge"] >= 5, per_tree
    assert per_tree["tools"] >= 2, per_tree
    assert sum(per_tree.values()) == len(document_readers(root)), per_tree


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
