# The framework's own build environment (R15).
#
# What it is: the image in which `studyforge`'s tests, quality floor and lint
# run, so that a contributor needs Docker and nothing else, and a result never
# depends on whose machine produced it.
#
# ⚠️ What it is NOT: the reader's IDE. E12's `code-server-toolchain` is a
# different image with a different job — it carries a consuming project's
# toolchain (a JDK, a build tool, their caches) so a reader can work an
# exercise. This one carries pytest and ruff so a contributor can prove a
# change. Conflating them would put a compiler in a lint image and a linter in
# a reader's IDE, and would tie the framework's build to whichever corpus
# happened to be first.
#
# ⛔ No Docker socket is mounted into anything here, and nothing in this image
# talks to a daemon (spec §8.3). The rule is written about the serving
# process; it is repeated here because a build image is exactly where somebody
# would reach for one "just to run the integration tests".
#
# ---------------------------------------------------------------------------
# Pinned by tag AND digest. The tag says what it is for a reader; the digest is
# what actually makes the build reproducible, because a tag is a moving
# pointer and `python:3.14-slim` will mean something different next month.
FROM python:3.14-slim@sha256:cad9a2c871761c413caa6fdd6441c783451e740a48aaeba60ae62a8b53525ef6

# git is a test dependency, not a convenience: `tests/test_repository.py`
# asks `git check-ignore` whether the ignore rules still keep FND-04's golden
# fixtures trackable. Without git in the image that check cannot answer, and a
# check that cannot answer is a check that has stopped guarding anything.
#
# ⛔ `--no-install-recommends` and the list cleanup keep this to git alone. An
# image that quietly grows a compiler is an image whose results stop being
# attributable to what it declares.
RUN apt-get update \
 && apt-get install --no-install-recommends -y git \
 && rm -rf /var/lib/apt/lists/*

# ---------------------------------------------------------------------------
# The JavaScript runtime (W8, Ruling 21).
#
# ⭐ Why it is here at all: `tests/studyforge/render/pageassets/
# test_highlight_grammars.py` runs the vendored Prism grammars for real, and
# without a runtime it **skipped every test in that module** in the one
# environment that is authoritative. ⛔ "Did not run" is not evidence, so those
# were claims this image could not certify — they passed only on a host that
# happened to have `node`, which is the divergence R15 exists to eliminate.
#
# ⭐ **The figure, with its UNIT and its REF, because a historical reading
# carrying neither is not a measurement** (Ruling 240's general clause, `W122`):
# **38 tests — every test in that module — DERIVED at `af31fd7` in this image by
# hiding `node` from `PATH` and reading the module both ways: 38 passed with the
# runtime, 38 without it.** ⚠️ The unit is *the module's whole population*,
# which is why the property above is stated in words and the number is dated —
# a grammar added tomorrow moves the figure and does not move the property.
#
# ⛔ Pinned by version AND checksum, for exactly the reason the `FROM` line
# above is pinned by tag and digest: the version says what it is for a reader,
# and the checksum is what makes the build reproducible. ⚠️ An unpinned `node`
# — `apt-get install nodejs`, or a `latest` tarball — would reintroduce the
# problem this closes, one layer down: the tests would run, and what they ran
# against would depend on the day the image was built.
#
# ⚠️ **`TARGETARCH`, so the pin is not secretly a pin to one machine.** A
# hardcoded `x64` builds on this repository's own hardware and fails on a
# contributor's arm64 laptop, which breaks "Docker and nothing else" for
# everyone it does not happen to fit. An architecture with no recorded checksum
# fails **loudly**, naming itself, rather than falling back to something
# unverified.
#
# ⛔ Network is required HERE and only here — the same build/run split the
# `pip install` below relies on. `compose.yaml` gives the service
# `network_mode: none`, so nothing can reach one at test time.
ARG NODE_VERSION=24.21.0
ARG NODE_SHA256_AMD64=6e1db87ef58b8819e5d5402eff1536491b18edd8eb7bee5ef7897876e88dc5ff
ARG NODE_SHA256_ARM64=724282c3b43aec998aa9527380465b45d229e021b58035f5f4f63095eabfe5d5
ARG TARGETARCH

RUN set -eu; \
    case "${TARGETARCH}" in \
      amd64) node_arch=x64;   node_sha="${NODE_SHA256_AMD64}" ;; \
      arm64) node_arch=arm64; node_sha="${NODE_SHA256_ARM64}" ;; \
      *) echo "no pinned Node.js recorded for TARGETARCH='${TARGETARCH}';" \
              "add its checksum to docker/dev/Dockerfile rather than" \
              "installing an unpinned runtime" >&2; exit 1 ;; \
    esac; \
    tarball="node-v${NODE_VERSION}-linux-${node_arch}.tar.gz"; \
    apt-get update; \
    apt-get install --no-install-recommends -y curl; \
    curl -fsSLO "https://nodejs.org/dist/v${NODE_VERSION}/${tarball}"; \
    echo "${node_sha}  ${tarball}" | sha256sum --check --strict -; \
    tar -xzf "${tarball}" -C /usr/local --strip-components=1 \
        --no-same-owner --exclude=CHANGELOG.md --exclude=LICENSE --exclude=README.md; \
    rm -f "${tarball}"; \
    rm -rf /usr/local/lib/node_modules /usr/local/bin/npm /usr/local/bin/npx \
           /usr/local/bin/corepack /usr/local/include/node /usr/local/share/doc \
           /usr/local/share/man /usr/local/share/systemtap; \
    apt-get purge -y curl; \
    apt-get autoremove -y; \
    rm -rf /var/lib/apt/lists/*; \
    node --version

# ⛔ `npm`, `npx` and `corepack` are removed on the way in, and that is the
# same rule the git install states: an image that quietly grows a package
# manager is an image whose results stop being attributable to what it
# declares. ⚠️ It is also the stronger guarantee — a build step that *could*
# install a dependency at test time would make `network_mode: none` the only
# thing standing between this suite and an unpinned tree of packages. Nothing
# here needs one: the grammars are vendored in `src/`, and the runtime's only
# job is to execute them.
#
# ⭐ `tar --no-same-owner` because this runs as root at build time but the
# container runs as the invoking uid; without it the extracted tree carries
# ownership from the tarball's author.

# ---------------------------------------------------------------------------
# The browser (W36, QA-03/1, Ruling 40).
#
# ⭐ Why it is here at all: `tests/visual/` opens a page this repository
# generated in a real browser and reads back what no assertion over the source
# can see. ⛔ Without a browser in *this* image those checks **did not run** —
# 57 of them, measured — and Ruling 40 makes the pinned container the only
# authority for a reading, so a check that cannot run here is a check with no
# authority anywhere. ⚠️ The defect that priced this: `--measure: 80ch`
# resolves `ch` against **the element's own font**, so one declaration produced
# three different columns. Every stylesheet assertion passed.
#
# ⛔ Pinned by version AND checksum, for exactly the reason the `FROM` line and
# the Node.js tarball above are. ⚠️ An unpinned browser — `apt-get install
# chromium`, or a `latest` build — is worse here than anywhere else in this
# file: a contrast ratio, a focus order and a resolved column width are all
# measured **against the engine**, so an engine that changes under the image
# changes the answer without changing the question.
#
# ⭐ Chrome for Testing rather than a distribution package, and that is the
# reproducibility argument rather than a preference: its archives are immutable
# per version at a stable URL, so `${CHROME_VERSION}` plus the digest below is
# a complete description of which browser produced a reading. A distribution's
# `chromium` moves with the distribution and records no version a reader can
# pin.
#
# ⭐ `chrome-headless-shell` rather than full Chrome: it is the binary
# `tests/visual/discovery.py` already searches PATH for, it speaks the same
# DevTools protocol over `--remote-debugging-pipe`, and it needs **far fewer
# shared libraries than full Chrome's desktop set** — which is why the apt list
# below is as short as it is.
#
# ⛔ **NO COUNT IN THAT SENTENCE, AND THAT IS RULING 240 RATHER THAN VAGUENESS**
# (`W122`). It used to carry a number. ⚠️ No unit made it true: `CTO-55/1`
# printed five populations beside it — apt `lib*` packages, all apt packages,
# the binary's `DT_NEEDED` entries, transitive `ldd` lines, and `not found`
# entries — and the claimed figure was none of the five. ⛔ `CTO-56/8` then
# found the only unit that did reproduce it, and it was an instrument rather
# than a fact: a grep for `lib*` over this file, which counted `liberation`,
# `deliberately`, and the comment's own word in the very sentence making the
# claim.
#
# ⚠️ A corrected number would be falsified again by the next edit to the apt
# list below, which is the most likely history of the first one — the list was
# trimmed and the comment was not. ⭐ So a shipped comment either states a
# property that survives a trim, or it states nothing.
#
# ⛔ **The DERIVATION, for a reader who wants a figure rather than a property:
# run `ldd` on the installed binary, in this image.** That answers it at the
# version in front of you instead of at the version somebody last edited a
# comment, which is the whole of why no number is written here.
#
# ⚠️ **`TARGETARCH`, for the reason the Node block states**: an architecture
# with no recorded checksum fails **loudly**, naming itself, rather than
# falling back to something unverified.
#
# ---------------------------------------------------------------------------
# ⛔ **THE FONT IS PINNED BY VERSION AND CHECKSUM (`W124`, Ruling 236), AND THE
# SHARED LIBRARIES ARE STILL ONLY SNAPSHOT-PINNED. The two are different on
# purpose and the difference is measured, not felt.**
#
# ⭐ Ruling 236's rule: R10's pin must reach every input whose value a shipped
# check compares against a **recorded number**, and an input compared against a
# deliberately **loose** threshold is adequately pinned at the base image's
# snapshot *provided the threshold says it is loose*.
#
# ⚠️ The font is on the wrong side of that line and the libraries are not.
# `fonts-liberation` is a **font-metric input**: `tests/visual/test_capture.py`
# compares a body height and a capture size against recorded figures, and
# `--measure: 80ch` resolves against whatever face the image ships. ⛔ An engine
# that links a different build of `libxcb` renders the same glyph boxes; a
# different font does not.
#
# ⭐ **Why a version constraint plus a checksum over the installed files, and
# not either remedy `rows/W124.md` offered.** Both of those were weighed against
# a build and the readings are in `../../docs/tasks/handoffs/W124.md`:
#
#   * a `.deb` from `snapshot.debian.org` pins the **package file** and adds a
#     fourth build-time host — and the least reliable one in the set — to buy
#     nothing: if `deb.debian.org` is unreachable, `apt-get update` two lines
#     up has already failed the build.
#   * a vendored font costs **4 360 440 bytes** of binary in the repository
#     (measured) plus an OFL-1.1 licence to carry, and still leaves three
#     build-time remotes, so it does not make the build offline either.
#   * ⭐ **What is recorded below pins the bytes the layout engine actually
#     reads** — the installed `.ttf` files — which is one level closer to the
#     input than a package file is, and it is the same two-part pin (a version
#     that says what was asked for, a checksum that says what arrived) that the
#     `FROM` line, the Node.js tarball and the browser archive all use.
#
# ⭐ `Architecture: all` and `Depends:` empty (both measured), so unlike `node`
# and the browser **one recorded version and one checksum list covers every
# architecture** — there is no per-arch case to get wrong here.
#
# ⚠️ **THE COST, STATED RATHER THAN DISCOVERED: when Debian bumps this package
# the pinned version leaves the pool and THIS BUILD FAILS, loudly, naming the
# version it wanted.** ⛔ That is the idiom this file already states twice for
# an unrecorded `TARGETARCH`, and the remedy is one line plus a checksum list —
# far cheaper than a reading nobody can reproduce. A build that breaks visibly
# is not the same defect as an input that moves invisibly.
#
# ⛔ `fonts-liberation` is not cosmetic — it is the vendor's own declared
# dependency, and a font-metric check on an image with no fonts at all would
# measure a fallback nobody chose. ⚠️ It is also the image's **entire** font
# surface: 12 files and nothing else (measured), so `serif`, `sans-serif` and
# `monospace` all resolve inside this one package and pinning it pins every
# face any page in `tests/visual/` can reach.
ARG CHROME_VERSION=153.0.8010.36
ARG CHROME_SHA256_AMD64=a0079df5617da34bcd1debad18196568b072ec3d8ec57944008972a4fc970580
ARG CHROME_SHA256_ARM64=66776cb47927f88a44dda83ebd113b226714a45e7cd3b6e845907477a0b7b096

# ⛔ The font's two-part pin (`W124`). ⚠️ The epoch is part of the version and
# apt will not match without it.
ARG FONTS_LIBERATION_VERSION=1:2.1.5-3

RUN set -eu; \
    case "${TARGETARCH}" in \
      amd64) chrome_platform=linux64;      chrome_sha="${CHROME_SHA256_AMD64}" ;; \
      arm64) chrome_platform=linux-arm64;  chrome_sha="${CHROME_SHA256_ARM64}" ;; \
      *) echo "no pinned browser recorded for TARGETARCH='${TARGETARCH}';" \
              "add its checksum to docker/dev/Dockerfile rather than" \
              "installing an unpinned browser" >&2; exit 1 ;; \
    esac; \
    archive="chrome-headless-shell-${chrome_platform}.zip"; \
    apt-get update; \
    apt-get install --no-install-recommends -y \
        ca-certificates curl unzip \
        "fonts-liberation=${FONTS_LIBERATION_VERSION}" \
        libasound2t64 libatk-bridge2.0-0t64 libatk1.0-0t64 libatspi2.0-0t64 \
        libdbus-1-3 libexpat1 libgbm1 libglib2.0-0t64 libnspr4 libnss3 \
        libx11-6 libxcb1 libxcomposite1 libxdamage1 libxext6 libxfixes3 \
        libxkbcommon0 libxrandr2; \
    installed=$(dpkg-query -W -f='${Version}' fonts-liberation); \
    if [ "${installed}" != "${FONTS_LIBERATION_VERSION}" ]; then \
        echo "fonts-liberation is '${installed}' and this image pins" \
             "'${FONTS_LIBERATION_VERSION}'; a font metric is an input to" \
             "tests/visual/ (W124, Ruling 236) — record the new version and" \
             "its checksums in docker/dev/Dockerfile rather than letting the" \
             "face move under the readings" >&2; exit 1; \
    fi; \
    cd /usr/share/fonts/truetype/liberation; \
    printf '%s\n' \
      "ddce09ee3483b2d5faf61f0baba8592e76e0ac6dd4ab36683e5334c288bf5eef  LiberationMono-Bold.ttf" \
      "2ec6f3e5bd9b24c7fb04c229a1ee64f600e4072c03a041c96c2d62974c2ede2c  LiberationMono-BoldItalic.ttf" \
      "016743fc425a1b61eb349c72c02f3da6a1349d1da7a5d9aded27321397eed955  LiberationMono-Italic.ttf" \
      "5883330d94debd992952cd8f0571b225f478c2d797d3f36c7521b0a5c9bde0f2  LiberationMono-Regular.ttf" \
      "1b5f2da6f4cadce4c05b9ecebe3a6fcd374eb95ae443605e799f4c3287978939  LiberationSans-Bold.ttf" \
      "352e9dc2be89f210dbd3c0fd5dfaf97135de70e0beb5f22378601861462493a7  LiberationSans-BoldItalic.ttf" \
      "93ff5260834141b6f9d8f2b846d427f3a5dc492dbdce8ebdad406e38a38f34bb  LiberationSans-Italic.ttf" \
      "bade59d822652f76e6941aa87b40a87c13d1cc70db98ededb5011127efafd1d3  LiberationSans-Regular.ttf" \
      "443a4dbd694b6e4689925947b456e0532e10b19c90fa32eb39ea6c2cd9db9ebd  LiberationSerif-Bold.ttf" \
      "4b2635d2ec4d992373dcae577c742a98ecfd841ffc1b8a103b5f10db163dbc7a  LiberationSerif-BoldItalic.ttf" \
      "de18fe26337e03241952dca46398d5b66f3c5738d080bfd284f66e67b926f597  LiberationSerif-Italic.ttf" \
      "9caef765d2e891c10dd73658894f01e660fe0c1c83e0bda7d6edf561d8f623d4  LiberationSerif-Regular.ttf" \
      | sha256sum --check --strict -; \
    present=$(find /usr/share/fonts -type f | wc -l); \
    if [ "${present}" -ne 12 ]; then \
        echo "this image carries ${present} font file(s) and 12 are pinned;" \
             "an unrecorded face is an undeclared input to every text-metric" \
             "reading in tests/visual/ (W124)" >&2; exit 1; \
    fi; \
    cd /; \
    curl -fsSLO \
        "https://storage.googleapis.com/chrome-for-testing-public/${CHROME_VERSION}/${chrome_platform}/${archive}"; \
    echo "${chrome_sha}  ${archive}" | sha256sum --check --strict -; \
    unzip -q "${archive}" -d /opt; \
    mv "/opt/chrome-headless-shell-${chrome_platform}" /opt/chrome-headless-shell; \
    ln -s /opt/chrome-headless-shell/chrome-headless-shell /usr/local/bin/headless-shell; \
    chmod -R a+rX /opt/chrome-headless-shell; \
    rm -f "${archive}"; \
    apt-get purge -y curl unzip; \
    apt-get autoremove -y; \
    rm -rf /var/lib/apt/lists/*; \
    headless-shell --version

# ⛔ `curl` and `unzip` are purged on the way out, the same rule the Node block
# states: an image that quietly grows a way to fetch things at test time is an
# image whose results stop being attributable to what it declares.
#
# ⭐ `chmod -R a+rX` because this runs as root and the container runs as
# whatever uid invoked it — the same reason the Node extraction passes
# `--no-same-owner`. Without it a browser installed by root is a browser a
# contributor's uid cannot execute, and the checks would go back to skipping
# for a reason that has nothing to do with the browser being absent.

# ⚠️ git refuses to operate on a repository owned by a different uid — "dubious
# ownership" — and this container deliberately runs as whatever uid invoked it,
# which is rarely the one that owns the image's own filesystem. Without this
# line `git check-ignore` returns 128 instead of a verdict, and the ignore-rule
# regression test loses its answer for a reason that has nothing to do with the
# ignore rules.
#
# ⛔ Scoped to the one path this image ever holds. `safe.directory` exists to
# stop git running hooks and config from a tree somebody else planted; inside a
# throwaway container whose only mount IS the project under test, that is not a
# threat that can arise. ⛔ The same line on a host would be wrong.
RUN git config --system --add safe.directory /workspace

# ⚠️ Network is required HERE and only here. This is the whole of the tension
# in FND-03's acceptance, and it resolves cleanly because the two happen at
# different times: `pip install` needs the network at IMAGE-BUILD time; the
# test run needs none, and `compose.yaml` gives the service `network_mode:
# none` so it could not reach one if something tried.
COPY requirements.txt /opt/studyforge/requirements.txt
RUN pip install --no-cache-dir --disable-pip-version-check \
        --requirement /opt/studyforge/requirements.txt

# ---------------------------------------------------------------------------
# ⭐ **THE INSTALLED COMMAND: `studyforge` IS ON THE PATH, AND IT RUNS THE MOUNT**
# (`W211`). Before this block `command -v studyforge` answered 127 in here, so
# every reading about the installed command was host-only.
#
# ⛔ FND-03 refused an install because a SECOND COPY in site-packages could
# shadow the bind mount. That ground still holds and this install has no copy:
# it is EDITABLE, so pip writes a `.pth` naming `/workspace/src`, a `dist-info`
# and the console script — and the code is read from the mount on every run.
# ⭐ It is built with `/workspace/src` EMPTY, so the image holds no module of
# this project at all: without the mount, `studyforge` fails on
# `ModuleNotFoundError` instead of running something stale.
#
# ⛔ Not `pip install -e .` at RUN time, which writes into the checkout (`W209`'s
# class). It happens here, against a `/workspace` that is not the checkout, and
# only `pyproject.toml` and `README.md` cross — BIND-MOUNTED from the `project`
# build context `compose.yaml` names, so no layer keeps them and a change to
# either re-runs this step under `check`'s `--build`.
#
# ⚠️ What IS baked is the METADATA: the entry-point table and version as of this
# build. `tests/docker/test_dev_image_command.py` compares them with the MOUNTED
# `pyproject.toml` from inside the image, so a stale image is a red, not a lie.
#
# ⛔ **The build backend is an image input, pinned by version AND hash** (`W124`'s
# two-part pin). `pyproject.toml` asks for a RANGE, and build isolation would
# fetch whatever met it that day; `--no-build-isolation --no-index` leaves the
# pinned wheel the only backend reachable. ⭐ It is UNINSTALLED on the way out,
# the rule `curl` and `npm` already follow: an image that can build this package
# is one where an offline `pip install -e .` into the mount succeeds.
#
# ⚠️ A plain `docker build docker/dev` now fails at this step, because the
# declaration's one source is the checkout. Name it:
#     docker build --build-context project=. docker/dev
ARG SETUPTOOLS_VERSION=84.0.0
ARG SETUPTOOLS_SHA256=51a52592b3b99e102b609654876bd65f19f999935166d1352678931132b0c670

RUN --mount=type=bind,from=project,source=pyproject.toml,target=/workspace/pyproject.toml \
    --mount=type=bind,from=project,source=README.md,target=/workspace/README.md \
    set -eu; \
    printf 'setuptools==%s --hash=sha256:%s\n' \
        "${SETUPTOOLS_VERSION}" "${SETUPTOOLS_SHA256}" > /tmp/backend.txt; \
    pip install --no-cache-dir --require-hashes --no-deps --requirement /tmp/backend.txt; \
    mkdir -p /workspace/src; \
    pip install --no-cache-dir --no-index --no-build-isolation --no-deps \
        --editable /workspace; \
    pip uninstall -y setuptools; \
    rm -rf /tmp/backend.txt /workspace/src; \
    command -v studyforge
#
# ⛔ And no `COPY . .`. The acceptance is "from a clean checkout", meaning the
# checkout on disk, not a snapshot baked into a layer at some earlier commit.
# A copied source is a source that silently goes stale.

# HOME is /tmp because the container runs as the invoking user's numeric uid
# (see `check`), which has no entry in /etc/passwd and therefore no home. Tools
# that want somewhere to write find it, and nothing needs a real account.
# ⛔ It is a fixed, generic path on purpose: no host home directory is ever
# named in this file (R7).
ENV HOME=/tmp \
    RUFF_CACHE_DIR=/tmp/ruff-cache \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPYCACHEPREFIX=/tmp/pycache \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    STUDYFORGE_DEV_CONTAINER=1

# ⚠️ `RUFF_CACHE_DIR` keeps ruff's cache out of the bind mount for the same
# reason, and with a second benefit: a contributor's working tree never grows a
# `.ruff_cache/` they then have to ignore.
#
# ⚠️ `PYTHONDONTWRITEBYTECODE` above is not a tidiness setting. The checkout is
# bind-mounted, so a `__pycache__` written in here appears in the contributor's
# working tree owned by whatever uid the container used.
#
# ⛔ `PYTHONPYCACHEPREFIX` is the OTHER half, and W30 exists because the first
# half alone reads as sufficient and is not (`CTO-21/1`). `DONTWRITEBYTECODE`
# stops this image CREATING the taint; it does nothing about READING one. The
# checkout is bind-mounted, so a `__pycache__/` a HOST run left behind is
# visible in here — and CPython validates a cached module by the source's
# (mtime, size), so a stale `.pyc` beside a source the host has since changed
# under the same mtime and size is loaded in preference to the source. The
# container then certifies code that is in nobody's working tree, which is the
# divergence R15 exists to eliminate.
#
# ⭐ Setting the prefix moves the cache path the loader COMPUTES out of the
# mount entirely, so the tree's `__pycache__/` is not consulted at all — the
# read side, closed by the same mechanism that would have closed the write
# side. ⛔ The value must be outside `/workspace`; `tests/docker/
# test_dev_image.py` asserts that, and proves the redirect in both directions
# rather than asserting the variable is merely set.
#
# ⭐ `STUDYFORGE_DEV_CONTAINER` is how the suite knows where it is running.
# `tests/docker/test_dev_image.py` builds this image and runs the suite inside
# it; without a marker to skip on, that test would build a container, run the
# suite, which would build a container, forever.

WORKDIR /workspace

# No ENTRYPOINT. The command is the same one a contributor runs on the host —
# `python3 -m pytest` — and burying it in an entrypoint would make the two
# look different when the entire point is that they are identical.
CMD ["python3", "-m", "pytest"]
