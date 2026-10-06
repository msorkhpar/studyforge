"""`regions`: a page cut at its language sections and example blocks, by line."""

from __future__ import annotations

import pytest

from studyforge.archive.markdown import MarkdownError, Region, parse, regions, undeclared

PAGE = """Common opening.

<!-- lang: aa -->
<!-- aa-unit: 1.1.1 -->
Prose in aa.
<!-- /lang -->

<!-- example: ex-1 tabs: aa,bb -->
```aa
code
```
<!-- /example -->

<!-- lang: bb -->
Prose in bb.
<!-- /lang -->

Common closing.
"""


def test_a_page_with_no_marker_is_one_common_region():
    found = regions("# Title\n\nSome text.\n")
    assert [(r.kind, r.lang, r.text) for r in found] == [("common", None, "# Title\n\nSome text.")]


def test_a_page_is_cut_in_order_into_common_sections_and_examples():
    found = regions(PAGE)
    assert [(r.kind, r.lang) for r in found] == [
        ("common", None),
        ("lang", "aa"),
        ("example", None),
        ("lang", "bb"),
        ("common", None),
    ]
    assert found[1].text == "Prose in aa."
    assert found[1].unit_ref == "1.1.1"
    assert found[3].unit_ref is None
    assert [r.line for r in found] == [1, 3, 8, 14, 18]


def test_an_example_carries_its_id_tabs_and_output():
    one = regions("<!-- example: e tabs: aa output: compiler -->\nx\n<!-- /example -->")[0]
    assert (one.id, one.tabs, one.output, one.languages) == ("e", ("aa",), "compiler", ("aa",))
    assert regions(PAGE)[2].output is None


def test_a_region_names_the_languages_it_is_written_in():
    found = regions(PAGE)
    assert [r.languages for r in found] == [(), ("aa",), ("aa", "bb"), ("bb",), ()]


def test_the_text_of_a_region_parses_to_blocks_and_the_markers_are_not_blocks():
    blocks = [parse(r.text) for r in regions(PAGE)]
    assert blocks[1] == [{"type": "para", "text": "Prose in aa."}]
    assert all(b["type"] != "html" for part in blocks for b in part)


def test_blank_common_text_between_regions_is_not_a_region():
    two = "<!-- lang: aa -->\nx\n<!-- /lang -->\n\n\n<!-- lang: bb -->\ny\n<!-- /lang -->"
    found = regions(two)
    assert [r.kind for r in found] == ["lang", "lang"]


def test_a_marker_inside_a_code_fence_is_code():
    text = "```text\n<!-- lang: aa -->\n```\n"
    found = regions(text)
    assert len(found) == 1
    assert found[0].kind == "common"
    assert "<!-- lang: aa -->" in found[0].text


def test_another_comment_is_left_in_the_text():
    found = regions("<!-- note -->\ntext\n")
    assert found[0].text == "<!-- note -->\ntext"


def test_crlf_text_reads_as_lf_text():
    assert regions(PAGE.replace("\n", "\r\n")) == regions(PAGE)


def test_the_languages_a_page_uses_and_a_corpus_does_not_declare_are_named_in_order():
    assert undeclared(regions(PAGE), {"aa"}) == ["bb"]
    assert undeclared(regions(PAGE), {"aa", "bb"}) == []
    assert undeclared(regions("plain"), set()) == []


@pytest.mark.parametrize(
    ("text", "fragment"),
    [
        ("<!-- lang: aa -->\nx\n", "line 1: a language section is never closed"),
        ("<!-- example: e tabs: aa -->\nx\n", "line 1: an example is never closed"),
        ("x\n<!-- /lang -->\n", "line 2: a language section is closed and none is open"),
        ("<!-- /example -->", "line 1: an example is closed and none is open"),
        ("<!-- lang: aa -->\n<!-- lang: bb -->", "line 2: a section or example opens inside"),
        ("<!-- lang: aa -->\n<!-- example: e tabs: aa -->", "line 2: a section or example"),
        ("<!-- lang: aa -->\nx\n<!-- /example -->", "line 3: an example closes a language section"),
        ("<!-- lang: Kotlin -->\nx\n<!-- /lang -->", "line 1: a language is named by"),
        ("<!-- example: e -->\nx\n<!-- /example -->", "line 1: an example names its tabs"),
        ("<!-- example: tabs: aa -->\nx\n<!-- /example -->", "line 1: an example names its id"),
        ("<!-- example: e tabs: aa,aa -->\nx\n<!-- /example -->", "distinct languages"),
        ("<!-- example: e tabs: aa,,bb -->\nx\n<!-- /example -->", "line 1: a tab is named by"),
        ("<!-- example: E tabs: aa -->\nx\n<!-- /example -->", "line 1: an example is named by"),
        ("<!-- example: e tabs: aa foo: x -->\nx\n<!-- /example -->", "tabs and output"),
        ("<!-- example: e tabs: aa tabs: bb -->\nx\n<!-- /example -->", "tabs and output"),
        ("<!-- example: e tabs: aa stray -->\nx\n<!-- /example -->", "text the grammar lacks"),
        ("<!-- lang: aa -->\n<!-- bb-unit: 2 -->\n<!-- /lang -->", "its section's language"),
    ],
)
def test_a_marker_the_grammar_cannot_read_is_refused_by_line(text, fragment):
    with pytest.raises(MarkdownError) as refused:
        regions(text)
    assert fragment in str(refused.value)


def test_a_refusal_never_quotes_the_text_it_refuses():
    secret = "/" + "home/someone/x"
    with pytest.raises(MarkdownError) as refused:
        regions(f"<!-- lang: {secret} -->\nx\n<!-- /lang -->")
    assert secret not in str(refused.value)


def test_regions_are_immutable_values():
    assert isinstance(regions("x")[0], Region)
    with pytest.raises(AttributeError):
        regions("x")[0].text = "y"


def test_a_section_may_name_several_languages_and_is_each_of_them():
    found = regions("<!-- lang: aa,bb -->\nBoth.\n<!-- /lang -->")
    assert [(r.kind, r.lang, r.languages) for r in found] == [("lang", "aa bb", ("aa", "bb"))]
    assert undeclared(found, {"aa"}) == ["bb"]


def test_a_unit_marker_may_use_any_language_the_section_names():
    page = "<!-- lang: aa,bb -->\n<!-- bb-unit: 2 -->\nx\n<!-- /lang -->"
    assert regions(page)[0].unit_ref == "2"


@pytest.mark.parametrize(
    "marker", ["<!-- lang: aa,aa -->", "<!-- lang: aa, bb -->", "<!-- lang: aa,Bb -->"]
)
def test_a_section_that_repeats_a_language_or_spells_the_list_oddly_is_refused(marker):
    with pytest.raises(MarkdownError):
        regions(f"{marker}\nx\n<!-- /lang -->")


def test_an_example_has_at_most_as_many_tabs_as_the_archive_allows():
    import importlib

    from studyforge.archive import example

    module = importlib.import_module("studyforge.archive.markdown.regions")

    assert module.MAX_TABS == example.EXAMPLE_MAX_TABS
    ids = [f"l{n}" for n in range(example.EXAMPLE_MAX_TABS + 1)]
    ok = ",".join(ids[:-1])
    assert regions(f"<!-- example: e tabs: {ok} -->\nx\n<!-- /example -->")[0].tabs
    with pytest.raises(MarkdownError, match="at most 8 tabs"):
        regions(f"<!-- example: e tabs: {','.join(ids)} -->\nx\n<!-- /example -->")
