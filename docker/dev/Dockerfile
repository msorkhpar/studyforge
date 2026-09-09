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
# ⭐ `STUDYFORGE_DEV_CONTAINER` is how the suite knows where it is running.
# `tests/docker/test_dev_image.py` builds this image and runs the suite inside
# it; without a marker to skip on, that test would build a container, run the
# suite, which would build a container, forever.

WORKDIR /workspace

# No ENTRYPOINT. The command is the same one a contributor runs on the host —
# `python3 -m pytest` — and burying it in an entrypoint would make the two
# look different when the entire point is that they are identical.
CMD ["python3", "-m", "pytest"]
