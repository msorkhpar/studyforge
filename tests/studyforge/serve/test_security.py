"""Mirror of `src/studyforge/serve/security.py` (R12)."""

from __future__ import annotations

from email.message import Message

import pytest

from studyforge.serve.security import (
    CONTENT_POLICY,
    PUBLISHED_BIND,
    REFUSED_HOST,
    REFUSED_ORIGIN,
    REFUSED_PEER,
    REFUSED_SITE,
    SECURITY_HEADERS,
    content_policy,
    framable,
    frame_origin,
    refusal,
    require_loopback,
    response_headers,
    security_headers,
)


def headers(**values: str) -> Message:
    message = Message()
    for name, value in values.items():
        message[name.replace("_", "-")] = value
    return message


def test_a_local_same_site_request_is_not_refused():
    assert refusal("127.0.0.1", headers(Host="127.0.0.1:8765")) is None
    assert refusal("::1", headers()) is None


@pytest.mark.parametrize("peer", ["10.0.0.5", "192.168.1.2", "0.0.0.0", "::ffff:10.0.0.5"])
def test_a_peer_off_this_machine_is_refused(peer):
    assert refusal(peer, headers(Host="127.0.0.1")) == REFUSED_PEER


@pytest.mark.parametrize("host", ["evil.example", "evil.example:8765", "127.0.0.2", "[::2]:1"])
def test_a_host_that_is_not_loopback_is_refused_as_rebinding(host):
    assert refusal("127.0.0.1", headers(Host=host)) == REFUSED_HOST


@pytest.mark.parametrize("host", ["localhost", "LOCALHOST:1", "127.0.0.1:8765", "[::1]:80"])
def test_every_loopback_spelling_of_host_is_accepted(host):
    assert refusal("127.0.0.1", headers(Host=host)) is None


@pytest.mark.parametrize("site", ["cross-site", "CROSS-SITE"])
def test_a_cross_site_fetch_is_refused(site):
    assert refusal("127.0.0.1", headers(Sec_Fetch_Site=site)) == REFUSED_SITE


@pytest.mark.parametrize("site", ["same-origin", "same-site", "none"])
def test_a_same_site_fetch_is_accepted(site):
    assert refusal("127.0.0.1", headers(Sec_Fetch_Site=site)) is None


@pytest.mark.parametrize(
    "origin", ["http://evil.example", "https://evil.example:8765", "file://", "ftp://127.0.0.1"]
)
def test_an_origin_that_is_not_a_loopback_http_origin_is_refused(origin):
    assert refusal("127.0.0.1", headers(Origin=origin)) == REFUSED_ORIGIN


@pytest.mark.parametrize("origin", ["null", "http://127.0.0.1:8765", "http://localhost"])
def test_a_loopback_or_file_origin_is_accepted(origin):
    assert refusal("127.0.0.1", headers(Origin=origin)) is None


@pytest.mark.parametrize("host", ["0.0.0.0", "localhost", "::1", "192.168.1.2", ""])
def test_only_the_loopback_literal_may_be_bound(host):
    with pytest.raises(ValueError):
        require_loopback(host)
    require_loopback("127.0.0.1")


@pytest.mark.parametrize("host", ["localhost", "::", "192.168.1.2", ""])
def test_the_published_form_binds_its_containers_every_address_and_nothing_else(host):
    require_loopback(PUBLISHED_BIND, published=True)
    require_loopback("127.0.0.1", published=True)
    with pytest.raises(ValueError):
        require_loopback(host, published=True)


@pytest.mark.parametrize("peer", ["172.18.0.1", "10.0.0.5"])
def test_the_published_form_admits_its_gateway_peer_and_checks_everything_else(peer):
    # ⭐ Inside its container the peer is the compose network's gateway; the
    # port is published on 127.0.0.1 alone, so the peer check is compose's.
    assert refusal(peer, headers(Host="127.0.0.1:18504"), peers=None) is None
    assert refusal(peer, headers(Host="evil.example:18504"), peers=None) == REFUSED_HOST
    assert refusal(peer, headers(Host="127.0.0.1", Sec_Fetch_Site="cross-site"), peers=None) == (
        REFUSED_SITE
    )
    assert refusal(peer, headers(Host="127.0.0.1")) == REFUSED_PEER, "the default still checks"


@pytest.mark.parametrize(
    "directive",
    [
        "default-src 'self'",
        "connect-src 'self'",
        "frame-src 'none'",
        "frame-ancestors 'none'",
        "object-src 'none'",
        "base-uri 'none'",
        "form-action 'none'",
    ],
)
def test_the_content_policy_closes_what_could_reach_off_the_machine(directive):
    assert directive in CONTENT_POLICY.split("; ")


def test_every_response_header_set_carries_the_policy_and_refuses_framing():
    sent = dict(SECURITY_HEADERS)
    assert sent["Content-Security-Policy"] == CONTENT_POLICY
    assert sent["X-Frame-Options"] == "DENY"
    assert sent["X-Content-Type-Options"] == "nosniff"


# --- what this page may EMBED, composed at serve time --------------

EDITOR = "http://127.0.0.1:8443"


def directives(policy: str) -> dict[str, str]:
    """The policy read back as `{name: value}`, as a browser would read it."""
    return dict(item.split(" ", 1) for item in policy.split("; "))


def test_a_discovered_editor_is_admitted_by_frame_src_and_nothing_else_moves():
    composed = directives(content_policy([EDITOR]))
    assert composed["frame-src"] == EDITOR
    assert composed == directives(CONTENT_POLICY) | {"frame-src": EDITOR}


def test_an_instance_with_no_editor_keeps_frame_src_none():
    assert directives(content_policy())["frame-src"] == "'none'"
    assert directives(content_policy([]))["frame-src"] == "'none'"


def test_every_editor_discovered_is_named_once_in_the_order_it_was_admitted():
    policy = directives(content_policy([EDITOR, EDITOR, "http://localhost:9000"]))
    assert policy["frame-src"] == f"{EDITOR} http://localhost:9000"


@pytest.mark.parametrize(
    "origin",
    [
        "*",
        "http://*",
        "http://127.0.0.1:*",
        "https://evil.example",
        "http://127.0.0.1:8443 'unsafe-inline'",
        "http://127.0.0.1:8443; script-src *",
        "http://user@127.0.0.1:8443",
        "ftp://127.0.0.1:8443",
        "javascript:alert(1)",
        "",
        "   ",
    ],
)
def test_an_origin_that_is_not_a_loopback_http_origin_widens_nothing(origin):
    assert frame_origin(origin) is None
    assert directives(content_policy([origin]))["frame-src"] == "'none'"


@pytest.mark.parametrize("origin", [EDITOR, "http://127.0.0.1:8443/", "https://localhost:9"])
def test_a_loopback_editor_origin_is_named_as_an_origin_and_never_a_path(origin):
    named = frame_origin(origin)
    assert named is not None and not named.endswith("/")


def test_being_framed_is_refused_however_wide_frame_src_gets():
    # ⛔ The whole point: `frame-src` and `frame-ancestors` are opposite
    # questions, and widening the first must never touch the second.
    sent = dict(security_headers([EDITOR]))
    assert directives(sent["Content-Security-Policy"])["frame-ancestors"] == "'none'"
    assert sent["X-Frame-Options"] == "DENY"
    assert dict(security_headers()) == dict(SECURITY_HEADERS)


# --- every accepted loopback name frames the editor ----------------


@pytest.mark.parametrize(
    "host",
    ["127.0.0.1", "127.0.0.1:8770", "localhost", "localhost:8770", "[::1]:8770", "[::1]", None],
)
def test_a_page_reached_at_any_loopback_name_frames_the_editor(host):
    # ⭐ The editor has no password, so no session cookie makes a
    # `localhost` reader's frame cross-site; every accepted loopback name frames it.
    assert framable([EDITOR], host) == [EDITOR]
    sent = dict(response_headers([EDITOR], host))
    assert directives(sent["Content-Security-Policy"])["frame-src"] == EDITOR
    assert directives(sent["Content-Security-Policy"])["frame-ancestors"] == "'none'"
    assert sent["X-Frame-Options"] == "DENY"


@pytest.mark.parametrize("host", ["example.invalid", "evil.example:8770", "10.0.0.5:8770"])
def test_a_host_that_is_not_a_loopback_name_is_given_no_frame(host):
    assert framable([EDITOR], host) == []
    sent = dict(response_headers([EDITOR], host))
    assert directives(sent["Content-Security-Policy"])["frame-src"] == "'none'"


@pytest.mark.parametrize("origin", ["*", "http://127.0.0.1:*", "http://evil.example:8443"])
def test_only_a_loopback_origin_is_ever_named_whatever_host_asks(origin):
    assert framable([origin], "localhost:8770") == []


def test_the_composed_policy_carries_exactly_one_frame_src_and_one_frame_ancestors():
    # ⭐ The drift canary: this policy is COMPOSED from its directives rather than
    # patched by replacing a literal, so a `frame-src` that quietly failed to move
    # cannot happen — but a second copy of either directive would be a browser's
    # choice to make, so it is asserted rather than assumed.
    for frames in ((), (EDITOR,)):
        composed = content_policy(frames).split("; ")
        assert [d for d in composed if d.startswith("frame-src ")] == [
            f"frame-src {EDITOR if frames else chr(39) + 'none' + chr(39)}"
        ]
        assert [d for d in composed if d.startswith("frame-ancestors ")] == [
            "frame-ancestors 'none'"
        ]
        assert "connect-src 'self'" in composed


NAVIGATE = {
    "Sec_Fetch_Site": "cross-site", "Sec_Fetch_Mode": "navigate", "Sec_Fetch_Dest": "document",
}


def test_a_cross_site_navigation_to_a_page_is_accepted_when_the_caller_says_it_is_a_page():
    assert refusal("127.0.0.1", headers(**NAVIGATE), navigation=True) is None


def test_a_cross_site_navigation_is_refused_unless_the_caller_says_it_is_a_page():
    assert refusal("127.0.0.1", headers(**NAVIGATE)) == REFUSED_SITE


@pytest.mark.parametrize(
    "other",
    [
        {"Sec_Fetch_Mode": "cors"},
        {"Sec_Fetch_Mode": "no-cors"},
        {"Sec_Fetch_Dest": "iframe"},
        {"Sec_Fetch_Dest": "script"},
        {"Sec_Fetch_Dest": "empty"},
    ],
)
def test_a_cross_site_load_that_is_not_a_document_navigation_is_still_refused(other):
    assert refusal("127.0.0.1", headers(**{**NAVIGATE, **other}), navigation=True) == REFUSED_SITE


def test_a_navigation_does_not_excuse_a_foreign_host_or_origin():
    evil = headers(Host="evil.example", **NAVIGATE)
    assert refusal("127.0.0.1", evil, navigation=True) == REFUSED_HOST
    foreign = headers(Origin="http://evil.example", **NAVIGATE)
    assert refusal("127.0.0.1", foreign, navigation=True) == REFUSED_ORIGIN
