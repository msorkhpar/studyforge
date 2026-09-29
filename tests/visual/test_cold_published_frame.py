"""A cold published instance frames its configured editor on the FIRST page load.

⛔ **The defect this reads:** a freshly started published site named no editor in
its `frame-src` until something asked for one, so a learner's first practice page
showed a blocked frame and needed a reload. ⭐ Here the editor origin is
configured (as a published compose configures it), NOTHING has been discovered,
and the page is opened straight onto a practice: the browser logs no
Content-Security-Policy violation and the stand-in editor, on its own origin, runs
its own script inside the frame — which it can do only if the frame was allowed to load.
"""

from __future__ import annotations

from collections.abc import Iterator

import pytest

from tests.visual import editor_standin, served, site
from tests.visual.page import OpenPage

CASE = "depth2-unit-01"


@pytest.fixture
def editor() -> Iterator[editor_standin.StandIn]:
    """The stand-in editor origin, for this check alone."""
    with editor_standin.running() as running:
        yield running


@pytest.mark.parametrize("name", [None, "localhost"])
def test_a_cold_published_page_frames_its_editor_with_no_reload(
    built_site: site.Site, open_page: OpenPage, editor: editor_standin.StandIn, name: str | None
) -> None:
    # ⭐ Both loopback names: the page at `127.0.0.1` and at `localhost` frame the editor.
    with served.serving(built_site, editor=editor.origin, configured=True) as cold:
        open_page.browser.call("Log.enable", session=open_page.session)
        open_page.open(cold.url(CASE, name))
        open_page.open_practice()
        open_page.evaluate(
            "new Promise((done, fail) => {"
            " const wanted = '[data-practice-frame=\"main\"] iframe';"
            " const stop = Date.now() + 20000;"
            " (function look() { if (document.querySelector(wanted)) { done(true); return; }"
            " if (Date.now() > stop) { fail(new Error('no editor frame')); return; }"
            " setTimeout(look, 50); })(); })"
        )
        editor.wait_for(lambda s: s.focused >= 1)
        complaints = [
            event["params"]["entry"]["text"]
            for event in open_page.browser.events
            if event.get("method") == "Log.entryAdded"
            and event["params"]["entry"].get("level") == "error"
            and "Content Security Policy" in event["params"]["entry"]["text"]
        ]
        assert complaints == [], f"the browser refused a frame on the first load: {complaints}"
