"""Whether this machine has a browser, said once and said out loud.

**What it does.** Looks for a Chromium-family binary, reports its version, and
turns absence into either a **named skip** or a **failure** — never into
silence.

**How you use it.** `state()` answers for the whole run and is cached.
`require_browser()` is what a test calls: it returns the binary or ends the test
with a reason a reader can act on. `report_line()` is the sentence the harness
prints at the end of *every* suite run, browser or no browser.

**Depends on.** `os`, `shutil`, `subprocess` and `pytest`. Nothing under `src/`.

## ⛔ The evidence state this harness claims, and which run it claims it from

⭐ **The pinned dev image carries a browser**, pinned by version AND checksum
the way `docker/dev/Dockerfile` pins its base image and its Node.js. ⛔ So a run
**inside the image** is `pinned green` — the engine that produced the reading is
named in a file, and a rebuild gets the same one.

⛔ **A run on a host is not, and this module refuses to let one claim it.** The
engine there is whatever the machine happens to have, so a contrast ratio or a
focus order measured on it is measured against something no file records. ⚠️ It
is not `host-verified` either: that state is for a subject the image is right to
exclude, and this image **includes** it.

⭐ **Therefore `report_line()` says which of the two a run was**, keyed on the
image's own `STUDYFORGE_DEV_CONTAINER` marker, so a review quotes the line
rather than deciding for itself.

## ⛔ Absence is loud, counted, and can be made fatal

⚠️ **A skip nobody reads is a check that silently did not run**, and a host and
the container can skip disjoint sets. So this harness does three things instead
of one:

1. every skipped check names **what is missing and how to supply it**;
2. `conftest.py` prints `report_line()` in the terminal summary of **every**
   run of the whole suite — not behind `-rs`, not behind `-v`;
3. `STUDYFORGE_VISUAL=required` turns absence into a **failure**, so a reviewer
   or a CI job that wants the guarantee can demand it in one word.

## ⛔ The three variables that reach a VERDICT here are DECLARED

⛔ **A committed verdict may not depend on the host's environment SILENTLY.**
⭐ **The unit is *the distinct `STUDYFORGE_*` names `tests/visual/` reads*,
never a bare count**, and they partition in two:

| name | what it decides | partition |
|---|---|---|
| `STUDYFORGE_VISUAL` | absence is a FAILURE or a SKIP | ⛔ **a verdict** |
| `STUDYFORGE_VISUAL_BROWSER` | WHICH engine produced every reading | ⛔ **a verdict** |
| `STUDYFORGE_DEV_CONTAINER` | ADMISSIBILITY: pinned or not (R15) | ⛔ **a verdict** |
| `STUDYFORGE_VISUAL_CAPTURES` | where the PNGs land | ⭐ an artifact only |

⭐ **`STUDYFORGE_VISUAL=required` stays** — that variable is the whole of how this
harness refuses to be a check that cannot fail. ⛔ **`environment_declaration()`
PRINTS all three, in force, at the end of every run**, so a green reading
carries the environment it was taken in instead of leaving a reader to assume
one, and a SKIP is admissible because it says so. ⚠️ **The partition itself is
asserted over a fixture in `test_host_environment.py`, which is also where the
licence for the one ambient reader is stated.**
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
#: second engine is a second transport, and that stays an open
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

#: The marker `docker/dev/Dockerfile` sets, and the only thing that tells this
#: module which of the two evidence states a run is entitled to claim. ⛔ Read
#: rather than guessed: a browser being *present* says nothing about whether
#: anybody pinned it, and `report_line()` must not print `pinned` on a host that
#: merely happens to have Chrome.
CONTAINER_VARIABLE = "STUDYFORGE_DEV_CONTAINER"


@dataclass(frozen=True)
class State:
    """What this machine can and cannot do, decided once per run."""

    binary: str | None
    version: str | None
    searched: tuple[str, ...]

    #: ⛔ Whether `$STUDYFORGE_VISUAL_BROWSER` named the engine, rather than
    #: `PATH` supplying it. ⚠️ **A BOOLEAN and never the value**: that variable
    #: holds a path, and a path is somebody's home directory (R7). ⭐ It is what
    #: lets `reason` stop saying *"`$STUDYFORGE_VISUAL_BROWSER` is unset"* on a
    #: run where it was set and named something unusable.
    named: bool = False

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

        ⚠️ **One line.** In the pinned image this reason is printed once per
        skipped check by `-rs`, and a five-line reason would bury the other
        skips under identical prose. ⭐ The long form is printed **once**, by
        `report_line`, at the end of every run.

        ⛔ **Two branches**: a run with `$STUDYFORGE_VISUAL_BROWSER` set to
        something this machine cannot run must not say the variable is unset.
        ⚠️ **The variable's VALUE is never printed — it is a path (R7).**
        """
        if self.named:
            return (
                f"no browser: ${BINARY_VARIABLE} is set and names one this machine cannot "
                f"run — the pinned dev image has one, so see the harness line below"
            )
        return (
            f"no browser: PATH has none of {self.searched[0]}… and "
            f"${BINARY_VARIABLE} is unset — the pinned dev image has one, so see the "
            f"harness line below"
        )

    @property
    def remedy(self) -> str:
        """The long form: what was searched for, and every way to change the answer."""
        return (
            f"searched PATH for {', '.join(self.searched)} and read "
            f"${BINARY_VARIABLE}. Install a Chromium-family browser, or name one in "
            f"${BINARY_VARIABLE}. ⭐ The pinned dev image HAS one — run "
            f"`docker/dev/check` and these checks run there. "
            f"Set ${DEMAND_VARIABLE}={DEMAND_VALUE} to fail instead of skipping."
        )


@cache
def state() -> State:
    """Find a browser once and reuse the answer for the whole session."""
    named = os.environ.get(BINARY_VARIABLE, "").strip()
    found = named or next((path for path in map(shutil.which, CANDIDATES) if path), None)
    if found and not os.path.exists(found):
        found = shutil.which(found)
    return State(binary=found, version=_version_of(found), searched=CANDIDATES, named=bool(named))


def demand_is_in_force() -> bool:
    """Whether this run demanded a browser — the ONE site that reads `$STUDYFORGE_VISUAL`.

    ⛔ **One reader, deliberately**: `require_browser()` and
    `environment_declaration()` need the same answer, and a second spelling of it is how a run
    comes to PRINT *"absence
    is a SKIP"* while `require_browser()` FAILS.

    ⭐ **Exact, never merely truthy** — `STUDYFORGE_VISUAL=0` reads as *off* and
    must not mean *demand it*, which `test_discovery.py` asserts as a control.
    """
    return os.environ.get(DEMAND_VARIABLE, "").strip().lower() == DEMAND_VALUE


def require_browser() -> str:
    """Return the browser binary, or end this test with a reason that names the remedy.

    ⛔ Fails rather than skips when `STUDYFORGE_VISUAL=required`, which is the
    whole of how this harness refuses to be a check that cannot fail.
    """
    current = state()
    if current.available:
        return str(current.binary)
    if demand_is_in_force():
        pytest.fail(f"${DEMAND_VARIABLE}={DEMAND_VALUE}, and {current.remedy}", pytrace=False)
    pytest.skip(current.reason)


def evidence_state() -> str:
    """Which evidence state a run of this harness may claim.

    ⛔ **Keyed on the image's marker and not on the browser's presence**, which
    is the whole of the distinction: a host that happens to have Chrome
    installed has a browser and no pin, so its readings are `unpinned green` —
    the engine that produced them is named by nothing a rebuild can consult.

    ⭐ Inside the pinned image the same readings are `pinned green`, because
    `docker/dev/Dockerfile` records the browser's version and its checksum and
    `sha256sum --check --strict` refuses anything else. That is the state a
    reading is taken in to count (R15).
    """
    if os.environ.get(CONTAINER_VARIABLE, "").strip() == "1":
        return "pinned (version and checksum in docker/dev/Dockerfile)"
    return "unpinned (this host's browser, pinned by nothing — the image's is)"


def environment_declaration() -> str:
    """Every environment variable that reaches a VERDICT here, with the state in force.

    ⛔ **What matters is not that `$STUDYFORGE_VISUAL` exists but that no
    verdict depends on it SILENTLY.** ⭐ This is the line that makes the
    dependence DECLARED, and it names all three of the verdict-reaching
    partition so that a reading quoted into a record carries the environment it
    was taken in rather than the one its reader assumed.

    ⚠️ **A STATE is printed and never a VALUE.** `$STUDYFORGE_VISUAL_BROWSER`
    holds a path and a path is somebody's home directory (R7); which engine it
    selected is named by `report_line()` through the browser's own version
    string, which the browser supplies rather than the host.

    ⭐ **`STUDYFORGE_VISUAL_CAPTURES` is absent from this line ON PURPOSE**: it
    reaches no verdict, only where PNGs land. ⛔ A declared list is a CLOSED
    claim, so an over-wide one is as wrong as a short one.
    """
    demand = (
        f"={DEMAND_VALUE}, absence is a FAILURE"
        if demand_is_in_force()
        else " unset, absence is a SKIP"
    )
    engine = " names the engine" if state().named else " unset, the engine came from PATH"
    pin = (
        "=1, readings are PINNED"
        if evidence_state().startswith("pinned")
        else " unset, readings are UNPINNED"
    )
    return (
        f"declared environment: ${DEMAND_VARIABLE}{demand} · "
        f"${BINARY_VARIABLE}{engine} · ${CONTAINER_VARIABLE}{pin}"
    )


def report_line(skipped: int | None = None) -> str:
    """The one sentence the whole suite prints about this harness, run or not.

    ⛔ **It carries `environment_declaration()` on BOTH branches**. A
    green run that does not say whether absence would have been fatal depends
    on the environment silently.
    """
    current = state()
    declaration = environment_declaration()
    if current.available:
        return (
            f"visual harness: RAN on {current.version} — evidence state: "
            f"{evidence_state()} — {declaration}"
        )
    counted = "" if skipped is None else f" — {skipped} visual check(s) DID NOT RUN"
    return f"visual harness: NO BROWSER{counted}. {current.remedy} — {declaration}"


def _version_of(binary: str | None) -> str | None:
    """The browser's own version string, or `None` if it will not say.

    ⭐ Recorded because the engine is pinned in exactly one place — the dev
    image — and a run anywhere else is measured against whatever that machine
    had. A review that cannot name the version cannot tell two runs apart.
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
