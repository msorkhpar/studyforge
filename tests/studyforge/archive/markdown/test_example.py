"""`example_block` and `blocks_of`: an example region read into the archive's `example` block."""

from __future__ import annotations

import pytest

from studyforge.archive.markdown import MarkdownError, blocks_of, example_block, regions

LABELS = {"aa": "aa", "alias": "aa", "bb": "bb"}

PAGE = """Intro words.

<!-- example: ex-1 tabs: aa,bb -->
```aa
first
```
```text
first printed
```
```bb
second
```
<!-- /example -->

Closing words.
"""


def only(text: str):
    return regions(text)[0]


def test_an_example_is_one_block_holding_its_fences_flat_and_cut_into_spans():
    blocks = blocks_of(regions(PAGE), LABELS)
    assert [block["type"] for block in blocks] == ["para", "example", "para"]
    example = blocks[1]
    assert list(example) == ["type", "id", "tabs", "blocks"]
    assert example["id"] == "ex-1"
    assert example["tabs"] == [{"lang": "aa", "span": 2}, {"lang": "bb", "span": 1}]
    assert [block["lang"] for block in example["blocks"]] == ["aa", "text", "bb"]


def test_a_fence_label_that_a_language_declares_opens_that_languages_tab():
    text = "<!-- example: e tabs: aa -->\n```alias\nx\n```\n<!-- /example -->"
    assert example_block(only(text), LABELS)["tabs"] == [{"lang": "aa", "span": 1}]


def test_the_output_word_is_carried_only_when_the_header_writes_one():
    text = "<!-- example: e tabs: aa output: compiler -->\n```aa\nx\n```\n<!-- /example -->"
    assert example_block(only(text), LABELS)["output"] == "compiler"
    assert "output" not in blocks_of(regions(PAGE), LABELS)[1]


@pytest.mark.parametrize(
    ("body", "fragment"),
    [
        ("prose between\n```aa\nx\n```", "code fences and nothing else"),
        ("```text\nx\n```\n```aa\ny\n```", "opens with the fence"),
        ("```bb\nx\n```\n```aa\ny\n```", "each once and in the order"),
        ("```aa\nx\n```", "each once and in the order"),
    ],
)
def test_a_shape_that_is_not_the_headers_tabs_is_refused_by_line(body: str, fragment: str):
    header = "<!-- example: e tabs: aa,bb -->"
    with pytest.raises(MarkdownError) as refused:
        example_block(only(f"{header}\n{body}\n<!-- /example -->"), LABELS)
    assert fragment in str(refused.value) and "line 1" in str(refused.value)


def test_a_page_with_no_example_reads_exactly_as_parse_reads_it():
    from studyforge.archive.markdown import parse

    text = "# Title\n\nSome words.\n\n```aa\ncode\n```\n"
    assert blocks_of(regions(text), LABELS) == parse(text)
