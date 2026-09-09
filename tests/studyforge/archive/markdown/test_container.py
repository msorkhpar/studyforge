"""Mirror of `src/studyforge/archive/markdown/container.py` (R12).

The two container blocks, and the fence-awareness that keeps a disclosure from
closing on a `</details>` somebody quoted inside a code fence.
"""

from __future__ import annotations

import pytest

from studyforge.archive.markdown import MarkdownError, parse
from studyforge.archive.markdown.container import find_close, read_disclosure, read_quote


def blocks(text: str, **kwargs) -> list[dict]:
    """Parse `text` and return its blocks."""
    return parse(text, **kwargs)


# --- quote holds blocks, not text -------------------------------------------


def test_a_quote_is_a_wrapper_block_holding_blocks():
    # ⚠️ The extraction source returns the inner blocks transparently, to agree
    # with its DOM reader. studyforge has no DOM reader to agree with, so the
    # reason does not carry over and the wrapper is correct here.
    assert blocks("> a quoted sentence\n") == [
        {"type": "quote", "blocks": [{"type": "para", "text": "a quoted sentence"}]}
    ]


def test_a_quote_can_hold_a_list_and_a_fence():
    # ⛔ The reason a container holds blocks rather than text: a `text`-only
    # quote loses exactly what *never silently drop* exists to keep.
    quoted = blocks("> - one\n> - two\n>\n> ```py\n> x = 1\n> ```\n")
    assert len(quoted) == 1
    inner = quoted[0]["blocks"]
    assert [block["type"] for block in inner] == ["list", "code"]
    assert inner[0]["items"] == ["one", "two"]
    assert inner[1]["lang"] == "py"


def test_a_quote_does_not_swallow_what_follows_it():
    assert [block["type"] for block in blocks("> quoted\n\nafter\n")] == ["quote", "para"]


def test_a_bare_marker_line_quotes_a_blank_line():
    quoted = blocks("> one\n>\n> two\n")[0]["blocks"]
    assert [block["text"] for block in quoted] == ["one", "two"]


def test_a_greater_than_inside_prose_is_not_a_quote():
    assert blocks("a > b is true\n") == [{"type": "para", "text": "a > b is true"}]


def test_read_quote_takes_the_dispatcher_rather_than_importing_it():
    # ⭐ The dependency is one-way by construction: the only recursing readers
    # receive `parse`, so nothing else in the package can loop back into the
    # document reader. Asserted with a stub, which is the other thing the
    # injection buys.
    seen = []

    def stub(text, *, lang_default=""):
        seen.append((text, lang_default))
        return [{"type": "para", "text": "stubbed"}]

    block, index = read_quote(["> a", "> b", "after"], 0, "java", stub)
    assert seen == [("a\nb", "java")]
    assert block == {"type": "quote", "blocks": [{"type": "para", "text": "stubbed"}]}
    assert index == 2


# --- disclosure is a container block, not markup and not one opaque string ---


def test_a_disclosure_holds_its_body_as_blocks():
    text = (
        "<details>\n"
        "<summary>Show the answer</summary>\n"
        "\n"
        "The answer is a query.\n"
        "\n"
        "```sparql\n"
        "SELECT ?s WHERE { ?s ?p ?o }\n"
        "```\n"
        "\n"
        "</details>\n"
    )
    assert blocks(text) == [
        {
            "type": "disclosure",
            "summary": "Show the answer",
            "open": False,
            "blocks": [
                {"type": "para", "text": "The answer is a query."},
                {"type": "code", "lang": "sparql", "text": "SELECT ?s WHERE { ?s ?p ?o }"},
            ],
        }
    ]


def test_the_body_is_recursed_into_rather_than_stored():
    # ⛔ The failure the rejected opaque-`html` reading had: a fenced query
    # inside the answer would not be a `code` block — uncounted, unhighlighted,
    # invisible to the block-count gate. A test asserting only that a
    # disclosure is present passes against a parser that stores and never looks
    # inside, which is why this asserts the inner types.
    text = "<details>\n<summary>s</summary>\n\n| a | b |\n| --- | --- |\n| 1 | 2 |\n\n</details>\n"
    inner = blocks(text)[0]["blocks"]
    assert [block["type"] for block in inner] == ["table"]
    assert inner[0]["rows"] == [["1", "2"]]


def test_the_authors_open_default_is_honoured_not_overridden():
    closed = blocks("<details>\n<summary>s</summary>\n\nx\n\n</details>\n")[0]
    opened = blocks("<details open>\n<summary>s</summary>\n\nx\n\n</details>\n")[0]
    assert closed["open"] is False
    assert opened["open"] is True


def test_the_open_attribute_is_read_in_its_several_spellings():
    for attrs in ("open", 'open=""', 'open="open"', "open=true", "class='x' open"):
        block = blocks(f"<details {attrs}>\n<summary>s</summary>\n\nx\n\n</details>\n")[0]
        assert block["open"] is True, attrs
    for attrs in ("class='x'", "data-opened='1'"):
        block = blocks(f"<details {attrs}>\n<summary>s</summary>\n\nx\n\n</details>\n")[0]
        assert block["open"] is False, attrs


def test_the_summary_is_content_and_survives_as_the_label():
    block = blocks("<details>\n<summary>Why there is no exercise</summary>\n\nx\n\n</details>\n")[0]
    assert block["summary"] == "Why there is no exercise"


def test_a_disclosure_with_no_summary_is_not_a_refusal():
    # ⚠️ Legal markup, and nothing is lost — the label is simply empty. Only
    # material that cannot be represented without loss raises.
    block = blocks("<details>\n\nthe body survives\n\n</details>\n")[0]
    assert block["summary"] == ""
    assert block["blocks"] == [{"type": "para", "text": "the body survives"}]


# --- fence awareness, which is the constraint that actually bites ------------


def test_a_fenced_details_does_not_close_the_disclosure_around_it():
    # ⛔ THE measured constraint. Material that teaches HTML quotes `<details>`
    # inside a fence; a line-by-line scan for the closing tag stops inside the
    # fence, ends the withheld section early and spills the answer onto the
    # page. Fails silently everywhere else, which is why it has its own test.
    text = (
        "<details>\n"
        "<summary>Show the answer</summary>\n"
        "\n"
        "```html\n"
        "<details>\n"
        "  <summary>Not a disclosure</summary>\n"
        "</details>\n"
        "```\n"
        "\n"
        "still inside the withheld section\n"
        "\n"
        "</details>\n"
        "\n"
        "after\n"
    )
    parsed = blocks(text)
    assert [block["type"] for block in parsed] == ["disclosure", "para"]
    assert [block["type"] for block in parsed[0]["blocks"]] == ["code", "para"]
    assert parsed[0]["blocks"][1]["text"] == "still inside the withheld section"
    assert parsed[1]["text"] == "after"


def test_a_fenced_details_outside_any_disclosure_stays_code():
    parsed = blocks("```html\n<details>\n<summary>s</summary>\n</details>\n```\n")
    assert [block["type"] for block in parsed] == ["code"]
    assert parsed[0]["lang"] == "html"


def test_a_nested_disclosure_closes_its_own_tag_first():
    text = (
        "<details>\n<summary>outer</summary>\n\n"
        "<details>\n<summary>inner</summary>\n\nx\n\n</details>\n\n"
        "after the inner one\n\n</details>\n"
    )
    outer = blocks(text)[0]
    assert outer["summary"] == "outer"
    assert [block["type"] for block in outer["blocks"]] == ["disclosure", "para"]
    assert outer["blocks"][0]["summary"] == "inner"


def test_find_close_reports_the_matching_line():
    lines = ["<details>", "<summary>s</summary>", "</details>", "after"]
    assert find_close(lines, 0) == 2
    assert find_close(["<details>", "no close"], 0) is None


def test_an_unclosed_disclosure_raises_rather_than_absorbing_the_document():
    # ⛔ Worse than an unclosed fence: the reader cannot even see what went
    # missing, because a withheld section is hidden by definition.
    with pytest.raises(MarkdownError) as raised:
        blocks("<details>\n<summary>s</summary>\n\nthe rest of the document\n")
    assert "never closed" in str(raised.value)
    assert "line 1" in str(raised.value)


def test_an_unclosed_fence_inside_a_disclosure_names_the_fence():
    # ⚠️ The right failure: an unclosed fence inside a withheld section is
    # still an unclosed fence, and the message points at the real defect.
    with pytest.raises(MarkdownError) as raised:
        blocks("<details>\n<summary>s</summary>\n\n```py\nx = 1\n\n</details>\n")
    assert "code fence" in str(raised.value)


def test_read_disclosure_takes_the_dispatcher_too():
    def stub(text, *, lang_default=""):
        return [{"type": "para", "text": text.strip()}]

    lines = ["<details open>", "<summary>label</summary>", "body", "</details>", "after"]
    block, index = read_disclosure(lines, 0, "", stub)
    assert block == {
        "type": "disclosure",
        "summary": "label",
        "open": True,
        "blocks": [{"type": "para", "text": "body"}],
    }
    assert index == 4
