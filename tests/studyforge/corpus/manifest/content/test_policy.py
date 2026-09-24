"""Mirror of `src/studyforge/corpus/manifest/content/policy.py` (R12).

⛔ Every test here asks a **built** policy a question. What it refuses at read
time is `test_parse.py`'s, and the two do not overlap: a refusal asserted in
both files is one nobody re-reads when the message changes.
"""

from __future__ import annotations

import pytest

from studyforge.corpus.manifest import Classification, ManifestError, parse_content
from tests.studyforge.corpus.manifest.content.policies import WHY, policy, scaffolding


@pytest.mark.parametrize("path", ["src/1.md", "src/16.md", "src/s4.md", "src/c11.md"])
def test_a_per_unit_file_is_included(path):
    assert policy().classify(path) is Classification.INCLUDED


@pytest.mark.parametrize("path", ["src/ISO.md", "src/Server.md", "src/Client.md"])
def test_an_aggregate_is_excluded_even_though_the_glob_matches_it(path):
    # ⚠️ Exclusion wins over inclusion, and this is the case it exists for.
    # Proved both ways: with the exclusions removed the same glob DOES match
    # the aggregate, which is the double ingest nobody was complaining about.
    assert policy().classify(path) is Classification.EXCLUDED
    assert policy(exclude=[]).classify(path) is Classification.INCLUDED


@pytest.mark.parametrize("path", ["README.md", "src/nested/deep.md", "pom.xml", "docs/notes.md"])
def test_a_file_matching_neither_list_is_unclassified(path):
    # ⛔ Silence is the failure C2 describes, so there is no silent third
    # answer: `validate` exits 1 on this (R6).
    assert policy().classify(path) is Classification.UNCLASSIFIED


def test_a_star_does_not_cross_a_directory_separator():
    # Otherwise `src/*.md` would swallow a whole tree, and an aggregate two
    # directories down would be ingested without anybody declaring it.
    assert policy().classify("src/a/b.md") is Classification.UNCLASSIFIED


def test_the_javas_shape_matches_only_module_readmes():
    java = parse_content({"include": ["*/*/README*.md"], "exclude": []})
    assert java.classify("basics/01-getting-started/README.md") is Classification.INCLUDED
    assert java.classify("basics/01-getting-started/README_1.1.md") is Classification.INCLUDED
    assert java.classify("pom.xml") is Classification.UNCLASSIFIED


def test_the_reason_an_exclusion_gives_is_retrievable():
    # ⭐ The `why` is not decoration: it is what stops the next maintainer
    # deleting an exclusion they cannot explain.
    assert "concatenation" in policy().why_excluded("src/ISO.md")
    assert policy().why_excluded("src/1.md") is None


@pytest.mark.parametrize("path", ["", None, 7])
def test_classify_refuses_a_path_that_is_not_one(path):
    with pytest.raises(ManifestError, match="non-empty str"):
        policy().classify(path)


def test_a_file_a_not_material_glob_matches_is_not_material():
    # ⛔ Not `EXCLUDED`: nothing is withheld from a reader here, and calling it
    # an exclusion makes every `why` in the audit a small lie.
    said = scaffolding(("docs/studyforge/*", WHY), ("LICENSE", WHY))
    assert said.classify("docs/studyforge/notes.md") is Classification.NOT_MATERIAL
    assert said.classify("LICENSE") is Classification.NOT_MATERIAL


def test_an_absent_third_state_is_an_empty_tuple_and_changes_nothing():
    # ⭐ The compatibility claim in one assertion: the same paths classify the
    # same way with the key absent as they did before the key existed.
    assert policy().not_material == ()
    assert policy().classify("src/1.md") is Classification.INCLUDED
    assert policy().classify("LICENSE") is Classification.UNCLASSIFIED


def test_a_file_matched_by_neither_list_nor_the_third_state_is_unclassified():
    # ⛔ Rule 4 is not weakened by one line: C2's countermeasure still fires.
    assert scaffolding(("LICENSE", WHY)).classify("notes.txt") is Classification.UNCLASSIFIED


def test_the_reason_a_not_material_entry_gives_is_retrievable():
    said = scaffolding(("docs/studyforge/*", WHY))
    assert said.why_not_material("docs/studyforge/notes.md") == WHY
    assert said.why_not_material("src/1.md") is None


# --- rule 3: two states at once is a finding, never a precedence ------------


def test_a_file_in_both_include_and_not_material_is_contested():
    # ⛔ **Never a precedence.** One order would drop material the reader was
    # promised; the other would read the repository's scaffolding aloud. The
    # manifest disagreed with itself and the classifier says so.
    both = scaffolding(("src/*", WHY))
    assert both.classify("src/1.md") is Classification.CONTESTED
    assert both.classify("src/1.md") is not Classification.INCLUDED
    assert both.classify("src/1.md") is not Classification.NOT_MATERIAL


def test_an_exclusion_still_wins_over_the_third_state():
    # ⚠️ The two-state precedence is untouched: an exclusion names one file
    # deliberately, which is a decision and not a disagreement.
    both = scaffolding(("src/*", WHY))
    assert both.classify("src/ISO.md") is Classification.EXCLUDED


def test_a_glob_matches_the_whole_path_and_never_only_its_tail():
    # ⛔ **Found by a mutant surviving, not by reading**. `classify`
    # uses `full_match`; `PurePosixPath.match` is anchored at the *right*, so
    # under it `deep/src/1.md` matches `src/*.md` and a file one directory
    # above the declared tree is read in without anybody declaring it.
    # ⚠️ That is C2's own shape — material ingested that nobody said was
    # material — so the two spellings must be told apart here rather than
    # left to agree by accident on the paths this file happens to use.
    assert policy().classify("deep/src/1.md") is Classification.UNCLASSIFIED
    assert policy().classify("src/1.md") is Classification.INCLUDED


def test_the_third_state_matches_the_whole_path_too():
    # ⭐ The twin, and it is the direction that matters more: a `not_material`
    # glob matching by tail would silence the unclassified check for a file in
    # a directory nobody declared not-material.
    said = scaffolding(("docs/studyforge/*", WHY))
    assert said.classify("above/docs/studyforge/notes.md") is Classification.UNCLASSIFIED
    assert said.why_not_material("above/docs/studyforge/notes.md") is None
    assert said.classify("docs/studyforge/notes.md") is Classification.NOT_MATERIAL
    assert said.why_not_material("docs/studyforge/notes.md") == WHY


def test_the_three_states_spell_themselves_the_way_a_manifest_reads():
    # ⚠️ **Nothing reads `.value` today** — every consumer compares members by
    # identity, measured across `src/`. ⭐ So this
    # pins a *vocabulary*, not a behaviour: the hyphen in `not-material` is a
    # decision, and `unclassified`/`contested` are the same two strings
    # `validate.source.classification` keeps as `RULE_*` constants of its own.
    # A mutant on any of them would otherwise survive the whole suite.
    assert [state.value for state in Classification] == [
        "included",
        "excluded",
        "not-material",
        "contested",
        "unclassified",
    ]
