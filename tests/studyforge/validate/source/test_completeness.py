"""Mirror of `src/studyforge/validate/source/completeness.py` (R12).

⭐ **This is the module SF-25 exists for.** Every other check compares the
archive against itself; a digest taken over the blocks and compared against the
blocks answers *"was this corrupted after we wrote it?"* and can never answer
*"did the adapter read everything?"*.

⚠️ The heading count on one side of this comparison comes from a regex in
`validate.headings` and on the other from the adapter's parser. ⛔ If it ever
comes from the same reader twice, the check is dead and the suite will not say
so — which is why `test_no_module_in_this_package_reaches_for_the_markdown_reader`
exists, in `test_init.py`, over every module of the package rather than one.

⚠️ **The `count_headings` rows below assert a PREMISE rather than this
module's own code** (`docs/conventions/module-structure.md`, *a test may assert
the premise of the bug it prevents*): `check_completeness` is only a real check
while the count is fence-aware and parser-independent, so the rows that hold
that live beside the check that rests on them. ⛔ They import from
`validate.headings`, which owns the function — never from this package, which
merely used to re-export it by accident of one import line.
"""

import json

import pytest

from studyforge.corpus.container import ContainerError
from studyforge.validate import validate
from studyforge.validate.headings import count_headings
from tests.studyforge.validate import corpora

# --------------------------------------------------------------------------
# counting a structural feature the parser did not produce
# --------------------------------------------------------------------------


def test_atx_headings_are_counted():
    assert count_headings("# One\n\ntext\n\n## Two\n### Three\n") == 3


def test_a_hash_inside_a_fence_is_a_comment_and_not_a_heading():
    # ⚠️ **Fence awareness is not decoration.** A `#` at the start of a line
    # inside a fence is a comment in Python, Ruby, shell and YAML; counting
    # those would make this check fire on correct output, and a check that
    # fires on correct output is a check somebody turns off.
    assert count_headings("# One\n\n```python\n# not a heading\n# nor this\n```\n") == 1


def test_a_tilde_fence_closes_only_on_a_tilde_fence():
    assert count_headings("~~~\n# no\n```\n# still no\n~~~\n# yes\n") == 1


def test_an_unclosed_fence_swallows_the_rest_of_the_file():
    # ⚠️ Recorded rather than "fixed": an unclosed fence is a malformed source
    # and guessing where it ends would invent a count. Undercounting produces
    # a *finding*, which is the safe direction — the check errs towards saying
    # "look at this file".
    assert count_headings("# One\n\n```\n# two\n# three\n") == 1


def test_up_to_three_spaces_of_indent_is_still_a_heading():
    assert count_headings("   # yes\n    # no, that is code\n") == 1


def test_a_hash_that_starts_no_heading_is_not_counted():
    assert count_headings("#no-space\n#\n# yes\n") == 2


def test_seven_hashes_is_not_a_heading():
    assert count_headings("####### no\n###### yes\n") == 1


# --------------------------------------------------------------------------
# the check, end to end
# --------------------------------------------------------------------------


def test_a_source_and_an_archive_that_agree_are_clean(tmp_path):
    report = validate(corpora.one_unit(tmp_path / "c", source=corpora.SOURCE))
    assert report.findings == ()
    assert "short-read" not in {u.rule for u in report.unchecked}


def test_a_heading_in_the_source_and_not_in_the_archive_is_a_short_read(tmp_path):
    root = corpora.one_unit(tmp_path / "c", source=corpora.SOURCE + "\n### Three\n\nSkipped.\n")
    report = validate(root)
    assert report.rules == ("short-read",)
    assert "the digest cannot see this" in report.findings[0].message.lower()


def test_the_message_names_both_counts(tmp_path):
    root = corpora.one_unit(tmp_path / "c", source=corpora.SOURCE + "\n### Three\n")
    message = validate(root).findings[0].message
    assert "3 heading line(s)" in message
    assert "2 heading block(s)" in message


# --------------------------------------------------------------------------
# ⛔ where the source is, and what happens when it is not there
# --------------------------------------------------------------------------


def test_an_absent_source_tree_is_unchecked_rather_than_failed(tmp_path):
    # ⭐ An archive is a shippable artifact on its own, and `validate` is the
    # adapter's definition of done for *the archive* (R2). What it may not do
    # is pretend it checked.
    report = validate(corpora.one_unit(tmp_path / "c"))
    assert report.findings == ()
    assert "short-read" in {u.rule for u in report.unchecked}


def test_a_half_present_source_tree_is_a_failure_and_not_a_discount(tmp_path):
    # ⛔ **All or nothing.** A per-file skip would excuse precisely the file
    # that went missing, which is where a short read hides.
    root = corpora.write(
        tmp_path / "c",
        containers={
            "demo": corpora.container(
                [
                    corpora.unit_entry(1, origin="src/one.md"),
                    corpora.unit_entry(2, origin="src/two.md"),
                ]
            )
        },
        documents={
            f"demo/raw/prose/unit-0{n}/lesson-1.json": {
                "source": "demo",
                "address": ["demo"],
                "variant": "prose",
                "unit": n,
                "kind": "lesson",
                "ordinal": 1,
                "ingested": "2026-01-05",
                "title": f"Unit {n}",
                "blocks": corpora.BLOCKS,
            }
            for n in (1, 2)
        },
        sources={"src/one.md": corpora.SOURCE},
    )
    assert "origin-missing" in validate(root).rules


# --------------------------------------------------------------------------
# ⛔ `W255` — "the source tree is absent" is CHECKED against the tree
# --------------------------------------------------------------------------

#: A unit origin that names no file, beside a source that is present.
MISSING = "src/missing.md"


def missing_origins(root, *, units=(1,), sources=None, manifest=None):
    """An archive whose every unit origin names no file, beside `sources`."""
    return corpora.write(
        root,
        manifest=manifest,
        containers={
            "demo": corpora.container(
                [corpora.unit_entry(n, origin=f"src/missing-{n}.md") for n in units]
            )
        },
        documents={
            f"demo/raw/prose/unit-0{n}/lesson-1.json": {
                "source": "demo",
                "address": ["demo"],
                "variant": "prose",
                "unit": n,
                "kind": "lesson",
                "ordinal": 1,
                "ingested": "2026-01-05",
                "title": f"Unit {n}",
                "blocks": corpora.BLOCKS,
            }
            for n in units
        },
        sources=sources,
    )


def test_a_ONE_unit_archive_whose_origin_is_missing_BESIDE_a_present_source_is_RED(tmp_path):
    # ⛔ Clause 4, the RED direction: ISO round 9's surviving plant, built for the test.
    root = corpora.one_unit(tmp_path / "c", origin=MISSING)
    (root / "src").mkdir()
    (root / "src" / "one.md").write_text(corpora.SOURCE, encoding="utf-8")
    report = validate(root)
    assert report.rules == ("origin-missing",)
    assert [finding.where for finding in report.findings] == ["demo/unit-01"]
    assert report.exit_code == 1
    assert "short-read" not in {u.rule for u in report.unchecked}


def test_the_SAME_one_unit_archive_ALONE_is_unchecked_and_exits_0(tmp_path):
    # ⭐ Clause 4's other direction, and clause 3: no source beside it stays `Unchecked` (R2).
    report = validate(corpora.one_unit(tmp_path / "c", origin=MISSING))
    assert report.findings == ()
    assert report.exit_code == 0
    [absent] = [u for u in report.unchecked if u.rule == "short-read"]
    assert "the manifest's 'content' declares" in absent.why


def test_EVERY_origin_missing_beside_a_present_source_names_EACH_unit(tmp_path):
    # ⛔ Clause 2: one finding per unit, not one for the corpus.
    root = missing_origins(tmp_path / "c", units=(1, 2), sources={"src/one.md": corpora.SOURCE})
    report = validate(root)
    assert report.rules == ("origin-missing",)
    assert sorted(finding.where for finding in report.findings) == ["demo/unit-01", "demo/unit-02"]
    assert "declares as source" in report.findings[0].message


def test_a_file_the_manifest_does_NOT_declare_as_source_is_not_a_present_source(tmp_path):
    # ⛔ Clause 1: presence is the manifest's declaration read against the disk. A file
    # where the origins point that `content` does not declare is not the source.
    root = missing_origins(tmp_path / "c", sources={"src/notes.txt": "not prose\n"})
    report = validate(root)
    assert "origin-missing" not in report.rules
    assert "short-read" in {u.rule for u in report.unchecked}


def test_a_ROOT_level_origin_missing_beside_a_root_level_source_is_RED(tmp_path):
    # ⭐ A root origin points at the root's own files (ISO's `TestCases.md` shape).
    manifest = {**corpora.MANIFEST, "content": {"include": ["*.md"]}}
    root = corpora.one_unit(tmp_path / "c", origin="missing.md")
    (root / "corpus.json").write_text(json.dumps(manifest), encoding="utf-8")
    (root / "present.md").write_text(corpora.SOURCE, encoding="utf-8")
    assert validate(root).rules == ("origin-missing",)


def test_DECLARED_an_origin_whose_top_directory_is_ABSENT_reads_the_tree_as_absent(tmp_path):
    # ⚠️ Ruling 292: declared, not decided. FND-04's invalid fixtures declare `*.md` over
    # their own `VIOLATION.md` beside origins under an absent directory, and stay one rule.
    manifest = {**corpora.MANIFEST, "content": {"include": ["*.md"]}}
    root = missing_origins(tmp_path / "c", manifest=manifest, sources={"NOTE.md": "# Note\n"})
    report = validate(root)
    assert "origin-missing" not in report.rules
    assert "short-read" in {u.rule for u in report.unchecked}


def test_an_EXCLUDED_file_on_disk_is_a_present_source(tmp_path):
    # ⭐ Withheld prose is still the source on disk: a whole-series aggregate alone reads RED.
    manifest = {
        **corpora.MANIFEST,
        "content": {
            "include": ["src/*.md"],
            "exclude": [{"path": "src/whole.md", "why": "an aggregate, built for the test"}],
        },
    }
    root = missing_origins(
        tmp_path / "c", manifest=manifest, sources={"src/whole.md": corpora.SOURCE}
    )
    assert validate(root).rules == ("origin-missing",)


def test_a_NESTED_source_directory_is_read(tmp_path):
    # ⭐ The walk descends: a glob reaching a subdirectory finds its file.
    manifest = {**corpora.MANIFEST, "content": {"include": ["src/**/*.md"]}}
    root = missing_origins(
        tmp_path / "c", manifest=manifest, sources={"src/part/one.md": corpora.SOURCE}
    )
    assert validate(root).rules == ("origin-missing",)


# --------------------------------------------------------------------------
# ⛔ SF-36 / Ruling 92 — a unit may be a REGION of a file
# --------------------------------------------------------------------------

#: One file, two units, and a heading each unit does not own. ⚠️ Four headings
#: in the file; two in the first region and one in the second.
SHARED = "# Test cases\n\n## 1. One\n\n### 1.1 Deeper\n\nProse.\n\n## 2. Two\n\nProse.\n"

REGION_BLOCKS = {
    1: [
        {"type": "heading", "level": 2, "text": "1. One"},
        {"type": "heading", "level": 3, "text": "1.1 Deeper"},
        {"type": "para", "text": "Prose."},
    ],
    2: [
        {"type": "heading", "level": 2, "text": "2. Two"},
        {"type": "para", "text": "Prose."},
    ],
}


def shared_file(tmp_path, *, first_origin=None, second_origin=None, source=SHARED):
    """Two units of one file, each declaring its own region by default."""
    origins = {
        1: first_origin or {"path": "src/shared.md", "section": "1. One"},
        2: second_origin or {"path": "src/shared.md", "section": "2. Two"},
    }
    return corpora.write(
        tmp_path,
        containers={
            "demo": corpora.container(
                [corpora.unit_entry(n, origin=origins[n]) for n in (1, 2)],
                container_api=2,
            )
        },
        documents={
            f"demo/raw/prose/unit-0{n}/lesson-1.json": {
                "source": "demo",
                "address": ["demo"],
                "variant": "prose",
                "unit": n,
                "kind": "lesson",
                "ordinal": 1,
                "ingested": "2026-01-05",
                "title": f"Unit {n}",
                "blocks": REGION_BLOCKS[n],
            }
            for n in (1, 2)
        },
        sources={"src/shared.md": source},
    )


def test_units_sharing_one_file_are_compared_against_their_own_regions(tmp_path):
    # ⭐ **`F21`, in two units instead of seventeen.** Each region is counted
    # on its own — 2 and 1 — and neither against the file's 4.
    report = validate(shared_file(tmp_path / "c"))
    assert report.findings == ()
    assert "short-read" not in {u.rule for u in report.unchecked}


def test_the_same_corpus_short_reads_when_the_units_name_the_whole_file(tmp_path):
    # ⛔ **The negative control for the row above, and it is the defect
    # itself**: with `origin` a plain path both units are compared against all
    # four headings, and both report a short read against 2 and 1.
    root = shared_file(tmp_path / "c", first_origin="src/shared.md", second_origin="src/shared.md")
    report = validate(root)
    assert report.rules == ("short-read",)
    assert len(report.findings) == 2


def test_a_region_ends_at_the_next_heading_of_the_same_or_shallower_depth(tmp_path):
    # ⛔ The clause, end to end. Unit 1's region holds `1.1 Deeper` and stops
    # at `2. Two`; a bound at the next heading of *any* depth would count 1
    # and report a short read against the archive's 2.
    assert validate(shared_file(tmp_path / "c")).findings == ()


def test_a_section_the_file_does_not_carry_is_its_own_finding(tmp_path):
    root = shared_file(
        tmp_path / "c", first_origin={"path": "src/shared.md", "section": "1. Renamed"}
    )
    report = validate(root)
    assert report.rules == ("origin-section-missing",)
    assert "exact text" in report.findings[0].message


def test_a_section_the_file_carries_twice_is_its_own_finding(tmp_path):
    root = shared_file(tmp_path / "c", source=SHARED + "\n## 1. One\n\nAgain.\n")
    report = validate(root)
    assert "origin-section-ambiguous" in report.rules
    assert "2 times" in report.findings[0].message


def test_an_ambiguous_section_is_refused_rather_than_resolved(tmp_path):
    # ⚠️ Taking the first match would leave the other unit reading a region
    # that begins somewhere else, with nothing reporting it.
    root = shared_file(tmp_path / "c", source=SHARED + "\n## 1. One\n\nAgain.\n")
    assert "short-read" not in validate(root).rules


def test_a_finding_about_a_section_never_reproduces_it(tmp_path):
    # ⛔ R7's rule as this package keeps it: a declared field is read out of a
    # file somebody else wrote, so a refusal names the field and not the value.
    root = shared_file(
        tmp_path / "c", first_origin={"path": "src/shared.md", "section": "1. Renamed"}
    )
    assert "1. Renamed" not in validate(root).findings[0].message


def test_a_region_still_names_a_file_that_must_be_on_disk(tmp_path):
    root = shared_file(tmp_path / "c", first_origin={"path": "src/missing.md", "section": "1. One"})
    assert "origin-missing" in validate(root).rules


def test_a_fragment_origin_is_refused_where_the_map_is_read(tmp_path):
    # ⛔ Ruling 92: `TestCases.md#…` was accepted and meant nothing. It is now
    # refused by `studyforge.sourcepath`, before any check runs.
    with pytest.raises(ContainerError) as raised:
        shared_file(tmp_path / "c", first_origin="src/shared.md#1. One")
    assert "fragment" in str(raised.value)
