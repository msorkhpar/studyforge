"""How the live namespace is wired into an instance, a page and the wire — and not wired.

Mirrors no one module: it reads `serve.app`'s `bodies`, `serve.routes.assets`'s `live` tag and
`serve.instance`'s registration together, because the claim is about all three at once: a corpus
that declares no live run, an instance without a live runner and a read-only preview get NOTHING:
no namespace, no body reaching a route, no script tag and no change to a page's bytes.
"""

from __future__ import annotations

import json
import pytest

from studyforge.execute import Published, Service
from studyforge.generate import read_corpus, write_site
from studyforge.serve.discovery import discover
from studyforge.serve.instance import (
    WRITERS,
    bodies_for,
    live_client_for,
    namespaces_of,
    writers_for,
)
from studyforge.serve.response import Request, Response, json_response
from studyforge.serve.routes import assets, live
from studyforge.serve.routes.content import CorpusContent
from tests.studyforge.generate.corpora import FIXTURES
from tests.studyforge.serve.routes.running import served_copy
from tests.studyforge.serve.routes.test_live import declare_live
from tests.studyforge.serve.serving import fetch, running

PAGE = b"<!doctype html><html><head><title>t</title></head><body><p>x</p></body></html>"
RUN, LIVE = "/api/v1/run/client.js", "/api/v1/live/client.js"


def published(live_service: Service | None) -> Published:
    return Published(None, (), None, Service("runner", 7123), live_service)


def sources_of(discovered):
    return {one.source: CorpusContent(one.corpus) for one in discovered.corpora}


def test_a_page_gains_the_live_tag_after_the_run_client_exactly_once():
    both = assets.with_client(PAGE, RUN, LIVE)
    assert both.count(b"<script") == 2
    assert both.index(RUN.encode()) < both.index(LIVE.encode()) < both.index(b"</head>")
    assert assets.with_client(both, RUN, LIVE) == both


def test_a_page_with_no_live_client_is_exactly_the_bytes_it_always_was():
    plain = assets.with_client(PAGE, RUN)
    assert plain == PAGE.replace(b"</head>", f'<script src="{RUN}" defer></script></head>'.encode())
    assert assets.with_client(PAGE, RUN, None) == plain
    assert LIVE.encode() not in plain


def test_a_validator_tells_the_live_page_from_the_plain_one():
    one, other = assets.client_etag('W/"a"'), assets.client_etag('W/"a"', True)
    assert one != other and one.endswith('+client"') and other.endswith('+client+live"')


def test_the_live_client_is_never_added_without_the_run_client():
    assert assets.with_client(PAGE, None, LIVE) == PAGE


@pytest.fixture
def declared(tmp_path):
    root = served_copy(tmp_path / "corpora")
    declare_live(root)
    return root


def test_the_namespace_exists_only_with_a_live_runner_and_a_declaring_corpus(declared, tmp_path):
    found = discover(declared.parent)
    present = namespaces_of(found, sources_of(found), published(Service("live", 7124)))
    assert live.NAMESPACE in present
    assert live_client_for(present) == live.CLIENT_PATH
    assert bodies_for(present) == (live.RUN_PATH,)
    assert writers_for(present) == (*WRITERS, live.NAMESPACE)
    # ⛔ No live runner declared by the compose: nothing is registered.
    assert live.NAMESPACE not in namespaces_of(found, sources_of(found), published(None))
    # ⛔ Not published at all (the host-process form): nothing is registered.
    assert live.NAMESPACE not in namespaces_of(found, sources_of(found))
    # ⛔ A corpus that declares no live run: nothing is registered, whatever the compose says.
    plain = discover(served_copy(tmp_path / "plain" / "corpora").parent)
    absent = namespaces_of(plain, sources_of(plain), published(Service("live", 7124)))
    assert live.NAMESPACE not in absent
    assert (writers_for(absent), bodies_for(absent), live_client_for(absent)) == (WRITERS, (), None)


def test_the_environment_names_a_live_service_only_when_one_is_declared():
    from studyforge.execute.published import LIVE_SERVICE, from_environment

    base = {"STUDYFORGE_RUN_SERVICE": "runner"}
    assert from_environment(base).live is None
    named = from_environment({**base, LIVE_SERVICE: "live-runner"})
    assert named.live == Service("live-runner", 7124)
    ported = from_environment({**base, LIVE_SERVICE: "live-runner:9"})
    assert ported.live == Service("live-runner", 9)
    from studyforge.execute import RunRefused

    with pytest.raises(RunRefused, match=LIVE_SERVICE):
        from_environment({**base, LIVE_SERVICE: "live:abc"})


def echo(request: Request, rest: str) -> Response:
    return json_response(200, {"seen": len(getattr(request, "body", b""))})


def post(server, path, body):
    import http.client

    connection = http.client.HTTPConnection(*server.server_address[:2], timeout=10)
    try:
        connection.request("POST", path, body=body)
        reply = connection.getresponse()
        return reply.status, reply.read().decode()
    finally:
        connection.close()


def test_a_body_reaches_only_a_route_registered_for_one_and_only_up_to_its_limit(tmp_path):
    site = tmp_path / "site"
    site.mkdir()
    write_site(FIXTURES / "depth1", site)
    source = CorpusContent(read_corpus(FIXTURES / "depth1"))
    options = {
        "namespaces": {"w": echo, "v": echo},
        "writers": ("w", "v"),
        "bodies": ("/api/v1/w/take",),
    }
    with running(site, source, **options) as server:
        assert json.loads(post(server, "/api/v1/w/take", b"abc")[1])["seen"] == 3
        # ⛔ Another path under a writer: the body is read and DROPPED.
        assert json.loads(post(server, "/api/v1/v/other", b"abc")[1])["seen"] == 0
        assert post(server, "/api/v1/w/take", b"x" * 9000)[0] == 413
        assert post(server, "/api/v1/w/take", b"")[0] == 200


def test_a_served_page_names_the_live_client_only_where_the_instance_offers_one(tmp_path):
    site = tmp_path / "site"
    site.mkdir()
    write_site(FIXTURES / "depth1", site)
    page = next(site.rglob("*.html")).relative_to(site).as_posix()
    source = CorpusContent(read_corpus(FIXTURES / "depth1"))
    with running(site, source, client=RUN) as server:
        plain = fetch(server, "/" + page)[2]
    with running(site, source, client=RUN, live=LIVE) as server:
        offered = fetch(server, "/" + page)[2]
    with running(site, source) as server:
        bare = fetch(server, "/" + page)[2]
    assert LIVE.encode() not in plain and LIVE.encode() not in bare
    assert offered == assets.with_client(bare, RUN, LIVE)
    assert plain == assets.with_client(bare, RUN)


def tree(root) -> dict[str, bytes]:
    """Every file under `root` but the manifest and the framework's own bookkeeping, by path."""
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
        and path.name != "corpus.json"
        and ".studyforge" not in path.relative_to(root).parts
    }


def test_declaring_live_runs_changes_no_byte_of_a_built_site_and_names_none_of_it(tmp_path):
    import shutil

    from studyforge.generate import write_site

    live_root = served_copy(tmp_path / "live" / "corpora")
    declare_live(live_root)
    plain_root = tmp_path / "plain" / "corpora" / live_root.name
    shutil.copytree(live_root, plain_root)
    manifest = plain_root / "corpus.json"
    document = json.loads(manifest.read_text(encoding="utf-8"))
    del document["live"]
    manifest.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    write_site(plain_root, plain_root)
    declared, undeclared = tree(live_root), tree(plain_root)
    assert declared == undeclared
    # ⛔ A read-only preview is this built tree: none of the feature's names is in any file.
    names = ("api/v1/live", "live-client", "X-Studyforge-Live", "data-live", "key_variable")
    pages = [text for path, text in declared.items() if path.endswith((".html", ".js", ".css"))]
    assert pages and not any(name.encode() in page for page in pages for name in names)
