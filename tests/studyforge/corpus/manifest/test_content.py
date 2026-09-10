"""Mirror of `src/studyforge/corpus/manifest/content.py` (R12)."""

from __future__ import annotations

import pytest

from studyforge.corpus.manifest import (
    MIN_WHY_CHARS,
    Classification,
    ManifestError,
    NotMaterial,
    parse_content,
)

#: ⭐ The ISO corpus's real shape, which is why the field exists: per-unit
#: files, and three whole-series aggregates that are digest-identical ordered
#: concatenations of them. `src/*.md` ingests all 38 units twice.
ISO = {
    "include": ["src/*.md"],
    "exclude": [
        {"path": "src/ISO.md", "why": "whole-series aggregate: a concatenation of 1.md…16.md (C2)"},
        {"path": "src/Server.md", "why": "whole-series aggregate: a concatenation of s1…s11 (C2)"},
        {"path": "src/Client.md", "why": "whole-series aggregate: a concatenation of c1…c11 (C2)"},
    ],
}


def policy(**overrides):
    return parse_content({**ISO, **overrides})


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


# --- what a content policy refuses -----------------------------------------


@pytest.mark.parametrize("include", [[], None, "src/*.md", [""], [7]])
def test_a_corpus_that_includes_nothing_is_refused(include):
    with pytest.raises(ManifestError, match="content.include"):
        policy(include=include)


def test_an_exclusion_must_say_why():
    with pytest.raises(ManifestError, match="why this file is withheld"):
        policy(exclude=[{"path": "src/ISO.md"}])


def test_an_exclusion_whose_reason_is_a_token_is_refused():
    # ⛔ Same argument and same number the quality floor already uses for a
    # size exception: it only stops `"why": "n/a"` being a way through.
    with pytest.raises(ManifestError, match=f"at least {MIN_WHY_CHARS} characters"):
        policy(exclude=[{"path": "src/ISO.md", "why": "aggregate"}])


def test_an_exclusion_names_one_file_and_never_a_pattern():
    # ⭐ One justification covering a pattern is one justification for a set
    # whose membership changes when somebody adds a file.
    with pytest.raises(ManifestError, match="must name one file"):
        policy(exclude=[{"path": "src/*.md", "why": "every aggregate, all at once, forever"}])


def test_the_same_file_cannot_be_excluded_twice():
    entry = {"path": "src/ISO.md", "why": "whole-series aggregate, declared once too often"}
    with pytest.raises(ManifestError, match=r"already excluded by content\.exclude\[0\]"):
        policy(exclude=[entry, entry])


@pytest.mark.parametrize(
    "pattern", ["/etc/passwd", "../outside/*.md", "~/notes.md", "src/../../escape.md"]
)
def test_a_path_that_escapes_the_source_root_is_refused(pattern):
    with pytest.raises(ManifestError, match="stay inside it"):
        policy(include=[pattern])


def test_an_unknown_key_in_content_is_refused():
    with pytest.raises(ManifestError, match="unknown key"):
        parse_content({"include": ["*.md"], "exclude": [], "ignore": ["x"]})


@pytest.mark.parametrize("value", [None, [], "content", 7])
def test_content_must_be_an_object(value):
    with pytest.raises(ManifestError, match="'content' must be an object"):
        parse_content(value)


@pytest.mark.parametrize("path", ["", None, 7])
def test_classify_refuses_a_path_that_is_not_one(path):
    with pytest.raises(ManifestError, match="non-empty str"):
        policy().classify(path)


# --- the third state: never material, rather than withheld ------------------

#: ⭐ Ruling 90's own three examples, copied rather than paraphrased. Rule 1a
#: was derived from what a loose glob does to rule 4, **not** fitted to these;
#: they are here so that a later tightening of the rule that would have
#: refused the ruling's own examples fails loudly.
RULING_90_GLOBS = ("docs/studyforge/*", "LICENSE", ".gitignore")

#: A reason long enough to be one. ⚠️ Written out rather than generated from
#: `MIN_WHY_CHARS`, for the same reason the boundary cases below are.
WHY = "the repository's own scaffolding, never read aloud"


def scaffolding(*entries, **overrides):
    """A policy whose third state is `entries`, each `(glob, why)`."""
    declared = [{"glob": glob, "why": why} for glob, why in entries]
    return policy(not_material=declared, **overrides)


@pytest.mark.parametrize("glob", RULING_90_GLOBS)
def test_the_rulings_own_three_examples_are_accepted(glob):
    assert scaffolding((glob, WHY)).not_material == (NotMaterial(glob, WHY),)


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


# --- rule 1a: an exact path, or one directory's wildcard --------------------


@pytest.mark.parametrize(
    "glob", ["docs/studyforge/*", "docs/studyforge/**", "src/notes/*.md", "a/b/c/*"]
)
def test_a_wildcard_under_a_directory_is_accepted(glob):
    assert scaffolding((glob, WHY)).not_material == (NotMaterial(glob, WHY),)


@pytest.mark.parametrize("glob", ["LICENSE", ".gitignore", "docs/studyforge/notes.md"])
def test_an_exact_path_is_accepted(glob):
    assert scaffolding((glob, WHY)).not_material == (NotMaterial(glob, WHY),)


@pytest.mark.parametrize("glob", ["[CLR]*", "*.md", "*", "[A-Z]*", "?ICENSE", "docs*/notes.md"])
def test_a_wildcard_with_no_directory_before_it_is_refused(glob):
    # ⛔ **`[CLR]*` is the measured case and it is refused.** It covers three
    # root files only because a fourth happens to begin with another letter —
    # the collision encoded rather than the intent — and a `why` cannot be
    # true of a file nobody has written yet.
    with pytest.raises(ManifestError, match="wildcard where no directory precedes it"):
        scaffolding((glob, WHY))


def test_a_wildcard_inside_a_directory_name_is_refused():
    # ⚠️ The wildcard must lie *under* a directory, not *span* one: the fixed
    # prefix of `docs/study*/x.md` is not a directory anybody declared.
    with pytest.raises(ManifestError, match="wildcard where no directory precedes it"):
        scaffolding(("docs/study*/x.md", WHY))


def test_the_rule_1a_refusal_does_not_reproduce_the_pattern():
    # ⭐ The actionable half is which rule was broken; the author has what
    # they wrote in front of them, and a refusal that echoes a path is where
    # a home directory ends up in a build log (R7, W19).
    with pytest.raises(ManifestError) as raised:
        scaffolding(("[CLR]*", WHY))
    assert "[CLR]*" not in str(raised.value)


# --- what the third state refuses -------------------------------------------


def test_a_not_material_entry_must_say_why():
    # ⛔ And it may not say "withheld", because nothing is: every declaration
    # that the framework will not read a file needs a reason, and this one's
    # reason is a different sentence from an exclusion's.
    with pytest.raises(ManifestError, match="why this file was never material"):
        policy(not_material=[{"glob": "LICENSE"}])


def test_a_nineteen_character_reason_is_refused_and_a_twenty_character_one_is_not():
    # ⛔ The boundary in literal characters, never `MIN_WHY_CHARS * "x"`: an
    # assertion built from the constant it pins passes whatever the constant
    # becomes, which is a defect this project has now caught twice.
    short, long = "the repo's own note", "the repo's own notes"
    assert (len(short), len(long)) == (19, 20)
    with pytest.raises(ManifestError, match="at least 20 characters"):
        scaffolding(("LICENSE", short))
    assert scaffolding(("LICENSE", long)).not_material[0].why == long


def test_the_length_the_module_enforces_is_the_one_this_file_pins():
    # ⚠️ The one place the constant is read, and it is read to catch a drift
    # between the module and the two literals above rather than to build them.
    assert MIN_WHY_CHARS == 20


def test_the_same_glob_cannot_be_declared_twice():
    with pytest.raises(ManifestError, match=r"already declared by content\.not_material\[0\]"):
        scaffolding(("LICENSE", WHY), ("LICENSE", WHY))


def test_an_unknown_key_in_a_not_material_entry_is_refused():
    with pytest.raises(ManifestError, match="unknown key"):
        policy(not_material=[{"path": "LICENSE", "why": WHY}])


@pytest.mark.parametrize("declared", [None, "LICENSE", 7, {}])
def test_not_material_must_be_a_list(declared):
    with pytest.raises(ManifestError, match="'content.not_material' must be a list"):
        policy(not_material=declared)


@pytest.mark.parametrize("entry", [None, "LICENSE", 7, []])
def test_a_not_material_entry_must_be_an_object(entry):
    with pytest.raises(ManifestError, match=r"content\.not_material\[0\] must be an object"):
        policy(not_material=[entry])


@pytest.mark.parametrize("glob", [None, "", 7, ["LICENSE"]])
def test_a_not_material_glob_must_be_a_non_empty_string(glob):
    with pytest.raises(ManifestError, match=r"content\.not_material\[0\]\.glob"):
        policy(not_material=[{"glob": glob, "why": WHY}])


@pytest.mark.parametrize("glob", ["/etc/passwd", "../outside/*", "~/notes.md"])
def test_a_not_material_glob_that_escapes_the_source_root_is_refused(glob):
    with pytest.raises(ManifestError, match="stay inside it"):
        scaffolding((glob, WHY))
