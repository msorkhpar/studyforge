"""The page's live client, read in a real headless browser against a real served instance.

⭐ **What is read is the traffic and the storage.** A Chromium-family browser loads a page that has
one live-capable example and one live-capable practice, a scenario script types a FAKE key
(`sk-test-` and random hex) and presses the buttons, and the SERVER records every request it was
sent (request line, headers, body) and every line it logged. The key must be in exactly one: the
body of the live-run `POST`. ⛔ No real key and no real API; the launcher is a stand-in.

Skipped where this machine has no browser. The scenario script lives in the test's own page, adds
nothing to the client, and removes its own text from the dumped page, so a key it carries cannot
be mistaken for one the client left in the markup.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

from studyforge.execute.live import redactions
from studyforge.serve.routes import live
from tests.studyforge.serve.routes.running import SOURCE, key, served_copy
from tests.studyforge.serve.routes.test_live import (
    EXAMPLE,
    Launches,
    declare_live,
    fake_key,
    serving_live,
)

BROWSER = next(
    (
        found
        for name in ("google-chrome", "chromium", "chromium-browser", "chrome-headless-shell")
        if (found := shutil.which(name))
    ),
    None,
)
pytestmark = pytest.mark.skipif(BROWSER is None, reason="no Chromium-family browser on PATH")

PAGE = """<!doctype html><html><head><meta charset="utf-8"><title>live page</title>
%(prelude)s</head>
<body>
<div data-code-examples data-corpus="%(corpus)s">
<details data-code-example data-code-open="%(path)s" open><summary>greet</summary>
<a data-code-path="%(path)s" href="#">greet.py</a></details></div>
<section data-practice="%(practice)s" data-corpus="%(corpus)s"><h3>a practice</h3></section>
<script>%(scenario)s</script>
</body></html>
"""

COMMON = r"""
(function () {
  var KEY = %(key)r, STORE = 'studyforge.live.key', log = {};
  document.currentScript.remove();
  function finish() {
    var out = document.createElement('pre'); out.id = 'result';
    out.textContent = JSON.stringify(log);
    document.body.appendChild(out); document.documentElement.setAttribute('data-done', '1');
  }
  function stored() {
    var s = null, l = null;
    try { s = sessionStorage.getItem(STORE) !== null; } catch (e) { s = 'blocked'; }
    try { l = localStorage.getItem(STORE) !== null; } catch (e) { l = 'blocked'; }
    return { session: s, local: l };
  }
  function when(test, then, limit) {
    var n = 0, t = setInterval(function () {
      n++;
      var found = test();
      if (found || n > (limit || 400)) { clearInterval(t); then(found); }
    }, 25);
  }
  function panel() { return document.querySelector('[data-live-panel]'); }
  function q(selector) { return document.querySelector(selector); }
  %(body)s
}());
"""

BASIC = r"""
  when(panel, function (found) {
    if (!found) { log.error = 'no panel'; return finish(); }
    var field = q('[data-live-field]');
    log.emptyAtStart = field.value === '';
    log.type = field.type; log.autocomplete = field.getAttribute('autocomplete');
    log.labelled = !!q('label[for="' + field.id + '"]');
    log.controls = document.querySelectorAll('[data-live-run]').length;
    log.statusBefore = q('[data-live-status]').textContent;
    field.value = KEY; q('[data-live-use]').click();
    log.fieldAfterUse = field.value; log.stored = stored();
    log.statusAfterUse = q('[data-live-status]').textContent;
    var buttons = [].slice.call(document.querySelectorAll('[data-live-run] button'))
      .filter(function (b) { return b.textContent === 'Run live'; });
    buttons[0].click();
    when(function () {
      var s = q('[data-live-run] p').textContent;
      return s && s !== 'Running live…' ? s : null;
    }, function (status) {
      log.runStatus = status; log.output = q('[data-live-run] pre').textContent;
      buttons[1].click();
      when(function () {
        var s = document.querySelectorAll('[data-live-run] p')[1].textContent;
        return s && s !== 'Running live…' ? s : null;
      }, function (second) { log.secondStatus = second; finish(); });
    });
  });
"""

OPTIN = r"""
  when(panel, function () {
    var field = q('[data-live-field]'), box = q('[data-live-remember]');
    log.boxStart = box.checked; log.start = stored();
    field.value = KEY; box.checked = true; q('[data-live-use]').click();
    log.afterUse = stored();
    q('[data-live-clear]').click();
    log.afterClear = stored(); log.boxAfterClear = box.checked;
    field.value = KEY; box.checked = false; q('[data-live-use]').click();
    log.afterNoOptin = stored();
    finish();
  });
"""

BLOCKED = r"""
  when(panel, function () {
    var field = q('[data-live-field]');
    field.value = KEY; q('[data-live-use]').click();
    log.status = q('[data-live-status]').textContent;
    var run = [].slice.call(document.querySelectorAll('[data-live-run] button'))[0];
    run.click();
    when(function () {
      var s = q('[data-live-run] p').textContent;
      return s && s !== 'Running live…' ? s : null;
    }, function (status) { log.runStatus = status; finish(); });
  });
"""

RELOAD = r"""
  log = JSON.parse(sessionStorage.getItem('log') || '{}');
  function keep() { sessionStorage.setItem('log', JSON.stringify(log)); }
  when(panel, function () {
    var field = q('[data-live-field]');
    if (!sessionStorage.getItem('phase')) {
      field.value = KEY; q('[data-live-use]').click();
      sessionStorage.setItem('phase', 'one');
      return location.reload();
    }
    if (sessionStorage.getItem('phase') === 'one') {
      log.afterReload = { empty: field.value === '', status: q('[data-live-status]').textContent,
                          stored: stored() };
      sessionStorage.removeItem(STORE); sessionStorage.setItem('phase', 'two'); keep();
      return location.reload();
    }
    log.afterClearedReload = { empty: field.value === '',
      status: q('[data-live-status]').textContent, stored: stored() };
    finish();
  });
"""

PRELUDE_BLOCKED = (
    "<script>Storage.prototype.setItem = function () { throw new Error('refused'); };</script>"
)


def forms(secret: str) -> list[str]:
    return [*redactions(secret), secret]


def drive(server, scenario: str, secret: str, tmp: Path, prelude: str = "") -> dict:
    """Load the page in the browser; return the scenario's result and the dumped page."""
    host, port = server.server_address[:2]
    page = PAGE % {
        "prelude": prelude,
        "corpus": SOURCE,
        "path": EXAMPLE["path"],
        "practice": key(1),
        "scenario": COMMON % {"key": secret, "body": scenario},
    }
    (server.site_root / "live-page.html").write_text(page, encoding="utf-8")
    profile = tmp / "profile"
    done = subprocess.run(  # noqa: S603 - fixed argv, a loopback address
        [
            BROWSER,
            "--headless=new",
            "--no-sandbox",
            "--disable-gpu",
            "--no-first-run",
            "--disable-background-networking",
            f"--user-data-dir={profile}",
            "--virtual-time-budget=60000",
            "--dump-dom",
            f"http://{host}:{port}/live-page.html",
        ],
        capture_output=True,
        text=True,
        check=False,
        timeout=180,
        stdin=subprocess.DEVNULL,
    )
    dumped = done.stdout
    found = re.search(r'<pre id="result">(.*?)</pre>', dumped, re.S)
    assert found, f"the scenario never finished: {dumped[-1500:]}"
    import html

    return {"result": json.loads(html.unescape(found.group(1))), "dom": dumped}


class Traffic:
    """What the server was sent: every request, and every line it logged."""

    def __init__(self, server) -> None:
        self.requests: list[tuple[str, str, dict, bytes]] = []
        self.logged: list[str] = []
        original = server.respond

        def record(request):
            body = getattr(request, "body", b"")
            heard = (request.method, request.path, dict(request.headers), body)
            self.requests.append(heard)
            return original(request)

        server.respond = record
        server._log = self.logged.append

    def holding(self, secret: str) -> list[tuple[str, str]]:
        """The `(method, path)` of every request that carries the key in any form, anywhere."""
        found = []
        for method, path, headers, body in self.requests:
            blob = (path + json.dumps(headers)).encode() + body
            if any(form.encode() in blob for form in forms(secret)):
                found.append((method, path))
        return found


@pytest.fixture
def world(tmp_path):
    root = served_copy(tmp_path / "corpora")
    declare_live(root)
    return root


def serve(world, launches=None):
    return serving_live(world, launches or Launches(["live output line"]))


def test_the_key_travels_in_the_body_of_one_live_request_and_nowhere_else(world, tmp_path):
    secret = fake_key()
    with serve(world) as server:
        traffic = Traffic(server)
        seen = drive(server, BASIC, secret, tmp_path)
    got = seen["result"]
    assert traffic.holding(secret) == [("POST", live.RUN_PATH)] * 2
    posted = [one for one in traffic.requests if one[1] == live.RUN_PATH]
    assert len(posted) == 2
    for _, _, headers, body in posted:
        assert json.loads(body)["key"] == secret
        assert headers["Content-Type"] == "application/json" and headers[live.HEADER] == "1"
        assert headers["Origin"].startswith("http://127.0.0.1:")
        assert "Cookie" not in headers and "Authorization" not in headers
    # ⛔ Not in a URL, a query string, a header of any other request, a log line or the page.
    assert not any(form in line for line in traffic.logged for form in forms(secret))
    assert not any("?" in line.split(" HTTP/")[0] for line in traffic.logged if "POST" in line)
    assert all("Cookie" not in headers for _, _, headers, _ in traffic.requests)
    assert not any(form in seen["dom"] for form in forms(secret))
    assert got["emptyAtStart"] is True and got["type"] == "password"
    assert got["autocomplete"] == "off" and got["labelled"] is True and got["controls"] == 2
    assert "not started" not in got["statusBefore"] and got["fieldAfterUse"] == ""
    assert got["stored"] == {"session": True, "local": False}
    assert got["statusAfterUse"] == "Key set."
    assert got["runStatus"] == "Finished." and "live output line" in got["output"]
    assert got["secondStatus"] == "Finished."


def test_storage_is_session_by_default_local_only_on_opt_in_and_cleared_from_both(world, tmp_path):
    secret = fake_key()
    with serve(world) as server:
        seen = drive(server, OPTIN, secret, tmp_path)["result"]
    assert seen["boxStart"] is False and seen["start"] == {"session": False, "local": False}
    assert seen["afterUse"] == {"session": True, "local": True}
    assert seen["afterClear"] == {"session": False, "local": False}
    assert seen["boxAfterClear"] is False
    assert seen["afterNoOptin"] == {"session": True, "local": False}


def test_storage_the_browser_refuses_leaves_the_page_working_with_the_key_in_memory(
    world, tmp_path
):
    secret = fake_key()
    launches = Launches(["live output line"])
    with serve(world, launches) as server:
        traffic = Traffic(server)
        seen = drive(server, BLOCKED, secret, tmp_path, PRELUDE_BLOCKED)["result"]
    assert "memory" in seen["status"] and seen["runStatus"] == "Finished."
    assert launches.calls and launches.calls[0][2] == secret
    assert traffic.holding(secret) == [("POST", live.RUN_PATH)]


def test_after_a_reload_the_field_is_empty_and_with_session_storage_cleared_no_key_is_set(
    world, tmp_path
):
    secret = fake_key()
    with serve(world) as server:
        seen = drive(server, RELOAD, secret, tmp_path)["result"]
    assert seen["afterReload"]["empty"] is True and seen["afterReload"]["status"] == (
        "A key is set. It is not shown."
    )
    assert seen["afterClearedReload"] == {
        "empty": True,
        "status": "No key is set.",
        "stored": {"session": False, "local": False},
    }


def test_the_client_writes_no_console_call_and_names_no_url_with_the_key():
    text = live.CLIENT_FILE.read_text(encoding="utf-8")
    code = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    assert "console" not in code and "document.cookie" not in code
    assert "window.name" not in code and "postMessage" not in code
    assert "location." not in code.replace("location.protocol", "")
    assert re.search(r"\?\s*['\"]\s*\+\s*held", code) is None
    # ⭐ The key reaches a request in exactly one place: the body of the live-run POST.
    assert code.count("held") >= 1 and code.count("JSON.stringify") == 1
