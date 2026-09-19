"""Clause 5 — R8's floor: opened from a file, and reaching nothing but files.

⛔ **R8 is *"the floor is `file://`"*, and until now it was checked by reading
the markup.** `SF-12`'s own test resolves every href against a written tree,
which is the right check and a different one: it proves the page *names* nothing
remote. This proves the browser *fetched* nothing remote — including what a
stylesheet's `@font-face`, an `@import`, a favicon guess or a script's own
`fetch` would ask for, none of which appear in the page's markup at all.
"""

from __future__ import annotations

import pytest

from tests.visual import site
from tests.visual.page import SCHEMES, OpenPage

#: The one scheme a request is allowed to use.
LOCAL = "file:"

#: ⭐ `W362`: the faces arrive inside the stylesheet as `data:` URIs (the
#: register's D3), and a `data:` URI is bytes the page already holds — the
#: browser reports it as a request, but nothing leaves the machine.
EMBEDDED = "data:"


@pytest.mark.parametrize("case", site.pages())
@pytest.mark.parametrize("scheme", SCHEMES)
def test_a_page_opened_from_a_file_asks_for_nothing_but_files(
    open_page: OpenPage, built_site: site.Site, case: str, scheme: str
) -> None:
    """Every request the browser made while loading, and every one is local.

    ⭐ **Every page kind since `W98`.** R8's floor is a property of the generated
    *site*, and a container page or a root index reaches for the same two shared
    assets from a different depth — which is the arithmetic `W57` was about.
    """
    open_page.open(built_site.url(case), scheme=scheme)
    requests = open_page.requests()
    assert requests, "the browser recorded no request at all, not even for the page itself"
    remote = [url for url in requests if not url.startswith((LOCAL, EMBEDDED))]
    assert not remote, f"{case} in {scheme} reached the network: {remote}"


def test_the_page_and_both_assets_are_actually_fetched(
    open_page: OpenPage, built_site: site.Site
) -> None:
    """⭐ The control for the check above, and it is not optional.

    ⚠️ *"No remote request"* is trivially true of a page that requested nothing
    — including one whose stylesheet link is broken, which is a page that opens
    with no styles at all. So this asserts the stylesheet and the script were
    both asked for, by name.
    """
    open_page.open(built_site.url("depth2-unit-01"))
    asked = open_page.requests()
    for wanted in ("page.css", "page.js"):
        assert any(url.endswith(wanted) for url in asked), f"nothing asked for {wanted}: {asked}"


def test_the_stylesheet_was_not_merely_requested_but_applied(
    open_page: OpenPage, built_site: site.Site
) -> None:
    """⛔ A `file://` stylesheet can be fetched and still not apply.

    ⚠️ The failure has a name in this repository already: *"a page that renders,
    carries every word, and is unstyled, with no error anywhere"*. A request log
    cannot see it; a computed style can.
    """
    open_page.open(built_site.url("depth2-unit-01"))
    applied = open_page.evaluate(
        "getComputedStyle(document.body).fontFamily.includes('Iowan')"
        " || getComputedStyle(document.body).maxWidth !== 'none'"
        " || getComputedStyle(document.querySelector('figure.code')).borderStyle !== 'none'"
    )
    assert applied, "the page's own stylesheet had no effect on any computed style"


def test_a_page_that_reaches_a_remote_host_is_caught(
    open_page: OpenPage, damaged_sites: dict[str, site.Site]
) -> None:
    """⛔ Negative control: the `network` tree must fail the first check.

    ⭐ `example.invalid` is an RFC 2606 reserved name that resolves nowhere, so
    the control proves the *request was made* without any packet leaving the
    machine — which is the only honest way to test this offline.
    """
    broken = damaged_sites["network"]
    open_page.open(broken.url("depth2-unit-01"))
    remote = [url for url in open_page.requests() if not url.startswith((LOCAL, EMBEDDED))]
    assert remote, (
        "a page carrying an <img> pointed at a remote host recorded no remote request — "
        "this harness cannot see an R8 violation"
    )
