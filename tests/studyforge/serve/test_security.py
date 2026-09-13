"""Mirror of `src/studyforge/serve/security.py` (R12)."""

from __future__ import annotations

from email.message import Message

import pytest

from studyforge.serve.security import (
    CONTENT_POLICY,
    REFUSED_HOST,
    REFUSED_ORIGIN,
    REFUSED_PEER,
    REFUSED_SITE,
    SECURITY_HEADERS,
    refusal,
    require_loopback,
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
