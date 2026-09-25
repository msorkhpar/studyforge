"""Mirror of `src/studyforge/render/page/code.py` (R12): a lesson's code links, and their panel.

⭐ `mark` is read on the one anchor shape the markup writes, from a page whose
place is known, and the build's end of it — a written page — is read in
`tests/studyforge/generate/test_linked_files.py`.
"""

from __future__ import annotations

from dataclasses import replace

import pytest

from studyforge.render.markup import inline
from studyforge.render.page import code
from studyforge.render.templates import placeholders
from tests.studyforge.render.page.pages import sample_placement

#: The sample page sits at `out/units/unit-01/`; three levels up is the corpus root.
UP = "../../../"
JAVA = replace(sample_placement(), code=(".java",))


def link(href: str, words: str = "Types.java") -> str:
    return inline(f"[{words}]({href})")


def test_a_link_to_a_code_file_is_marked_with_its_corpus_relative_path():
    body, found = code.mark(link(f"{UP}m/src/test/java/p/TypesTest.java"), JAVA)
    assert found == ("m/src/test/java/p/TypesTest.java",)
    assert f'href="{UP}m/src/test/java/p/TypesTest.java"' in body, "the href is W488's, kept"
    assert 'data-code-path="m/src/test/java/p/TypesTest.java"' in body


def test_each_file_is_named_once_in_the_order_the_page_links_it():
    body = link(f"{UP}b/B.java") + link(f"{UP}a/A.java") + link(f"{UP}b/B.java")
    assert code.mark(body, JAVA)[1] == ("b/B.java", "a/A.java")


@pytest.mark.parametrize(
    "href",
    [
        f"{UP}m/pom.xml",
        f"{UP}.studyforge/x/Types.java",
        "../../../../outside/Types.java",
        "https://example.invalid/Types.java",
        "#types",
        f"{UP}m/Types.java#top".replace("Types.java#top", "README.md"),
    ],
)
def test_a_link_that_is_not_a_code_file_of_the_corpus_is_left_alone(href):
    body = link(href)
    assert code.mark(body, JAVA) == (body, ())


def test_an_encoded_path_is_named_as_the_file_it_is():
    assert code.mark(link(f"{UP}m/My%20Types.java"), JAVA)[1] == ("m/My Types.java",)


def test_a_corpus_that_declares_no_code_marks_nothing_and_the_page_is_unchanged():
    # ⭐ The first corpus's case, and a site written away from its corpus's files.
    body = link(f"{UP}m/Types.java")
    assert code.mark(body, sample_placement()) == (body, ())
    assert code.render((), sample_placement()) == ""


def test_a_link_inside_a_code_block_is_text_and_never_a_link():
    body = '<pre><code>&lt;a href="../../../m/A.java" rel="noopener noreferrer"&gt;</code></pre>'
    assert code.mark(body, JAVA) == (body, ())


def test_the_panel_ships_saying_why_the_file_is_plain_text_and_hides_the_copy_sentence():
    panel = code.render(("m/Types.java",), JAVA)
    assert '<section data-code data-corpus="demo"' in panel
    plain = panel.split('data-practice-part="plain"', 1)[1].split("</p>", 1)[0]
    assert "hidden" not in plain.split(">", 1)[0]
    assert "because the course's editor is not running here" in plain
    copy = panel.split('data-practice-part="copy"', 1)[1].split(">", 1)[0]
    assert "hidden" in copy
    assert "copy of the course's code" in panel and "never changed" in panel
    # ⛔ The page names no API, no origin and no port (R8).
    assert "/api/" not in panel and "127.0.0.1" not in panel
    assert placeholders(code.CODE_TEMPLATE) == frozenset({"corpus"})
