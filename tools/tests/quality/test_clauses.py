"""Mirror of `tools/quality/clauses.py` (R12).

⛔ **Asserted in BOTH directions** (`W141`'s fourth clause): a planted heading whose
stated count disagrees with its children is FOUND and named with its pair, and
`RULED ROUND 60` at *nine* is the LIVE agreeing inhabitant, so the negative arm is
not asserted against a fixture alone. ⚠️ And the live population is asserted
non-empty and word-spelled (the fifth clause): a digit-only predicate reads empty
there and turns this file red. Each fixture tree is a real git repository, because
the population is what git TRACKS (`W148`).
"""

from __future__ import annotations

import tools.quality.clauses as clauses
from tests.support import assert_package_contract, git, init_repository, repository_root, run
from tools.quality.clauses import (
    RULE_CLAUSES,
    check_clause_counts,
    claims,
    clause_census,
    scan,
    stated_count,
)

DOCUMENT = "docs/conventions/rubric.md"


def tree(tmp_path, files: dict[str, str]):
    """A git repository under `tmp_path` TRACKING `files`."""
    root = init_repository(tmp_path / "repo")
    for name, text in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    result = run([git(), "add", "--", *files], cwd=root)
    assert result.returncode == 0, result.stdout + result.stderr
    return root


def pairs(text: str) -> list[tuple[str, int, int]]:
    """Every claim in `text` as `(spelling, stated, counted)`."""
    return [(c.spelling, c.stated, c.counted) for c in claims(DOCUMENT, text)]


def test_states_its_contract():
    assert_package_contract(clauses, "tools.quality.clauses")


# --- the predicate: the heading's own number, words first ---------------------


def test_a_number_WORD_is_read():
    assert stated_count("⛔ RULED ROUND 60 — nine clauses, each one command") == ("nine", 9)
    assert stated_count("RULED ROUND 61 — Thirteen Clauses") == ("Thirteen", 13)
    assert stated_count("RULED ROUND 62 — one clause, its command") == ("one", 1)


def test_a_longer_word_is_not_read_as_its_prefix():
    assert stated_count("nineteen clauses") == ("nineteen", 19)


def test_digits_are_read_too():
    assert stated_count("R — 2 clauses") == ("2", 2)


def test_a_heading_stating_NO_count_is_silent():
    # ⛔ Say it and it is checked — never "you must say it" (Ruling 180).
    assert stated_count("RULED ROUND 66 — each clause one command and one pass condition") is None
    assert pairs("## R — each clause one command\n\n### a\n") == []


def test_a_count_inside_a_code_span_is_a_mention():
    assert stated_count("R — `four clauses` quoted") is None


# --- the count: direct children only -------------------------------------------


def test_only_DIRECT_children_up_to_the_next_sibling_are_counted():
    text = (
        "# Top\n\n## A — two clauses\n\n### one\n\n#### deeper\n\n### two\n\n"
        "## B — one clause\n\n### three\n\n# Next\n\n### orphan\n"
    )
    assert pairs(text) == [("two", 2, 2), ("one", 1, 1)]


def test_a_fenced_heading_is_not_a_child():
    text = "## A — one clause\n\n### real\n\n```sh\n### not a heading\n```\n"
    assert pairs(text) == [("one", 1, 1)]


# --- both directions, planted and live -----------------------------------------


def test_a_planted_DISAGREEING_heading_is_found_and_named_with_its_pair(tmp_path):
    root = tree(tmp_path, {DOCUMENT: "## ⛔ RULED ROUND 9 — four clauses\n\n### a\n\n### b\n"})
    (finding,) = check_clause_counts(root)
    assert (finding.path, finding.line, finding.rule) == (DOCUMENT, 1, RULE_CLAUSES)
    assert "'⛔ RULED ROUND 9' states 'four' (4), parents 2" in finding.message
    first, pair = clause_census(root)
    assert "1 of 3 headings in 1 documents" in first
    assert "1 disagree" in first
    assert pair == f"  {DOCUMENT}:1 '⛔ RULED ROUND 9' states 'four' (4), parents 2 — DISAGREES"


def test_an_AGREEING_heading_reads_clean_and_still_prints_its_pair(tmp_path):
    root = tree(tmp_path, {DOCUMENT: "## RULED ROUND 9 — two clauses\n\n### a\n\n### b\n"})
    assert check_clause_counts(root) == []
    assert clause_census(root)[1] == f"  {DOCUMENT}:1 'RULED ROUND 9' states 'two' (2), parents 2"


def test_a_document_outside_the_conventions_is_not_read(tmp_path):
    root = tree(tmp_path, {"docs/tasks/row.md": "## R — four clauses\n\n### a\n"})
    assert check_clause_counts(root) == []
    (only,) = clause_census(root)
    assert "0 of 0 headings in 0 documents" in only


def test_the_LIVE_agreeing_inhabitant_is_round_60_at_nine():
    live = [c for c in scan(repository_root()).claims if "RULED ROUND 60" in c.heading]
    assert [(c.spelling, c.stated, c.counted) for c in live] == [("nine", 9, 9)]


def test_the_LIVE_population_is_inhabited_and_spelled_in_WORDS():
    # ⛔ Ruling 48: a digit-only predicate reads EMPTY here and passes vacuously,
    # so emptiness and a word-free population are both failures.
    live = scan(repository_root()).claims
    assert live, "no heading under docs/conventions/ states a clause count"
    assert any(claim.spelling.isalpha() for claim in live)


def test_the_LIVE_population_is_TRUE():
    # ⭐ The third clause: the instrument lands with no known-red row.
    assert check_clause_counts(repository_root()) == []
