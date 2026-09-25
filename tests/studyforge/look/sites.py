"""A built site to look at, and the browser to look with, for `studyforge.look`'s tests.

**What it does.** Copies the flat fixture corpus into a test's own directory and
builds it there with the installed command's own `build` verb, so every test
reads a site exactly as a reader's build writes one.

**How you use it.** `site = built(tmp_path)`; `stand_in(tmp_path, exit=0)` for a
browser that answers as a real one does, with no browser installed;
`binary = a_browser()` in a test
that needs a real browser, which skips (or fails, under `STUDYFORGE_VISUAL=required`)
with the visual harness's own reason when this machine has none.

**Depends on.** `studyforge.cli` for the build, `tests.support` for the fixture's
place, and `tests.visual.discovery` for the one browser search the suite trusts.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

from studyforge.cli import main as studyforge
from tests.support import repository_root
from tests.visual.discovery import require_browser

#: The fixture corpus looked at: three units of prose, placed under `tree`.
FIXTURE = "tests/fixtures/depth1"


def built(tmp_path: Path) -> Path:
    """Build the flat fixture into its own root under `tmp_path`, and return that root."""
    root = tmp_path / "site"
    shutil.copytree(repository_root() / FIXTURE, root)
    assert studyforge(["build", str(root), "--out", str(root)]) == 0
    return root


def a_browser() -> str:
    """The browser the visual harness found, or this test ends with its reason."""
    return require_browser()


#: What the stand-in does: write a PNG for `--screenshot=`, print a DOM for
#: `--dump-dom`, and exit with the code it was made with. `{png}` is the file's
#: bytes: a real PNG signature, or not.
STAND_IN = """#!{python}
import os, signal, sys
args = sys.argv[1:]
with open(sys.argv[0] + ".args", "a") as log:
    log.write(" ".join(args) + "\\n")
if {die!r} == "always" or ({die!r} == "sandboxed" and "--no-sandbox" not in args):
    os.kill(os.getpid(), signal.SIGTRAP)
shot = next((a.split("=", 1)[1] for a in args if a.startswith("--screenshot=")), None)
if shot:
    open(shot, "wb").write({png!r})
elif "--dump-dom" in args:
    print("<html><head><title>stand-in</title></head><body>stand-in</body></html>")
sys.exit({exit})
"""

#: The first bytes of a PNG, which is all a capture checks of one.
PNG = b"\x89PNG\r\n\x1a\n" + b"stand-in"


def stand_in(tmp_path: Path, *, exit: int = 0, png: bytes = PNG, die: str = "") -> str:
    """Write an executable that answers the two flags a look uses; return its path.

    `die` is `"sandboxed"` for a browser whose sandbox cannot start here, which
    a signal ends unless `--no-sandbox` is passed, and `"always"` for one a
    signal ends whatever it is given. Every launch's flags land in `<path>.args`.
    """
    path = tmp_path / "stand-in-browser"
    text = STAND_IN.format(python=sys.executable, png=png, exit=exit, die=die)
    path.write_text(text, "utf-8")
    path.chmod(0o755)
    return str(path)
