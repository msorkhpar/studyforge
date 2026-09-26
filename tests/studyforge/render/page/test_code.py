"""Mirror of `src/studyforge/render/page/code.py` (R12): a lesson's code links, and their panel.

⭐ `mark` is read on the one anchor shape the markup writes, from a page whose
place is known, and the build's end of it — a written page — is read in
`tests/studyforge/generate/test_linked_files.py`.
"""

from __future__ import annotations

import re
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
    assert f'href="{UP}m/src/test/java/p/TypesTest.java"' in body, "the plain view's href is kept"
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
    assert code.examples(body, (), sample_placement()) == body


def test_a_link_inside_a_code_block_is_text_and_never_a_link():
    body = '<pre><code>&lt;a href="../../../m/A.java" rel="noopener noreferrer"&gt;</code></pre>'
    assert code.mark(body, JAVA) == (body, ())


# --- the examples -----------------------------------------------------------------

SOURCE = "m/src/main/java/p/Wrapper.java"
TEST = "m/src/test/java/p/BoxingTest.java"
ALONE = "m/src/test/java/p/AloneTest.java"

#: The build's answer: the test names its source in its text only.
PAIRS = {SOURCE: (SOURCE, TEST), TEST: (SOURCE, TEST), ALONE: (None, ALONE)}
PAIRED = replace(JAVA, pairing=lambda path: PAIRS.get(path, (path, None)))


def item(label: str, path: str, audio: str = "") -> str:
    """One list item as `blocks.prose` writes it, narrated when `audio` is given."""
    said = f' data-audio="{audio}"' if audio else ""
    return f"<li{said}>{label}{link(f'{UP}{path}', path.rsplit('/', 1)[1])}</li>"


def listed(*items: str) -> str:
    return f'<ul class="items">{"".join(items)}</ul>'


def drawn(body: str, placement=PAIRED) -> str:
    return code.examples(*code.mark(body, placement), placement)


def entries(page: str) -> list[str]:
    return page.split("<details data-code-example ")[1:]


def test_a_list_of_code_links_is_one_entry_per_pair_named_for_its_source():
    page = drawn(listed(item("Test: ", TEST), item("Source: ", SOURCE), item("Test: ", ALONE)))
    assert page.startswith('<div data-code-examples data-corpus="demo">')
    assert re.findall(r"<summary>([^<]*)</summary>", page) == ["Wrapper.java", "AloneTest.java"]
    pair, alone = entries(page)
    assert f'data-code-open="{TEST}"' in pair, "it opens by the file its pair was read from"
    assert re.findall(r'role="tab" data-code-tab="(\w+)"[^>]*>(\w+)<', pair) == [
        ("main", "Source"),
        ("test", "Test"),
    ]
    # ⭐ A test with no source is its own entry, with one tab that says so.
    assert re.findall(r'data-code-tab="(\w+)"[^>]*>(\w+)<', alone) == [("main", "Test")]


def test_every_item_keeps_its_element_and_its_words_and_the_panel_carries_no_audio():
    # ⛔ Register ruling: a code example is never narrated. The items are carried
    # whole but for their audio, even where a record still names a clip for them.
    lines = [item("Test: ", TEST, "a1"), item("Source: ", SOURCE, "")]
    page = drawn(listed(*lines).replace("<li>", '<li data-audio="">'))
    for line in (item("Test: ", TEST), item("Source: ", SOURCE)):
        assert code.mark(line, PAIRED)[0] in page
    assert "data-audio" not in page
    assert page.index(TEST) < page.index(SOURCE), "each item keeps its place"


def test_a_pair_the_list_separates_is_drawn_together_in_its_first_item_s_place():
    page = drawn(listed(item("", TEST), item("", ALONE), item("", SOURCE)))
    assert re.findall(r"<summary>([^<]*)</summary>", page) == ["Wrapper.java", "AloneTest.java"]


def test_as_built_an_entry_loads_nothing_and_says_why_each_file_is_plain_text():
    (entry,) = entries(drawn(listed(item("", SOURCE))))
    assert "<iframe" not in entry and "src=" not in entry
    assert '<div data-code-part="editor" hidden>' in entry
    plain = entry.split('data-code-part="plain"', 1)[1].split("</p>", 1)[0]
    assert "hidden" not in plain.split(">", 1)[0]
    assert "because the course's editor is not running here" in plain
    copy = entry.split('data-code-part="copy"', 1)[1].split(">", 1)[0]
    assert "hidden" in copy
    # ⭐ The runner's sentence names the runner, and is hidden until the served
    # page finds the editor up and the runner down.
    no_runner = entry.split('data-code-part="no-runner"', 1)[1].split("</p>", 1)[0]
    assert "hidden" in no_runner.split(">", 1)[0]
    assert "runner is not running here" in no_runner
    assert "the editor still opens each file" in no_runner
    assert "copy of the course's code" in entry and "never changed" in entry
    assert ">Run tests</button>" in entry
    # ⛔ The page names no API, no origin and no port (R8).
    assert "/api/" not in entry and "127.0.0.1" not in entry
    assert placeholders(code.EXAMPLE_TEMPLATE) == frozenset({"path", "name", "lines", "tabs"})
    assert placeholders(code.EXAMPLES_TEMPLATE) == frozenset({"corpus", "entries"})


@pytest.mark.parametrize(
    "body",
    [
        pytest.param(
            listed(item("", SOURCE)).replace(
                "</li>", " and more words than a label ever carries, which is prose.</li>"
            ),
            id="prose",
        ),
        pytest.param(listed(item("", SOURCE), "<li>A line with no link.</li>"), id="no-link"),
        pytest.param(listed(f"<li>{link(f'{UP}m/README.md', 'README')}</li>"), id="not-code"),
        pytest.param(link(f"{UP}{SOURCE}"), id="inline"),
    ],
)
def test_anything_but_a_list_of_code_links_is_left_as_it_is(body):
    marked, paths = code.mark(body, PAIRED)
    assert code.examples(marked, paths, PAIRED) == marked


def test_a_corpus_with_no_pairing_draws_no_examples():
    marked, paths = code.mark(listed(item("", SOURCE)), JAVA)
    assert paths and code.examples(marked, paths, JAVA) == marked
