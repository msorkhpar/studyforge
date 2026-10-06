"""Mirror of `src/studyforge/serve/routes/pagetag.py` (R12): the tags a served page gains."""

from __future__ import annotations

import pytest

from studyforge.serve.routes import assets, pagetag

PAGE = b"<!doctype html><html><head><title>t</title></head><body></body></html>"


def test_the_names_are_the_ones_assets_has_always_exported():
    for name in (
        "with_client",
        "client_tag",
        "client_etag",
        "CLIENT_TAG",
        "HEAD_CLOSE",
        "CLIENT_ETAG_MARK",
        "CLIENT_PATH_FORBIDDEN",
    ):
        assert getattr(assets, name) is getattr(pagetag, name)


def test_a_page_with_no_live_client_gains_exactly_the_run_clients_tag():
    tag = b'<script src="/c.js" defer></script>'
    assert pagetag.with_client(PAGE, "/c.js") == PAGE.replace(b"</head>", tag + b"</head>")


def test_a_live_client_follows_the_run_client_and_never_stands_alone():
    both = pagetag.with_client(PAGE, "/c.js", "/l.js")
    assert both.index(b"/c.js") < both.index(b"/l.js") < both.index(b"</head>")
    assert pagetag.with_client(PAGE, None, "/l.js") == PAGE
    assert pagetag.with_client(both, "/c.js", "/l.js") == both


@pytest.mark.parametrize("path", ["l.js", '/a"b', "/a b", "/a<b", "/a'b", "/a&b"])
def test_a_path_that_could_close_the_attribute_is_refused(path):
    with pytest.raises(ValueError):
        pagetag.client_tag(path)


def test_a_live_page_has_a_validator_of_its_own():
    assert pagetag.client_etag('W/"x"', True) == 'W/"x+client+live"'
    assert pagetag.client_etag('W/"x"') == 'W/"x+client"'
    assert pagetag.client_etag("W/x") == "W/x+client"
