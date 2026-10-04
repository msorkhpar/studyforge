"""Mirror of `render/page/examplerun.py` (R12): the Run strip an example tab draws, and what a page
links."""

from __future__ import annotations

from dataclasses import replace

from studyforge.render.page import blocks, examplerun
from tests.studyforge.render.page.blocks.test_example import EXAMPLE, OFFER
from tests.studyforge.render.page.pages import sample_placement

PY_SOURCE = "examples/x/python/x.py"
PY_TEST = "examples/x/python/test_x.py"
PAIRS = {PY_SOURCE: (PY_SOURCE, PY_TEST), "examples/x/ts/x.ts": ("examples/x/ts/x.ts", None)}
RUNNABLE = replace(
    sample_placement(),
    code=(".py", ".ts"),
    pairing=lambda path: PAIRS.get(path, (path, None)),
    offer=OFFER,
)


def named(code: str | None, lang: str = "aa") -> dict:
    tab = {"lang": lang, "span": 2}
    return {**tab, "code": code} if code else tab


def draw(placement, **tab):
    block = {**EXAMPLE, "tabs": [{**EXAMPLE["tabs"][0], **tab}, EXAMPLE["tabs"][1]]}
    return blocks.render_one(block, 3, placement=placement, section="prose")


def test_a_tab_that_names_a_file_with_a_test_beside_it_draws_a_run_strip_in_its_panel():
    page = draw(RUNNABLE, code=PY_SOURCE)
    assert page.count("data-example-run=") == 1
    assert f'data-example-run="{PY_SOURCE}"' in page
    assert f'data-corpus="{RUNNABLE.corpus}"' in page
    panel = page.split('role="tabpanel"')[2]
    assert 'data-lang="aa"' in panel.split(">")[0]
    assert panel.index("<code") < panel.index("data-example-run="), "the strip follows the code"
    assert "hidden" in page.split("data-example-run=")[1].split(">")[0]


def test_only_the_tab_that_names_a_file_gets_one():
    page = draw(RUNNABLE, code=PY_SOURCE)
    other = page.split('role="tabpanel"')[1]
    assert 'data-lang="bb"' in other.split(">")[0] and "data-example-run" not in other


def test_a_tab_with_no_test_beside_its_file_or_no_code_or_a_page_beside_nothing_draws_none():
    assert "data-example-run" not in draw(RUNNABLE, code="examples/x/ts/x.ts")
    assert "data-example-run" not in draw(RUNNABLE, code="examples/x/python/other.rs")
    assert "data-example-run" not in draw(RUNNABLE)
    elsewhere = replace(RUNNABLE, code=(), pairing=None)
    assert "data-example-run" not in draw(elsewhere, code=PY_SOURCE)


def test_a_block_whose_tabs_name_no_code_is_the_block_it_always_was():
    plain = blocks.render_one(EXAMPLE, 3, placement=RUNNABLE, section="prose")
    bare = replace(RUNNABLE, code=())
    assert plain == blocks.render_one(EXAMPLE, 3, placement=bare, section="prose")
    assert "example-run" not in plain


def test_a_page_links_the_two_shared_files_only_when_its_body_has_a_strip():
    page = draw(RUNNABLE, code=PY_SOURCE)
    tags = examplerun.links(page, RUNNABLE)
    assert "example-run.css" in tags and 'example-run.js" defer' in tags
    assert examplerun.links("<p>no strip</p>", RUNNABLE) == ""
    assert sorted(examplerun.files()) == ["example-run.css", "example-run.js"]


def test_the_script_asks_the_serving_clients_names_and_composes_no_address():
    script = examplerun.files()["example-run.js"]
    for word in ("window.studyforge.run", "codeTest", "runnable", "available"):
        assert word in script
    for forbidden in ("fetch(", "XMLHttpRequest", "http://", "https://", "/api"):
        assert forbidden not in script
