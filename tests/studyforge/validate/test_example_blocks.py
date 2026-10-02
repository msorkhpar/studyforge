"""An `example` block on disk: the shape `validate` reads and the tabs it checks."""

from __future__ import annotations

from studyforge.validate import validate
from studyforge.validate.blocks import block_problems
from tests.studyforge.validate.test_languages import READING, corpus, document, rules


def example(**changes):
    block = {
        "type": "example",
        "id": "ex",
        "tabs": [{"lang": "aa", "span": 2}, {"lang": "bb", "span": 1}],
        "blocks": [
            {"type": "code", "lang": "aa", "text": "a"},
            {"type": "code", "lang": "text", "text": "out"},
            {"type": "code", "lang": "bb", "text": "b"},
        ],
    }
    return {**block, **changes}


def problems(block):
    return [(at, what) for at, what in block_problems([block])]


def test_a_well_formed_example_has_no_problem():
    assert problems(example()) == []
    assert problems(example(output="compiler")) == []
    assert problems(example(output="warning")) == []


def test_a_repeated_language_is_refused():
    block = example(tabs=[{"lang": "aa", "span": 2}, {"lang": "aa", "span": 1}])
    assert [what for _, what in problems(block)] == [
        "repeats a language; the tabs of an example name distinct ones"
    ]


def test_spans_that_do_not_cover_the_blocks_are_refused():
    short = example(tabs=[{"lang": "aa", "span": 1}, {"lang": "bb", "span": 1}])
    assert [at for at, _ in problems(short)] == ["blocks[0].tabs"]
    zero = example(tabs=[{"lang": "aa", "span": 0}, {"lang": "bb", "span": 3}])
    assert any(at == "blocks[0].tabs[0].span" for at, _ in problems(zero))


def test_a_tab_that_is_not_an_object_with_a_language_and_a_span_is_refused():
    assert problems(example(tabs=["aa"]))[0][0] == "blocks[0].tabs[0]"
    assert problems(example(tabs=[]))[0][0] == "blocks[0].tabs"


def test_an_output_outside_the_vocabulary_and_a_block_that_is_not_code_are_refused():
    assert problems(example(output="runtime"))[0][0] == "blocks[0].output"
    odd = example(blocks=[{"type": "para", "text": "x"}], tabs=[{"lang": "aa", "span": 1}])
    assert [at for at, _ in problems(odd)] == ["blocks[0].blocks[0]"]


def test_an_example_with_no_id_is_refused():
    assert problems(example(id=""))[0][0] == "blocks[0].id"


def test_a_tab_in_a_language_the_corpus_does_not_declare_is_named(tmp_path):
    tabs = [{"lang": "aa", "span": 1}, {"lang": "zz", "span": 1}]
    block = example(tabs=tabs, blocks=example()["blocks"][:1] + example()["blocks"][2:])
    root = corpus(tmp_path, [{**document(), "blocks": [block]}])
    report = validate(root)
    assert "language-undeclared" in rules(report)
    assert "'zz'" in " ".join(f.message for f in report.findings)


def test_the_tabs_of_a_declared_pair_are_valid(tmp_path):
    root = corpus(tmp_path, [{**document(), "blocks": [example()]}])
    assert [f for f in validate(root).findings if f.rule == "language-undeclared"] == []
    assert READING["languages"][0]["id"] == "aa"
