"""An `example` block on disk: the shape `validate` reads and the tabs it checks."""

from __future__ import annotations

import pytest

from studyforge.validate import validate
from studyforge.validate.blocks import block_problems
from tests.studyforge.validate import corpora
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


def many(count):
    langs = [f"l{n}" for n in range(count)]
    return example(
        tabs=[{"lang": x, "span": 1} for x in langs],
        blocks=[{"type": "code", "lang": x, "text": x} for x in langs],
    )


@pytest.mark.parametrize("count", [1, 2, 3, 4, 8])
def test_an_example_of_one_to_eight_tabs_has_no_problem(count):
    assert problems(many(count)) == []


def test_an_example_of_more_than_eight_tabs_is_refused():
    found = problems(many(9))
    assert found == [("blocks[0].tabs", "has 9 tabs; an example has at most 8")]


def test_four_tabs_in_four_declared_languages_are_valid_and_an_undeclared_fourth_is_named(
    tmp_path,
):
    from tests.studyforge.generate import four_corpus as four

    good = four.example("quad", four.LANGS)
    bad = four.example("quad", (*four.LANGS[:3], "zz"))
    for name, block, expected in (("good", good, []), ("bad", bad, ["language-undeclared"])):
        units = [corpora.unit_entry(1, origin="src/one.md")]
        root = corpora.write(
            tmp_path / name,
            manifest={**corpora.MANIFEST, **four.declared()},
            containers={"demo": corpora.container(units)},
            documents={
                "demo/raw/prose/unit-01/lesson-1.json": {**document(), "blocks": [block]}
            },
        )
        assert [f.rule for f in validate(root).findings if f.rule == "language-undeclared"] == (
            expected
        )


def test_a_tab_may_name_the_code_file_it_shows_and_nothing_else_is_added_to_it():
    tabs = [{"lang": "aa", "span": 2, "code": "examples/x/a.py"}, {"lang": "bb", "span": 1}]
    assert problems(example(tabs=tabs)) == []
    unsafe = [{"lang": "aa", "span": 2, "code": "../x.py"}, {"lang": "bb", "span": 1}]
    assert [at for at, _ in problems(example(tabs=unsafe))] == ["blocks[0].tabs[0].code"]
    extra = [{"lang": "aa", "span": 2, "run": "x"}, {"lang": "bb", "span": 1}]
    assert problems(example(tabs=extra))[0][0] == "blocks[0].tabs[0]"


def test_a_code_file_the_corpus_does_not_hold_is_named_and_one_it_holds_is_not(tmp_path):
    tabs = [{"lang": "aa", "span": 2, "code": "examples/x/a.py"}, {"lang": "bb", "span": 1}]
    block = example(tabs=tabs)
    root = corpus(tmp_path / "missing", [{**document(), "blocks": [block]}])
    missing = [f for f in validate(root).findings if f.rule == "example-code-missing"]
    assert len(missing) == 1 and "'aa'" in missing[0].message
    assert "examples" not in missing[0].message
    held = corpus(tmp_path / "held", [{**document(), "blocks": [block]}])
    (held / "examples" / "x").mkdir(parents=True)
    (held / "examples" / "x" / "a.py").write_text("x = 1\n", encoding="utf-8")
    assert [f for f in validate(held).findings if f.rule == "example-code-missing"] == []


def test_an_example_may_declare_support_paths_and_only_safe_ones():
    assert problems(example(support=["harness", "examples/_shared/util.py"])) == []
    assert [at for at, _ in problems(example(support=["../x"]))] == ["blocks[0].support[0]"]
    assert [at for at, _ in problems(example(support=[]))] == ["blocks[0].support"]
    assert [at for at, _ in problems(example(support="harness"))] == ["blocks[0].support"]
    assert [at for at, _ in problems(example(support=[3]))] == ["blocks[0].support[0]"]


def released(tmp_path, tab_code, support=None):
    tabs = [{"lang": "aa", "span": 2, "code": tab_code}, {"lang": "bb", "span": 1}]
    block = example(tabs=tabs, **({} if support is None else {"support": support}))
    root = corpus(tmp_path, [{**document(), "blocks": [block]}])
    (root / "examples" / "x").mkdir(parents=True)
    (root / "examples" / "x" / "a.py").write_text("x = 1\n", encoding="utf-8")
    (root / "harness").mkdir()
    (root / "harness" / "h.py").write_text("y = 2\n", encoding="utf-8")
    (root / "stash" / ".cache").mkdir(parents=True)
    (root / "stash" / ".cache" / "a.py").write_text("z\n", encoding="utf-8")
    return root


def findings(root, rule):
    return [f for f in validate(root).findings if f.rule == rule]


def test_a_code_file_the_release_would_not_carry_is_refused(tmp_path):
    root = released(tmp_path / "hid", "stash/.cache/a.py")
    refused = findings(root, "example-code-unreleased")
    assert len(refused) == 1 and "cache" not in refused[0].message
    assert findings(released(tmp_path / "ok", "examples/x/a.py"), "example-code-unreleased") == []


def test_a_support_path_must_be_a_released_file_or_folder_of_the_corpus(tmp_path):
    ok = released(tmp_path / "ok", "examples/x/a.py", ["harness"])
    assert findings(ok, "example-support-missing") == []
    for bad in (["nowhere"], ["stash/.cache"], ["archive"]):
        root = released(tmp_path / bad[0].replace("/", "_"), "examples/x/a.py", bad)
        assert len(findings(root, "example-support-missing")) == 1, bad
