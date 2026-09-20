"""The one way a served page gets the run client (`W370`, `SF-24`).

⛔ Part of `src/studyforge/serve/routes/assets.py`'s mirror (R12), kept in its
own module because it is its own clause and `test_assets.py` is already at the
size a module divides at.

⭐ **The property under test is a pair, and only the pair is the property:** a
SERVED page carries exactly one script tag, and the FILE ON DISK carries none —
because R8's floor reads a built text that names the client as a defect, and a
page that could only be run from a server is the failure the floor exists for.
"""

from __future__ import annotations

import pytest

from studyforge.generate import write_site
from studyforge.serve.caching import weak_etag
from studyforge.serve.response import Request
from studyforge.serve.routes.assets import (
    CLIENT_ETAG_MARK,
    client_etag,
    client_tag,
    route,
    serve,
    with_client,
)
from studyforge.serve.routes.run import CLIENT_PATH
from tests.studyforge.generate.corpora import FIXTURES

#: What a page looks like before anything is added to it.
PAGE = b"<!doctype html>\n<html>\n<head>\n<title>x</title>\n</head>\n<body>hi</body>\n</html>\n"

#: The tag the serving process adds, at the path the run namespace serves it at.
TAG = f'<script src="{CLIENT_PATH}" defer></script>'.encode()


@pytest.fixture
def site(tmp_path):
    root = tmp_path / "site"
    root.mkdir()
    write_site(FIXTURES / "depth1", root)
    return root


def get(root, path, client=None, **headers):
    return serve(root, Request("GET", path, headers), path, client=client)


# --- the insertion itself ---------------------------------------------------


def test_the_tag_goes_in_once_before_the_first_head_close():
    # ⛔ Exactly one, and before `</head>`: a deferred script in the head runs
    # before the deferred page script at the end of the body, so the panel finds
    # `window.studyforge.run` already published when it looks.
    served = with_client(PAGE, CLIENT_PATH)
    assert served.count(TAG) == 1
    assert served.index(TAG) < served.index(b"</head>")
    assert served.replace(TAG, b"") == PAGE


def test_a_second_head_close_gets_nothing():
    # ⚠️ `replace(..., 1)` rather than a global one, asserted: a page carrying
    # the string twice would otherwise load the client twice.
    doubled = PAGE + PAGE
    assert with_client(doubled, CLIENT_PATH).count(TAG) == 1


def test_no_client_named_means_the_bytes_are_untouched():
    # ⭐ The `None` arm is the ordinary one: an instance that registers no run
    # namespace serves exactly what is on disk.
    assert with_client(PAGE, None) == PAGE
    assert with_client(PAGE, "") == PAGE


def test_a_page_already_carrying_the_tag_gains_no_second_one():
    once = with_client(PAGE, CLIENT_PATH)
    assert with_client(once, CLIENT_PATH) == once


def test_a_text_with_no_head_to_close_is_served_unchanged():
    # ⚠️ Anything a corpus happens to ship as `.html` that is not a built page:
    # a script pushed into the middle of it would be worse than no client.
    fragment = b"<p>not a page</p>\n"
    assert with_client(fragment, CLIENT_PATH) == fragment


@pytest.mark.parametrize(
    "path", ['/api/v1/run/"onload="x', "/api/v1/run/<script>", "api/v1/run/client.js", "/a b.js"]
)
def test_a_client_path_that_could_escape_the_attribute_is_refused(path):
    # ⛔ Checked rather than escaped: the only caller passes the run route's own
    # constant, so a value that needed escaping here is a value this route
    # should not have been given.
    with pytest.raises(ValueError):
        client_tag(path)


def test_the_real_client_path_is_accepted():
    # ⭐ The negative control, run negatively: the refusals above are the paths
    # and not the check.
    assert client_tag(CLIENT_PATH) == TAG


# --- the pair: served carries it, the file does not -------------------------


def test_a_served_page_carries_the_client_and_the_file_on_disk_does_not(site):
    before = (site / "index.html").read_bytes()
    answer = get(site, "/index.html", client=CLIENT_PATH)
    assert answer.status == 200
    assert TAG in answer.body
    assert (site / "index.html").read_bytes() == before
    assert TAG not in before


def test_the_same_page_served_with_no_client_is_the_file_exactly(site):
    answer = get(site, "/index.html")
    assert answer.body == (site / "index.html").read_bytes()
    assert TAG not in answer.body


@pytest.mark.parametrize("path", ["/.studyforge/assets/page.css", "/.studyforge/assets/page.js"])
def test_only_html_gains_the_client(site, path):
    # ⛔ A stylesheet or a script with a tag pushed into it is a file a browser
    # cannot parse — and the client belongs in the document, once.
    answer = get(site, path, client=CLIENT_PATH)
    assert answer.status == 200
    assert TAG not in answer.body
    assert answer.body == (site / path.lstrip("/")).read_bytes()


def test_the_api_assets_namespace_answers_the_same_way(site):
    # ⛔ One resolver, never two — this module's own rule, and two would be two
    # answers to *does this page carry the client?*.
    request = Request("GET", "/api/v1/assets/index.html", {})
    through = route(site, lambda path: False, request, "index.html", client=CLIENT_PATH)
    assert TAG in through.body
    assert through.body == get(site, "/index.html", client=CLIENT_PATH).body


# --- the validator tells the two forms apart --------------------------------


def test_the_served_form_carries_a_different_validator_from_the_file(site):
    # ⛔ The weak ETag is size and mtime, which do not move when the client is
    # inserted — so without a mark a page cached from a served origin and one
    # cached from a plain mount would collide under one tag.
    plain = dict(get(site, "/index.html").headers)["ETag"]
    served = dict(get(site, "/index.html", client=CLIENT_PATH).headers)["ETag"]
    assert plain != served
    assert served == client_etag(plain)
    assert CLIENT_ETAG_MARK in served


def test_a_conditional_request_matches_its_own_form_and_not_the_other(site):
    plain = dict(get(site, "/index.html").headers)["ETag"]
    served = dict(get(site, "/index.html", client=CLIENT_PATH).headers)["ETag"]
    assert get(site, "/index.html", **{"If-None-Match": plain}).status == 304
    assert get(site, "/index.html", client=CLIENT_PATH, **{"If-None-Match": served}).status == 304
    assert get(site, "/index.html", client=CLIENT_PATH, **{"If-None-Match": plain}).status == 200
    assert get(site, "/index.html", **{"If-None-Match": served}).status == 200


def test_a_validator_that_is_not_quoted_is_marked_rather_than_mangled():
    # ⚠️ `weak_etag` quotes, and this is the arm that says what happens if it
    # ever stops: a mark appended is still a distinct tag.
    assert client_etag("W/nope") == "W/nope" + CLIENT_ETAG_MARK
    assert client_etag('W/"a-b"') == 'W/"a-b' + CLIENT_ETAG_MARK + '"'


def test_the_mark_is_inside_the_opaque_tag(site):
    # ⭐ So `If-None-Match`'s weak comparison still matches it against itself:
    # the mark is part of the tag, not a second header a proxy could drop.
    stat = (site / "index.html").stat()
    assert client_etag(weak_etag(stat)).startswith('W/"')
    assert client_etag(weak_etag(stat)).endswith('"')
