"""Mirror of `tools/quality/collisions.py` (R12).

⛔ **Every arm is asserted in both directions, and the IMPOSSIBLE control is
inhabited rather than waived** (Rulings 123, 191). The live tree's inbound
population is EMPTY — measured `0` at `94ad941` — so the finding arm's subject
is SYNTHESISED here by planting, and the plant owes its own positive row:
without it, an instrument stuck on *"nothing is ever an inbound link"* returns
the refusing control's reading for free.

⚠️ **And the fold is asserted from both sides.** `heading_slugs` MUST keep
absorbing duplicates — its callers ask a set question — while `heading_bases`
MUST keep them. A test that only checked the new function would pass over a
change that quietly made the old one report collisions it was never asked for.
"""

from __future__ import annotations

from tests.support import git, init_repository, repository_root, run
from tools.quality.collisions import (
    RULE_COLLISION,
    check_anchor_collisions,
    colliding_names,
    collision_census,
    scan,
)
from tools.quality.pointers import check_pointers, heading_bases, heading_slugs
from tools.quality.report import DISK_WALK, TRACKED_WALK

#: ⛔ The archive's own shape, reduced to four lines: a house template gives
#: every row the same section name, and the close copies it in. This is the
#: real mechanism, not a lookalike — the collision is between two rows.
TEMPLATE = "# W1\n\n## What settles it\n\n# W2\n\n## What settles it\n"


def write(tmp_path, name: str, text: str):
    """Write a document into a temporary tree and return its path."""
    path = tmp_path / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


# --- the fold, from both sides ---------------------------------------------


def test_heading_slugs_still_folds_because_its_callers_ask_a_set_question():
    # ⛔ The row's own ground: this is CORRECT, and it is why the floor cannot
    # see a collision. Asserted so a later edit cannot "fix" it by accident.
    assert heading_slugs(TEMPLATE) == {"w1", "w2", "what-settles-it", "what-settles-it-1"}


def test_heading_bases_does_not_fold_and_that_is_the_whole_difference():
    assert heading_bases(TEMPLATE) == ["w1", "what-settles-it", "w2", "what-settles-it"]


def test_the_two_agree_on_what_a_heading_is():
    # A fenced `#` comment is not a heading in either, because one is defined
    # in terms of the other rather than parsing headings a second way.
    text = "# Real\n\n```sh\n# not a heading\n```\n\n# Real\n"
    assert heading_bases(text) == ["real", "real"]
    assert heading_slugs(text) == {"real", "real-1"}


# --- the census: the population, found and refused -------------------------


def test_a_duplicated_heading_is_found_with_its_count(tmp_path):
    write(tmp_path, "rows.md", TEMPLATE)
    result = scan(tmp_path)
    assert len(result.collisions) == 1
    collision = result.collisions[0]
    assert collision.document == "rows.md"
    assert collision.name == "what-settles-it"
    assert collision.headings == 2
    assert collision.inbound == ()


def test_a_document_with_no_duplicate_heading_reads_empty(tmp_path):
    # ⛔ The impossible control (Ruling 123 row 3): it must DIFFER from the
    # live reading, and it does — an empty population, not a smaller one.
    write(tmp_path, "clean.md", "# One\n\n## Two\n\n### Three\n")
    result = scan(tmp_path)
    assert result.collisions == ()
    assert result.findings == ()
    assert colliding_names("# One\n\n## Two\n") == {}


def test_the_census_states_its_denominators_when_the_population_is_empty(tmp_path):
    # Ruling 191(a): 0 is a reading, printed with what it was drawn from.
    write(tmp_path, "clean.md", "# One\n\n[t](clean.md#one)\n")
    line = collision_census(tmp_path)[0]
    assert "anchor collisions: none" in line
    assert "1 markdown documents" in line
    assert "1 anchored pointers" in line


def test_the_census_prints_every_name_with_its_count(tmp_path):
    write(tmp_path, "rows.md", TEMPLATE + "\n# W3\n\n## Findings\n\n# W4\n\n## Findings\n")
    lines = collision_census(tmp_path)
    assert "2 anchor names in 1 of 1 markdown documents (disk walk) answer for 4" in lines[0]
    assert "0 of them carry an inbound pointer" in lines[0]
    assert lines[1] == "  rows.md: findings x2; what-settles-it x2"


def test_the_census_groups_by_document_and_grows_with_documents(tmp_path):
    write(tmp_path, "a.md", TEMPLATE)
    write(tmp_path, "b.md", TEMPLATE)
    lines = collision_census(tmp_path)
    assert "2 anchor names in 2 of 2 markdown documents" in lines[0]
    assert lines[1:] == [
        "  a.md: what-settles-it x2",
        "  b.md: what-settles-it x2",
    ]


# --- the finding: an inbound link, planted, in both directions -------------


def test_a_planted_link_into_a_colliding_anchor_is_reported(tmp_path):
    write(tmp_path, "rows.md", TEMPLATE)
    write(tmp_path, "brief.md", "one\n\n[what settles it](rows.md#what-settles-it)\n")
    findings = check_anchor_collisions(tmp_path)
    assert len(findings) == 1
    finding = findings[0]
    assert finding.path == "brief.md"
    assert finding.line == 3
    assert finding.rule == RULE_COLLISION
    assert "what-settles-it" in finding.message
    assert "2 headings answer to" in finding.message


def test_the_pointer_floor_calls_that_exact_link_green(tmp_path):
    # ⛔ The positive row the plant owes (Ruling 191(c)), and the row's whole
    # argument in one assertion: the link RESOLVES. `0 unresolved` is true.
    write(tmp_path, "rows.md", TEMPLATE)
    write(tmp_path, "brief.md", "[w](rows.md#what-settles-it)\n")
    assert check_pointers(tmp_path) == []
    assert len(check_anchor_collisions(tmp_path)) == 1


def test_a_link_into_a_unique_heading_is_not_reported(tmp_path):
    write(tmp_path, "rows.md", TEMPLATE)
    write(tmp_path, "brief.md", "[w1](rows.md#w1)\n")
    assert check_anchor_collisions(tmp_path) == []


def test_an_explicit_suffix_is_not_a_finding(tmp_path):
    # ⭐ `#what-settles-it-1` addresses the second one deterministically; a
    # reader who has already disambiguated is not failed for it.
    write(tmp_path, "rows.md", TEMPLATE)
    write(tmp_path, "brief.md", "[second](rows.md#what-settles-it-1)\n")
    assert check_anchor_collisions(tmp_path) == []
    assert check_pointers(tmp_path) == []


def test_a_same_document_link_into_its_own_collision_is_reported(tmp_path):
    write(tmp_path, "rows.md", TEMPLATE + "\n[up](#what-settles-it)\n")
    findings = check_anchor_collisions(tmp_path)
    assert len(findings) == 1
    assert findings[0].path == "rows.md"
    assert "this document" in findings[0].message


def test_a_mention_in_backticks_is_not_an_inbound_link(tmp_path):
    # The parser is the exemption mechanism, inherited from `pointers`.
    write(tmp_path, "rows.md", TEMPLATE)
    write(tmp_path, "brief.md", "`[w](rows.md#what-settles-it)`\n")
    assert check_anchor_collisions(tmp_path) == []


def test_the_census_marks_a_collision_that_carries_an_inbound_pointer(tmp_path):
    write(tmp_path, "rows.md", TEMPLATE)
    write(tmp_path, "brief.md", "[w](rows.md#what-settles-it)\n")
    lines = collision_census(tmp_path)
    assert "1 of them carry an inbound pointer" in lines[0]
    assert lines[1] == "  rows.md: what-settles-it x2, 1 inbound"


def test_the_population_is_ordered_by_inbound_pointers_not_by_depth(tmp_path):
    # ⛔ Ordered by COST. The deeper name has nothing pointing at it.
    deep = "# A\n\n## Deep\n\n# B\n\n## Deep\n\n# C\n\n## Deep\n"
    write(tmp_path, "rows.md", deep + "\n## Shallow\n\n## Shallow\n")
    write(tmp_path, "brief.md", "[s](rows.md#shallow)\n")
    names = [collision.name for collision in scan(tmp_path).collisions]
    assert names == ["shallow", "deep"]


def test_no_finding_carries_an_absolute_path(tmp_path):
    # R7: an absolute path in a build log carries the user's home directory.
    write(tmp_path, "deep/rows.md", TEMPLATE)
    write(tmp_path, "deep/brief.md", "[w](rows.md#what-settles-it)\n")
    findings = check_anchor_collisions(tmp_path)
    assert findings
    for finding in findings:
        assert not finding.path.startswith("/")
        assert str(tmp_path) not in finding.message


# --- the tree itself -------------------------------------------------------


def test_the_repository_has_no_link_into_a_colliding_anchor():
    assert check_anchor_collisions(repository_root()) == []


def test_the_live_population_is_inhabited_so_the_census_is_not_zero_equals_zero():
    # ⛔ Ruling 48: the assertion above passes on a tree with no collisions at
    # all. This is the denominator that stops it reading as coverage — and the
    # population is archived bytes no office may edit (Ruling 106), so it is
    # asserted as a floor rather than as a figure that has to be maintained.
    result = scan(repository_root())
    assert len(result.collisions) >= 11
    assert result.headings > len(result.collisions)
    assert result.documents_colliding >= 2
    assert result.anchored > 100


def test_the_census_names_the_walk_that_produced_its_population(tmp_path):
    # ⛔ `W148`: this census and `pointer_coverage`'s denominator are the SAME
    # population, so both name the walk they came off. ⚠️ A `tmp_path` under no
    # repository is Ruling 216's third answer, and the line SAYS so rather than
    # falling through to the disk in silence.
    write(tmp_path, "one.md", "# Same\n\n# Same\n")
    line = collision_census(tmp_path)[0]
    assert "(disk walk)" in line
    assert "not reproducible from another checkout" in line
    assert scan(tmp_path).walk == DISK_WALK


def test_an_untracked_document_is_outside_the_census(tmp_path):
    # ⛔ `W148` clause 3: asserted in a REAL repository, because in a tree git
    # cannot answer for the disk walk still runs and this would pass anyway.
    init_repository(tmp_path)
    write(tmp_path, "tracked.md", "# Same\n\n# Same\n")
    result = run([git(), "add", "--", "tracked.md"], cwd=tmp_path)
    assert result.returncode == 0, result.stdout + result.stderr
    write(tmp_path, "untracked.md", "# Other\n\n# Other\n")
    census = scan(tmp_path)
    assert census.documents == 1
    assert census.walk == TRACKED_WALK
    assert [collision.document for collision in census.collisions] == ["tracked.md"]
    assert "(tracked walk)" in collision_census(tmp_path)[0]
