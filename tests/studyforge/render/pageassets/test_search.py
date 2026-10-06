"""The search index: what a build lets a reader find, and what it never does.

Mirrors `render/pageassets/search.py`. ⛔ The clause that matters most is negative: a quiz's
questions, its key and a mock exam's key are on the page and are never in the index, because a
search box that finds the answer to the question under it is a defect no reader would forgive.
Code, examples, their output, practices and exam pages are not prose and are never in it either.

⭐ The index is precompiled under `node` and loaded in the page; the tests that build or load it
need `node` and say so when it is missing. Without it the build writes the records as it always
did, and the tests of that path name `node=None`.
"""

from __future__ import annotations

import json
import random
import shutil
import subprocess
from pathlib import Path

import pytest

from studyforge.execute import NODE_ON_PATH, search_index_builder
from studyforge.render.pageassets import SCRIPT_PARTS, STYLE_PARTS, text
from studyforge.render.pageassets import search as searchindex
from studyforge.serve.routes.assets import GATE_MAX_BYTES

NODE = shutil.which("node")
needs_node = pytest.mark.skipif(
    NODE is None, reason="node is not installed: the precompiled index cannot be built or loaded"
)


def built(pages, node=NODE_ON_PATH, **options):
    """The search files of `pages`, precompiled under `node` (`None`: there is none)."""
    return searchindex.files(pages, build=search_index_builder(node), **options)


SEARCH_JS = Path(searchindex.__file__).parents[1] / "assets" / "search.js"

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
<section data-practice-quiz="k"><ol><li><legend>{STEM}</legend></li></ol>
<script type="application/json" data-practice-part="key">{{"q1":"{KEY}"}}</script></section>
<section data-form-part="start"><p>{KEY}</p></section>
<script>var hidden_script = "{KEY}";</script>
</main></body></html>"""

CONTENTS = """<html><head><title>Module</title>
<script type="application/json" id="studyforge-identity">{"kind":"container"}</script></head>
<body><main><h2>Units</h2><p>body-of-a-listing</p></main></body></html>"""


PAGES = [("../a/unit.html", UNIT), ("../a/module.html", CONTENTS)]


def index(**options) -> str:
    """The index file of the record path, which writes every kept text as it is."""
    files = built(PAGES, node=None, **options)
    return files[searchindex.INDEX_NAME]


def records() -> dict:
    return searchindex.document(PAGES)


def _parse(body: str) -> dict:
    return json.loads(body[len(searchindex.GLOBAL) : body.rindex(";")])


def _piece(body: str) -> str:
    return json.loads(body[body.index("]=") + 2 : body.rindex(";")])


def index_json(out: dict[str, str]) -> str:
    """The serialised index a precompiled build wrote, its pieces joined in order."""
    manifest = _parse(out[searchindex.INDEX_NAME])
    assert manifest["version"] == searchindex.PRECOMPILED_VERSION
    if "index" in manifest:
        return manifest["index"]
    return "".join(_piece(out[name]) for name in manifest["parts"])


#: Loads the written files with nothing but a `window`, joins the pieces, calls `loadJSON` once and
#: answers each query with its hits.
ROUND_TRIP = r"""
const fs = require('fs'); const path = require('path');
const dir = process.argv[2]; const queries = JSON.parse(process.argv[3]);
global.window = globalThis;
const run = (name) => (0, eval)(fs.readFileSync(path.join(dir, name), 'utf8'));
run('minisearch.js'); run('search-index.js');
const found = window.studyforge.searchIndex;
const json = typeof found.index === 'string' ? found.index
  : found.parts.map((name) => { run(name); return window.studyforge.searchParts[name]; }).join('');
const engine = MiniSearch.loadJSON(json, { fields: found.fields, storeFields: found.storeFields });
const results = {};
for (const query of queries) { results[query] = engine.search(query); }
console.log(JSON.stringify({ version: found.version, pages: found.pages, results }));
"""


def round_trip(out: dict[str, str], where: Path, queries: list[str]) -> dict:
    where.mkdir(parents=True, exist_ok=True)
    for name, body in out.items():
        (where / name).write_text(body, encoding="utf-8")
    (where / "round-trip.js").write_text(ROUND_TRIP, encoding="utf-8")
    run = subprocess.run(
        [NODE, str(where / "round-trip.js"), str(where), json.dumps(queries)],
        capture_output=True, text=True, timeout=300,
    )
    assert run.returncode == 0, run.stderr
    return json.loads(run.stdout)


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


def test_a_code_example_is_not_indexed_in_any_language():
    body = index()
    assert "python_only_token" not in body
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
    for node in (None, NODE_ON_PATH):
        files = built([], node=node)
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


# --- size: a large course is split under the serve gate ---------------------------------------


def _big(monkeypatch, pages=400, words=1500):
    """A document of `pages` units of distinct lorem-like prose, each 4th text repeated."""
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
        searchindex,
        "document",
        lambda pages_, clean=None: {"version": 1, "pages": table, "records": records},
    )
    return records


def test_a_small_course_is_still_one_file():
    out = built(PAGES, node=None)
    assert sorted(out) == sorted(
        [searchindex.INDEX_NAME, searchindex.LIBRARY_NAME, searchindex.BUILD_NAME]
    )
    assert _parse(out[searchindex.INDEX_NAME])["version"] == 1
    assert "shards" not in _parse(out[searchindex.INDEX_NAME])


def test_a_small_course_keeps_every_record_and_text():
    found = records()["records"]
    assert [r[1] for r in found if r[0] == 1] == ["", "Hooks", "Plugins"]
    assert all(isinstance(r[3], str) for r in found)


def test_an_index_over_the_cap_is_split_into_shards_each_under_the_gate(monkeypatch):
    original = _big(monkeypatch)
    out = built([], node=None)
    names = [n for n in out if n not in (searchindex.LIBRARY_NAME, searchindex.BUILD_NAME)]
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
    out = built([], node=None)
    found = []
    for name in _parse(out[searchindex.INDEX_NAME])["shards"]:
        found += json.loads(out[name][out[name].index("]=[") + 2 : out[name].rindex(";")])
    assert any(isinstance(r[3], int) for r in found)
    for record, source in zip(found, original):
        text = record[3] if isinstance(record[3], str) else found[record[3]][3]
        assert text == source[3]


#: A page stub just big enough to open the search box, let it load its files with the real ranking
#: library, and hand back what it loaded, whether it built an index, its status and the hits of a
#: query.
HARNESS = r"""
const fs = require('fs'); const path = require('path');
const [dir, source, query] = process.argv.slice(2);
const loaded = []; const clicks = []; const nodes = {};
const node = (name) => ({ setAttribute() {}, getAttribute: (n) => n, removeAttribute() {},
  appendChild() {}, replaceChild() {}, querySelector: (s) => nodes[s] || (nodes[s] = node(s)),
  querySelectorAll: () => [], addEventListener(type, fn) { if (type === 'click') clicks.push(fn); },
  parentNode: { replaceChild() {} }, hidden: true, focus() {}, select() {}, textContent: '',
  value: '' });
global.window = globalThis;
window.studyforge = {};
let engine = null; let docs = null;
function spy() {
  const M = globalThis.MiniSearch; const load = M.loadJSON; const add = M.prototype.addAllAsync;
  M.loadJSON = function (json, options) { engine = load.call(M, json, options); return engine; };
  M.prototype.addAllAsync = function (d, o) {
    engine = this; docs = d; return add.call(this, d, o);
  };
}
global.document = { querySelector: (s) => nodes[s] || (nodes[s] = node(s)), addEventListener() {},
  head: { appendChild() {} }, scripts: [{ src: 'http://site/assets/page.js' }], activeElement: null,
  createElement() { const t = node('script'); Object.defineProperty(t, 'src', { set(v) {
    const name = path.basename(v); loaded.push(name);
    setTimeout(() => {
      const file = path.join(dir, name);
      if (!fs.existsSync(file)) { t.onerror(); return; }
      (0, eval)(fs.readFileSync(file, 'utf8'));
      if (name === 'minisearch.js') { spy(); }
      t.onload();
    }, 0);
  } }); return t; } };
(0, eval)(fs.readFileSync(source, 'utf8'));
clicks[clicks.length - 1]();
const status = nodes['[data-search-status]'];
const started = Date.now();
(function wait() {
  if (status.textContent === 'data-search-loading' && Date.now() - started < 120000) {
    setTimeout(wait, 20); return;
  }
  const hits = engine && query ? engine.search(query) : [];
  console.log(JSON.stringify({ loaded, docs, status: status.textContent, hits }));
}());
"""


def opened(out: dict[str, str], where: Path, query: str = "") -> dict:
    """Open the search box over the files `out` in node and report what the search part did."""
    where.mkdir(parents=True, exist_ok=True)
    for name, body in out.items():
        (where / name).write_text(body, encoding="utf-8")
    (where / "run.js").write_text(HARNESS, encoding="utf-8")
    run = subprocess.run(
        [NODE, str(where / "run.js"), str(where), str(SEARCH_JS), query],
        capture_output=True, text=True, timeout=300,
    )
    assert run.returncode == 0, run.stderr
    return json.loads(run.stdout)


def _in_order(names):
    return sorted(names, key=lambda n: int(n.rsplit("-", 1)[1].split(".")[0]))


@needs_node
@pytest.mark.parametrize("big", [False, True])
def test_without_node_the_search_part_builds_the_records_in_order(monkeypatch, tmp_path, big):
    if big:
        original = _big(monkeypatch)
        out = built([], node=None)
    else:
        out = built([("../a/unit.html", UNIT)], node=None)
        original = [r for r in _parse(out[searchindex.INDEX_NAME])["records"]]
    seen = opened(out, tmp_path, "Head" if big else "plugin")
    shards = [n for n in out if n.startswith("search-index-")]
    assert seen["loaded"] == [
        searchindex.LIBRARY_NAME, searchindex.INDEX_NAME, searchindex.BUILD_NAME, *_in_order(shards)
    ]
    assert bool(shards) is big
    assert seen["status"] == ""
    docs = seen["docs"]
    assert [d["heading"] for d in docs] == [r[1] for r in original]
    texts = [r[3] if isinstance(r[3], str) else original[r[3]][3] for r in original]
    assert [d["text"] for d in docs] == texts
    assert seen["hits"], "the index the page built answers a query"


@needs_node
@pytest.mark.parametrize("big", [False, True])
def test_with_node_the_search_part_loads_the_index_and_builds_nothing(monkeypatch, tmp_path, big):
    if big:
        _big(monkeypatch)
    out = built([] if big else [("../a/unit.html", UNIT)])
    assert searchindex.BUILD_NAME not in out
    seen = opened(out, tmp_path, "Head" if big else "plugin")
    parts = [n for n in out if n.startswith("search-index-")]
    assert seen["loaded"] == [searchindex.LIBRARY_NAME, searchindex.INDEX_NAME, *_in_order(parts)]
    assert bool(parts) is big
    assert seen["docs"] is None, "nothing was added to an index in the page"
    assert seen["status"] == "" and seen["hits"]


@needs_node
@pytest.mark.parametrize("version", [0, 4, 99])
def test_a_version_the_search_part_does_not_know_fails(tmp_path, version):
    out = built([("../a/unit.html", UNIT)])
    manifest = _parse(out[searchindex.INDEX_NAME])
    unknown = json.dumps({**manifest, "version": version})
    out[searchindex.INDEX_NAME] = searchindex.GLOBAL + unknown + ";"
    seen = opened(out, tmp_path, "plugin")
    assert seen["status"] == "data-search-failed"
    assert seen["loaded"] == [searchindex.LIBRARY_NAME, searchindex.INDEX_NAME]


@needs_node
def test_a_missing_piece_fails(monkeypatch, tmp_path):
    _big(monkeypatch)
    out = built([])
    parts = _in_order(n for n in out if n.startswith("search-index-"))
    del out[parts[-1]]
    assert opened(out, tmp_path, "Head")["status"] == "data-search-failed"


def test_no_index_is_built_in_the_browser_by_the_search_part():
    source = SEARCH_JS.read_text(encoding="utf-8")
    assert "addAll" not in source and "addAllAsync" not in source
    assert "loadJSON" in source


# -- a quiz option sentence that the page's own prose repeats is never in the index --------------

OPTION = "A log that the agent can edit is not an audit trail at all."
OTHER = "Both comparisons are inclusive, so reaching the minimum is enough."

QUIZ_UNIT = f"""<!doctype html><html><head><title>Audit logs</title>
<script type="application/json" id="studyforge-identity">{{"kind":"unit"}}</script></head><body>
<main id="content"><section data-section="prose"><h2 id="s-a">Audit</h2>
<p>Before the quiz. {OPTION} After the sentence, more prose stays searchable: zebrafinch.</p>
<h2 id="s-b">Limits</h2><p>{OTHER} Tail words: quokka.</p></section>
<section data-practice-quiz="k"><script>var quiz={{"q-1":{{"keys":["b"],"says":{{"a":"{OPTION}",
"b":"Ruled out because \\u0026quot;{OTHER}\\u0026quot;"}}}}}};</script></section>
</main></body></html>"""


def _marks():
    from studyforge.serve.withheld import Marks

    return Marks(frozenset({OPTION, f'Ruled out because "{OTHER}"'}), frozenset({"q-1"}))


def _built(monkeypatch, shard=None, node=None):
    if shard:
        monkeypatch.setattr(searchindex, "SHARD_BYTES", shard)
    return built([("../a/unit.html", QUIZ_UNIT)], node=node)


def test_a_single_file_index_passes_the_serve_gate_and_keeps_the_rest_of_the_prose(monkeypatch):
    from studyforge.serve.withheld import carries

    out = _built(monkeypatch)
    body = out[searchindex.INDEX_NAME]
    assert not carries(body.encode(), _marks())
    assert "zebrafinch" in body and "quokka" in body and "Before the quiz." in body


def test_sharded_index_files_pass_the_serve_gate_and_are_served_200(monkeypatch, tmp_path):
    from studyforge.serve.response import Request
    from studyforge.serve.routes.assets import serve
    from studyforge.serve.withheld import carries

    out = _built(monkeypatch, shard=150)
    out = {n: c for n, c in out.items() if n.startswith("search-index")}
    assert len(out) > 1, "the cap forced a manifest and shards"
    for name, content in out.items():
        assert not carries(content.encode(), _marks()), name
        (tmp_path / name).write_text(content, encoding="utf-8")
        request = Request("GET", f"/{name}", {})
        got = serve(tmp_path, request, f"/{name}", withheld=lambda b: carries(b, _marks()))
        assert got.status == 200, name


def test_the_plant_is_caught_when_an_option_sentence_is_left_in_the_index(monkeypatch):
    from studyforge.serve.withheld import carries

    monkeypatch.setattr(searchindex, "quiz_sentences", lambda pages: set())
    body = _built(monkeypatch)[searchindex.INDEX_NAME]
    assert carries(body.encode(), _marks())
