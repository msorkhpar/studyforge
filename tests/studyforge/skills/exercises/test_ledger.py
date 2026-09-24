"""Mirror of `src/studyforge/skills/exercises/ledger.py` (R12) — the planning pass's first half.

**What it asserts.** That every fenced example and every test file a source
carries is in the ledger, that the gate-facing view is the `Mapping[str, str]`
`G5` already consumes, and that two readings of an unchanged corpus agree (R10).

⭐ **The population claim is read on a REAL fixture corpus**,
`tests/fixtures/runnable/`, and the count it is compared against is derived by
an instrument of the tests' own — counting fence openers line by line — rather
than typed in. ⛔ A number typed here would agree with the ledger by
construction the first time and go stale on the next fixture edit.

**Depends on.** The module under test, and `pages` for the fixtures. ⛔ Nothing
from `validate`: the scan borrows that module's two patterns and these files
must be able to disagree with the result.
"""

from __future__ import annotations

import pytest

from studyforge.skills.exercises.ledger import (
    ENTRY_KINDS,
    EXAMPLE,
    TESTS,
    Entry,
    LedgerError,
    digests,
    key_of,
    take,
)
from tests.studyforge.skills.exercises.pages import PAGE, fence_openers, fixture_corpus, written


def test_every_fenced_example_and_test_file_in_a_fixture_corpus_is_in_the_ledger():
    root = fixture_corpus()
    material = sorted(str(path.relative_to(root)) for path in (root / "kata").glob("*.md"))
    graders = sorted(
        str(path.relative_to(root)) for path in (root / "practice").rglob("check_*.py")
    )
    assert material and graders, "the fixture corpus carries neither material nor graders"
    ledger = take(root, material, graders, "the ledger")
    expected = sum(fence_openers((root / path).read_text(encoding="utf-8")) for path in material)
    assert expected > 0, "the fixture corpus carries no fence, so this claim is vacuous"
    examples = [entry for entry in ledger.entries if entry.kind == EXAMPLE]
    graded = [entry for entry in ledger.entries if entry.kind == TESTS]
    assert len(examples) == expected, "the ledger and an independent count disagree"
    assert sorted(entry.path for entry in graded) == graders, "a test file is missing"
    assert {entry.kind for entry in ledger.entries} <= set(ENTRY_KINDS)


def test_every_file_the_ledger_read_is_recorded_with_its_digest():
    root = fixture_corpus()
    material = sorted(str(path.relative_to(root)) for path in (root / "kata").glob("*.md"))
    ledger = take(root, material, (), "the ledger")
    assert sorted(source.path for source in ledger.sources) == material
    assert all(source.digest.startswith("sha256:") for source in ledger.sources)


def test_the_gate_facing_view_is_one_digest_per_file_keyed_by_path(tmp_path):
    """⛔ `G5` asks `ledger.get(origin.path)` and nothing else — the shape is landed."""
    page = written(tmp_path, "guide.md", PAGE)
    ledger = take(tmp_path, (page,), (), "the ledger")
    answer = digests(ledger)
    assert set(answer) == {page}, "the mapping is keyed by path, one entry per file read"
    assert answer[page].startswith("sha256:"), "the digest names its algorithm"
    assert all(isinstance(value, str) for value in answer.values())


def test_an_examples_digest_is_its_own_bytes_and_not_the_files(tmp_path):
    """⭐ What lets a re-run say WHICH example moved, rather than only which file did."""
    page = written(tmp_path, "guide.md", PAGE)
    ledger = take(tmp_path, (page,), (), "the ledger")
    examples = [entry for entry in ledger.entries if entry.kind == EXAMPLE]
    assert len({entry.digest for entry in examples}) > 1, "two different examples digest alike"
    assert all(entry.digest != digests(ledger)[page] for entry in examples)


def test_a_test_file_is_one_entry_and_its_digest_is_the_files_own(tmp_path):
    grader = written(tmp_path, "check_it.py", "def test_x():\n    assert True\n")
    ledger = take(tmp_path, (), (grader,), "the ledger")
    assert [entry.kind for entry in ledger.entries] == [TESTS]
    assert ledger.entries[0].digest == digests(ledger)[grader], "a test file is carried whole"
    assert ledger.entries[0].ordinal == 0, "a test file has no position inside itself"
    assert ledger.entries[0].sections == (), "a test file is not scanned for headings"


def test_key_of_tells_an_example_from_a_test_file_in_the_same_file():
    example = Entry(EXAMPLE, "a/b.md", 2, (), None, "sha256:0")
    grader = Entry(TESTS, "a/b.md", 0, (), None, "sha256:0")
    assert key_of(example) == "example:a/b.md:2"
    assert key_of(grader) == "tests:a/b.md"
    assert key_of(example) != key_of(grader)


def test_a_file_declared_both_material_and_a_test_is_refused(tmp_path):
    page = written(tmp_path, "guide.md", PAGE)
    with pytest.raises(LedgerError) as refusal:
        take(tmp_path, (page,), (page,), "the ledger")
    assert "both material and a test" in str(refusal.value)


def test_a_declared_file_that_is_not_there_is_refused(tmp_path):
    with pytest.raises(LedgerError) as refusal:
        take(tmp_path, ("absent.md",), (), "the ledger")
    assert "absent.md" in str(refusal.value)
    assert str(tmp_path) not in str(refusal.value), "the refusal names the file, not the machine"


def test_a_file_that_is_not_utf8_text_is_refused_by_name(tmp_path):
    (tmp_path / "binary.md").write_bytes(b"\xff\xfe not text at all")
    with pytest.raises(LedgerError) as refusal:
        take(tmp_path, ("binary.md",), (), "the ledger")
    assert "not UTF-8 text" in str(refusal.value)


def test_a_path_that_is_not_inside_the_source_is_refused(tmp_path):
    for bad in ("/etc/passwd", "../outside.md", "page.md#anchor", "D:/material/page.md"):
        with pytest.raises(LedgerError) as refusal:
            take(tmp_path, (bad,), (), "the ledger")
        assert bad not in str(refusal.value), "the value is not reproduced (R7)"
    for bad in (None, 7, b"page.md"):
        with pytest.raises(LedgerError):
            take(tmp_path, (bad,), (), "the ledger")


def test_an_unclosed_fence_is_refused_rather_than_guessed_at(tmp_path):
    body = "a line only this file carries"
    page = written(tmp_path, "open.md", f"# Open\n\n```py\n{body}\n")
    with pytest.raises(LedgerError) as refusal:
        take(tmp_path, (page,), (), "the ledger")
    assert body not in str(refusal.value), "the file's contents are not reproduced (R7)"
    assert "never closes it" in str(refusal.value)
    assert page in str(refusal.value), "the refusal names the file"


def test_the_entries_are_ordered_by_file_then_position_whatever_order_was_handed_in(tmp_path):
    """⛔ R10: the caller's iteration order is part of what must not matter."""
    first = written(tmp_path, "a-guide.md", PAGE)
    second = written(tmp_path, "b-guide.md", PAGE)
    grader = written(tmp_path, "check_it.py", "def test_x():\n    assert True\n")
    forwards = take(tmp_path, (first, second), (grader,), "the ledger")
    backwards = take(tmp_path, [second, first], [grader], "the ledger")
    assert forwards == backwards, "two readings of one unchanged corpus disagree"
    placed = [(entry.path, entry.ordinal) for entry in forwards.entries]
    assert placed == sorted(placed), "the entries are not in the order the files are"
    assert [source.path for source in forwards.sources] == [first, second, grader]


def test_a_material_file_that_is_also_read_for_its_headings_records_them(tmp_path):
    page = written(tmp_path, "guide.md", PAGE)
    ledger = take(tmp_path, (page,), (), "the ledger")
    assert ledger.sources[0].sections == ("Adding up", "Edge cases", "Elsewhere")
