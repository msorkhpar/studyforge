"""The precompiled search index: prose only, a few stored fields, loaded and never built in a page.

Mirrors the precompiled half of `render/pageassets/search.py`. ⭐ Each test builds the index under
`node` and reads it back the way the search part does, with `MiniSearch.loadJSON`, so what it
asserts is what a reader can find; each is skipped, with the reason, where `node` is missing.
"""

from __future__ import annotations

import pytest

from studyforge.archive.scrub import PersonalDataLeak, assert_clean, scrub
from studyforge.execute import NODE_ON_PATH
from studyforge.render.pageassets import search as searchindex
from studyforge.serve.routes.assets import GATE_MAX_BYTES
from tests.studyforge.render.pageassets.test_search import (
    OPTION,
    PAGES,
    _big,
    _built,
    _marks,
    _parse,
    _piece,
    built,
    index_json,
    needs_node,
    round_trip,
)


@needs_node
def test_a_precompiled_index_passes_the_serve_gate_and_cuts_the_option(monkeypatch, tmp_path):
    from studyforge.serve.withheld import carries

    for shard in (None, 400):
        out = _built(monkeypatch, shard=shard, node=NODE_ON_PATH)
        for name, body in out.items():
            if name.startswith("search-index"):
                assert not carries(body.encode(), _marks()), name
        # ⭐ The sentence is cut from the text before it is indexed: its own words are not found
        # where only it said them, and the rest of the sentence's paragraph is.
        found = round_trip(out, tmp_path / f"cut-{shard}", ["zebrafinch", "quokka", "audit trail"])
        assert found["results"]["zebrafinch"] and found["results"]["quokka"]
        snippets = " ".join(h["snippet"] for h in found["results"]["zebrafinch"])
        assert OPTION not in snippets and "Before the quiz." in snippets


#: One word per kind of content, planted where that content sits on a real page.
NEVER = {
    "code block": "codeblockmarker",
    "bare pre": "barepremarker",
    "standalone code": "standalonecodemarker",
    "example tab": "exampletabmarker",
    "example code": "examplecodemarker",
    "run output": "runoutputmarker",
    "practice": "practicemarker",
    "practice heading": "practiceheadingmarker",
    "quiz option": "quizoptionmarker",
    "mock page prose": "mockpagemarker",
    "mock page title": "mocktitlemarker",
}
FOUND = {
    "prose": "prosemarker",
    "heading": "headingmarker",
    "title": "titlemarker",
    "menu label": "menulabelmarker",
    "inline code": "inlinecodemarker",
}
OPTION_SENTENCE = "The quizoptionmarker answer names the setting that is read first."

LESSON = f"""<!doctype html><html><head><title>A titlemarker lesson</title>
<script type="application/json" id="studyforge-identity">{{"kind":"unit"}}</script></head><body>
<header><nav aria-label="Breadcrumb"><ol><li><a href="x">The course</a></li>
<li><span aria-hidden="true">› </span><span data-kind="level">module</span>
A menulabelmarker module</li>
<li aria-current="page"><span aria-hidden="true">› </span>A titlemarker lesson</li></ol></nav>
<h1>A titlemarker lesson</h1></header>
<main id="content"><section id="s1" data-section="prose" data-kind="lesson" data-label="Lesson">
<p>Some prosemarker words about settings, and a call to <code>inlinecodemarker()</code>
in a sentence.</p>
<h2 id="s-head">The headingmarker part</h2><p>More words under it.</p>
<figure class="code"><figcaption><span class="what">main.py</span></figcaption>
<pre><code class="language-python">codeblockmarker = 1</code></pre></figure>
<div><code>standalonecodemarker</code></div>
<pre>barepremarker output</pre>
<div data-example="ex" data-langs="aa bb">
<div role="tabpanel" id="p-aa" tabindex="0" data-lang="aa"><p data-example-label>Aa</p>
<p>exampletabmarker words</p><figure class="code"><pre><code>examplecodemarker</code></pre></figure>
<p data-example-run="x.py" data-corpus="c"><button type="button" data-example-act="run">Run</button>
</p><pre data-example-part="output" tabindex="0">runoutputmarker</pre></div></div>
</section>
<section id="s2" data-section="practice-1" data-kind="practice" data-label="Practice">
<h2 id="s-practice">The practiceheadingmarker</h2><p>practicemarker words of a practice.</p>
<section data-practice-quiz="q" data-corpus="c" aria-label="Questions" tabindex="-1">
<ol data-practice-part="questions"><li data-practice-question="q-1"><fieldset>
<legend>Which is read first?</legend><label>{OPTION_SENTENCE}</label></fieldset></li></ol>
<script>var quiz={{"q-1":{{"keys":["a"],"says":{{"a":"{OPTION_SENTENCE}"}}}}}};</script></section>
</section></main></body></html>"""

#: The page a mock exam is on: its prose is what the questions are written from.
EXAM = """<!doctype html><html><head><title>The mocktitlemarker exam</title>
<script type="application/json" id="studyforge-identity">{"kind":"unit"}</script></head><body>
<main id="content"><section id="s1" data-section="prose" data-kind="lesson" data-label="Lesson">
<h2 id="s-a">A request</h2><p>The mockpagemarker passage the questions are taken from.</p></section>
<section id="s2" data-section="practice-1" data-kind="practice" data-label="Practice">
<section data-practice-quiz="m" data-practice-mock="70" data-corpus="c" aria-label="Mock exam"
tabindex="-1">
<p data-mock-part="progress">0 of 6 answered</p></section></section></main></body></html>"""

MODULE = """<!doctype html><html><head><title>A menulabelmarker module</title>
<script type="application/json" id="studyforge-identity">{"kind":"container"}</script></head>
<body><main><h2>Units</h2><p>A titlemarker lesson</p></main></body></html>"""

KINDS = [("../m/lesson.html", LESSON), ("../m/exam.html", EXAM), ("../m/module.html", MODULE)]


@needs_node
def test_only_prose_titles_headings_and_menu_labels_are_findable(tmp_path):
    out = built(KINDS)
    serialised = index_json(out).lower()
    joined = "".join(out[n] for n in out if n.startswith("search-index")).lower()
    found = round_trip(out, tmp_path, [*NEVER.values(), *FOUND.values()])["results"]
    for kind, word in NEVER.items():
        assert word not in serialised and word not in joined, kind
        assert found[word] == [], kind
    for kind, word in FOUND.items():
        assert word in serialised, kind
        assert found[word], kind


#: A lesson whose quiz is drawn with the mock form's markup, as a course quiz is.
QUIZ_PAGE = """<!doctype html><html><head><title>A quizpagetitlemarker lesson</title>
<script type="application/json" id="studyforge-identity">{"kind":"unit"}</script></head><body>
<main id="content"><section id="s1" data-section="prose" data-kind="lesson" data-label="Lesson">
<h2 id="s-a">A request</h2><p>The quizpageprosemarker passage.</p></section>
<section id="s2" data-section="practice-1" data-kind="practice" data-label="Practice">
<section data-practice-quiz="q" data-practice-mock="100" data-mock-form="exam"
data-form-kind="quiz" data-corpus="c" aria-label="Questions" tabindex="-1">
<p data-mock-domain="d">quizoptionmarker words</p></section></section></main></body></html>"""


def test_a_lesson_with_a_quiz_drawn_as_a_mock_form_is_still_indexed():
    page = searchindex.read(QUIZ_PAGE)
    assert page["exam"] is False
    text = " ".join(section[2] for section in page["sections"])
    assert "quizpageprosemarker" in text and "quizoptionmarker" not in text


@needs_node
def test_an_exam_page_is_not_in_the_index_at_all(tmp_path):
    found = round_trip(built(KINDS), tmp_path, [])
    assert found["pages"] == ["../m/lesson.html", "../m/module.html"]


@needs_node
def test_a_term_only_in_an_inline_code_span_is_found_at_its_heading(tmp_path):
    hits = round_trip(built(KINDS), tmp_path, ["inlinecodemarker"])["results"]
    [hit] = hits["inlinecodemarker"]
    assert hit["anchor"] == "" and hit["title"] == "A titlemarker lesson"
    assert "inlinecodemarker()" in hit["snippet"]


#: What a hit carries beside the stored fields: the ranking library's own.
RANKING_KEYS = {"id", "score", "terms", "queryTerms", "match"}


@needs_node
def test_a_hit_carries_exactly_the_stored_fields_and_never_the_text(tmp_path):
    long_prose = " ".join(f"word{n}" for n in range(200))
    page = LESSON.replace("More words under it.", f"More words under it. {long_prose}")
    out = built([("../m/lesson.html", page)])
    hits = round_trip(out, tmp_path, ["headingmarker", "word150"])
    for hit in hits["results"]["headingmarker"] + hits["results"]["word150"]:
        assert set(hit) - RANKING_KEYS == set(searchindex.STORE_FIELDS)
        assert "text" not in hit
        assert len(hit["snippet"]) <= searchindex.SNIPPET_CHARS
    [hit] = hits["results"]["word150"]
    assert (hit["heading"], hit["anchor"], hit["trail"]) == (
        "The headingmarker part", "s-head", "A menulabelmarker module"
    )
    assert hit["snippet"].endswith("…") and "word150" not in hit["snippet"]
    assert hit["snippet"][:-1].split(" ")[-1].startswith("word"), "cut on a word"


def test_a_snippet_is_cut_on_a_word_and_never_longer_than_the_cap():
    text = " ".join(["alpha"] * 100)
    cut = searchindex.snippet(text)
    assert len(cut) <= searchindex.SNIPPET_CHARS and cut.endswith("alpha…")
    assert searchindex.snippet("short text") == "short text"
    assert len(searchindex.snippet("x" * 500)) == searchindex.SNIPPET_CHARS


REDACTION = """<!doctype html><html><head><title>Redaction</title>
<script type="application/json" id="studyforge-identity">{"kind":"unit"}</script></head><body>
<header><h1>Redaction</h1></header><main id="content"><section data-section="prose">
<h2 id="s-r">Shapes</h2><p>Redact <code>Bearer</code> followed by 16 or more characters.</p>
</section></main></body></html>"""


@needs_node
@pytest.mark.parametrize("shard", [None, 200])
def test_a_scrubbed_precompiled_index_holds_no_secret_shape_and_loads(monkeypatch, tmp_path, shard):
    if shard:
        monkeypatch.setattr(searchindex, "SHARD_BYTES", shard)
    raw = built([("../a/unit.html", REDACTION)])
    assert "followed" in index_json(raw)
    shape = "Bearer " + "followed"
    with pytest.raises(PersonalDataLeak):
        assert_clean(index_json(raw), "index")
    # ⭐ What `generate.site` writes: each text scrubbed before it is indexed, each file after.
    made = built([("../a/unit.html", REDACTION)], clean=scrub)
    cleaned = {n: scrub(b) for n, b in made.items()}
    for name, body in cleaned.items():
        if name.startswith("search-index"):
            assert_clean(body, name)
            assert shape not in body
    assert shape not in index_json(cleaned)
    found = round_trip(cleaned, tmp_path, ["redact", "followed"])["results"]
    assert found["redact"], "the scrubbed index loads and answers"
    assert found["followed"] == [], "the scrubbed words are gone"


@needs_node
def test_pieces_are_each_under_a_lowered_cap_and_join_to_the_same_json(monkeypatch, tmp_path):
    whole = built(KINDS)
    json_text = index_json(whole)
    monkeypatch.setattr(searchindex, "SHARD_BYTES", 600)
    out = built(KINDS)
    parts = _parse(out[searchindex.INDEX_NAME])["parts"]
    assert len(parts) > 2 and parts == [searchindex.part_name(n) for n in range(len(parts))]
    assert sorted(out) == sorted([searchindex.INDEX_NAME, searchindex.LIBRARY_NAME, *parts])
    for name in parts + [searchindex.INDEX_NAME]:
        assert len(out[name].encode("utf-8")) <= 600, name
    assert "".join(_piece(out[name]) for name in parts) == json_text
    assert round_trip(out, tmp_path, ["prosemarker"])["results"]["prosemarker"]


def test_pieces_never_lose_or_reorder_a_character():
    text = 'a"b\\\\c</d\\u2028é' * 300
    for limit in (40, 97, 1000):
        cut = searchindex.pieces(text, limit)
        assert "".join(cut) == text
        assert all(len(searchindex._dump(p).encode("utf-8")) <= limit for p in cut)


@needs_node
def test_a_large_course_at_the_real_cap_is_in_pieces_each_under_the_gate(monkeypatch, tmp_path):
    _big(monkeypatch)
    out = built([])
    parts = _parse(out[searchindex.INDEX_NAME])["parts"]
    assert len(parts) > 1
    for name, body in out.items():
        assert len(body.encode("utf-8")) < GATE_MAX_BYTES, name
        size = len(body.encode("utf-8"))
        assert size <= searchindex.SHARD_BYTES or name == searchindex.LIBRARY_NAME
    found = round_trip(out, tmp_path, ["Head"])
    assert len(found["pages"]) == 400 and found["results"]["Head"]


@needs_node
def test_with_node_nothing_is_printed_and_no_build_part_is_written(capsys):
    out = built(PAGES)
    assert capsys.readouterr().err == ""
    assert searchindex.BUILD_NAME not in out


@needs_node
def test_the_precompiled_index_is_the_same_bytes_on_every_build():
    assert built(KINDS) == built(KINDS)
