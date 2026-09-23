"""`W450` — the page's own faces load where the page is SERVED, under the policy it is served with.

⛔ **What went wrong, and why nothing here saw it** (`W447/1`). `faces.py` carries
the seven vendored faces inside `page.css` as `data:` URIs, on purpose, because a
`file://` page cannot rely on a font file (R8). ⛔ The served policy said
`font-src 'self'`, which does not admit `data:`, so every face was blocked on every
served page and the reader saw only the fallbacks. ⚠️ Every other clause in this
package opens `file://`, which carries no policy at all, so the faces loaded in
every reading the harness took.

⭐ **The reading, and why it takes this shape.**

- ⛔ **The real `serve` process**, started as a reader starts it, over a site
  `studyforge build` wrote. Not `served.py`'s in-process app, and never a header
  written here: the policy the browser applies must be the one the verb sends.
- ⭐ **Every face is asked to load**, because a face the page happens not to use
  stays `unloaded` whatever the policy says, and a check that read only the used
  ones would pass over a blocked italic. Each `FontFace` is the stylesheet's own,
  so its load is governed by `font-src` exactly as a used face's is.
- ⭐ **The face count is `faces.FACES`, not a number typed here**, so an eighth
  face is read on the day it lands.
- ⛔ **No CSP violation from any directive.** A listener is installed before the
  document exists, so a violation raised while the stylesheet parses is counted.

⚠️ **A test that only reads the header string is a proxy and does not settle
this** (the row's own words). What is asserted here is what the BROWSER did.
"""

from __future__ import annotations

import contextlib
import os
import signal
import subprocess
import sys
from collections.abc import Iterator
from pathlib import Path

import pytest

from studyforge.render.pageassets.faces import FACES
from tests.studyforge.cli.serving import LISTENING, build, pages_of
from tests.support import ProcessOutput, repository_root
from tests.visual.page import OpenPage

#: The fixture served. ⭐ `depth2` because its pages sit below the site root,
#: which is where a relative asset path would differ from the root's.
FIXTURE = "depth2"

#: Installed before any document exists, so a violation raised while the
#: stylesheet is parsed is recorded rather than missed.
LISTEN = """
window.__violations = [];
document.addEventListener('securitypolicyviolation', (event) => {
  window.__violations.push({
    directive: event.effectiveDirective,
    blocked: String(event.blockedURI).slice(0, 40),
  });
});
"""

#: Ask every face to load, then report each one's status. ⛔ A rejected load is
#: caught and its status read, so a blocked face reads `error` and not a throw.
FACE_STATES = """
(async () => {
  await document.fonts.ready;
  const faces = [...document.fonts];
  await Promise.all(faces.map((face) => face.load().catch(() => null)));
  return faces.map((face) => ({
    family: face.family.replace(/^["']|["']$/g, ''),
    weight: String(face.weight),
    style: face.style,
    status: face.status,
  }));
})()
"""


@contextlib.contextmanager
def serving(root: Path, site: Path) -> Iterator[str]:
    """`python3 -m studyforge.cli serve` over `site` on a free port; yield its origin."""
    with subprocess.Popen(  # noqa: S603 - fixed argv, no shell
        [sys.executable, "-m", "studyforge.cli", "serve", str(root), "--site", str(site)]
        + ["--port", "0"],
        cwd=repository_root(),
        env={**os.environ, "PYTHONPATH": "src"},
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ) as process:
        output = ProcessOutput(process)
        try:
            first = output.line(timeout=30)
            found = LISTENING.match(first)
            if found is None:
                process.kill()
                _, stderr = output.rest(timeout=10)
                pytest.fail(f"the verb did not start listening: {first!r} {stderr[-400:]!r}")
            yield f"http://127.0.0.1:{found.group(1)}"
        finally:
            if process.poll() is None:
                process.send_signal(signal.SIGINT)
            output.rest(timeout=30)
            process.wait(timeout=30)


def test_every_vendored_face_loads_on_a_served_page_and_no_policy_is_violated(
    open_page: OpenPage, tmp_path: Path
) -> None:
    """Every face in `faces.FACES` reports `loaded` over the served origin, with no violation."""
    root, site = build(FIXTURE, tmp_path)
    page = next(path for path in pages_of(root) if "/" in path)
    open_page.browser.call(
        "Page.addScriptToEvaluateOnNewDocument", {"source": LISTEN}, session=open_page.session
    )
    with serving(root, site) as origin:
        open_page.open(f"{origin}/{page}")
        assert open_page.evaluate("location.protocol") == "http:", "the page was not served"
        states = open_page.evaluate(FACE_STATES)
        violations = open_page.evaluate("window.__violations")
    expected = sorted((face.family, str(face.weight), face.style) for face in FACES)
    declared = sorted((state["family"], state["weight"], state["style"]) for state in states)
    assert declared == expected, f"the page declares other faces than faces.FACES: {declared}"
    unloaded = [state for state in states if state["status"] != "loaded"]
    assert not unloaded, f"{len(unloaded)} of {len(states)} faces did not load: {unloaded}"
    assert violations == [], f"the served page raised CSP violations: {violations}"
