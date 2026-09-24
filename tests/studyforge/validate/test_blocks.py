"""Mirror of `src/studyforge/validate/blocks.py` (R12) — every block's shape, through ONE reader.

⛔ **A `list`'s shape, and every type and field set.** `validate` refuses by
where it sits every block spec §6 does not admit, at any depth, and
`tests/fixture_checks.check_blocks` says the same, at the same path, through the same function:

| the block | ⛔ the expectation, written BEFORE the run |
|---|---|
| every shape §6 admits, nested lists and `start` included | clean in both |
| an item that is neither a string nor an array of strings and lists | `document`, exit `1`, named |
| the same, inside a quote and a nested list | named at its full depth |
| `start` that is not an integer (a string, a boolean, a float) | named; `0` is admitted |
| a key out of order or unknown | named |
| ⛔ An unknown type, or keys not its fields then its optional ones | named, any depth |
| the reader planted to say something | ⭐ both consumers repeat it — one reader, never two |
"""

from __future__ import annotations

import json

import pytest

from studyforge.archive.document import content_sha256
from studyforge.validate import blocks as block_shapes
from studyforge.validate import validate
from tests.fixture_checks import shape
from tests.fixture_checks.shape import check_blocks
from tests.studyforge.validate import corpora


def _list(items, ordered=False, **extra):
    return {"type": "list", "ordered": ordered, "items": items, **extra}


#: ⭐ Every shape §6 admits: strings, arrays of text and whole lists, nesting, and `start`.
ADMITTED = [
    {"type": "para", "text": "Prose."},
    _list(["one", "two"]),
    _list(
        ["a", ["b", _list(["c", ["d", _list(["e"])]], ordered=True, start=0), "after"]],
        ordered=True,
        start=3,
    ),
    {"type": "quote", "blocks": [_list(["quoted"])]},
    _list([]),
    # ⭐ Every other type with exactly its fields, and containers at depth.
    {"type": "heading", "level": 2, "text": "A heading"},
    {"type": "code", "lang": "python", "text": "x = 1"},
    {"type": "table", "headers": ["a"], "rows": [["b"]]},
    {"type": "image", "src": "a.png", "alt": "an image", "width": None},
    {"type": "video", "src": "a.mp4", "title": "a video"},
    {"type": "rule"},
    {"type": "html", "text": "<br>"},
    {
        "type": "disclosure",
        "summary": "more",
        "open": False,
        "blocks": [{"type": "quote", "blocks": [_list(["deep"], ordered=True, start=2)]}],
    },
]

#: ⛔ `(the blocks, where the problem must be named)`.
MALFORMED = {
    "an integer item": ([_list(["a", 42])], "blocks[0].items[1]"),
    "an object item": ([_list([{"text": "a"}])], "blocks[0].items[0]"),
    "a number inside an item's array": ([_list([["a", 7]])], "blocks[0].items[0][1]"),
    "a paragraph inside an item's array": (
        [_list([["a", {"type": "para", "text": "x"}]])],
        "blocks[0].items[0][1]",
    ),
    "items that are not an array": ([_list("a")], "blocks[0].items"),
    "a bad item at depth": (
        [{"type": "quote", "blocks": [_list([["a", _list([42])]])]}],
        "blocks[0].blocks[0].items[0][1].items[0]",
    ),
    "a string start": ([_list(["a"], ordered=True, start="2")], "blocks[0].start"),
    "a boolean start": ([_list(["a"], ordered=True, start=True)], "blocks[0].start"),
    "a float start": ([_list(["a"], ordered=True, start=1.5)], "blocks[0].start"),
    "a nested list's bad start": (
        [_list([["a", _list(["b"], ordered=True, start="x")]])],
        "blocks[0].items[0][1].start",
    ),
    "start before items": (
        [{"type": "list", "ordered": True, "start": 2, "items": ["a"]}],
        "blocks[0] has keys",
    ),
    "an unknown key": ([_list(["a"], numbering="roman")], "blocks[0] has keys"),
    # ⛔ Any type's field set, and a type the vocabulary does not name.
    "an unknown type": ([{"type": "aside", "text": "x"}], "blocks[0] has type a str"),
    "no type at all": ([{"text": "x"}], "blocks[0] has type"),
    "a paragraph with an extra key": (
        [{"type": "para", "text": "x", "lang": "en"}],
        "blocks[0] has keys",
    ),
    "a heading missing a field": ([{"type": "heading", "text": "x"}], "blocks[0] has keys"),
    "a code block's keys out of order": (
        [{"type": "code", "text": "x", "lang": "python"}],
        "blocks[0] has keys",
    ),
    "an image carrying a list's optional key": (
        [{"type": "image", "src": "a.png", "alt": "a", "width": None, "start": 2}],
        "blocks[0] has keys",
    ),
    "an unknown type inside a disclosure": (
        [{"type": "disclosure", "summary": "s", "open": True, "blocks": [{"type": "aside"}]}],
        "blocks[0].blocks[0] has type a str",
    ),
    "an extra key on a list nested in a quoted item": (
        [{"type": "quote", "blocks": [_list([["a", _list(["b"], numbering="x")]])]}],
        "blocks[0].blocks[0].items[0][1] has keys",
    ),
}


def test_every_shape_section_6_admits_reads_clean_in_validate_and_the_fixture_check(tmp_path):
    # ⭐ Clause 2: nothing admitted is refused, by either consumer.
    report = validate(corpora.one_unit(tmp_path / "c", blocks=ADMITTED))
    assert report.findings == (), [f.line() for f in report.findings]
    assert list(check_blocks({"blocks": ADMITTED}, "doc")) == []


@pytest.mark.parametrize("case", sorted(MALFORMED))
def test_a_malformed_list_is_refused_BY_WHERE_IT_SITS_exit_1(tmp_path, case):
    # ⛔ Clause 1: `document`, exit 1, the place named.
    blocks, named = MALFORMED[case]
    report = validate(
        corpora.one_unit(tmp_path / "c", blocks=[{"type": "para", "text": "x"}, *blocks])
    )
    assert report.rules == ("document",), [f.line() for f in report.findings]
    assert report.exit_code == 1
    shifted = named.replace("blocks[0]", "blocks[1]", 1)
    assert any(shifted in finding.message for finding in report.findings), report.findings


@pytest.mark.parametrize("case", sorted(MALFORMED))
def test_the_fixture_check_names_the_SAME_place(case):
    # ⛔ Clause 2's other half: the harness agrees with `validate`, case by case, and at the
    # SAME path, because it hands the reader the whole block list.
    blocks, named = MALFORMED[case]
    said = [message for rule, message in check_blocks({"blocks": blocks}, "doc")]
    assert said, f"the fixture check read {case} as clean"
    assert all(rule == "vocabulary" for rule, _ in check_blocks({"blocks": blocks}, "doc"))
    assert any(f"doc {named}" in message for message in said), said


def test_ONE_reader_a_planted_reader_speaks_through_BOTH_consumers(tmp_path, monkeypatch):
    # ⛔ Never a second copy: plant the reader, and both consumers repeat what it says.
    root = corpora.one_unit(tmp_path / "c", blocks=[_list(["clean"])])
    assert validate(root).findings == (), "⛔ born vacuous: the control must read clean"
    monkeypatch.setattr(
        block_shapes,
        "block_problems",
        lambda blocks, where="blocks": iter([("planted-where", "planted-what")]),
    )
    assert any("planted-where planted-what" in f.message for f in validate(root).findings)
    # ⭐ A paragraph, not a list, so every type reaches the reader, not only `list`.
    said = [
        message
        for _rule, message in check_blocks({"blocks": [{"type": "para", "text": "x"}]}, "doc")
    ]
    assert said == ["doc planted-where planted-what"], said


def test_the_fixture_check_holds_no_vocabulary_of_its_own():
    # ⛔ Never a second copy: the harness's module imports no field or type table to decide with.
    for name in ("BLOCK_FIELDS", "BLOCK_OPTIONAL", "BLOCK_TYPES", "CONTAINER_TYPES"):
        assert not hasattr(shape, name), f"tests/fixture_checks/shape.py still holds {name}"


def test_a_list_carrying_start_AFTER_its_fields_is_not_a_vocabulary_error():
    # ⭐ The optional key after the fields is admitted by the fixture check.
    assert list(check_blocks({"blocks": [_list(["a"], ordered=True, start=4)]}, "doc")) == []


def test_every_OTHER_type_still_carries_exactly_its_fields():
    # ⛔ The optional-key allowance is per type, and `para` names none.
    said = list(check_blocks({"blocks": [{"type": "para", "text": "x", "start": 2}]}, "doc"))
    assert [rule for rule, _ in said] == ["vocabulary"], said


def test_a_block_that_is_not_an_object_is_named_and_validate_never_raises(tmp_path):
    # ⛔ R6: every check yields. `check_counts` read a type off every block and raised on this
    # shape. The archive's builder cannot write it, so it is edited into the written document.
    root = corpora.one_unit(tmp_path / "c", blocks=[{"type": "para", "text": "x"}])
    [path] = (root / "archive").rglob("lesson-1.json")
    document = json.loads(path.read_text(encoding="utf-8"))
    document["blocks"].append("just text")
    document["content_sha256"] = content_sha256(document["blocks"])
    path.write_text(json.dumps(document), encoding="utf-8")

    report = validate(root)

    assert report.rules == ("document",), [f.line() for f in report.findings]
    assert report.exit_code == 1
    assert any("blocks[1] is a str; a block is an object" in f.message for f in report.findings)
    said = [message for _rule, message in check_blocks({"blocks": document["blocks"]}, "doc")]
    assert said == ["doc blocks[1] is a str; a block is an object with a type"], said
