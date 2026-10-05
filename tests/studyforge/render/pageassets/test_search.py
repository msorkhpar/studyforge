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


# --- size: a large course is shrunk and split under the serve gate -------------------------------

import shutil
import subprocess
from pathlib import Path

import pytest

from studyforge.serve.routes.assets import GATE_MAX_BYTES


def _parse(body: str) -> dict:
    return json.loads(body[len(searchindex.GLOBAL) : body.rindex(";")])


def _big(monkeypatch, pages=400, words=1500):
    """A document of `pages` units of distinct lorem-like prose, every 5th heading's text repeated."""
    import random

    rng = random.Random(7)
    vocab = [f"w{rng.randrange(10**6):06d}x{i}" for i in range(6000)]
    repeated = " ".join(rng.choice(vocab) for _ in range(60))
    table, records = [], []
    for n in range(pages):
        table.append([f"../m/p{n}.html", f"Page {n}", "Module"])
        for h in range(4):
            text = repeated if h == 3 else " ".join(rng.choice(vocab) for _ in range(words // 4))
            records.append([n, f"Head {h}", f"h{h}", text])
    monkeypatch.setattr(
        searchindex, "document", lambda pages_: {"version": 1, "pages": table, "records": records}
    )
    return records


def test_a_small_course_is_still_one_file():
    out = searchindex.files([("../a/unit.html", UNIT), ("../a/module.html", CONTENTS)])
    assert sorted(out) == sorted([searchindex.INDEX_NAME, searchindex.LIBRARY_NAME])
    assert _parse(out[searchindex.INDEX_NAME])["version"] == 1
    assert "shards" not in _parse(out[searchindex.INDEX_NAME])


def test_a_small_course_keeps_every_record_and_text():
    found = records()["records"]
    assert [r[1] for r in found if r[0] == 1] == ["", "Hooks", "Plugins"]
    assert all(isinstance(r[3], str) for r in found)


def test_an_index_over_the_cap_is_split_into_shards_each_under_the_gate(monkeypatch):
    original = _big(monkeypatch)
    out = searchindex.files([])
    names = [n for n in out if n != searchindex.LIBRARY_NAME]
    assert searchindex.INDEX_NAME in names and len(names) > 2
    for name in names:
        assert len(out[name].encode("utf-8")) < GATE_MAX_BYTES, name
    manifest = _parse(out[searchindex.INDEX_NAME])
    assert manifest["shards"] == [searchindex.shard_name(n) for n in range(len(names) - 1)]
    assert "records" not in manifest and len(manifest["pages"]) == 400
    # Every record is in exactly one shard, in order, with its text or the number standing for it.
    joined = []
    for name in manifest["shards"]:
        body = out[name]
        joined += json.loads(body[body.index("]=[") + 2 : body.rindex(";")])
    assert len(joined) == len(original)
    assert [r[:3] for r in joined] == [r[:3] for r in original]


def test_a_repeated_text_is_written_once_and_resolves_to_the_same_words(monkeypatch):
    original = _big(monkeypatch)
    out = searchindex.files([])
    found = []
    for name in _parse(out[searchindex.INDEX_NAME])["shards"]:
        found += json.loads(out[name][out[name].index("]=[") + 2 : out[name].rindex(";")])
    assert any(isinstance(r[3], int) for r in found)
    for record, source in zip(found, original):
        text = record[3] if isinstance(record[3], str) else found[record[3]][3]
        assert text == source[3]


NODE = shutil.which("node")

#: A page stub just big enough to open the search box, let it load its files and hand back the
#: documents it gave the ranking library.
HARNESS = r"""
const fs = require('fs'); const path = require('path');
const [dir, source] = process.argv.slice(2);
const loaded = []; const clicks = [];
const node = () => ({ setAttribute() {}, getAttribute: () => '', appendChild() {}, replaceChild() {},
  querySelector: () => node(), querySelectorAll: () => [], addEventListener(type, fn) { if (type === 'click') clicks.push(fn); },
  parentNode: { replaceChild() {} }, hidden: true, focus() {}, select() {}, textContent: '', value: '' });
let docs = null;
global.window = { studyforge: {}, clearTimeout() {}, setTimeout() {},
  MiniSearch: function () { this.addAllAsync = (d) => { docs = d; return Promise.resolve(); }; } };
global.navigator = {};
global.document = { querySelector: () => node(), addEventListener() {}, head: { appendChild() {} },
  scripts: [{ src: 'http://site/assets/page.js' }], activeElement: null,
  createElement() { const t = node(); Object.defineProperty(t, 'src', { set(v) {
    loaded.push(path.basename(v));
    setTimeout(() => { (0, eval)(fs.readFileSync(path.join(dir, path.basename(v)), 'utf8')); t.onload(); }, 0);
  } }); return t; } };
(0, eval)(fs.readFileSync(source, 'utf8'));
clicks[clicks.length - 1]();
setTimeout(() => { console.log(JSON.stringify({ loaded, docs })); }, 400);
"""


@pytest.mark.skipif(NODE is None, reason="node is not installed")
@pytest.mark.parametrize("big", [False, True])
def test_the_search_part_loads_the_shards_and_merges_them_in_order(monkeypatch, tmp_path, big):
    if big:
        original = _big(monkeypatch)
        out = searchindex.files([])
    else:
        out = searchindex.files([("../a/unit.html", UNIT)])
        original = [r for r in _parse(out[searchindex.INDEX_NAME])["records"]]
    for name, body in out.items():
        (tmp_path / name).write_text(body, encoding="utf-8")
    # The ranking library is a stand-in written by the harness: only the merge is under test.
    (tmp_path / searchindex.LIBRARY_NAME).write_text("", encoding="utf-8")
    (tmp_path / "run.js").write_text(HARNESS, encoding="utf-8")
    source = Path(searchindex.__file__).parents[1] / "assets" / "search.js"
    run = subprocess.run(
        [NODE, str(tmp_path / "run.js"), str(tmp_path), str(source)],
        capture_output=True, text=True, timeout=120,
    )
    assert run.returncode == 0, run.stderr
    seen = json.loads(run.stdout)
    shards = [n for n in out if n.startswith("search-index-")]
    assert seen["loaded"] == [searchindex.LIBRARY_NAME, searchindex.INDEX_NAME, *sorted(
        shards, key=lambda n: int(n.rsplit("-", 1)[1].split(".")[0]))]
    assert bool(shards) is big
    docs = seen["docs"]
    assert [d["heading"] for d in docs] == [r[1] for r in original]
    texts = [r[3] if isinstance(r[3], str) else original[r[3]][3] for r in original]
    assert [d["text"] for d in docs] == texts
