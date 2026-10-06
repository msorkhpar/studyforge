r"""The tags a served page gains, and the validator that tells such a page from the file.

**What it does.** Adds the run client's script tag to an HTML page's bytes as the page is
answered (`with_client`), and, for an instance that offers live runs, the live client's tag
after it; spells the validator of such a page (`client_etag`). Split from `routes.assets` (R11).

**How you use it.** `with_client(body, client, live)` before the page's gate;
`client_etag(etag, live)` for its `ETag`. ⛔ Nothing here reads a file or a request, and a built
page is never edited: the tags exist only in the bytes a served response carries (R8).
"""

from __future__ import annotations

#: The one tag a served page gains, and where it goes. ⛔ Before the FIRST
#: `</head>`, and exactly once: a deferred script in the head runs before the
#: deferred page script at the end of the body, so the panel finds
#: `window.studyforge.run` already published when it looks.
CLIENT_TAG = '<script src="{path}" defer></script>'
HEAD_CLOSE = b"</head>"

#: What marks the validator of a page the client was added to. ⚠️ Inside the
#: opaque tag, so `If-None-Match`'s weak comparison still matches it against
#: itself and never against the plain file's.
CLIENT_ETAG_MARK = "+client"

#: The same, for a page the live client was added to as well.
LIVE_ETAG_MARK = "+live"

#: What a client path may be: one rooted URL path, and nothing that could close
#: the attribute it is written into. ⛔ Checked rather than escaped, because the
#: only caller passes `serve.routes.run.CLIENT_PATH` — a value that needed
#: escaping here would be a value this route should not have been given.
CLIENT_PATH_FORBIDDEN = "\"'<>& \t\r\n"


def client_tag(client: str) -> bytes:
    """Return the one script tag a served page gains, or raise on an unusable path."""
    if not client.startswith("/") or any(char in client for char in CLIENT_PATH_FORBIDDEN):
        raise ValueError(
            "the run client is served at one rooted URL path carrying no attribute "
            "delimiter; the value is not reproduced here, since a refusal never quotes a value "
            "that may be personal"
        )
    return CLIENT_TAG.format(path=client).encode("utf-8")


def with_client(body: bytes, client: str | None, live: str | None = None) -> bytes:
    """Return `body` with exactly one client tag before its first `</head>`.

    ⭐ `live` is the live client's path where this instance offers live runs, and then ONE more
    tag follows the run client's; `None`, which is every instance that declares none, adds nothing
    and the bytes are exactly what they were.

    ⛔ **Exactly one, and only where there is a head to close.** A page already
    carrying the tag is left alone, and a text with no `</head>` — anything a
    corpus happens to ship as `.html` that is not a built page — is served
    unchanged rather than having a script pushed into the middle of it.
    """
    if not client:
        return body
    tag = client_tag(client)
    if live:
        tag += client_tag(live)
    if client_tag(client) in body or HEAD_CLOSE not in body:
        return body
    return body.replace(HEAD_CLOSE, tag + HEAD_CLOSE, 1)


def client_etag(etag: str, live: bool = False) -> str:
    """Return the validator for the served form of a page, told apart from the file's."""
    mark = CLIENT_ETAG_MARK + (LIVE_ETAG_MARK if live else "")
    return f'{etag[:-1]}{mark}"' if etag.endswith('"') else etag + mark
