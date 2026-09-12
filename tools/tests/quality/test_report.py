"""Mirror of `tools/quality/report.py` (R12)."""

from __future__ import annotations

from pathlib import Path

from tools.quality.report import (
    DISK_WALK,
    TRACKED_WALK,
    WALK_CAVEAT,
    DocumentPopulation,
    Finding,
    format_findings,
)


def test_a_finding_renders_where_an_editor_can_jump_to_it():
    finding = Finding(path="src/studyforge/x.py", line=12, rule="size", message="too long.")
    assert str(finding) == "src/studyforge/x.py:12: [size] too long."


def test_clean_says_so_rather_than_saying_nothing():
    # A checker that prints nothing on success is a checker nobody can tell
    # apart from one that failed to run.
    assert format_findings([]) == "quality floor: clean"


def test_findings_are_sorted_so_the_report_is_the_same_everywhere():
    later = Finding(path="src/studyforge/z.py", line=1, rule="size", message="a.")
    earlier = Finding(path="src/studyforge/a.py", line=9, rule="size", message="b.")
    report = format_findings([later, earlier])
    assert report.splitlines()[0].startswith("src/studyforge/a.py")
    assert report.splitlines()[1].startswith("src/studyforge/z.py")


def test_the_count_is_pluralised_honestly():
    one = Finding(path="a.py", line=1, rule="size", message="x.")
    assert format_findings([one]).endswith("quality floor: 1 finding")
    two = Finding(path="b.py", line=1, rule="size", message="x.")
    assert format_findings([one, two]).endswith("quality floor: 2 findings")


# --- W148: what a NOTICE's denominator says about itself --------------------


def test_the_two_walks_are_the_only_two_and_each_has_a_caveat_entry():
    # ⛔ Two NAMED walks and never a boolean: a reader of a figure must not have
    # to infer that the disk answer is the fallback one.
    assert set(WALK_CAVEAT) == {TRACKED_WALK, DISK_WALK}


def test_only_the_disk_walk_carries_a_caveat():
    # ⭐ Ruling 216's third answer wearing a sentence: git failing to answer
    # neither falls through in silence nor fails the build — it SAYS so.
    assert WALK_CAVEAT[TRACKED_WALK] == ""
    caveat = WALK_CAVEAT[DISK_WALK]
    assert "DISK" in caveat
    assert "not reproducible from another checkout" in caveat


def test_a_population_carries_its_paths_and_the_walk_that_found_them():
    population = DocumentPopulation((Path("a.md"),), TRACKED_WALK)
    assert population.paths == (Path("a.md"),)
    assert population.walk == TRACKED_WALK
