"""FND-04's fixtures check themselves, so twelve epics can trust them.

The checks live in `tests/fixture_checks/`, one module per seam; this module is
what asserts them. ⭐ The two are separate because they answer different
questions — *what does this corpus break?* is reusable and is what SF-25 will
re-ask of a real source, while *and is that empty?* is a test.

Run `python3 -m tests.fixture_checks` for the block-type coverage table.
"""

from __future__ import annotations

import pytest

from tests.fixture_checks import (
    BLOCK_FIELDS,
    FIXTURES,
    INVALID_CORPORA,
    MARKUP_SHAPED,
    PERSONAL_DATA,
    REQUIRED_TYPES,
    VALID,
    block_types,
    blocks_of_type,
    violations,
)


@pytest.mark.parametrize("name", VALID)
def test_valid_corpus_violates_nothing(name):
    found = violations(FIXTURES / name)
    assert found == [], "\n".join(f"{rule}: {message}" for rule, message in found)


@pytest.mark.parametrize("name", VALID)
def test_every_block_type_appears(name):
    missing = sorted(set(REQUIRED_TYPES[name]) - set(block_types(FIXTURES / name)))
    assert missing == [], f"{name} never exercises {missing}"


@pytest.mark.parametrize("name", VALID)
def test_no_unknown_block_type(name):
    unknown = sorted(set(block_types(FIXTURES / name)) - set(BLOCK_FIELDS))
    assert unknown == [], f"{name} uses {unknown}, which the vocabulary does not name"


@pytest.mark.parametrize("name", VALID)
def test_fenced_code_carries_markup_shaped_text(name):
    """⛔ The fence-awareness fixture, and it is not decoration.

    A parser that scans for raw HTML without tracking fences reads a Maven POM
    or a Spring bean definition as markup. That is not hypothetical: a recount
    of the ISO corpus found every one of its 26 `<tag>`-shaped matches to be
    XML **inside a fenced code block**, and none of its 38 files to contain raw
    HTML at all. This asserts each corpus makes such a parser fail here, where
    a fixture names the defect, rather than against real material.
    """
    fenced = [
        block
        for block in blocks_of_type(FIXTURES / name, "code")
        if MARKUP_SHAPED.search(block["text"])
    ]
    assert fenced, f"{name} has no code block carrying markup-shaped text"


def test_the_same_tags_appear_fenced_and_raw_in_one_corpus():
    """The discriminator: identical tags, two block types, one document.

    Coverage of each type separately does not prove a parser can tell them
    apart — it can only be proved by material where the two are the same text.
    """
    root = FIXTURES / "depth1"
    fenced = " ".join(block["text"] for block in blocks_of_type(root, "code"))
    raw = " ".join(block["text"] for block in blocks_of_type(root, "html"))
    shared = {m.group() for m in MARKUP_SHAPED.finditer(fenced)} & {
        m.group() for m in MARKUP_SHAPED.finditer(raw)
    }
    assert shared, "no tag appears both inside a fence and as raw HTML"


@pytest.mark.parametrize("name,rule", sorted(INVALID_CORPORA.items()))
def test_invalid_corpus_violates_exactly_its_one_rule(name, rule):
    found = violations(FIXTURES / "invalid" / name)
    broken = sorted({found_rule for found_rule, _message in found})
    assert broken == [rule], "\n".join(f"{r}: {m}" for r, m in found)


@pytest.mark.parametrize("name,rule", sorted(INVALID_CORPORA.items()))
def test_invalid_corpus_names_its_rule(name, rule):
    text = (FIXTURES / "invalid" / name / "VIOLATION.md").read_text(encoding="utf-8")
    assert "**Rule violated:**" in text
    assert text.startswith(f"# {name}\n")


def test_the_invalid_set_is_exactly_what_is_on_disk():
    on_disk = sorted(p.name for p in (FIXTURES / "invalid").iterdir() if p.is_dir())
    assert on_disk == sorted(INVALID_CORPORA)


def test_only_the_personal_data_fixture_carries_personal_data():
    """R7's sweep over the whole fixture tree, with one sanctioned exception."""
    sanctioned = FIXTURES / "invalid" / "personal-data"
    offenders = []
    for path in sorted(FIXTURES.rglob("*")):
        if not path.is_file() or sanctioned in path.parents:
            continue
        text = path.read_text(encoding="utf-8")
        for label, pattern in PERSONAL_DATA:
            if pattern.search(text):
                offenders.append(f"{path.relative_to(FIXTURES)}: {label}")
    assert offenders == []


def test_the_sanctioned_fixture_really_does_carry_it():
    """Otherwise SF-08 and SF-25 would be accepted against a fixture that passes."""
    found = violations(FIXTURES / "invalid" / "personal-data")
    assert [rule for rule, _ in found] == ["personal-data"]
