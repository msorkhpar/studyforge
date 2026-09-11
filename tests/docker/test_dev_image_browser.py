"""The browser in the build environment, asserted rather than described (W36, QA-03/1).

⛔ **This is a second module and not a section of `test_dev_image.py`**, and the
reason is R11: that file is 583 lines against a 600-line ceiling for tests, so
the checks below would have taken it over. ⭐ They also have one subject —
*which browser this image carries and how a rebuild gets the same one* — which
is exactly the seam a module is supposed to be cut along.

**The split is the same one `test_dev_image.py` states.** Static checks read
`docker/dev/` and need no daemon and no network. One check asks the environment
it is running in, and can only answer inside the image — so it skips, named, on
a host.

## ⛔ Why a browser is in a build image at all

⚠️ `tests/visual/` opens a page this repository generated in a real browser and
reads back what no assertion over the source can see. ⛔ **Before `W36` those 57
checks DID NOT RUN in the pinned image** — `5277 passed, 68 skipped` at
`a0d7e88` — and Ruling 40 makes the pinned container the only authority for a
reading, so a check that cannot run there is a check with no authority
anywhere. ⭐ The defect that priced it: `--measure: 80ch` resolves `ch` against
the element's own font, so one correct declaration produced three different
columns and every stylesheet assertion passed.

## ⛔ Why the pin is the whole of it

⚠️ A contrast ratio, a focus order and a resolved column width are measured
**against the engine**. An engine that moves under the image changes the answer
without changing the question, which is worse here than for any other tool in
this file — so the browser is pinned by version AND checksum, the same two-part
pin the `FROM` line and the Node.js tarball use, and for the same reason.
"""

from __future__ import annotations

import os
import shutil

import pytest

from tests.docker.test_dev_image import DEV, MARKER, instructions, read

#: What `tests/visual/discovery.py` searches `PATH` for. ⛔ Imported in spirit
#: rather than by reference on purpose: this asserts that the image and the
#: harness agree, and a check that read the harness's own list could not
#: notice them disagreeing.
CANDIDATE_NAMES = (
    "google-chrome",
    "google-chrome-stable",
    "chromium",
    "chromium-browser",
    "chrome",
    "headless-shell",
)

#: The three variables `compose.yaml` carries across the boundary (W36).
PASSED_THROUGH = (
    "STUDYFORGE_VISUAL",
    "STUDYFORGE_VISUAL_BROWSER",
    "STUDYFORGE_VISUAL_CAPTURES",
)


# --- the pin ---------------------------------------------------------------


def test_a_browser_is_installed_and_pinned_by_version():
    # ⛔ The version says which bytes were asked for; the checksum below says
    # which arrived. Neither alone is a pin.
    dockerfile = instructions("Dockerfile")
    assert "ARG CHROME_VERSION=" in dockerfile, "no browser version is pinned"
    version = dockerfile.split("ARG CHROME_VERSION=")[1].split()[0]
    assert version[0].isdigit(), f"CHROME_VERSION is not a version: {version!r}"
    assert "${CHROME_VERSION}/" in dockerfile, "the pin is not what is fetched"


def test_the_browser_is_verified_against_a_recorded_checksum():
    # ⛔ **The half that makes the pin real**, in the same words the Node.js
    # check uses because it is the same requirement.
    dockerfile = instructions("Dockerfile")
    recorded = [line for line in dockerfile.splitlines() if line.startswith("ARG CHROME_SHA256_")]
    assert recorded, "no browser checksum is recorded"
    for line in recorded:
        digest = line.split("=", 1)[1].strip()
        assert len(digest) == 64 and all(c in "0123456789abcdef" for c in digest), line
    assert "sha256sum --check --strict" in dockerfile, "the download is not verified"


def test_the_archive_comes_from_an_immutable_per_version_url():
    # ⭐ Why Chrome for Testing rather than a distribution package: its archives
    # are immutable per version at a stable URL, so `${CHROME_VERSION}` plus the
    # digest is a complete description of which browser produced a reading.
    # ⛔ A `latest`, a channel name or a branch in the URL would make the
    # checksum a check on today's bytes and nothing more.
    dockerfile = instructions("Dockerfile")
    fetched = [line for line in dockerfile.splitlines() if "chrome-for-testing" in line]
    assert fetched, "the browser is not fetched from an immutable per-version archive"
    for line in fetched:
        for moving in ("/latest/", "/stable/", "/canary/", "LATEST_RELEASE"):
            assert moving not in line, f"the browser URL moves under the pin: {line.strip()!r}"


def test_an_architecture_with_no_recorded_checksum_fails_loudly():
    # ⛔ **Reaching for an unverified fallback is the failure the pin exists to
    # close.** An architecture nobody pinned must stop the build and say so —
    # and name itself, because the person who meets the message is on hardware
    # this repository has never built on.
    dockerfile = instructions("Dockerfile")
    assert "no pinned browser recorded for TARGETARCH" in read("Dockerfile")
    both = [line for line in dockerfile.splitlines() if "CHROME_SHA256_" in line]
    assert len(both) >= 3, f"fewer than two architectures are pinned: {both}"
    assert "amd64)" in dockerfile and "arm64)" in dockerfile, (
        "the browser is pinned to one architecture by accident, which breaks "
        "'Docker and nothing else' for everyone that architecture does not fit"
    )


def test_the_browser_does_not_arrive_from_a_package_manager():
    # ⚠️ `apt-get install chromium` reintroduces exactly what the pin closes:
    # the checks would run, and what they ran against would depend on the day
    # the image was built and on the distribution's snapshot.
    #
    # ⛔ Asserted against the **install lines**, not the whole file, for the
    # reason the Node.js version of this check records: a check that fires on
    # the correct implementation is a check somebody deletes.
    installed = [
        line
        for line in instructions("Dockerfile").splitlines()
        if "apt-get install" in line or "apt install" in line
    ]
    assert installed, "nothing is installed at all; has the base image changed?"
    for line in installed:
        for unpinned in ("chromium", "google-chrome", "chrome-headless-shell"):
            assert unpinned not in line, f"the browser is installed unpinned: {line.strip()!r}"


def test_nothing_that_can_fetch_at_test_time_survives_into_the_image():
    # ⛔ The same rule the git and Node.js installs state. `curl` and `unzip`
    # are needed at BUILD time and are purged on the way out, so
    # `network_mode: none` is not the only thing standing between this suite
    # and an unpinned download.
    dockerfile = instructions("Dockerfile")
    assert "apt-get purge -y curl unzip" in dockerfile, (
        "the fetch tools the browser install needs are not removed again"
    )


# --- how the image is RUN, which is what makes the checks survivable --------


def test_the_shared_memory_is_large_enough_for_a_full_page_capture():
    # ⛔ **A measurement, not a precaution.** Docker's default `/dev/shm` is
    # 64 MB; `tests/visual/page.py` asks for `captureBeyondViewport`, a
    # full-page screenshot transferred through shared memory. At the default
    # the GPU process crash-looped on `VALIDATION_ERROR_DESERIALIZATION_FAILED`
    # and the suite HUNG — 5 of 7 capture checks passed and the 6th never
    # returned. ⚠️ A hang is worse than a failure: it has no verdict at all.
    compose = instructions("compose.yaml")
    assert "shm_size:" in compose, (
        "no shared memory is declared; a full-page capture crash-loops the "
        "browser's GPU process at Docker's 64 MB default and the suite hangs"
    )


@pytest.mark.parametrize("variable", PASSED_THROUGH)
def test_the_visual_harness_variables_cross_into_the_container(variable: str):
    # ⭐ The pass-through, asserted where it is declared. ⛔ Without it a
    # reviewer who ran `STUDYFORGE_VISUAL=required docker/dev/check` would get
    # a green run that proved nothing, because the demand would have stopped at
    # the host — which is the most expensive way this could be wrong.
    # ⚠️ The exact list entry, not the bare name: `STUDYFORGE_VISUAL` is a
    # prefix of the other two, so a substring test would pass for a file that
    # carried only the longest of them.
    entries = [line.strip() for line in instructions("compose.yaml").splitlines()]
    assert f"- {variable}" in entries, (
        f"{variable} does not cross into the container, so a caller cannot ask "
        f"the one environment Ruling 40 makes authoritative for anything"
    )


def test_the_pass_through_sets_no_default_of_its_own():
    # ⛔ Pass-through and not policy. A default written in here would set what
    # every run of the pinned image demands, which changes what every reading
    # is taken against — and `compose.yaml` is not where that decision belongs.
    compose = instructions("compose.yaml")
    for name in PASSED_THROUGH:
        assert f"{name}:" not in compose, (
            f"{name} is given a value in compose.yaml; the bare-name form "
            f"passes the caller's answer through and invents nothing"
        )


# --- the acceptance, asserted from inside ----------------------------------


def test_a_browser_is_actually_on_the_path_in_here():
    # ⭐ **The acceptance, asked of the environment rather than of a file.**
    # Every check above reads `docker/dev/`; this one is the difference between
    # "the Dockerfile says it installs a browser" and "the browser is here".
    # ⛔ Ruling 21 exists because 38 tests were skipping on precisely that gap,
    # and this row exists because 57 more were.
    if not os.environ.get(MARKER):
        pytest.skip(
            f"not inside the dev image, where the browser is pinned. The static "
            f"checks above assert {DEV}/Dockerfile installs one; only a run "
            f"inside the image can assert it arrived."
        )
    found = {name: shutil.which(name) for name in CANDIDATE_NAMES}
    assert any(found.values()), (
        f"no browser on PATH inside the dev image, so 57 visual checks skip in "
        f"the one environment that certifies a result (Ruling 40). Searched "
        f"{list(CANDIDATE_NAMES)}, found none — W36 is undone."
    )


def test_the_harness_calls_a_run_in_here_pinned_and_a_run_outside_it_not():
    # ⛔ The evidence state is a CLAIM a review inherits, so it is asserted in
    # the environment that is entitled to make it. ⚠️ A host with Chrome
    # installed has a browser and no pin; only in here are the two the same.
    from tests.visual import discovery

    if not os.environ.get(MARKER):
        pytest.skip(
            "not inside the dev image, where the browser is pinned. "
            "tests/visual/test_discovery.py asserts both branches against a "
            "faked marker; only a run in here asserts the real one."
        )
    assert discovery.evidence_state().startswith("pinned"), discovery.evidence_state()
    assert discovery.state().available, "the state says no browser, inside the image"
    assert "evidence state: pinned" in discovery.report_line(0)
