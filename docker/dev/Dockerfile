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
# without a runtime it **skipped 38 tests** in the one environment that is
# authoritative. ⛔ "Did not run" is not evidence, so those were 38 claims this
# image could not certify — they passed only on a host that happened to have
# `node`, which is the divergence R15 exists to eliminate.
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
# DevTools protocol over `--remote-debugging-pipe`, and it links against 21
# shared libraries instead of Chrome's full desktop set.
#
# ⚠️ **`TARGETARCH`, for the reason the Node block states**: an architecture
# with no recorded checksum fails **loudly**, naming itself, rather than
# falling back to something unverified.
#
# ⚠️ The shared libraries and the fonts come from apt, and that is a stated
# limit rather than an oversight: the *engine* is checksum-pinned, its
# dependencies are pinned only as far as the base image's Debian snapshot is.
# ⛔ `fonts-liberation` is not cosmetic — it is the vendor's own declared
# dependency, and a font-metric check on an image with no fonts at all would
# measure a fallback nobody chose.
ARG CHROME_VERSION=153.0.8010.36
ARG CHROME_SHA256_AMD64=a0079df5617da34bcd1debad18196568b072ec3d8ec57944008972a4fc970580
ARG CHROME_SHA256_ARM64=66776cb47927f88a44dda83ebd113b226714a45e7cd3b6e845907477a0b7b096

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
        fonts-liberation \
        libasound2t64 libatk-bridge2.0-0t64 libatk1.0-0t64 libatspi2.0-0t64 \
        libdbus-1-3 libexpat1 libgbm1 libglib2.0-0t64 libnspr4 libnss3 \
        libx11-6 libxcb1 libxcomposite1 libxdamage1 libxext6 libxfixes3 \
        libxkbcommon0 libxrandr2; \
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

# ⛔ `studyforge` itself is deliberately NOT installed, not even with `-e`.
# The source arrives as a bind mount and `pyproject.toml`'s
# `pythonpath = ["src", "."]` resolves it from there. Installing it would put
# a second copy in site-packages that could shadow the mount, so the container
# and the host would be running different code while reporting the same
# result — which is precisely the failure R15 exists to prevent.
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
