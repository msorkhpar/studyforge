"""Mirror of `src/studyforge/serve/app.py` (R12) — over a real loopback socket.

⭐ **These are the row's loopback measurement.** Every test here binds `127.0.0.1`
port `0` and connects to it; run inside `docker/dev/check` they are what says
loopback exists in a container started with no network.
"""

from __future__ import annotations

import http.client
import json
import threading

import pytest

from studyforge.generate import write_site
from studyforge.generate.declarations import read_corpus
from studyforge.serve.app import ServingServer, make_server
from studyforge.serve.response import Response, json_response
from studyforge.serve.routes.content import CorpusContent
from studyforge.serve.security import REFUSED_HOST, REFUSED_ORIGIN, REFUSED_SITE, SECURITY_HEADERS
from tests.studyforge.generate.corpora import FIXTURES
from tests.studyforge.serve.serving import LEAK, fetch, running

CLIP = bytes(range(256)) * 4


@pytest.fixture
def site(tmp_path):
    root = tmp_path / "site"
    root.mkdir()
    write_site(FIXTURES / "depth1", root)
    (root / ".studyforge" / "clip.mp3").write_bytes(CLIP)
    return root


@pytest.fixture
def source():
    return CorpusContent(read_corpus(FIXTURES / "depth1"))


def assert_secured(headers):
    for name, value in SECURITY_HEADERS:
        assert headers[name.lower()] == value, name


def test_the_server_binds_loopback_on_an_ephemeral_port_and_answers(site, source):
    with running(site, source) as server:
        address, port = server.server_address[:2]
        assert address == "127.0.0.1"
        assert port > 0
        status, headers, body = fetch(server, "/api")
    assert status == 200
    assert json.loads(body)["versions"] == ["v1"]
    assert_secured(headers)


@pytest.mark.parametrize("address", ["0.0.0.0", "localhost", "::"])
def test_a_bind_off_the_loopback_literal_is_refused_before_a_socket_exists(site, source, address):
    with pytest.raises(ValueError):
        ServingServer((address, 0), site, source)


def test_a_missing_root_and_a_taken_namespace_are_refused(tmp_path, site, source):
    with pytest.raises(ValueError):
        make_server(tmp_path / "absent", source, port=0)
    with pytest.raises(ValueError, match="content"):
        make_server(site, source, port=0, namespaces={"content": lambda r, rest: None})


def test_the_version_document_names_the_namespaces_and_which_cache(site, source):
    with running(site, source) as server:
        status, _, body = fetch(server, "/api/v1")
    document = json.loads(body)
    assert status == 200
    assert document["namespaces"] == ["assets", "content"]
    assert document["cacheable"] == ["/api/v1/content/", "/api/v1/assets/"]


def test_content_revalidates_over_the_wire(site, source):
    with running(site, source) as server:
        status, headers, body = fetch(server, "/api/v1/content/toc")
        again, revalidated, empty = fetch(
            server, "/api/v1/content/toc", {"If-None-Match": headers["etag"]}
        )
    assert status == 200 and json.loads(body)["resource"] == "toc"
    assert (again, empty) == (304, b"")
    assert revalidated["etag"] == headers["etag"]
    assert "content-length" not in revalidated
    assert_secured(revalidated)


def test_a_unit_is_served_by_its_key(site, source):
    with running(site, source) as server:
        status, _, body = fetch(server, "/api/v1/content/units/depth-one/unit-02")
    assert status == 200
    assert json.loads(body)["key"] == "depth-one/unit-02"


def test_an_asset_range_arrives_as_exactly_those_bytes(site, source):
    with running(site, source) as server:
        status, headers, body = fetch(
            server, "/api/v1/assets/.studyforge/clip.mp3", {"Range": "bytes=10-19"}
        )
        refused, refused_headers, _ = fetch(
            server, "/.studyforge/clip.mp3", {"Range": "bytes=1024-"}
        )
    assert (status, body) == (206, CLIP[10:20])
    assert headers["content-range"] == "bytes 10-19/1024"
    assert headers["content-length"] == "10"
    assert refused == 416 and refused_headers["content-range"] == "bytes */1024"
    assert_secured(refused_headers)


def test_head_sends_the_headers_of_the_whole_file_and_no_body(site, source):
    with running(site, source) as server:
        status, headers, body = fetch(server, "/.studyforge/clip.mp3", method="HEAD")
    assert (status, body) == (200, b"")
    assert headers["content-length"] == str(len(CLIP))


def test_the_static_mount_and_the_assets_namespace_serve_the_same_built_bytes(site, source):
    css = site / ".studyforge" / "assets" / "page.css"
    with running(site, source) as server:
        index = fetch(server, "/")
        static = fetch(server, "/.studyforge/assets/page.css")
        api = fetch(server, "/api/v1/assets/.studyforge/assets/page.css")
    assert index[0] == 200 and index[1]["content-type"].startswith("text/html")
    assert static[2] == api[2] == css.read_bytes()


@pytest.mark.parametrize(
    ("offence", "message"),
    [
        ({"host": "evil.example:8765"}, REFUSED_HOST),
        ({"headers": {"Origin": "http://evil.example"}}, REFUSED_ORIGIN),
        ({"headers": {"Sec-Fetch-Site": "cross-site"}}, REFUSED_SITE),
    ],
)
def test_a_cross_site_or_rebinding_request_is_refused_and_the_same_request_without_it_is_not(
    site, source, offence, message
):
    with running(site, source) as server:
        refused = fetch(server, "/api/v1/content/toc", **offence)
        control = fetch(server, "/api/v1/content/toc")
    assert refused[0] == 403
    assert json.loads(refused[2])["error"] == message
    assert refused[1]["connection"] == "close"
    assert_secured(refused[1])
    assert control[0] == 200


def test_every_other_method_is_405_after_the_same_gate(site, source):
    with running(site, source) as server:
        status, headers, _ = fetch(server, "/api/v1/content/toc", method="POST")
        gated, _, _ = fetch(server, "/api/v1/content/toc", method="POST", host="evil.example")
    assert (status, headers["allow"]) == (405, "GET, HEAD")
    assert gated == 403


def test_a_namespace_nobody_registered_is_404_and_a_registered_one_is_reached(site, source):
    def state(request, rest):
        return json_response(200, {"rest": rest})

    with running(site, source) as server:
        unregistered = fetch(server, "/api/v1/state/snapshot")
    with running(site, source, namespaces={"state": state}) as server:
        registered = fetch(server, "/api/v1/state/snapshot")
        version = json.loads(fetch(server, "/api/v1")[2])
    assert unregistered[0] == 404
    assert (registered[0], json.loads(registered[2])["rest"]) == (200, "snapshot")
    assert "state" in version["namespaces"]
    assert "/api/v1/state/" not in version["cacheable"]


def test_a_failing_route_answers_a_fixed_500_and_logs_only_the_type(site, source):
    def boom(request, rest):
        raise RuntimeError(LEAK)

    lines = []
    with running(site, source, namespaces={"boom": boom}, log=lines.append) as server:
        status, _, body = fetch(server, "/api/v1/boom/x")
    assert status == 500
    assert LEAK.encode() not in body
    assert any("RuntimeError" in line for line in lines)
    assert not any(LEAK in line for line in lines)


def test_a_private_file_is_404_on_both_mounts(site, source):
    record = site / ".studyforge" / "clip.mp3"
    with running(site, source, private=lambda path: path == record.resolve()) as server:
        assert fetch(server, "/.studyforge/clip.mp3")[0] == 404
        assert fetch(server, "/api/v1/assets/.studyforge/clip.mp3")[0] == 404


# --- writers and streams -----------------------------------------------------


def echo(request, rest):
    return json_response(200, {"method": request.method, "rest": rest})


def test_post_reaches_a_writer_namespace_and_only_a_writer(site, source):
    spaces = {"writer": echo, "reader": echo}
    with running(site, source, namespaces=spaces, writers=("writer",)) as server:
        written = fetch(server, "/api/v1/writer/x", method="POST")
        read = fetch(server, "/api/v1/reader/x", method="POST")
        content = fetch(server, "/api/v1/content/toc", method="POST")
        static = fetch(server, "/index.html", method="POST")
    assert (written[0], json.loads(written[2])["method"]) == (200, "POST")
    assert [read[0], content[0], static[0]] == [405, 405, 405]


def test_a_writer_must_be_a_registered_namespace_and_never_content(site, source):
    with pytest.raises(ValueError, match="only a registered namespace"):
        make_server(site, source, port=0, writers=("content",))
    with pytest.raises(ValueError, match="only a registered namespace"):
        make_server(site, source, port=0, namespaces={"a": echo}, writers=("b",))


def test_a_post_body_is_drained_and_never_reaches_a_route(site, source):
    seen = []

    def writer(request, rest):
        seen.append(request)
        return json_response(200, {})

    with running(site, source, namespaces={"w": writer}, writers=("w",)) as server:
        small = _post(server, "/api/v1/w/x", b'{"command": ["rm"]}')
        large = fetch(server, "/api/v1/w/x", {"Content-Length": str(10**6)}, method="POST")
    assert small == 200 and large[0] == 413
    assert len(seen) == 1 and not hasattr(seen[0], "body")


class Chunks:
    """One chunk, then a stream WAITING on its next one — the shape of a quiet run.

    ⚠️ A stream that kept writing would find the hang-up by its own failed write;
    only one that is waiting needs the watcher, so that is the one read.
    """

    def __init__(self, waits: float):
        self.waits = waits
        self.sent = False
        self.cancelled = threading.Event()
        self.closed = threading.Event()

    def __iter__(self):
        return self

    def __next__(self):
        if not self.sent:
            self.sent = True
            return b"tick\n"
        self.cancelled.wait(self.waits)
        raise StopIteration

    def cancel(self):
        self.cancelled.set()

    def close(self):
        self.closed.set()


def serve_chunks(site, source, chunks):
    def streaming(request, rest):
        return Response(200, (("Content-Type", "text/plain"),), stream=chunks)

    return running(site, source, namespaces={"s": streaming})


def test_a_waiting_stream_is_cancelled_and_closed_when_the_client_hangs_up(site, source):
    chunks = Chunks(waits=60)
    with serve_chunks(site, source, chunks) as server:
        connection = http.client.HTTPConnection(*server.server_address[:2], timeout=10)
        connection.request("GET", "/api/v1/s/")
        reply = connection.getresponse()
        first = reply.readline()
        headers = {k.lower(): v for k, v in reply.getheaders()}
        reply.close()
        connection.close()
        assert chunks.cancelled.wait(10) and chunks.closed.wait(10)
    assert first == b"tick\n"
    assert headers["connection"] == "close" and "content-length" not in headers
    assert_secured(headers)


def test_a_stream_the_client_reads_to_its_end_is_closed_and_never_cancelled(site, source):
    chunks = Chunks(waits=0.5)
    with serve_chunks(site, source, chunks) as server:
        status, _, body = fetch(server, "/api/v1/s/")
    assert (status, body) == (200, b"tick\n")
    assert chunks.closed.is_set() and not chunks.cancelled.is_set()


def _post(server, path, body):
    connection = http.client.HTTPConnection(*server.server_address[:2], timeout=10)
    try:
        connection.request("POST", path, body=body)
        reply = connection.getresponse()
        reply.read()
        return reply.status
    finally:
        connection.close()


# --- what a served page may EMBED, on the wire ---------------------

EDITOR = "http://127.0.0.1:8443"


def policy_sent(headers) -> dict[str, str]:
    """The `Content-Security-Policy` a real response carried, read as a browser reads it."""
    sent = headers["content-security-policy"]
    return dict(item.split(" ", 1) for item in sent.split("; "))


def test_a_served_page_may_frame_the_editor_this_instance_discovered(site, source):
    # ⛔ Asserted on the RESPONSE, never on the constant: the constant is one
    # half of framing, and the reader's browser reads this.
    with running(site, source, frames=lambda: [EDITOR]) as server:
        status, headers, _ = fetch(server, "/index.html")
    assert status == 200
    assert policy_sent(headers)["frame-src"] == EDITOR


def test_a_served_instance_with_no_editor_still_sends_frame_src_none(site, source):
    with running(site, source, frames=lambda: []) as server:
        absent = fetch(server, "/index.html")[1]
    with running(site, source) as server:
        never = fetch(server, "/index.html")[1]
    assert policy_sent(absent)["frame-src"] == "'none'"
    assert policy_sent(never)["frame-src"] == "'none'"


def test_the_policy_widens_and_narrows_with_the_editor_rather_than_being_fixed(site, source):
    up = []
    with running(site, source, frames=lambda: list(up)) as server:
        before = fetch(server, "/index.html")[1]
        up.append(EDITOR)
        during = fetch(server, "/index.html")[1]
        up.clear()
        after = fetch(server, "/index.html")[1]
    assert policy_sent(before)["frame-src"] == "'none'"
    assert policy_sent(during)["frame-src"] == EDITOR
    assert policy_sent(after)["frame-src"] == "'none'"


def test_this_page_is_never_framable_however_wide_frame_src_gets(site, source):
    # ⛔ The other half of the two-sided property, and its answer is still no.
    with running(site, source, frames=lambda: [EDITOR]) as server:
        headers = fetch(server, "/index.html")[1]
        refused = fetch(server, "/api", headers={"Sec-Fetch-Site": "cross-site"})
    assert policy_sent(headers)["frame-ancestors"] == "'none'"
    assert headers["x-frame-options"] == "DENY"
    assert refused[0] == 403
    assert policy_sent(refused[1])["frame-ancestors"] == "'none'"


def test_an_origin_nobody_discovered_is_not_served_into_the_policy(site, source):
    hostile = ["https://evil.example", "*", "http://127.0.0.1:8443 'unsafe-inline'"]
    with running(site, source, frames=lambda: hostile) as server:
        headers = fetch(server, "/index.html")[1]
    assert policy_sent(headers)["frame-src"] == "'none'"
    assert "evil.example" not in headers["content-security-policy"]


def test_a_streamed_response_carries_the_same_composed_policy(site, source):
    # ⭐ `_write_stream` sends its own headers; a fix that reached only `_write`
    # would leave a streamed answer under the policy that blocked the frame.
    def stream(request, rest):
        return Response(200, (("Content-Type", "text/plain"),), stream=iter([b"one\n"]))

    with running(site, source, namespaces={"s": stream}, frames=lambda: [EDITOR]) as server:
        headers = fetch(server, "/api/v1/s/")[1]
    assert policy_sent(headers)["frame-src"] == EDITOR


NAVIGATE = {
    "Sec-Fetch-Site": "cross-site", "Sec-Fetch-Mode": "navigate", "Sec-Fetch-Dest": "document",
}


def test_a_page_may_be_navigated_to_from_another_site_but_the_api_and_a_fetch_may_not(site, source):
    with running(site, source) as server:
        page = fetch(server, "/index.html", headers=NAVIGATE)
        api = fetch(server, "/api/v1/content/toc", headers=NAVIGATE)
        root = fetch(server, "/api", headers=NAVIGATE)
        script = fetch(
            server, "/index.html",
            headers={**NAVIGATE, "Sec-Fetch-Mode": "cors", "Sec-Fetch-Dest": "empty"},
        )
    assert page[0] == 200
    assert api[0] == root[0] == script[0] == 403
    assert REFUSED_SITE.encode() in api[2]
