"""Whether this machine has a browser, said once and said out loud.

**What it does.** Looks for a Chromium-family binary, reports its version, and
turns absence into either a **named skip** or a **failure** — never into
silence.

**How you use it.** `state()` answers for the whole run and is cached.
`require_browser()` is what a test calls: it returns the binary or ends the test
with a reason a reader can act on. `report_line()` is the sentence the harness
prints at the end of *every* suite run, browser or no browser.

**Depends on.** `os`, `shutil`, `subprocess` and `pytest`. Nothing under `src/`.

## ⛔ The evidence state this harness claims, and the one it does not

⚠️ **The pinned image has no browser** — `docker/dev/Dockerfile` installs `git`
and a checksum-pinned Node.js and says of both that *"an image that quietly
grows a package manager is an image whose results stop being attributable to
what it declares"*. So these checks cannot be **pinned green** today.

⛔ **And they are not `host-verified` either, and claiming so would be an abuse
of that row.** The rubric §4b bounds `host-verified` by *the image is right to
exclude the subject*, and its tell is one question: **would the image's answer
be wrong, or just absent?** The subject here is how a *page* behaves in a
browser engine — a property of this repository's own output, not of the
workspace, not of the image, not of the developer's machine. A Chromium in the
image would answer the same question **better**, because it would be pinned. So
the answer is *absent*, which the rubric calls a gap to close and not a licence.

⭐ **Therefore: the honest state for every clause below is `unpinned green`, and
the gap is a finding with an owner** (`QA-03/1`, routed to whoever owns
`docker/dev/`). ⛔ Nothing here edits that image — `TC-00` and `FND-03` own it.

## ⛔ Absence is loud, counted, and can be made fatal

⚠️ **`SF-01` was approved on a host run whose two skips nobody read**, and this
wave the container's eight skips and the host's eight were found to be disjoint
sets. A skip nobody reads is this project's most repeated defect, so this
harness does three things instead of one:

1. every skipped check names **what is missing and how to supply it**;
2. `conftest.py` prints `report_line()` in the terminal summary of **every**
   run of the whole suite — not behind `-rs`, not behind `-v`;
3. `STUDYFORGE_VISUAL=required` turns absence into a **failure**, so a reviewer
   or a CI job that wants the guarantee can demand it in one word.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass
from functools import cache

import pytest

#: The binaries looked for, in order. ⛔ Chromium-family only: the harness
#: speaks the DevTools protocol, and Firefox's is not the same protocol. A
#: second engine is a second transport, and `QA-03/3` records that as an open
#: question rather than pretending one binary covers both.
CANDIDATES = (
    "google-chrome",
    "google-chrome-stable",
    "chromium",
    "chromium-browser",
    "chrome",
    "headless-shell",
)

#: The environment variable that names a browser explicitly, for a machine
#: where it is installed somewhere `PATH` does not reach.
BINARY_VARIABLE = "STUDYFORGE_VISUAL_BROWSER"

#: The environment variable that makes absence a failure instead of a skip.
DEMAND_VARIABLE = "STUDYFORGE_VISUAL"

#: Its one meaningful value.
DEMAND_VALUE = "required"


@dataclass(frozen=True)
class State:
    """What this machine can and cannot do, decided once per run."""

    binary: str | None
    version: str | None
    searched: tuple[str, ...]

    @property
    def available(self) -> bool:
        """Whether a browser was found."""
        return self.binary is not None

    @property
    def reason(self) -> str:
        """Why the visual checks did not run, in one line that names the remedy.

        ⛔ Never *"no browser"* on its own. A reason that does not name the
        remedy is a reason the next reader has to re-derive, which is how a
        skip becomes invisible.

        ⚠️ **One line, and that is a measurement rather than a preference.** In
        the pinned image this reason is printed 55 times by `-rs`, and the first
        draft ran to five lines — 275 lines of identical prose above the eight
        pre-existing skips, which is a way of hiding them. ⭐ The long form is
        printed **once**, by `report_line`, at the end of every run.
        """
        return (
            f"no browser: PATH has none of {self.searched[0]}… and "
            f"${BINARY_VARIABLE} is unset — QA-03/1, and see the harness line below"
        )

    @property
    def remedy(self) -> str:
        """The long form: what was searched for, and every way to change the answer."""
        return (
            f"searched PATH for {', '.join(self.searched)} and read "
            f"${BINARY_VARIABLE}. Install a Chromium-family browser, or name one in "
            f"${BINARY_VARIABLE}. ⛔ The pinned dev image has none either — QA-03/1. "
            f"Set ${DEMAND_VARIABLE}={DEMAND_VALUE} to fail instead of skipping."
        )


@cache
def state() -> State:
    """Find a browser once and reuse the answer for the whole session."""
    named = os.environ.get(BINARY_VARIABLE, "").strip()
    found = named or next((path for path in map(shutil.which, CANDIDATES) if path), None)
    if found and not os.path.exists(found):
        found = shutil.which(found)
    return State(binary=found, version=_version_of(found), searched=CANDIDATES)


def require_browser() -> str:
    """Return the browser binary, or end this test with a reason that names the remedy.

    ⛔ Fails rather than skips when `STUDYFORGE_VISUAL=required`, which is the
    whole of how this harness refuses to be a check that cannot fail.
    """
    current = state()
    if current.available:
        return str(current.binary)
    if os.environ.get(DEMAND_VARIABLE, "").strip().lower() == DEMAND_VALUE:
        pytest.fail(f"${DEMAND_VARIABLE}={DEMAND_VALUE}, and {current.remedy}", pytrace=False)
    pytest.skip(current.reason)


def report_line(skipped: int | None = None) -> str:
    """The one sentence the whole suite prints about this harness, run or not."""
    current = state()
    if current.available:
        where = "unpinned (the dev image has no browser — QA-03/1)"
        return f"visual harness: RAN on {current.version} — evidence state: {where}"
    counted = "" if skipped is None else f" — {skipped} visual check(s) DID NOT RUN"
    return f"visual harness: NO BROWSER{counted}. {current.remedy}"


def _version_of(binary: str | None) -> str | None:
    """The browser's own version string, or `None` if it will not say.

    ⭐ Recorded because the engine is **not pinned**: a contrast ratio or a
    focus order measured here is measured against whatever the machine had, and
    a review that cannot name the version cannot tell two runs apart.
    """
    if binary is None:
        return None
    try:
        result = subprocess.run(  # noqa: S603 - a path this module resolved
            [binary, "--version"], capture_output=True, text=True, timeout=30, check=False
        )
    except OSError, subprocess.SubprocessError:  # pragma: no cover - a broken binary
        return None
    return result.stdout.strip() or None
