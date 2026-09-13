"""Mirror of `src/studyforge/serve/app.py` (R12) — over a real loopback socket.

⭐ **These are the row's loopback measurement.** Every test here binds `127.0.0.1`
port `0` and connects to it; run inside `docker/dev/check` they are what says
loopback exists in a container started with no network.
"""

from __future__ import annotations

import json

import pytest

from studyforge.generate import write_site
from studyforge.generate.declarations import read_corpus
from studyforge.serve.app import ServingServer, make_server
from studyforge.serve.response import json_response
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
