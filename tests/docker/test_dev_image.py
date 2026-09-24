"""The framework's build environment, asserted rather than described (R15).

Two kinds of test live here and the split is deliberate.

**Static checks — always run, need no daemon and no network.** They read the
files under `docker/dev/` and assert the properties that make the image a
reproducible build environment rather than a convenience: a pinned base, exact
tool versions, no network at run time, no Docker socket, no path from anybody's
machine. These are the checks that would otherwise be a reviewer's memory.

**Integration checks — opt-in.** They build the image and run the suite inside
it. ⛔ They are gated on `STUDYFORGE_DOCKER_TESTS=1` and not on "is Docker
reachable", because a build on a COLD cache needs the **network** and
*running* the tests must need none (R15). ⭐ The gate and its
reason live in `devgate.py`: the reason tells a cold cache from a warm
one and names the invocation that reaches these checks.

⛔ And they are gated a second time on not already being inside the image.
Without that, the suite would build a container, run the suite, which would
build a container, forever.

⚠️ No YAML parser is used, and not for want of one: framework source is
standard library only, so a test that needed PyYAML would be the first
dependency in the repository. The compose file is asserted as text, which is
also closer to what a reviewer reads.
"""

from __future__ import annotations

import os
import py_compile
import shutil
import sys
import tomllib
from pathlib import Path

import pytest

from tests.docker.devfiles import DEV, commands, instructions, read
from tests.docker.devgate import MARKER, announced_image, require_docker_run
from tests.support import repository_root, run, tool_on_path


def pyproject() -> dict:
    """`pyproject.toml`, parsed."""
    return tomllib.loads((repository_root() / "pyproject.toml").read_text("utf-8"))


def requirement_names() -> set[str]:
    """Every distribution pinned in `docker/dev/requirements.txt`, lowercased."""
    names = set()
    for line in read("requirements.txt").splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            names.add(stripped.split("==")[0].strip().lower())
    return names


# --- the files exist and say what they must --------------------------------


def test_the_three_files_exist_and_the_runner_is_executable():
    root = repository_root()
    for name in ("Dockerfile", "compose.yaml", "requirements.txt", "check"):
        assert (root / DEV / name).is_file(), f"{DEV}/{name} is missing"
    assert os.access(root / DEV / "check", os.X_OK), f"{DEV}/check is not executable"


def test_the_base_image_is_pinned_by_digest():
    # ⛔ A tag is a moving pointer. `python:3.14-slim` will mean different
    # bytes next month, and an image whose contents depend on the day it was
    # built is not the reproducible environment R15 asks for.
    from_lines = [line for line in read("Dockerfile").splitlines() if line.startswith("FROM ")]
    assert len(from_lines) == 1, f"expected one FROM, found {from_lines}"
    assert "@sha256:" in from_lines[0], f"base image is not pinned by digest: {from_lines[0]}"


def test_the_base_image_is_python_314():
    # The project declares `requires-python = ">=3.14"`; an image below that runs a
    # different language from the one the project says it needs.
    from_line = next(line for line in read("Dockerfile").splitlines() if line.startswith("FROM "))
    assert "python:3.14" in from_line, from_line
    assert pyproject()["project"]["requires-python"] == ">=3.14"


def test_every_tool_version_is_pinned_exactly():
    # ⛔ `>=` here would make the image's contents depend on the day it was
    # built. Transitive dependencies included: a pin that stops at the direct
    # ones is not a pin.
    for line in read("requirements.txt").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        assert "==" in stripped, f"unpinned requirement: {stripped!r}"
        assert not stripped.startswith("-"), f"pip option in a pin file: {stripped!r}"


def test_the_image_carries_everything_the_declared_extras_name():
    # ⭐ This is the join that stops the declaration and the image drifting.
    # `pyproject.toml` says what the tests need; `requirements.txt` says what
    # the image has. A tool added to one and not the other is a suite that
    # passes in one place and errors in the other — which is the exact failure
    # R15 exists to prevent.
    extras = pyproject()["project"]["optional-dependencies"]
    declared = {
        requirement.split(">")[0].split("=")[0].split("<")[0].strip().lower()
        for group in ("test", "lint")
        for requirement in extras[group]
    }
    missing = declared - requirement_names()
    assert not missing, f"declared in pyproject but not pinned in the image: {sorted(missing)}"


def test_ruff_is_in_the_image_because_that_is_what_unblocks_fnd_01():
    # ⭐ The package skeleton's lint clause was once blocked on this image: no linter
    # was installed and no network install could be assumed. This line is where
    # that closes. If ruff ever leaves this file, the clause silently reopens
    # and two tests go back to skipping — which looks green.
    assert "ruff" in requirement_names()


# --- the properties that make it a build environment -----------------------


def test_the_run_has_no_network():
    # ⛔ R15, enforced rather than asserted in prose: no
    # network access is required to run tests. `none` means no interface at
    # all, so a test that quietly reached for a package index fails here
    # rather than passing on whichever machine had one.
    assert 'network_mode: "none"' in read("compose.yaml")


def test_the_network_is_needed_only_at_build_time():
    # ⚠️ The tension worth stating: `pip install` DOES need the network, and
    # gets it, because a build and a test run are different moments. The
    # install must therefore be in the Dockerfile and nowhere else.
    assert "pip install" in instructions("Dockerfile")
    for name in ("compose.yaml", "check"):
        assert "pip install" not in instructions(name), (
            f"{name} installs at run time; the run has no network"
        )


def test_no_docker_socket_is_mounted_anywhere():
    # ⛔ Spec §8.3, the one non-negotiable: the Docker socket is never mounted
    # into a serving process. Not behind a flag, not "only locally". This is a
    # build image and it should never arise — which is exactly why the check
    # is cheap and permanent. The extraction source's own compose file states
    # the same rule for the same reason.
    for name in ("Dockerfile", "compose.yaml", "check"):
        text = instructions(name)
        assert "docker.sock" not in text, f"{name} mounts the Docker socket (§8.3)"
        assert "/var/run/docker" not in text, f"{name} reaches for the Docker socket (§8.3)"


def test_the_source_is_mounted_not_copied():
    # ⛔ "From a clean checkout" means the checkout on disk, not a snapshot
    # baked into a layer at some earlier commit. A copied source goes stale
    # silently, and the container then reports on code the contributor is not
    # editing.
    copies = [line for line in instructions("Dockerfile").splitlines() if line.startswith("COPY ")]
    assert copies == ["COPY requirements.txt /opt/studyforge/requirements.txt"], copies
    assert "../..:/workspace" in instructions("compose.yaml")


def test_the_container_never_runs_as_root():
    # ⛔ Root plus a bind mount leaves a contributor with files in their own
    # checkout that they cannot delete.
    compose = instructions("compose.yaml")
    assert "user:" in compose
    assert "${STUDYFORGE_UID" in compose, "the uid must be supplied at run time, not written down"


def test_no_path_from_anybody_s_machine_is_written_down():
    # R7. A bind mount is written relative or parameterised, never with a
    # literal home path baked in. ⚠️ `HOME=/tmp` is deliberate and generic —
    # the container runs as a numeric uid with no /etc/passwd entry, so tools
    # that want a home need one that belongs to nobody.
    for name in ("Dockerfile", "compose.yaml", "check", "requirements.txt"):
        text = read(name)  # the raw text: a home path in a comment is still a leak
        for shape in ("/home/", "/Users/", "/root/"):
            assert shape not in text, f"{name} names a home directory: {shape}"


# --- the bytecode cache, which the mount turns into a READ problem ---
#
# ⛔ Why these four tests are not one: the image sets
# `PYTHONDONTWRITEBYTECODE=1` and therefore **cannot create** the taint — but
# the checkout is bind-mounted, so a container run **read** a stale `.pyc` a
# HOST run had left behind. ⚠️ Running in the container is necessary and
# **not sufficient**.
#
# ⭐ Which side runs which, and why. The first three need no daemon and no
# network and run **on both sides**: two of them are the redirect proved in
# both directions against a real interpreter, which is a fact about CPython
# and is therefore as true on a host as in the image. The fourth asks the
# **running** interpreter and can only be answered inside the image, so it
# skips on a host — ⛔ named, and on the host side, so it is not a sixth
# container skip hiding behind the five recursion guards above.

#: A module the probe imports. The name is deliberately unlike anything on
#: `sys.path`, so an import that resolves is resolving what the test planted.
PROBE_MODULE = "sf_pycache_probe"

#: What the probe prints: the value it got, and where it got it from. ⛔ Both,
#: because the value alone cannot distinguish "read the source" from "read a
#: cache that happens to agree".
PROBE = f"import {PROBE_MODULE} as m; print(m.VALUE, m.__cached__)"

#: The two revisions. ⛔ **The same length, deliberately.** CPython validates a
#: cached module against the source's `(mtime, size)`, so a mutant of a
#: different size invalidates the cache — and the scenario would stop being a
#: stale-cache scenario while still looking like one.
CACHED_REVISION = 'VALUE = "old"\n'
SOURCE_REVISION = 'VALUE = "new"\n'


def plant_stale_bytecode(tmp_path: Path) -> Path:
    """Write a module whose `__pycache__` is one revision behind it.

    Returns the path of the planted `.pyc`, which is inside the tree beside
    the source — exactly where a host run leaves one in the bind-mounted
    checkout.

    ⚠️ The cache path is spelled out rather than taken from
    `importlib.util.cache_from_source`, because that function honours
    `sys.pycache_prefix` — inside the image it would hand back the redirected
    path, and the test would plant its evidence somewhere the scenario does
    not need it.
    """
    source = tmp_path / f"{PROBE_MODULE}.py"
    source.write_text(CACHED_REVISION, encoding="utf-8")
    cache = tmp_path / "__pycache__" / f"{PROBE_MODULE}.{sys.implementation.cache_tag}.pyc"
    cache.parent.mkdir(exist_ok=True)
    py_compile.compile(str(source), cfile=str(cache), doraise=True)

    before = source.stat()
    source.write_text(SOURCE_REVISION, encoding="utf-8")
    os.utime(source, (before.st_atime, before.st_mtime))
    after = source.stat()
    assert (after.st_size, after.st_mtime) == (before.st_size, before.st_mtime), (
        "the mutant changed the source's size or mtime, so the cache is no longer stale"
    )
    assert cache.is_file(), cache
    return cache


def test_the_bytecode_cache_is_redirected_out_of_the_workspace():
    # ⛔ The line itself, read from the image's declaration. On its own this
    # asserts only that a variable is set, which is why the two tests below
    # exist — but the value has to be checked somewhere, and "outside the
    # mount" is the whole of the requirement.
    dockerfile = instructions("Dockerfile")
    assert "PYTHONPYCACHEPREFIX=" in dockerfile, (
        "the image does not redirect the bytecode cache; a stale `.pyc` from a "
        "host run is read out of the bind mount"
    )
    value = dockerfile.split("PYTHONPYCACHEPREFIX=")[1].split()[0].rstrip("\\").strip()
    assert value.startswith("/"), f"the cache prefix is not an absolute path: {value!r}"
    assert not value.startswith("/workspace"), (
        f"the cache prefix is inside the bind-mounted checkout: {value!r}"
    )
    # ⚠️ The write side stays too. The redirect closes the read; only this
    # closes "a `__pycache__` owned by the container's uid in somebody's tree".
    assert "PYTHONDONTWRITEBYTECODE=1" in dockerfile


def test_a_stale_bytecode_file_in_the_tree_is_ignored_when_the_prefix_redirects(tmp_path):
    # ⭐ Direction one: **with** the redirect, the planted `.pyc` is not read.
    # The prefix goes somewhere `tmp_path` does not contain, which is what the
    # image's `/tmp/pycache` is to `/workspace`.
    cache = plant_stale_bytecode(tmp_path)
    redirect = tmp_path.parent / "redirected-cache"
    result = run(
        [
            "env",
            "PYTHONDONTWRITEBYTECODE=1",
            f"PYTHONPYCACHEPREFIX={redirect}",
            "python3",
            "-c",
            PROBE,
        ],
        cwd=tmp_path,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    value, cached = result.stdout.split()
    assert value == "new", f"a stale `.pyc` was read in preference to the source: {result.stdout}"
    assert Path(cached).is_relative_to(redirect), cached
    assert cache.is_file(), "the planted `.pyc` vanished; the scenario did not happen"


def test_without_the_prefix_that_same_stale_bytecode_is_read(tmp_path):
    # ⛔ Direction two, and the reason this is a test rather than a comment:
    # this is the defect, reproduced. `PYTHONDONTWRITEBYTECODE=1` is set here
    # exactly as the image sets it, and it changes nothing — the interpreter
    # loads a module whose source says something else.
    #
    # ⚠️ `env -u` is the image's own line removed and nothing else. Inside the
    # image that is a real removal; on a host it is a no-op, and the test
    # asserts the same thing on both sides either way.
    cache = plant_stale_bytecode(tmp_path)
    result = run(
        ["env", "-u", "PYTHONPYCACHEPREFIX", "PYTHONDONTWRITEBYTECODE=1", "python3", "-c", PROBE],
        cwd=tmp_path,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    value, cached = result.stdout.split()
    assert value == "old", (
        "the stale `.pyc` was NOT read without the redirect, so the test above "
        f"proves nothing: {result.stdout}"
    )
    assert Path(cached) == cache, cached


def test_no_bytecode_from_the_bind_mount_is_read_in_here():
    # ⭐ **The acceptance, asserted from inside**, in the same shape as the
    # runtime check below: every test above reads a file or a temporary tree;
    # this one asks the interpreter that is running the suite.
    if not os.environ.get(MARKER):
        pytest.skip(
            "not inside the dev image, where the cache prefix is set. The "
            "checks above assert the Dockerfile sets one and that the redirect "
            "works in both directions; only a run inside the image can assert "
            "that this interpreter read no `.pyc` out of the bind mount."
        )
    assert sys.pycache_prefix, (
        "no cache prefix in the running interpreter: the ENV line is declared "
        "but is not reaching Python"
    )
    root = repository_root()
    assert not Path(sys.pycache_prefix).is_relative_to(root), sys.pycache_prefix
    from_the_mount = sorted(
        module.__cached__
        for module in list(sys.modules.values())
        if isinstance(getattr(module, "__cached__", None), str)
        and Path(module.__cached__).is_relative_to(root)
    )
    assert not from_the_mount, (
        "modules were loaded from bytecode inside the bind-mounted checkout, "
        f"which a host run wrote and this container did not: {from_the_mount}"
    )


# --- the JavaScript runtime --------------------------------


def test_a_javascript_runtime_is_installed_and_pinned_by_version():
    # ⛔ The version says what it is for a reader; the checksum below is what
    # makes the build reproducible — the same two-part pin the `FROM` line
    # uses, for the same reason.
    dockerfile = instructions("Dockerfile")
    assert "ARG NODE_VERSION=" in dockerfile, "no JavaScript runtime version is pinned"
    version = dockerfile.split("ARG NODE_VERSION=")[1].split()[0]
    assert version[0].isdigit(), f"NODE_VERSION is not a version: {version!r}"
    assert "nodejs.org/dist/v${NODE_VERSION}/" in dockerfile, "the pin is not what is fetched"


def test_the_runtime_is_verified_against_a_recorded_checksum():
    # ⛔ **The half that makes the pin real.** A version in a URL says which
    # bytes were asked for; only a checksum says which bytes arrived.
    dockerfile = instructions("Dockerfile")
    assert "sha256sum --check --strict" in dockerfile, "the download is not verified"
    recorded = [line for line in dockerfile.splitlines() if line.startswith("ARG NODE_SHA256_")]
    assert recorded, "no checksum is recorded"
    for line in recorded:
        digest = line.split("=", 1)[1].strip()
        assert len(digest) == 64 and all(c in "0123456789abcdef" for c in digest), line


def test_an_architecture_with_no_recorded_checksum_fails_loudly():
    # ⛔ **Reaching for an unverified fallback is the failure this whole task
    # closes, one layer down.** An arch nobody pinned must stop the build and
    # say so, never quietly install whatever is available — and the message
    # has to tell the reader what to do, because the person who meets it is on
    # hardware this repository has never built on.
    dockerfile = instructions("Dockerfile")
    assert "TARGETARCH" in dockerfile, "the runtime is pinned to one architecture by accident"
    assert "no pinned Node.js recorded for TARGETARCH" in read("Dockerfile")
    assert "exit 1" in dockerfile, "an unrecorded architecture does not fail the build"


def test_the_runtime_arrives_pinned_rather_than_from_a_package_manager():
    # ⚠️ `apt-get install nodejs` reintroduces exactly the problem this closes:
    # the tests would run, and what they ran against would depend on the day
    # the image was built and on the distribution's snapshot.
    #
    # ⛔ Asserted against the **install lines**, not the whole file. The first
    # version of this check matched the substring `nodejs` anywhere and failed
    # on `nodejs.org` in the download URL — a check that fires on the correct
    # implementation, which is a check somebody deletes.
    #
    # ⛔ **AND IT SHIPPED VACUOUS FOR THE OPPOSITE REASON**, confirmed by plant.
    # The raw-line version asserted over the
    # LINE carrying `apt-get install`, and every package this Dockerfile installs
    # sits on a CONTINUATION below it — so a planted bare `nodejs` in the
    # browser block's package list passed, green. ⭐ `commands()` collapses the
    # continuations and then cuts at the shell separators, which is what keeps
    # `nodejs.org` in a different command from the install.
    installed = [
        command
        for command in commands("Dockerfile")
        if "apt-get install" in command or "apt install" in command
    ]
    assert installed, "nothing is installed at all; has the base image changed?"
    for command in installed:
        for unpinned in ("nodejs", "npm", "nvm"):
            assert unpinned not in command, (
                f"the runtime is installed unpinned: {command.strip()!r}"
            )
    for anywhere in ("nvm install", "corepack enable"):
        assert anywhere not in instructions("Dockerfile"), anywhere


def test_no_javascript_package_manager_survives_into_the_image():
    # ⛔ The same rule the git install states: an image that quietly grows a
    # package manager is an image whose results stop being attributable to
    # what it declares. ⭐ And it is the stronger guarantee — with no `npm`,
    # `network_mode: none` is not the only thing standing between this suite
    # and an unpinned tree of packages. The grammars are vendored in `src/`.
    dockerfile = instructions("Dockerfile")
    for tool in ("/usr/local/bin/npm", "/usr/local/bin/npx", "/usr/local/bin/corepack"):
        assert tool in dockerfile, f"{tool} is not removed from the image"


def test_the_runtime_is_actually_on_the_path_in_here():
    # ⭐ **The acceptance, asserted from inside.** Every static check above
    # reads a file; this one asks the environment. ⛔ It is the difference
    # between "the Dockerfile says it installs a runtime" and "the runtime is
    # here", and tests that need the runtime skip on precisely that gap.
    if not os.environ.get(MARKER):
        pytest.skip(
            "not inside the dev image, where the runtime is pinned. The static "
            "checks above assert the Dockerfile installs one; only a run inside "
            "the image can assert it arrived."
        )
    assert shutil.which("node"), (
        "no JavaScript runtime on PATH inside the dev image. The pinned "
        "environment is the one that certifies a result, so this is a failure "
        "here even though it is a skip on a host."
    )


# --- the formatter excludes nothing ----------------------------------------


def test_the_formatter_excludes_nothing():
    # ⛔ The exclusion list is **empty rather than short**: a file too long to
    # format is split along its seams (R11), never excluded. An empty
    # list cannot become the place difficult files go.
    assert "exclude" not in pyproject()["tool"]["ruff"]["format"]


# --- integration: it builds, and the suite passes inside it ----------------


@pytest.fixture(scope="session")
def dev_image() -> str:
    """Build the image once for the whole session through `check`, and return what it printed.

    ⛔ Not `docker compose build`: the image is named by an identity only `check` derives.
    """
    require_docker_run()
    result = run([f"./{DEV}/check", "true"], cwd=repository_root())
    assert result.returncode == 0, result.stdout + result.stderr
    return announced_image(result.stderr)


def test_the_image_builds(dev_image):
    docker = tool_on_path("docker")
    result = run([docker, "image", "inspect", dev_image], cwd=repository_root())
    assert result.returncode == 0, result.stdout + result.stderr


def test_the_image_runs_python_314(dev_image):
    docker = tool_on_path("docker")
    result = run(
        [
            docker,
            "run",
            "--rm",
            "--network",
            "none",
            dev_image,
            "python3",
            "-c",
            "import sys; print(sys.version_info[:2])",
        ],
        cwd=repository_root(),
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout.strip() == "(3, 14)", result.stdout


def test_the_suite_passes_inside_the_image_with_no_network(dev_image):
    # ⭐ The acceptance, executed. `--network none` is on the service, so this
    # is the suite proving it needs nothing from outside the image.
    require_docker_run()
    result = run([f"./{DEV}/check"], cwd=repository_root())
    assert result.returncode == 0, result.stdout + result.stderr
    assert "failed" not in result.stdout.splitlines()[-1], result.stdout


def test_the_suite_passes_for_a_uid_that_owns_nothing(dev_image):
    # ⚠️ `docker/dev/check` passes the invoking user's uid, so the everyday path
    # runs as the owner of the checkout. This runs Compose directly, which
    # falls back to `nobody` — a uid that owns none of the mounted files. It is
    # the case that found two real defects: git refused the tree as "dubious
    # ownership" and returned 128 instead of a verdict, and ruff tried to write
    # its cache into the bind mount. Both are fixed in the image, and this is
    # what stops them coming back.
    require_docker_run()
    # 65534 is `nobody`: it owns none of the mounted files. Passed through
    # `check` rather than raw Compose so that a linked worktree still gets its
    # git directory — this test is about the uid, not about the mount.
    result = run(
        ["env", "STUDYFORGE_UID=65534", "STUDYFORGE_GID=65534", f"./{DEV}/check"],
        cwd=repository_root(),
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_lint_actually_runs_in_there_rather_than_skipping(dev_image):
    # ⭐ The skeleton's blocked lint clause, closed and asserted. On the host these two
    # tests skip because ruff is not installed; in the image they must RUN.
    # ⛔ A skip that nobody notices is how a blocked clause stays blocked while
    # looking green.
    require_docker_run()
    # ⛔ Named node ids, not `-k ruff`: a keyword filter also catches the tests
    # in THIS module that have "ruff" in their names, and the count it then
    # asserts on stops meaning what it says.
    lint = "tests/test_repository.py::test_ruff_lint_is_clean_where_ruff_exists"
    fmt = "tests/test_repository.py::test_ruff_format_is_clean_where_ruff_exists"
    result = run(
        [f"./{DEV}/check", "python3", "-m", "pytest", "-rs", "-q", lint, fmt],
        cwd=repository_root(),
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "2 passed" in result.stdout, result.stdout
    assert "skipped" not in result.stdout, "ruff is missing from the image: " + result.stdout
