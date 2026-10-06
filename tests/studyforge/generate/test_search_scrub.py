"""The search index written by the site build passes the serve gate's personal-data check."""

from __future__ import annotations

import json

from studyforge.archive.scrub import assert_clean, scrub
from studyforge.render.pageassets import search as searchindex
from tests.studyforge.render.pageassets.test_search import built

PAGE = """<!doctype html><html><head><title>Redaction</title>
<script type="application/json" id="studyforge-identity">{"kind":"unit"}</script></head><body>
<header><h1>Redaction</h1></header><main id="content"><section data-section="prose">
<h2 id="s-r">Shapes</h2><p>Redact <code>Bearer</code> followed by 16 or more characters.</p>
</section></main></body></html>"""


def test_prose_that_describes_a_secret_shape_is_scrubbed_out_of_the_index():
    # The record path, whose file holds every text as it is; `test_search_site` covers the
    # precompiled one.
    raw = built([("../a/unit.html", PAGE)], node=None)
    body = raw[searchindex.INDEX_NAME]
    try:
        assert_clean(body, "index")
        tripped = False
    except Exception:
        tripped = True
    assert tripped, "the flattened prose is expected to read as a bearer token"
    cleaned = {n: scrub(b) for n, b in raw.items()}  # what generate.site writes
    for name, text in cleaned.items():
        assert_clean(text, name)
    text = cleaned[searchindex.INDEX_NAME]
    data = json.loads(text[len(searchindex.GLOBAL) : text.rindex(";")])
    assert any("Redact" in r[3] for r in data["records"])
