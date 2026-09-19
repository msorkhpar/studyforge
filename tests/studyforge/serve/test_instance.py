"""Mirror of `src/studyforge/serve/instance.py` (R12) — over a real loopback socket.

⭐ **E05 SF-19b, the wire half**: one instance, given a root and nothing else, serves two
corpora with different placement profiles — content, state and the private progress
record — and the state namespace answers `no-store` over the wire.
"""

from __future__ import annotations

import contextlib
import json
import threading

import pytest

from studyforge.generate import read_corpus, write_site
from studyforge.progress import store_dir
from studyforge.serve.discovery import DiscoveryRefused, discover
from studyforge.serve.instance import (
    WRITERS,
    SiteCorpus,
    instance_of,
    make_instance,
    namespaces_of,
    site_discovery,
)
from studyforge.serve.routes import run, state
from studyforge.serve.routes.content import CorpusContent
from tests.studyforge.cli.serving import digests
from tests.studyforge.generate.corpora import BOTH
from tests.studyforge.serve.built import a_workspace, record, source_of, unit_keys
from tests.studyforge.serve.serving import fetch


@contextlib.contextmanager
def instance(root, **options):
    server = make_instance(root, port=0, **options)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield server
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def body(server, path):
    status, _, raw = fetch(server, path)
    assert status == 200, path
    return json.loads(raw)


def test_an_instance_given_only_a_root_serves_both_corpora_content_and_state(tmp_path):
    workspace = a_workspace(tmp_path)
    lines = []
    sources = sorted(source_of(workspace / name) for name in BOTH)
    with instance(workspace, log=lines.append) as server:
        assert [c["corpus"] for c in body(server, "/api/v1/state/")["corpora"]] == sources
        toc = body(server, "/api/v1/content/toc")["document"]
        assert [entry["corpus"] for entry in toc["corpora"]] == sources
        for name in BOTH:
            root = workspace / name
            source, key = source_of(root), unit_keys(root)[0]
            content = body(server, f"/api/v1/content/units/{source}/{key}")
            assert content["key"] == f"{source}/{key}"
            status, headers, raw = fetch(server, f"/api/v1/state/{source}/units/{key}")
            assert (status, headers["cache-control"]) == (200, "no-store")
            assert "etag" not in headers and "last-modified" not in headers
            assert json.loads(raw)["present"] is True
        version = body(server, "/api/v1")
    assert "state" in version["namespaces"]
    assert not any("/state/" in cacheable for cacheable in version["cacheable"])
    assert lines and not any(str(tmp_path) in line for line in lines)


def test_a_sibling_profile_page_is_served_where_state_says_it_is(tmp_path):
    workspace = a_workspace(tmp_path)
    root = workspace / "depth2"
    with instance(workspace) as server:
        state = body(server, f"/api/v1/state/{source_of(root)}/units/{unit_keys(root)[0]}")
        assert state["pages"]
        for page in state["pages"]:
            assert fetch(server, page)[0] == 200, page


def test_an_instance_over_one_corpus_root_serves_its_pages_and_never_its_record(tmp_path):
    root = a_workspace(tmp_path, ("depth1",)) / "depth1"
    key = unit_keys(root)[0]
    record(root, key)
    with instance(root) as server:
        state = body(server, f"/api/v1/state/{source_of(root)}/units/{key}")
        assert state["practices"]["practice-one"]["passed"] is True
        assert fetch(server, state["pages"][0])[0] == 200
        for path in (
            "/.studyforge/progress/progress.json",
            "/api/v1/assets/.studyforge/progress/progress.json",
        ):
            assert fetch(server, path)[0] == 404, path


def test_a_link_to_a_nested_corpus_record_is_refused_and_any_other_link_is_not(tmp_path):
    workspace = a_workspace(tmp_path)
    root = workspace / "depth2"
    record(root, unit_keys(root)[0])
    (root / "linked.json").symlink_to(store_dir(root) / "progress.json")
    (root / "other.json").write_text("{}\n", encoding="utf-8")
    (root / "linked-other.json").symlink_to(root / "other.json")
    with instance(workspace) as server:
        assert fetch(server, "/depth2/linked.json")[0] == 404
        assert fetch(server, "/api/v1/assets/depth2/linked.json")[0] == 404
        assert fetch(server, "/depth2/linked-other.json")[0] == 200


def test_state_ignores_the_query_and_refuses_every_write(tmp_path):
    workspace = a_workspace(tmp_path)
    root = workspace / "depth2"
    source, key = source_of(root), unit_keys(root)[0]
    with instance(workspace) as server:
        plain = fetch(server, f"/api/v1/state/{source}")
        queried = fetch(server, f"/api/v1/state/{source}?read={key}&passed=true")
        written = fetch(server, f"/api/v1/state/{source}", method="POST")
    assert plain[0] == queried[0] == 200
    assert plain[2] == queried[2]
    assert written[0] == 405


def test_a_root_with_no_corpus_is_refused_before_a_socket_exists(tmp_path):
    with pytest.raises(DiscoveryRefused):
        make_instance(tmp_path, port=0)


def test_an_instance_of_one_discovery_serves_every_corpus_it_found(tmp_path):
    # ⭐ The half the verb calls (`W230`): the same wiring as `make_instance`, from a
    # discovery already taken, and nothing is re-scanned to build it.
    workspace = a_workspace(tmp_path)
    discovered = discover(workspace)
    server = instance_of(discovered, port=0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        corpora = [c["corpus"] for c in body(server, "/api/v1/state/")["corpora"]]
        assert corpora == sorted(served.source for served in discovered.corpora)
        assert len(corpora) == len(BOTH)
        assert fetch(server, "/depth1/.studyforge/assets/page.css")[0] == 200
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_the_root_form_registers_what_the_one_constructor_builds_and_its_writers(tmp_path):
    discovered = discover(a_workspace(tmp_path))
    sources = {served.source: CorpusContent(served.corpus) for served in discovered.corpora}
    built = namespaces_of(discovered, sources)
    assert set(built) == {state.NAMESPACE, run.NAMESPACE}
    assert WRITERS == (run.NAMESPACE,)
    server = instance_of(discovered, port=0)
    try:
        assert {state.NAMESPACE, run.NAMESPACE} <= set(server.namespaces)
        assert server.writers == frozenset(WRITERS)
    finally:
        server.server_close()


def test_a_site_discovery_scans_the_site_writes_nothing_and_reports_nothing(tmp_path):
    root = a_workspace(tmp_path, ("depth1",)) / "depth1"
    site = tmp_path / "elsewhere"
    site.mkdir()
    write_site(root, site)
    corpus = read_corpus(root)
    before = digests(site), digests(root)
    discovered = site_discovery(corpus, root, site)
    (served,) = discovered.corpora
    assert (digests(site), digests(root)) == before
    assert isinstance(served, SiteCorpus) and discovered.report == ()
    assert (served.root, served.site, discovered.root) == (root, site, root)
    assert served.progress().directory == store_dir(root)
    scanned = served.rescan()
    assert scanned.units and scanned == served.startup.site
    # ⭐ The other way: the site emptied, the corpus root still built, and the scan finds nothing.
    for artifact in scanned.units:
        (site / artifact.path).unlink()
    assert not served.rescan().units
