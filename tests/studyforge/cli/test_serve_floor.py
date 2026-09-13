"""R8, asserted where a serve verb could break it: a site `studyforge build` wrote needs no server.

⛔ **Spec §11.0 and R8: the reading floor opens over `file://` with no network and no
server.** A serve verb is the first thing that can quietly make the floor depend on
it — a page that fetches the API, a rooted href that only an origin resolves, or a
serve that writes into the site it serves. Each is read here, over sites the verb
itself built, and each has a planted reading that turns it red.
"""

from __future__ import annotations

from urllib.parse import quote

import pytest

from studyforge.cli.serve import main
from tests.studyforge.cli.serving import (
    NAMES,
    build,
    digests,
    floor,
    missing_media,
    pages_of,
    verb_running,
)
from tests.studyforge.serve.serving import fetch


@pytest.mark.parametrize("name", NAMES)
def test_a_site_built_by_the_verb_opens_with_no_server(name, tmp_path):
    root, site = build(name, tmp_path)
    reading = floor(site, missing_media(root, tmp_path))
    # ⭐ Inhabitation first: a floor check over no pages, no references or no script
    # reads exactly like a pass.
    assert reading.pages == len(pages_of(root))
    assert reading.references > reading.pages
    assert reading.texts.get(".js", 0) >= 1 and reading.texts.get(".css", 0) >= 1
    assert reading.defects == []


@pytest.mark.parametrize("name", NAMES)
def test_serving_a_built_site_writes_nothing_into_it(name, tmp_path):
    root, site = build(name, tmp_path)
    before = digests(site)
    unit = [page for page in pages_of(root) if page != "index.html"][0]
    with verb_running([str(root), "--site", str(site), "--port", "0"]) as serving:
        for path in ("/index.html", "/api/v1/content/toc", "/" + quote(unit)):
            assert fetch(serving.server, path)[0] == 200, path
    assert serving.code == [0]
    assert digests(site) == before
    assert floor(site, missing_media(root, tmp_path)).defects == []


def test_the_missing_allowance_is_the_builds_own_report_and_nothing_wider(tmp_path):
    # ⭐ `depth2` names media its archive lacks. Without the build's own report
    # those references dangle; with it, only they are excused.
    root, site = build("depth2", tmp_path)
    missing = missing_media(root, tmp_path)
    unexcused = floor(site).defects
    assert missing and unexcused
    assert all("(no such file)" in defect for defect in unexcused)
    assert floor(site, missing).defects == []


PLANTS = [
    ("index.html", '<a href="/api/v1/content/toc">toc</a>', "rooted"),
    ("index.html", '<script src="http://127.0.0.1:8765/api/v1/x.js"></script>', "origin"),
    (".studyforge/assets/page.js", 'fetch("/api/v1/content/toc");', "origin"),
    (".studyforge/assets/page.js", "fetch('http://localhost:8765/state');", "origin"),
    ("index.html", '<a href="nowhere-a-build-writes.html">x</a>', "no such file"),
]


@pytest.mark.parametrize(("where", "planted", "said"), PLANTS)
def test_the_floor_check_reads_red_on_a_page_that_needs_the_server(tmp_path, where, planted, said):
    _, site = build("depth1", tmp_path)
    target = site / where
    target.write_text(target.read_text(encoding="utf-8") + planted, encoding="utf-8")
    defects = floor(site).defects
    assert any(said in defect and defect.startswith(where) for defect in defects), defects


def test_the_floor_check_passes_a_third_party_api_url_and_a_relative_api_directory(tmp_path):
    # ⭐ The lookalikes, whose reading must DIFFER from the plants': the bundled
    # player already names `https://player.vimeo.com/api/…`, and a relative
    # `../api/` is a directory on disk rather than an origin.
    _, site = build("depth1", tmp_path)
    (site / "api").mkdir()
    (site / "api" / "notes.html").write_text("<p>notes</p>", encoding="utf-8")
    script = site / ".studyforge" / "assets" / "page.js"
    script.write_text(
        script.read_text(encoding="utf-8") + '"https://player.vimeo.com/api/player.js";',
        encoding="utf-8",
    )
    index = site / "index.html"
    index.write_text(index.read_text(encoding="utf-8") + '<a href="api/notes.html">n</a>', "utf-8")
    assert floor(site).defects == []


def test_the_verb_is_what_these_sites_are_served_by():
    # ⚠️ Pins that `verb_running` drives the registered callable and not a copy.
    from studyforge.cli import VERBS

    assert VERBS["serve"].run is main
