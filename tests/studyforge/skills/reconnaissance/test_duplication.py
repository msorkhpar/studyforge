"""The same material twice — as a whole file, and as a region of one."""

from __future__ import annotations

from studyforge.skills.reconnaissance import take
from studyforge.skills.reconnaissance.duplication import (
    aggregates,
    headings_of,
    observe,
    structural,
)
from studyforge.skills.reconnaissance.report import Uncertainty
from tests.studyforge.skills.reconnaissance import sources


def questions(root):
    return [i for i in observe(take(root)) if isinstance(i, Uncertainty)]


def test_a_whole_series_aggregate_is_found_and_named(tmp_path):
    # ⭐ **Trap 2.** Measured: three aggregates, exact ordered concatenations,
    # 50.2% of one corpus's lines. A glob ingests everything twice and nothing
    # fails; narration then synthesises the whole corpus twice.
    found = aggregates(take(sources.aggregated(tmp_path / "c")))
    assert [a.path for a in found] == ["src/Whole.md"]
    assert found[0].covers == ("src/1.md", "src/2.md", "src/3.md")


def test_the_claim_is_ordered_concatenation_not_similarity(tmp_path):
    # ⛔ Asserted by digest. "Contains the same words" is a much weaker claim
    # and not one a person can act on.
    root = sources.aggregated(tmp_path / "c")
    whole = root / "src/Whole.md"
    whole.write_text(whole.read_text(encoding="utf-8") + "\nAn extra line.\n", encoding="utf-8")
    assert aggregates(take(root)) == []


def test_a_corpus_with_no_duplication_reports_none(tmp_path):
    assert aggregates(take(sources.flat_prose(tmp_path / "c"))) == []
    assert structural(take(sources.flat_prose(tmp_path / "c"))) == []


def test_a_region_reproducing_another_heading_tree_is_found(tmp_path):
    # ⛔ **The half a whole-file digest cannot see.** Measured: 361 headings,
    # digest-identical, 53.7% of the curriculum document — and no file
    # duplicates a file.
    found = structural(take(sources.copied_heading_tree(tmp_path / "c")))
    assert any(item.path == "README.md" and item.reproduces == "TestCases.md" for item in found)


def test_the_copied_document_is_reported_even_though_it_cannot_be_excluded(tmp_path):
    # ⚠️ It is the only record of the corpus's addresses, titles and ordinals,
    # so the answer is a region rather than an exclusion — and a report saying
    # "no duplication found" would be wrong in a way its reader acts on (R6).
    asked = questions(sources.copied_heading_tree(tmp_path / "c"))
    assert any("really about this corpus" in q.question for q in asked)
    assert any("region, not an exclusion" in q.settles_it for q in asked)


def test_excluding_an_aggregate_is_flagged_as_losing_an_attestation(tmp_path):
    # ⭐ The limit worth knowing: deduplication removes the copy **and the
    # attestation the copy constituted** — here, an independent recording of
    # the reading order, which is the one thing nothing else verifies.
    asked = questions(sources.aggregated(tmp_path / "c"))
    assert any("before excluding it" in q.settles_it for q in asked)


def test_a_hash_inside_a_fence_is_not_a_heading():
    # ⚠️ A `#` at the start of a line inside a fence is a comment in half the
    # languages real material quotes; counting it reports duplication that is
    # not there.
    assert headings_of("# One\n\n```python\n# not a heading\n```\n## Two\n") == ["1:One", "2:Two"]
