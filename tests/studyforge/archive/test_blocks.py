"""The block vocabulary and a practice's layout.

⭐ **This module spells the block types out, and is cleared by the same rule
that clears every other module: it imports the vocabulary from the module that
owns it.** A contract's assertion is not a second definition — a test that
derived its expectation from the thing under test would assert nothing — and
the check does not need to know that, because the rule is about *deriving from
one source of truth*, not about *not spelling*.

⚠️ **The allow-list is empty and should stay that way.** A path allow-list
grows with every table a module spells, and it is a list of files nobody
re-examines.
"""

import ast
import json
from pathlib import Path

import pytest

from studyforge.archive.blocks import (
    BLOCK_FIELDS,
    BLOCK_OPTIONAL,
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
    item_parts,
    list_start,
    read_layout,
    walk,
)
from studyforge.archive.document import VIDEO_KEYS, content_sha256
from studyforge.archive.errors import ArchiveError
from tests.fixture_checks import archive_documents, coverage
from tests.support import imports_module, repository_root

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


# --------------------------------------------------------------------------
# One list
# --------------------------------------------------------------------------


def test_the_vocabulary_is_eleven_types_in_counts_order():
    assert BLOCK_TYPES == EXPECTED
    assert len(set(BLOCK_TYPES)) == 11


def test_every_derived_view_comes_from_the_same_rows():
    # ⭐ Asserted rather than described: four views are four readings of one
    # list, so they cannot fall out of step.
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
VOCABULARY_MODULE = "studyforge.archive.blocks"

#: ⭐ **Empty, and that is the result.** The rule is about *importing*, not
#: about being on a list: a module that takes the vocabulary from its owner may
#: spell as much of it as it likes, because what it spells is checked against
#: the source of truth. A path allow-list would grow with every such module —
#: see this module's docstring.
SPELLERS: tuple[str, ...] = ()


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


def imports_the_vocabulary(path: Path) -> bool:
    """Does `path` take the block vocabulary from the module that owns it?

    ⛔ Equality, not a prefix, and not a re-export chain. A module deriving
    from the one source of truth says where it got it.
    """
    return imports_module(path, VOCABULARY_MODULE)


def copies(root: Path) -> list[str]:
    """Modules carrying a literal block-type list they did not get from its owner.

    ⛔ **The rule is not "no module may spell four vocabulary names".** That
    would have been narrowed to definitions to let `surface.py` through, and a
    genuine fifth copy that happened to be a mapping would have stopped being
    caught. The rule is the one the version guard already uses: *a literal
    collection of four or more vocabulary names in a module that does not
    import the vocabulary.*
    """
    vocabulary = set(BLOCK_TYPES) | set(COUNT_KEYS)
    found = []
    for path in sorted((root / "src").rglob("*.py")) + sorted((root / "tests").rglob("*.py")):
        relative = str(path.relative_to(root))
        if relative == OWNER or relative in SPELLERS or imports_the_vocabulary(path):
            continue
        if any(len(names & vocabulary) >= 4 for names in literal_collections(path)):
            found.append(relative)
    return sorted(set(found))


def test_there_is_exactly_one_block_type_list():
    # ⛔ A test rather than a comment asking people not to write one. A copy
    # would sit in a reader's tuple, a fixture checker's count keys, its
    # block fields or its container tuple.
    # Two copies of a contract is the defect this project has diagnosed four
    # times, and a vocabulary that disagrees with its own checker means the
    # gate and the parser have different ideas of what a document may hold.
    assert copies(repository_root()) == []


def written(tmp_path: Path, name: str, body: str) -> Path:
    (tmp_path / "src").mkdir(exist_ok=True)
    (tmp_path / "tests").mkdir(exist_ok=True)
    path = tmp_path / "src" / name
    path.write_text(body, encoding="utf-8")
    return path


#: A module shaped like a copy of the vocabulary.
COPY = 'BLOCK_TYPES = ("heading", "para", "code", "table")\n'


def test_that_check_catches_a_copy_that_did_not_come_from_the_owner(tmp_path):
    # ⭐ The scanner is asserted against a module shaped like a copy of the
    # vocabulary, so "no offenders" is a result and not an artefact of the
    # scanner seeing nothing.
    written(tmp_path, "vocabulary.py", COPY)
    assert copies(tmp_path) == ["src/vocabulary.py"]


def test_and_clears_the_same_module_once_it_derives_from_the_owner(tmp_path):
    # ⭐ The other direction, and the one the rule turns on: identical literal,
    # cleared — because it is checked against the source of truth rather
    # than competing with it. ⛔ This is what makes the rule about *deriving*
    # rather than about *not spelling*, which is the distinction a narrowing to
    # definitions would have lost.
    written(tmp_path, "vocabulary.py", f"from {VOCABULARY_MODULE} import BLOCK_TYPES\n\n{COPY}")
    assert copies(tmp_path) == []


def test_a_re_export_does_not_count_as_deriving(tmp_path):
    # ⚠️ Stated so it is a decision rather than an oversight: importing the
    # vocabulary from something that re-exports it does not clear a module.
    # The point is to say where the names came from.
    written(
        tmp_path,
        "vocabulary.py",
        f"from tests.fixture_checks.vocabulary import BLOCK_TYPES  # not {VOCABULARY_MODULE}\n\n"
        + COPY,
    )
    assert copies(tmp_path) == ["src/vocabulary.py"]


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
    # ⭐ Two properties, so two rule ids: the counts object's own
    # key tuple is an ordering claim, and its values are a counting claim.
    # ⚠️ No fixture declares `key-order` today; naming it costs nothing and is
    # what makes the day one arrives a decision rather than a surprise.
    seen = 0
    for where, document in archive_documents(asserting={"counts", "key-order"}):
        assert tuple(document["counts"]) == EXPECTED_COUNT_KEYS, where
        assert document["counts"] == counts_of(document["blocks"]), where
        seen += 1
    # ⛔ The sweep's denominator, not `> 0`: `seen > 0` passes on a sweep that
    # read one document of twenty, and passes identically the day an exclusion
    # is widened by mistake. `coverage` states what this sweep was entitled to.
    assert seen == coverage(asserting={"counts", "key-order"}).swept


def test_every_block_type_in_the_fixtures_is_in_the_vocabulary():
    seen = set()
    read = 0
    for _where, document in archive_documents(asserting={"vocabulary"}):
        seen.update(block["type"] for block in walk(document["blocks"]))
        read += 1
    assert read == coverage(asserting={"vocabulary"}).swept
    assert seen <= set(BLOCK_TYPES)
    # ⚠️ And the fixtures exercise all of them, so the vocabulary is not
    # eleven types of which four are theoretical.
    assert seen == set(BLOCK_TYPES), sorted(set(BLOCK_TYPES) - seen)


def test_every_block_carries_exactly_the_fields_its_row_names():
    # ⚠️ `vocabulary` is one id covering both halves — `check_blocks` yields it
    # for an unknown type *and* for a known type with the wrong fields — so
    # this sweep and the one above name the same set, correctly.
    seen = 0
    for where, document in archive_documents(asserting={"vocabulary"}):
        for block in walk(document["blocks"]):
            assert tuple(block) == BLOCK_FIELDS[block["type"]], f"{where}: {block['type']}"
        seen += 1
    assert seen == coverage(asserting={"vocabulary"}).swept


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
    # ⛔ **An empty set, said deliberately rather than by omission.** No rule id
    # names a practice's three-section layout — no fixture declares it and no
    # check in `tests/fixture_checks/` yields it — so there is nothing to
    # exclude and every document is swept. ⚠️ Inventing an id here would be a
    # second vocabulary; if one is added to the checker, name it here, and
    # until then `sweeping` is what tells whoever hits the red to do that.
    seen = read = 0
    for where, document in archive_documents(asserting=()):
        read += 1
        layout = read_layout(document, where)
        assert (layout is not None) == (document["kind"] == "practice"), where
        if layout is not None:
            assert layout.starting_code == document["starting_code"]
            seen += 1
    # ⚠️ The denominator here is the practices, not the documents: this sweep
    # reads every document and asserts a property of the practices among them,
    # so its floor is pinned rather than derived. ⛔ Never `> 0`.
    assert seen >= 3, seen
    assert read == coverage(asserting=()).swept


def test_an_item_without_a_nested_list_is_its_one_string_part():
    # ⛔ An unnested item is unchanged, so every list before it reads alike.
    assert item_parts("one") == ["one"]


def test_an_item_with_a_nested_list_is_its_parts_in_reading_order():
    nested = {"type": "list", "ordered": False, "items": ["x"]}
    item = ["before", nested, "after"]
    assert item_parts(item) == ["before", nested, "after"]
    assert item_parts(item) is not item


def test_a_nested_list_is_not_a_block_in_reading_order():
    # ⚠️ It is part of its item: `counts` and `walk` see one list, not two.
    block = {"type": "list", "ordered": False, "items": [["a", {"type": "list", "items": []}]]}
    assert counts_of([block])["lists"] == 1
    assert list(walk([block])) == [block]


def test_start_is_the_one_optional_key_and_only_a_list_carries_it():
    # ⛔ An optional key sits after a block's fields, so the fields keep
    # their order and a block without it is unchanged.
    assert BLOCK_OPTIONAL == {name: (("start",) if name == "list" else ()) for name in BLOCK_TYPES}


@pytest.mark.parametrize(
    ("block", "start"),
    [({}, 1), ({"start": 3}, 3), ({"start": 0}, 0), ({"start": True}, 1), ({"start": "3"}, 1)],
)
def test_a_lists_start_is_one_unless_it_records_a_number(block, start):
    assert list_start({"type": "list", "ordered": True, "items": [], **block}) == start


def test_a_committed_ordered_list_with_no_start_keeps_its_documents_digest():
    # ⛔ The fixture's recorded digest carries no `start` key.
    path = repository_root() / (
        "tests/fixtures/depth2/archive/basics/01-getting-started/raw/java/unit-01/lesson-1.json"
    )
    document = json.loads(path.read_text(encoding="utf-8"))
    lists = [block for block in walk(document["blocks"]) if block["type"] == "list"]
    assert any(block["ordered"] for block in lists), "the fixture holds no ordered list"
    assert all("start" not in block for block in lists)
    assert document["content_sha256"] == content_sha256(document["blocks"])


# --------------------------------------------------------------------------
# ⛔ A block that is not an object is refused BY NAME, never `.get`-ed
# --------------------------------------------------------------------------

#: Everything `json.loads` can produce where a block belongs, but an object.
#: ⛔ Closed on the *domain* rather than on taste (a closed set, R6): JSON
#: has six value kinds and five of them are here, so the shape nobody thought
#: of cannot be the one that gets through.
NOT_OBJECTS = ("a string", 7, 1.5, True, None, ["nested"])


@pytest.mark.parametrize("block", NOT_OBJECTS)
def test_a_non_object_block_reaches_no_get_and_is_refused_by_name(block):
    # ⛔ `AttributeError` would name a TYPE where the reader needs an INDEX.
    # ⭐ `ArchiveError` is a `ValueError`, so an `AttributeError` escaping here
    # FAILS this test rather than passing it —
    # which is what makes the assertion an instrument and not a restatement.
    with pytest.raises(ArchiveError) as raised:
        counts_of([{"type": "para", "text": "one"}, block])

    assert "blocks[1]" in str(raised.value), "the refusal names which block"
    assert "a block is an object with a type" in str(raised.value)


def test_the_counts_of_a_document_of_objects_are_unchanged():
    # ⭐ The positive direction. Without it the refusal above is satisfied by a
    # `counts_of` that refuses everything.
    counted = counts_of([{"type": "para", "text": "one"}, {"type": "rule"}])

    assert tuple(counted) == EXPECTED_COUNT_KEYS
    assert counted["paras"] == 1
    assert counted["rules"] == 1


def test_the_refusal_describes_the_value_and_never_quotes_a_string():
    # ⚠️ R7: a refusal names what a value IS, never what it SAYS — `describe`'s
    # `SAFE_TO_QUOTE` is `(int,)`, so a block that is a string is *"a str"*.
    words = "the material's own sentence"

    with pytest.raises(ArchiveError) as raised:
        counts_of([words])

    assert words not in str(raised.value)
    assert "a str" in str(raised.value)


def test_the_caller_names_the_document_the_refusal_belongs_to():
    # ⭐ `where` is the document's own, spelled as `assert_clean`'s is, so the
    # builder's refusal says which FILE as well as which block.
    with pytest.raises(ArchiveError) as raised:
        counts_of(["x"], "solo/unit-1/lesson-1 blocks")

    assert "solo/unit-1/lesson-1 blocks[0]" in str(raised.value)


def test_a_non_object_block_inside_a_container_is_not_this_functions_business():
    # ⚠️ The boundary, asserted so it is not read as an oversight: `counts_of`
    # counts TOP-LEVEL blocks, so a malformed block inside a quote is
    # `validate.blocks`'s to name and this function neither counts nor refuses
    # it. ⛔ Widening it here would make `counts` disagree with what it means.
    quote = {"type": "quote", "blocks": ["not an object"]}

    assert counts_of([quote])["quotes"] == 1
