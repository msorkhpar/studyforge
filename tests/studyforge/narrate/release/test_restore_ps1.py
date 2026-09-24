"""The generated `restore.ps1`, parsed and run by a pinned PowerShell.

⭐ **A HOST reading, opt-in behind `STUDYFORGE_PWSH_READING=1`**, because it
starts a container: `PWSH_IMAGE`, pinned by digest and never pulled here
(`--pull never`; pull it once by that digest). The container runs as the
invoking user, with no identity passed in, and is removed when it exits.

- ⭐ the script parses with no error under PowerShell's own parser;
- ⭐ volumes on disk restore every clip byte for byte and are left in place;
- ⭐ a public and a private release served by `stand_in.StandIn` on loopback
  restore every clip, the private one by asset id with the token as a header;
- ⛔ a corrupt volume is refused and nothing is extracted.

Plants: `test_restore.plant_a_corrupt_volume`.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

from studyforge.narrate.release import RESTORE_PS1
from tests.studyforge.narrate.release.restoring import DEAD_PROXY, prepared, restored
from tests.studyforge.narrate.release.stand_in import OWNER_REPO, TOKEN, StandIn
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
        "--user", f"{os.getuid()}:{os.getgid()}",
        "-e", "HOME=/tmp",
        "-v", f"{tmp_path}:{WORK}",
    ]  # fmt: skip
    if network != "none":
        # ⛔ A request that escaped the stand-in fails at a dead proxy instead of leaving.
        env = {"HTTPS_PROXY": DEAD_PROXY, "HTTP_PROXY": DEAD_PROXY, "NO_PROXY": "127.0.0.1", **env}
    for name, value in env.items():
        argv += ["-e", f"{name}={value}"]
    return subprocess.run(
        [*argv, PWSH_IMAGE, "pwsh", "-NoProfile", "-NonInteractive", *command],
        capture_output=True,
        text=True,
        timeout=300,
    )


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


@pytest.mark.parametrize("private", [False, True], ids=["public", "private"])
def test_a_release_restores_every_clip_and_leaves_no_download(tmp_path, private):
    corpus = prepared(tmp_path)

    with StandIn(corpus.release, private=private) as host:
        env = (
            {"NARRATION_REPO": OWNER_REPO, "NARRATION_API_URL": host.api, "GITHUB_TOKEN": TOKEN}
            if private
            else {"NARRATION_BASE_URL": host.base_url()}
        )
        done = pwsh(tmp_path, ["-File", script(tmp_path, corpus)], env, network="host")

    assert done.returncode == 0, done.stdout + done.stderr
    assert restored(corpus) == corpus.clips
    assert TOKEN not in done.stdout + done.stderr
    assert not (corpus.root / ".studyforge/narration-release/download").exists()
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
