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

from studyforge.execute import Editor
from studyforge.generate import read_corpus, write_site
from studyforge.progress import store_dir
from studyforge.serve.discovery import DiscoveryRefused, ServedCorpus, discover
from studyforge.serve.instance import (
    WRITERS,
    frames_for,
    instance_of,
    make_instance,
    namespaces_of,
    site_discovery,
)
from studyforge.serve.routes import quiz, run, state
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
    assert set(built) == {state.NAMESPACE, run.NAMESPACE, quiz.NAMESPACE}
    assert WRITERS == (run.NAMESPACE, quiz.NAMESPACE)
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
    # ⭐ `W385`: the plain `ServedCorpus`, its record at the root and its scan at the site.
    assert type(served) is ServedCorpus and discovered.report == ()
    assert (served.root, served.scan_root, discovered.root) == (root, site, root)
    assert served.progress().directory == store_dir(root)
    scanned = served.rescan()
    assert scanned.units and scanned == served.startup.site
    # ⭐ The other way: the site emptied, the corpus root still built, and the scan finds nothing.
    for artifact in scanned.units:
        (site / artifact.path).unlink()
    assert not served.rescan().units


# --- the frame policy an instance serves (`W427`) ---------------------------

#: An editor that is up. ⚠️ The folder is a made-up container path; the probe
#: reads the real one out of the container and never composes one.
UP = Editor(origin="http://127.0.0.1:8443", folder="/w/sources")


class StubEditors:
    """A probe factory and its probe in one: answers `UP`, forks nothing.

    ⛔ **`known()` answers only after `editor()` has been asked** (`W427`), because
    that is what a real probe's cache does and it is the property the frame policy
    rests on: composing a policy asks nothing, so a cold instance frames nothing.

    ⛔ **And it EXPIRES** (`W430`, `expire()`): the real cache goes cold again
    `EDITOR_TTL` seconds after the ask, and a stub that modelled only *cold
    until asked* could not tell a policy that LASTS from one that lapses.
    """

    def __init__(self, where: Editor | None) -> None:
        self.where = where
        self.asked = 0
        self.expired = False

    def __call__(self, corpus: ServedCorpus) -> StubEditors:
        return self

    def editor(self) -> Editor | None:
        self.asked += 1
        self.expired = False
        return self.where

    def known(self) -> Editor | None:
        return None if self.expired or not self.asked else self.where

    def expire(self) -> None:
        """Age the reading past the TTL, as `EditorProbe.known()` does by itself."""
        self.expired = True


def policy_sent(headers) -> dict[str, str]:
    """The policy a real response carried, read back as a browser reads it."""
    return dict(item.split(" ", 1) for item in headers["content-security-policy"].split("; "))


@contextlib.contextmanager
def instance_serving(server):
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield server
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_an_instance_with_no_editor_up_serves_frame_src_none(tmp_path):
    # ⭐ The real wiring, with the real probe: no editor container is running
    # for a temp fixture (and the pinned gate has no daemon to ask), so the
    # policy a reader is sent stays closed.
    server = instance_of(discover(a_workspace(tmp_path)), port=0)
    with instance_serving(server):
        headers = fetch(server, "/depth1/index.html")[1]
    assert policy_sent(headers)["frame-src"] == "'none'"


def test_a_served_page_may_frame_exactly_the_editor_the_run_index_publishes(tmp_path):
    # ⛔ **The two halves, read off ONE instance** — `W416/2`'s lesson: measuring
    # one side of framing proved nothing. Here the index says where the editor
    # is and the served header says the page may embed it, or the frame is dead.
    # ⭐ The index is asked FIRST, because the index is the reader that may ask.
    server = instance_of(discover(a_workspace(tmp_path)), port=0)
    server.namespaces[run.NAMESPACE].live.editor = StubEditors(UP)
    with instance_serving(server):
        published = body(server, f"/api/v1/{run.NAMESPACE}/")[run.EDITOR]
        headers = fetch(server, "/depth1/index.html")[1]
    assert published and all(
        where == {"origin": UP.origin, "folder": UP.folder} for where in published.values()
    )
    assert policy_sent(headers)["frame-src"] == UP.origin
    assert policy_sent(headers)["frame-ancestors"] == "'none'"
    assert headers["x-frame-options"] == "DENY"


def test_a_page_served_before_anything_asked_frames_nothing_and_forks_nothing(tmp_path):
    # ⛔ **Spec §8.3, and it is the whole shape of `W427`.** `frame-src` is composed
    # on EVERY response, so composing it may not ASK: a version that did would fork
    # `docker` to render a static page, putting a subprocess on the critical path
    # of every request. ⭐ A cold instance frames nothing; the run index warms it.
    editors = StubEditors(UP)
    server = instance_of(discover(a_workspace(tmp_path)), port=0)
    server.namespaces[run.NAMESPACE].live.editor = editors
    with instance_serving(server):
        page = fetch(server, "/depth1/index.html")[1]
        toc = fetch(server, "/api/v1/content/toc")[1]
        asset = fetch(server, "/depth1/.studyforge/assets/page.css")[1]
        cold = editors.asked
        warmed = body(server, f"/api/v1/{run.NAMESPACE}/")[run.EDITOR]
        after = fetch(server, "/depth1/index.html")[1]
    assert cold == 0, "serving pages asked the probe, and asking forks `docker`"
    assert [policy_sent(each)["frame-src"] for each in (page, toc, asset)] == ["'none'"] * 3
    assert warmed and policy_sent(after)["frame-src"] == UP.origin


def test_a_page_served_after_the_reading_expires_still_frames_the_editor(tmp_path):
    # ⛔ **`W430`, on the real instance wiring, ACROSS the TTL boundary.** The
    # policy used to be read through `EditorProbe.known()`, which goes cold
    # `EDITOR_TTL` seconds after the ask — so a served `frame-src` named the
    # editor for ten seconds and `'none'` from then on, and a reader was
    # essentially never inside that window. ⚠️ **A reading that does not cross
    # the boundary is not a reading of this**, which is how it shipped.
    editors = StubEditors(UP)
    server = instance_of(discover(a_workspace(tmp_path)), port=0)
    server.namespaces[run.NAMESPACE].live.editor = editors
    with instance_serving(server):
        body(server, f"/api/v1/{run.NAMESPACE}/")
        editors.expire()
        # ⭐ The aged state asserted and PRINTED, so a stub that quietly stayed
        # warm cannot make the line below pass while measuring nothing.
        print(f"probe reading after expiry: {editors.known()!r}")
        assert editors.known() is None, "the reading did not expire, so nothing was crossed"
        after = fetch(server, "/depth1/index.html")[1]
        asset = fetch(server, "/depth1/.studyforge/assets/page.css")[1]
    assert policy_sent(after)["frame-src"] == UP.origin
    assert policy_sent(asset)["frame-src"] == UP.origin
    assert policy_sent(after)["frame-ancestors"] == "'none'"


def test_the_policy_and_the_index_are_read_off_the_one_runs_and_one_probe(tmp_path):
    # ⭐ One `Runs` answers both, so a page load does not fork `docker` twice.
    discovered = discover(a_workspace(tmp_path))
    namespaces = namespaces_of(
        discovered, {served.source: CorpusContent(served.corpus) for served in discovered.corpora}
    )
    registered = namespaces[run.NAMESPACE]
    assert frames_for(namespaces) == registered.live.origins
    assert frames_for({state.NAMESPACE: namespaces[state.NAMESPACE]}) is None


def test_a_site_form_seam_that_registers_no_run_namespace_frames_nothing(tmp_path):
    # ⛔ `W386`'s replaceable seam: no execution means no editor, and a policy
    # naming one would be a widening nobody asked for.
    assert frames_for({}) is None


def test_a_page_reached_by_another_host_is_not_given_the_editor_and_is_told_why(tmp_path):
    # ⛔ **The trap this row was warned about, and it is silent without this.** An
    # editor authenticates with a `SameSite=Lax` cookie; a PORT is not part of a
    # site but a HOSTNAME is, so a page at `localhost` framing one at `127.0.0.1`
    # is cross-site, the cookie is withheld, and the frame shows a login form that
    # never succeeds with nothing in the browser to explain it. ⭐ So the editor is
    # withheld from that page and the server SAYS so.
    lines = []
    server = instance_of(discover(a_workspace(tmp_path)), port=0, log=lines.append)
    server.namespaces[run.NAMESPACE].live.editor = StubEditors(UP)
    with instance_serving(server):
        fetch(server, f"/api/v1/{run.NAMESPACE}/")  # the one reader that may ask (`W427`)
        matched = fetch(server, "/depth1/index.html")[1]
        crossed = fetch(server, "/depth1/index.html", host="localhost")[1]
        again = fetch(server, "/depth1/index.html", host="localhost")[1]
    assert policy_sent(matched)["frame-src"] == UP.origin
    assert policy_sent(crossed)["frame-src"] == "'none'"
    assert policy_sent(again)["frame-src"] == "'none'"
    withheld = [line for line in lines if "withheld" in line]
    assert len(withheld) == 1, withheld
    assert UP.origin in withheld[0] and "localhost" in withheld[0]


def test_the_site_itself_is_still_served_to_a_host_the_editor_is_withheld_from(tmp_path):
    # ⭐ **The design call, and its reason.** Narrowing the `Host` allow-list while
    # an editor is up would 403 a reader's whole site because a CONTAINER came up,
    # which is a refusal that moves under them. ⛔ Only the frame is withheld, and
    # the log names the host to use.
    server = instance_of(discover(a_workspace(tmp_path)), port=0)
    server.namespaces[run.NAMESPACE].live.editor = StubEditors(UP)
    with instance_serving(server):
        fetch(server, f"/api/v1/{run.NAMESPACE}/")
        page = fetch(server, "/depth1/index.html", host="localhost")
        api = fetch(server, "/api/v1/state/", host="localhost")
    assert page[0] == 200 and api[0] == 200
