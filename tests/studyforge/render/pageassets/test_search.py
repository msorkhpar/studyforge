"""The search index: what a build lets a reader find, and what it never does.

Mirrors `render/pageassets/search.py`. ⛔ The clause that matters most is negative: a quiz's
questions, its key and a mock exam's key are on the page and are never in the index, because a
search box that finds the answer to the question under it is a defect no reader would forgive.
"""

from __future__ import annotations

import json

from studyforge.render.pageassets import search as searchindex
from studyforge.render.pageassets import SCRIPT_PARTS, STYLE_PARTS, text

KEY = "zqx-answer-marker-7731"
STEM = "zqx-question-stem-4410"

UNIT = f"""<!doctype html><html><head><title>Hooks and plugins</title>
<script type="application/json" id="studyforge-identity">{{"kind":"unit"}}</script></head><body>
<header><nav aria-label="Breadcrumb"><ol><li><a href="x">The course</a></li>
<li><span aria-hidden="true">› </span><span data-kind="level">module</span> Extending Claude</li>
<li aria-current="page"><span aria-hidden="true">› </span>Hooks and plugins</li></ol></nav>
<h1>Hooks and plugins</h1></header>
<main id="content"><section data-section="prose">
<p>Intro about idempotency keys.</p>
<h2 id="s-hooks">Hooks</h2><p>A hook runs a command before a tool call.</p>
<div data-example="e1"><div role="tablist" data-example-tabs><button>Python tab word</button></div>
<div role="tabpanel" data-lang="python"><p data-example-label>Python</p>
<pre><code>python_only_token()</code></pre></div>
<div role="tabpanel" data-lang="java"><p data-example-label>Java</p>
<pre><code>java_only_token()</code></pre></div></div>
<details><summary>Show the answer</summary><p>folded {KEY}</p></details>
<details><summary>More background</summary><p>background-token</p></details>
<h2 id="s-plugins">Plugins</h2><p>A plugin marketplace lists plugins.</p>
</section>
<section data-practice-quiz="k" data-practice-mock="60"><ol><li><legend>{STEM}</legend></li></ol>
<script type="application/json" data-practice-part="key">{{"q1":"{KEY}"}}</script></section>
<section data-mock-form="exam"><p>{KEY}</p></section>
<script>var hidden_script = "{KEY}";</script>
</main></body></html>"""

CONTENTS = """<html><head><title>Module</title>
<script type="application/json" id="studyforge-identity">{"kind":"container"}</script></head>
<body><main><h2>Units</h2><p>body-of-a-listing</p></main></body></html>"""


def index() -> str:
    files = searchindex.files([("../a/unit.html", UNIT), ("../a/module.html", CONTENTS)])
    return files[searchindex.INDEX_NAME]


def records() -> dict:
    body = index()
    return json.loads(body[len(searchindex.GLOBAL) : body.rindex(";")])


def test_a_unit_is_cut_at_its_headings_and_each_part_keeps_its_anchor():
    found = records()["records"]
    heads = [r[1:3] for r in found if r[0] == 1]
    assert heads == [["", ""], ["Hooks", "s-hooks"], ["Plugins", "s-plugins"]]
    assert "hook runs a command" in found[2][3]


def test_the_page_table_carries_title_trail_and_address():
    assert records()["pages"][1] == ["../a/unit.html", "Hooks and plugins", "Extending Claude"]


def test_a_quiz_a_mock_exam_and_their_keys_are_never_indexed():
    body = index()
    assert KEY not in body and STEM not in body


def test_a_folded_answer_is_never_indexed_and_other_folds_are():
    body = index()
    assert "folded" not in body
    assert "background-token" in body


def test_a_code_example_is_indexed_once_not_once_per_language():
    body = index()
    assert "python_only_token" in body
    assert "java_only_token" not in body
    assert "Python tab word" not in body


def test_scripts_inside_the_page_are_not_indexed():
    assert "hidden_script" not in index()


def test_a_page_that_is_not_a_unit_is_indexed_by_title_alone():
    body = index()
    assert "body-of-a-listing" not in body
    assert [r for r in records()["records"] if r[0] == 0] == [[0, "", "", ""]]


def test_the_index_survives_being_placed_in_a_page_script():
    assert "</script" not in index().replace("<\\/", "")


def test_the_library_ships_beside_the_index_and_is_the_vendored_file():
    files = searchindex.files([])
    assert files[searchindex.LIBRARY_NAME] == text("minisearch.js")


def test_the_search_parts_are_in_the_bundle_and_the_rail_part_follows_the_store():
    assert SCRIPT_PARTS.index("study-progress.js") < SCRIPT_PARTS.index("rail-scroll.js")
    assert "search.js" in SCRIPT_PARTS
    assert "topbar.css" in STYLE_PARTS and "search.css" in STYLE_PARTS


def test_the_plant_is_caught_when_the_index_includes_a_quiz_key(monkeypatch):
    # ⭐ A defect planted by replacement: the reader no longer skips `data-practice*` regions,
    # which is how a key would reach the index. The clause above must go red.
    monkeypatch.setattr(searchindex, "WITHHELD_PREFIXES", ("data-never-present",))
    body = index()
    assert KEY in body or STEM in body
