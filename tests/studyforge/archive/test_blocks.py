"""The block vocabulary and a practice's layout (SF-06).

⭐ **This module is the one place outside `archive/blocks.py` allowed to spell
the block types out**, and `test_there_is_exactly_one_block_type_list` exempts
it by name. A contract's assertion is not a second definition: nobody imports
their vocabulary from a test, and a test that derived its expectation from the
thing under test would assert nothing at all.
"""

import ast
import json
from pathlib import Path

import pytest

from studyforge.archive.blocks import (
    BLOCK_FIELDS,
    BLOCK_TYPES,
    BLOCKS,
    BY_NAME,
    CONTAINER_TYPES,
    COUNT_KEYS,
    LESSON_HEADING,
    STARTING_CODE_HEADING,
    STATEMENT_HEADING,
    Layout,
    counts_of,
    read_layout,
    walk,
)
from studyforge.archive.document import VIDEO_KEYS
from studyforge.archive.errors import ArchiveError
from tests.support import repository_root

#: The vocabulary, written out. ⛔ In `counts` order, which is the order that
#: reaches disk — see `test_the_fixtures_counts_are_in_this_order`.
EXPECTED = (
    "heading",
    "para",
    "code",
    "table",
    "list",
    "image",
    "video",
    "rule",
    "quote",
    "html",
    "disclosure",
)

EXPECTED_COUNT_KEYS = (
    "headings",
    "paras",
    "code",
    "tables",
    "lists",
    "images",
    "videos",
    "rules",
    "quotes",
    "html",
    "disclosures",
)

FIXTURES = Path("tests/fixtures")


def archive_documents():
    root = repository_root() / FIXTURES
    for path in sorted(root.rglob("*.json")):
        if "/raw/" in path.as_posix():
            yield path, json.loads(path.read_text(encoding="utf-8"))


# --------------------------------------------------------------------------
# One list
# --------------------------------------------------------------------------


def test_the_vocabulary_is_eleven_types_in_counts_order():
    assert BLOCK_TYPES == EXPECTED
    assert len(set(BLOCK_TYPES)) == 11


def test_every_derived_view_comes_from_the_same_rows():
    # ⭐ The consolidation, asserted rather than described: four things that
    # used to be four literals are four readings of one list, so they cannot
    # fall out of step.
    assert tuple(COUNT_KEYS.values()) == BLOCK_TYPES
    assert tuple(BLOCK_FIELDS) == BLOCK_TYPES
    assert tuple(BY_NAME) == BLOCK_TYPES
    assert CONTAINER_TYPES == tuple(b.name for b in BLOCKS if b.holds_blocks)


def test_the_count_keys_are_the_ones_that_reach_disk():
    assert tuple(COUNT_KEYS) == EXPECTED_COUNT_KEYS


def test_the_containers_are_quote_and_disclosure():
    # ⚠️ `disclosure` is present-but-withheld — a third state between shown
    # and absent. The archive records the semantics; that the markup is
    # `<details><summary>` is the renderer's decision (R13).
    assert CONTAINER_TYPES == ("quote", "disclosure")
    assert all(BY_NAME[name].fields[-1] == "blocks" for name in CONTAINER_TYPES)


def test_a_count_key_is_declared_and_not_pluralised():
    # ⛔ English plurals are irregular where it matters. A rule with two
    # exceptions is a lookup table that has not admitted what it is.
    assert BY_NAME["code"].count_key == "code"
    assert BY_NAME["html"].count_key == "html"
    assert BY_NAME["heading"].count_key == "headings"


def test_the_video_block_and_the_video_record_are_different_things():
    # ⚠️ Both exist, and losing one into the other is the mistake this
    # consolidation was most likely to make. The block is content in reading
    # order; the record is the unit's headline video and its provenance.
    assert BLOCK_FIELDS["video"] == ("type", "src", "title")
    assert VIDEO_KEYS == ("src", "poster", "mime", "remote", "poster_remote")
    assert set(BLOCK_FIELDS["video"]) & set(VIDEO_KEYS) == {"src"}


# --------------------------------------------------------------------------
# ...and only one, tree-wide
# --------------------------------------------------------------------------


OWNER = "src/studyforge/archive/blocks.py"
#: ⭐ The vocabulary's own test may spell it out; nothing else may. See this
#: module's docstring for why that is not the second copy in disguise.
SPELLERS = (OWNER, "tests/studyforge/archive/test_blocks.py")


def literal_collections(path: Path):
    """Every module-level literal collection of strings in `path`."""
    for node in ast.parse(path.read_text(encoding="utf-8")).body:
        if not isinstance(node, ast.Assign):
            continue
        value = node.value
        if isinstance(value, (ast.Tuple, ast.List, ast.Set)):
            yield {e.value for e in value.elts if isinstance(e, ast.Constant)}
        elif isinstance(value, ast.Dict):
            yield {k.value for k in value.keys if isinstance(k, ast.Constant)}


def test_there_is_exactly_one_block_type_list():
    # ⛔ SF-06's acceptance, and it is a test rather than a comment asking
    # people not to write one. Four copies existed: the reader's tuple, the
    # fixture checker's count keys, its block fields and its container tuple.
    # Two copies of a contract is the defect this project has diagnosed four
    # times, and a vocabulary that disagrees with its own checker means the
    # gate and the parser have different ideas of what a document may hold.
    root = repository_root()
    vocabulary = set(BLOCK_TYPES) | set(COUNT_KEYS)
    offenders = []
    for path in sorted((root / "src").rglob("*.py")) + sorted((root / "tests").rglob("*.py")):
        if str(path.relative_to(root)) in SPELLERS:
            continue
        for names in literal_collections(path):
            if len(names & vocabulary) >= 4:
                offenders.append(str(path.relative_to(root)))
    assert sorted(set(offenders)) == []


def test_that_check_would_have_caught_the_copies_it_was_written_for(tmp_path):
    # ⭐ Both directions. The scanner is asserted against a module shaped like
    # the ones this task consolidated, so "no offenders" is a result and not
    # an artefact of the scanner seeing nothing.
    copy = tmp_path / "vocabulary.py"
    copy.write_text(
        'COUNT_KEYS = {"headings": "heading", "paras": "para", '
        '"code": "code", "tables": "table"}\n',
        encoding="utf-8",
    )
    vocabulary = set(BLOCK_TYPES) | set(COUNT_KEYS)
    assert any(len(names & vocabulary) >= 4 for names in literal_collections(copy))


def test_the_reader_and_the_fixture_checker_both_import_the_one_list():
    root = repository_root()
    reader = (root / "src/studyforge/archive/markdown/__init__.py").read_text(encoding="utf-8")
    checker = (root / "tests/fixture_checks/vocabulary.py").read_text(encoding="utf-8")
    assert "from studyforge.archive.blocks import" in reader
    assert "from studyforge.archive.blocks import" in checker


# --------------------------------------------------------------------------
# counts and the walk
# --------------------------------------------------------------------------


def test_counts_always_carries_every_key_including_the_zeroes():
    # ⛔ A count that disappears when it is zero cannot be told from a count
    # nobody wrote, and noticing a short ingest is the whole point (R6).
    counted = counts_of([{"type": "para", "text": "one"}])
    assert tuple(counted) == EXPECTED_COUNT_KEYS
    assert counted["paras"] == 1
    assert counted["headings"] == 0


def test_counts_are_of_top_level_blocks_only():
    quote = {"type": "quote", "blocks": [{"type": "para", "text": "inside"}]}
    counted = counts_of([quote])
    assert counted["quotes"] == 1
    assert counted["paras"] == 0


def test_walk_reaches_blocks_inside_every_container():
    inner = {"type": "para", "text": "inside"}
    deep = {"type": "disclosure", "summary": "s", "open": False, "blocks": [inner]}
    quote = {"type": "quote", "blocks": [deep]}
    assert list(walk([quote])) == [quote, deep, inner]


def test_walk_keys_off_the_container_list_and_not_off_a_name():
    # ⭐ The next container must not have to be remembered. Every container in
    # the vocabulary is reached by the same recursion.
    for name in CONTAINER_TYPES:
        block = {"type": name, "blocks": [{"type": "rule"}]}
        assert len(list(walk([block]))) == 2


def test_the_counts_in_every_fixture_agree_with_this_module():
    seen = 0
    for path, document in archive_documents():
        assert tuple(document["counts"]) == EXPECTED_COUNT_KEYS, path.name
        assert document["counts"] == counts_of(document["blocks"]), path.name
        seen += 1
    assert seen > 0


def test_every_block_type_in_the_fixtures_is_in_the_vocabulary():
    seen = set()
    for _path, document in archive_documents():
        seen.update(block["type"] for block in walk(document["blocks"]))
    assert seen <= set(BLOCK_TYPES)
    # ⚠️ And the fixtures exercise all of them, so the vocabulary is not
    # eleven types of which four are theoretical.
    assert seen == set(BLOCK_TYPES), sorted(set(BLOCK_TYPES) - seen)


def test_every_block_carries_exactly_the_fields_its_row_names():
    for path, document in archive_documents():
        for block in walk(document["blocks"]):
            assert tuple(block) == BLOCK_FIELDS[block["type"]], f"{path.name}: {block['type']}"


# --------------------------------------------------------------------------
# A practice's layout
# --------------------------------------------------------------------------


def practice(*, statement_heading=STATEMENT_HEADING, lesson_heading=LESSON_HEADING, tail=None):
    blocks = [
        {"type": "heading", "level": 2, "text": statement_heading},
        {"type": "para", "text": "Do the thing."},
        {"type": "heading", "level": 2, "text": lesson_heading},
        {"type": "para", "text": "Here is how."},
        {"type": "heading", "level": 2, "text": STARTING_CODE_HEADING},
    ]
    blocks.extend(tail if tail is not None else [{"type": "code", "lang": "java", "text": "//"}])
    return {"kind": "practice", "blocks": blocks}


def test_a_lesson_has_no_layout():
    assert read_layout({"kind": "lesson", "blocks": practice()["blocks"]}, "x") is None


def test_a_practice_exposes_its_parts_without_reparsing():
    layout = read_layout(practice(), "practice-1.json")
    assert isinstance(layout, Layout)
    assert layout.statement == ({"type": "para", "text": "Do the thing."},)
    assert layout.lesson == ({"type": "para", "text": "Here is how."},)
    assert layout.lesson_title is None
    assert layout.starting_code == "//"
    assert layout.starting_lang == "java"


def test_a_lesson_heading_may_carry_a_title():
    layout = read_layout(practice(lesson_heading="Lesson: Streams"), "x")
    assert layout.lesson_title == "Streams"


def test_a_bare_fence_reports_no_language():
    layout = read_layout(practice(tail=[{"type": "code", "lang": "", "text": "x"}]), "x")
    assert layout.starting_lang is None


@pytest.mark.parametrize(
    "broken",
    [
        practice(statement_heading="Overview"),
        practice(lesson_heading="Notes"),
        practice(tail=[]),
        practice(tail=[{"type": "para", "text": "not a fence"}]),
        practice(tail=[{"type": "code", "lang": "", "text": "a"}, {"type": "rule"}]),
        {"kind": "practice", "blocks": []},
    ],
)
def test_a_practice_without_its_sections_is_refused_not_downgraded(broken):
    # ⛔ R6. Returning it quietly as a lesson is the "looking finished while
    # being short" failure the counts exist to catch, arriving by another door.
    with pytest.raises(ArchiveError, match="practice"):
        read_layout(broken, "practice-1.json")


def test_the_refusal_names_the_three_headings_it_wanted():
    with pytest.raises(ArchiveError) as raised:
        read_layout({"kind": "practice", "blocks": []}, "practice-1.json")
    message = str(raised.value)
    assert "practice-1.json" in message
    for heading in (STATEMENT_HEADING, LESSON_HEADING, STARTING_CODE_HEADING):
        assert heading in message


def test_the_real_practice_fixtures_are_laid_out():
    seen = 0
    for path, document in archive_documents():
        layout = read_layout(document, path.name)
        assert (layout is not None) == (document["kind"] == "practice"), path.name
        if layout is not None:
            assert layout.starting_code == document["starting_code"]
            seen += 1
    assert seen > 0
