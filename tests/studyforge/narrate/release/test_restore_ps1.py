"""The generated `restore.ps1`, parsed and run by a pinned PowerShell.

⭐ **A HOST reading, opt-in behind `STUDYFORGE_PWSH_READING=1`**, because it
starts a container: `PWSH_IMAGE`, pinned by digest and never pulled here
(`--pull never`; pull it once by that digest). The container runs as the
invoking user, with no identity passed in, and is removed when it exits.

- ⭐ the script parses with no error under PowerShell's own parser;
- ⭐ volumes on disk restore every clip byte for byte and are left in place;
- ⭐ a public and a private release served by `stand_in.StandIn` restore every
  clip, the private one by asset id with the token as a header. ⭐ The stand-in
  runs in a container of its own (`STAND_IN_IMAGE`, pinned, never pulled here)
  on an INTERNAL user network the restore's container joins, and is reached by
  name: on Docker Desktop the host network is the engine VM's, so a stand-in on
  the host's loopback is out of reach, and an internal network has no route out;
- ⛔ a corrupt volume is refused and nothing is extracted;
- ⛔ a volume whose members are not the committed clips, another corpus's release,
  and clips whose bytes are not the committed ones are each refused, with the
  corpus byte-identical and no clip signal written.

Plants: `test_restore.plant_a_corrupt_volume`.
"""

from __future__ import annotations

import contextlib
import os
import shutil
import subprocess
import time
import uuid
from pathlib import Path

import pytest

from studyforge.narrate.release import RESTORE_PS1
from studyforge.skills.execution.siteimage import BASE
from tests.harness import engine
from tests.studyforge.narrate.release import stand_in
from tests.studyforge.narrate.release.restoring import (
    DEAD_PROXY,
    files_of,
    forge_release,
    prepared,
    restored,
    signal,
)
from tests.studyforge.narrate.release.stand_in import OWNER_REPO, TAG, TOKEN
from tests.studyforge.narrate.release.test_restore import plant_a_corrupt_volume
from tests.support import tool_on_path

#: The switch that lets this module start a container.
CONSENT = "STUDYFORGE_PWSH_READING"

#: The PowerShell image, pinned by the digest of its index.
PWSH_IMAGE = (
    "mcr.microsoft.com/powershell"
    "@sha256:810c4f1e0c9d23022c3ec18c50a6205ee4b60766f1739d329b2948df1fd7d5b0"
)

#: Where the test's directory is mounted inside the container.
WORK = "/work"

#: The stand-in's image: the site image's own pinned base, standard library only.
STAND_IN_IMAGE = BASE

#: The stand-in's name on the network, and the port it listens on there.
STAND_IN_NAME = "stand-in"
STAND_IN_PORT = 8080


@pytest.fixture
def tmp_path():
    """⭐ Engine-visible, never the host's temporary directory (`tests.harness.engine`).

    A container in this module binds the test's directory, and Docker Desktop shares
    no host `/tmp` while Windows has none.
    """
    with engine.shared("restore-ps1") as where:
        yield where


@pytest.fixture(autouse=True)
def consented():
    """Skip unless the host reading was asked for and can run."""
    if os.environ.get(CONSENT) != "1":
        pytest.skip(f"set {CONSENT}=1 to let this module run the pinned PowerShell image")
    if tool_on_path("docker") is None:
        pytest.skip("no docker CLI in this environment (the pinned dev image carries none)")
    present = subprocess.run(
        ["docker", "image", "inspect", PWSH_IMAGE], capture_output=True, text=True
    )
    if present.returncode != 0:
        pytest.skip("the pinned PowerShell image is not on this host; pull it by its digest")


def pwsh(tmp_path: Path, command: list[str], env: dict[str, str], network: str = "none"):
    """Run `pwsh` in the pinned image over `tmp_path`, as this user, and remove the container."""
    argv = [
        "docker", "run", "--rm", "--pull", "never", "--network", network,
        *engine.run_as(),
        "-e", "HOME=/tmp",
        "-v", f"{engine.bindable(tmp_path)}:{WORK}",
    ]  # fmt: skip
    if network != "none":
        # ⛔ A request that escaped the stand-in fails at a dead proxy instead of leaving.
        proxy = {"HTTPS_PROXY": DEAD_PROXY, "HTTP_PROXY": DEAD_PROXY, "NO_PROXY": STAND_IN_NAME}
        env = {**proxy, **env}
    for name, value in env.items():
        argv += ["-e", f"{name}={value}"]
    return subprocess.run(
        [*argv, PWSH_IMAGE, "pwsh", "-NoProfile", "-NonInteractive", *command],
        capture_output=True,
        text=True,
        timeout=300,
    )


class Contained:
    """A stand-in running in its own container: where it answers, and what it was asked."""

    def __init__(self, log: Path) -> None:
        self.log = log
        self.api = f"http://{STAND_IN_NAME}:{STAND_IN_PORT}"

    def base_url(self, tag: str = TAG) -> str:
        return f"{self.api}/{OWNER_REPO}/releases/download/{tag}"

    @property
    def requests(self) -> list[tuple[str, str, dict[str, str]]]:
        return stand_in.logged(self.log)


@contextlib.contextmanager
def contained(tmp_path: Path, release: Path, *, private: bool):
    """The stand-in in its own container on a fresh internal network; yield `(network, it)`.

    ⛔ Both are removed whatever happens.
    """
    present = subprocess.run(["docker", "image", "inspect", STAND_IN_IMAGE], capture_output=True)
    if present.returncode != 0:
        pytest.skip("the stand-in's pinned Python image is not on this engine; pull it by digest")
    where = tmp_path / "stand-in"
    where.mkdir()
    shutil.copy(stand_in.__file__, where / "stand_in.py")
    suffix = uuid.uuid4().hex[:12]
    network, name = f"restore-ps1-{suffix}", f"restore-ps1-stand-in-{suffix}"
    inside = f"{WORK}/{where.relative_to(tmp_path).as_posix()}"
    served = f"{WORK}/{release.relative_to(tmp_path).as_posix()}"
    created = ["docker", "network", "create", "--internal", network]
    subprocess.run(created, capture_output=True, check=True)
    try:
        started = subprocess.run(
            [
                "docker", "run", "--detach", "--rm", "--pull", "never",
                "--name", name, "--network", network, "--network-alias", STAND_IN_NAME,
                *engine.run_as(),
                "-v", f"{engine.bindable(tmp_path)}:{WORK}",
                STAND_IN_IMAGE, "python3", f"{inside}/stand_in.py", served,
                "--port", str(STAND_IN_PORT),
                "--log", f"{inside}/requests.jsonl", "--ready", f"{inside}/ready",
                *(["--private"] if private else []),
            ],
            capture_output=True,
            text=True,
        )  # fmt: skip
        assert started.returncode == 0, started.stderr
        deadline = time.monotonic() + 30
        while not (where / "ready").exists():
            assert time.monotonic() < deadline, "the contained stand-in never listened"
            time.sleep(0.1)
        yield network, Contained(where / "requests.jsonl")
    finally:
        subprocess.run(["docker", "rm", "--force", name], capture_output=True)
        subprocess.run(["docker", "network", "rm", network], capture_output=True)


def script(tmp_path: Path, corpus) -> str:
    """The corpus's `restore.ps1` as the container sees it."""
    return f"{WORK}/{corpus.root.relative_to(tmp_path).as_posix()}/{RESTORE_PS1}"


def test_the_script_parses_with_no_error(tmp_path):
    corpus = prepared(tmp_path)
    parse = (
        "$errors = $null; "
        "[System.Management.Automation.Language.Parser]::ParseFile("
        f"'{script(tmp_path, corpus)}', [ref]$null, [ref]$errors) | Out-Null; "
        "$errors | ForEach-Object { $_.Message }; exit $errors.Count"
    )
    done = pwsh(tmp_path, ["-Command", parse], {})
    assert done.returncode == 0, done.stdout + done.stderr


def test_volumes_on_disk_restore_every_clip_and_are_left_in_place(tmp_path):
    corpus = prepared(tmp_path)
    before = sorted(path.name for path in corpus.release.iterdir())

    done = pwsh(
        tmp_path,
        ["-File", script(tmp_path, corpus), "-LocalDir", f"{WORK}/release"],
        {},
    )

    assert done.returncode == 0, done.stdout + done.stderr
    assert restored(corpus) == corpus.clips
    assert sorted(path.name for path in corpus.release.iterdir()) == before
    assert signal(corpus) is None


@pytest.mark.parametrize("private", [False, True], ids=["public", "private"])
def test_a_release_restores_every_clip_and_leaves_no_download(tmp_path, private):
    corpus = prepared(tmp_path)

    with contained(tmp_path, corpus.release, private=private) as (network, host):
        env = (
            {"NARRATION_REPO": OWNER_REPO, "NARRATION_API_URL": host.api, "GITHUB_TOKEN": TOKEN}
            if private
            else {"NARRATION_BASE_URL": host.base_url()}
        )
        done = pwsh(tmp_path, ["-File", script(tmp_path, corpus)], env, network=network)

    assert done.returncode == 0, done.stdout + done.stderr
    assert restored(corpus) == corpus.clips
    assert TOKEN not in done.stdout + done.stderr
    assert not (corpus.root / ".studyforge/narration-release/download").exists()
    assert signal(corpus) is None
    if private:
        assert all(TOKEN not in path for _, path, _ in host.requests)
        assert any("/releases/assets/" in path for _, path, _ in host.requests)


def test_a_corrupt_volume_is_refused_and_nothing_is_extracted(tmp_path):
    corpus = prepared(tmp_path)
    plant_a_corrupt_volume(corpus.release)

    done = pwsh(
        tmp_path,
        ["-File", script(tmp_path, corpus), "-LocalDir", f"{WORK}/release"],
        {},
    )

    assert done.returncode != 0
    assert "checksum mismatch on narration.zip.001" in done.stdout + done.stderr
    assert set(restored(corpus).values()) == {None}
    assert signal(corpus) is None


def local(tmp_path: Path, corpus):
    """Run the corpus's `restore.ps1` over the release directory on disk."""
    return pwsh(tmp_path, ["-File", script(tmp_path, corpus), "-LocalDir", f"{WORK}/release"], {})


def test_a_volume_carrying_the_manifest_and_an_escape_is_refused_and_the_corpus_is_untouched(
    tmp_path,
):
    corpus = prepared(tmp_path)
    forge_release(corpus, {"corpus.json": b"{}", "../ESCAPED.txt": b"out"}, committed=True)
    before = files_of(corpus.root)

    done = local(tmp_path, corpus)

    assert done.returncode != 0
    assert "not this corpus's clips" in done.stdout + done.stderr
    assert files_of(corpus.root) == before
    assert not (tmp_path / "ESCAPED.txt").exists()
    assert signal(corpus) is None


def test_another_corpus_release_with_its_own_matching_sums_is_refused_at_the_volumes(tmp_path):
    corpus = prepared(tmp_path, part_bytes=10_000_000)
    forge_release(corpus, {path: b"another corpus" for path in corpus.clips}, committed=False)
    before = files_of(corpus.root)

    done = local(tmp_path, corpus)

    assert done.returncode != 0
    assert "checksum mismatch on narration.zip.000" in done.stdout + done.stderr
    assert files_of(corpus.root) == before
    assert signal(corpus) is None


def test_clips_whose_bytes_are_not_the_committed_ones_are_refused_before_any_is_placed(tmp_path):
    corpus = prepared(tmp_path)
    forge_release(corpus, {path: b"another corpus" for path in corpus.clips}, committed=True)
    before = files_of(corpus.root)

    done = local(tmp_path, corpus)

    assert done.returncode != 0
    assert "is not the clip this corpus packed" in done.stdout + done.stderr
    assert files_of(corpus.root) == before
    assert signal(corpus) is None
