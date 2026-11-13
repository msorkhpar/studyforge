"""Mirror of `render/page/diagram.py` (R12): which pages link Mermaid, and the files a corpus with a
diagram writes."""

from __future__ import annotations

import re

import pytest

from studyforge.archive.markdown import parse
from studyforge.render.page import blocks, diagram
from studyforge.render.page.blocks import figure
from studyforge.render.pageassets import vendored
from studyforge.render.pageassets.errors import AssetError
from studyforge.render.pageassets.source import text
from tests.studyforge.render.page.pages import sample_placement

PLACEMENT = sample_placement()
LESSON = (
    "A purchase goes out and comes back:\n\n"
    '```mermaid title="Request and response"\nsequenceDiagram\n  Terminal->>Host: 0200\n'
    "  Host-->>Terminal: 0210\n```\n"
)


def rendered(markdown: str) -> str:
    return "".join(blocks.render_one(block, n, placement=PLACEMENT, section="prose")
                   for n, block in enumerate(parse(markdown)))


def test_a_mermaid_fence_renders_a_diagram_figure_with_its_source_kept():
    page = rendered(LESSON)
    assert '<figure class="code" data-frame="diagram">' in page
    assert "Request and response" in page
    assert "sequenceDiagram\n  Terminal-&gt;&gt;Host: 0200" in page
    assert diagram.carries(page)


def test_the_mark_is_the_figure_renderer_s_own_frame_attribute():
    assert diagram.MARK == figure.DIAGRAM_FRAME


def test_a_page_with_a_diagram_links_mermaid_before_the_script_that_calls_it():
    tags = diagram.links(rendered(LESSON), PLACEMENT)
    for name in ('diagram.css"', 'mermaid.min.js" defer', 'diagram.js" defer'):
        assert name in tags
    assert tags.index("mermaid.min.js") < tags.index("diagram.js")


@pytest.mark.parametrize(
    "markdown",
    [
        "Plain prose and a `mermaid` code span.\n",
        "```java\nclass Mermaid {}\n```\n",
        '```text\ndata-frame="diagram"\n```\n',
        'A paragraph that says data-frame="diagram" in words.\n',
    ],
)
def test_a_page_without_a_diagram_links_nothing(markdown):
    assert diagram.links(rendered(markdown), PLACEMENT) == ""


def test_the_files_are_the_three_parts_and_mermaid_is_vendored_with_its_licence():
    files = diagram.files()
    assert sorted(files) == sorted(diagram.PARTS)
    assert vendored.is_vendored("mermaid.min.js")
    assert vendored.licence_for("mermaid.min.js") == "mermaid.LICENSE"
    header = files["mermaid.min.js"][:1100]
    for marker in ("MIT", "VENDORED, UNMODIFIED", "re-vendor", diagram.VERSION):
        assert marker in header


def test_the_bundle_is_mermaid_as_pinned_and_an_edited_one_is_refused():
    stored = text("mermaid.min.js")
    assert diagram.checked(stored) == stored
    with pytest.raises(AssetError, match="pinned"):
        diagram.checked(stored.replace("mermaid", "Mermaid", 1).replace("*/\n", "*/\n;", 1))
    with pytest.raises(AssetError, match="no vendoring header"):
        diagram.checked("globalThis.mermaid = {};")


def test_the_authored_pair_names_no_host_draws_no_colour_and_pins_nothing():
    files = diagram.files()
    for name in ("diagram.js", "diagram.css"):
        body = files[name]
        assert "http://" not in body and "https://" not in body, name
        assert not re.search(r"#[0-9a-fA-F]{3,8}\b|\brgba?\(", body), name
    declarations = re.sub(r"/\*.*?\*/", "", files["diagram.css"], flags=re.DOTALL)
    assert not re.search(r"(transform|filter|will-change|perspective|contain)\s*:", declarations)


def test_the_script_draws_strictly_themed_from_the_palette_and_redraws_on_a_theme_change():
    script = diagram.files()["diagram.js"]
    assert "startOnLoad: false" in script and 'securityLevel: "strict"' in script
    assert 'theme: "base"' in script and "getComputedStyle" in script
    for name in ("--surface", "--fg", "--rule-strong", "--accent", "--font-ui"):
        assert f'"{name}"' in script, name
    assert 'attributeFilter: ["data-theme"]' in script
    assert "prefers-color-scheme: dark" in script
    assert 'figure.code[data-frame="diagram"]' in script
