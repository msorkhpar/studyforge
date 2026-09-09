"""Mirror of `src/studyforge/corpus/manifest/content.py` (R12)."""

from __future__ import annotations

import pytest

from studyforge.corpus.manifest import (
    MIN_WHY_CHARS,
    Classification,
    ManifestError,
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
    with pytest.raises(ManifestError, match="excluded twice"):
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
