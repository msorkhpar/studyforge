"""`docker/dev/check.ps1`, the PowerShell twin of `check`, runs the same command.

⭐ A contributor on Windows has PowerShell and Docker Desktop and no POSIX shell,
so `check`, which is POSIX sh, is not their route. The twin must name the same
image, bound the same command the same way and hand compose the same run.

**Static — always run.** The twin carries each value `check` carries, read off
both texts, so one moving alone is a red.

**Readings — opt-in.**

- ⭐ `STUDYFORGE_DOCKER_TESTS=1` with `STUDYFORGE_PWSH_READING=1` (this directory
  calls no docker on a default run): both wrappers run over one scratch copy of the
  build inputs with a FAKE `docker` that logs its argv and answers the identity:
  `check` on this host, the twin under the pinned PowerShell image
  (`test_restore_ps1.PWSH_IMAGE`, never pulled here). ⛔ The two must hand docker
  the same arguments, the checkout's own spelling aside.
- ⭐ `STUDYFORGE_DOCKER_TESTS=1`: the twin's identity script and `check`'s, each
  run in the Dockerfile's pinned base over this checkout, print one identity.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

from tests.docker.devfiles import DEV, instructions, read
from tests.docker.devgate import OPT_IN, base_image
from tests.docker.test_dev_image_identity import hashed_inputs
from tests.harness import engine
from tests.studyforge.narrate.release.test_restore_ps1 import PWSH_IMAGE
from tests.support import repository_root, tool_on_path

TWIN = "check.ps1"

#: The PowerShell image's own `PATH`, which the fake `docker` is put in front of.
PWSH_PATH = ":".join(
    (
        "/usr/local/sbin",
        "/usr/local/bin",
        "/usr/sbin",
        "/usr/bin",
        "/sbin",
        "/bin",
        "/opt/microsoft/powershell/7",
    )
)

#: The identity script `check` runs in the pinned base, single-quoted on its line.
SH_IDENTITY = re.compile(r"sh -c '(set -eu; listing=.*?)' \\?$", re.MULTILINE)


def twin() -> str:
    return instructions(TWIN)


def identity_script(text: str) -> str:
    """The script the twin runs in the pinned base: its here-string's one line."""
    found = re.search(r"\$Identify = @'\n(.*?)\n'@", text, flags=re.DOTALL)
    assert found, "the twin carries no identity script"
    return found.group(1)


def test_the_twin_hashes_the_same_checkout_files_as_check():
    assert hashed_inputs(instructions("check")) == set(twin_inputs().split())


def twin_inputs() -> str:
    found = re.findall(r"^\$INPUTS = '([^']*)'$", twin(), flags=re.MULTILINE)
    assert len(found) == 1, "the twin names its inputs once"
    return found[0]


def test_the_twin_defaults_to_the_image_s_own_command():
    cmd = [line for line in instructions("Dockerfile").splitlines() if line.startswith("CMD ")]
    declared = json.loads(cmd[0][len("CMD ") :])
    found = re.findall(r"\$command = @\(([^)]*)\)", twin())
    defaults = [re.findall(r"'([^']*)'", one) for one in found]
    assert [one for one in defaults if one] == [declared]


def test_the_twin_bounds_the_run_inside_the_container_as_check_does():
    sh = re.search(r"STUDYFORGE_CHECK_TIMEOUT=\$\{STUDYFORGE_CHECK_TIMEOUT:-(\d+)\}", read("check"))
    ps = re.search(r"else \{ '(\d+)' \}", twin())
    assert sh and ps and sh.group(1) == ps.group(1)
    assert "timeout --kill-after=30s $timeout @command" in twin()
    assert "timeout --kill-after=30s" in read("check")


def test_the_twin_sets_the_attestation_variable_unconditionally():
    assert re.search(r"^\$env:BUILDX_NO_DEFAULT_ATTESTATIONS = '1'$", twin(), flags=re.MULTILINE)


def test_the_twin_derives_the_identity_offline_read_only_over_the_same_listing():
    text = twin()
    for part in ("--network none", '"$($Root):/inputs:ro"', "--workdir /inputs"):
        assert part in text
    script = identity_script(text)
    assert "find docker/dev -type f | LC_ALL=C sort" in script
    assert '"' not in script, "Windows PowerShell 5.1 strips a double quote from an argument"


def test_the_twin_announces_the_image_as_check_does():
    assert '"docker/dev/check: image studyforge/dev:inputs-$identity"' in twin()
    assert 'echo "docker/dev/check: image studyforge/dev:inputs-' in read("check")


def test_the_twin_names_no_host_path_and_no_posix_only_tool():
    text = twin()
    assert "/home/" not in text and "C:\\" not in text
    for posix in ("$(id", "`id ", "/dev/null", "exec docker"):
        assert posix not in text


# --- the readings ------------------------------------------------------------

#: A `docker` that logs each call's arguments, one per line and a lone `--end--`
#: after each call, and answers a `run` (the identity) with a fixed digest.
#: ⛔ Starts nothing, and needs only `sh`, which both hosts of the reading have.
FAKE = """#!/bin/sh
log=$(dirname "$0")/calls
for argument in "$@"; do printf '%s\\n' "$argument" >> "$log"; done
echo --end-- >> "$log"
[ "$1" = run ] && echo "0000000000000000000000000000000000000000000000000000000000000000  -"
exit 0
"""


def scratch_root(where: Path) -> Path:
    """A scratch checkout holding the build inputs alone, with no git directory."""
    root = where / "checkout"
    shutil.copytree(repository_root() / DEV, root / DEV)
    for name in twin_inputs().split():
        shutil.copy2(repository_root() / name, root / name)
    return root


def logged(log: Path, root: str) -> list[list[str]]:
    calls, call = [], []
    for line in log.read_text("utf-8").splitlines() if log.exists() else []:
        if line == "--end--":
            calls.append(call)
            call = []
        else:
            call.append(line.replace(root, "<root>"))
    return calls


def test_both_wrappers_hand_docker_the_same_run():
    if os.environ.get(OPT_IN) != "1" or os.environ.get("STUDYFORGE_PWSH_READING") != "1":
        pytest.skip(
            f"set {OPT_IN}=1 and STUDYFORGE_PWSH_READING=1 to run the twin in the pinned PowerShell"
        )
    if tool_on_path("docker") is None:
        pytest.skip("no docker CLI in this environment")
    if subprocess.run(["docker", "image", "inspect", PWSH_IMAGE], capture_output=True).returncode:
        pytest.skip("the pinned PowerShell image is not on this host; pull it by its digest")
    with engine.shared("check-ps1") as where:
        root = scratch_root(where)
        host_fake, pwsh_fake = where / "host-fake", where / "pwsh-fake"
        for fake in (host_fake, pwsh_fake):
            fake.mkdir()
            (fake / "docker").write_text(FAKE, encoding="utf-8")
            (fake / "docker").chmod(0o755)
        owner = {"STUDYFORGE_UID": "1000", "STUDYFORGE_GID": "1000"}
        env = {**os.environ, **owner, "PATH": f"{host_fake}{os.pathsep}{os.environ['PATH']}"}
        env.pop("STUDYFORGE_CHECK_TIMEOUT", None)
        sh = subprocess.run(
            [str(root / DEV / "check"), "python3", "-m", "tests.floor"],
            env=env,
            capture_output=True,
            text=True,
        )
        assert sh.returncode == 0, sh.stderr
        inside = "/work"
        ps = subprocess.run(
            [
                "docker", "run", "--rm", "--pull", "never", "--network", "none",
                *engine.run_as(), "-e", "HOME=/tmp",
                "-e", f"PATH={inside}/pwsh-fake:{PWSH_PATH}",
                *(part for key, value in owner.items() for part in ("-e", f"{key}={value}")),
                "-v", f"{engine.bindable(where)}:{inside}",
                PWSH_IMAGE, "pwsh", "-NoProfile", "-NonInteractive",
                "-File", f"{inside}/checkout/{DEV}/{TWIN}", "python3", "-m", "tests.floor",
            ],
            capture_output=True,
            text=True,
            timeout=300,
        )  # fmt: skip
        assert ps.returncode == 0, ps.stdout + ps.stderr
        assert "docker/dev/check: image studyforge/dev:inputs-" + "0" * 64 in ps.stderr
        from_sh = logged(host_fake / "calls", str(root))
        from_ps = logged(pwsh_fake / "calls", f"{inside}/checkout")
    # ⭐ The identity scripts differ by design (no double quote in the twin's); the
    # last reading below holds them to one identity, so here each is its slot.
    assert len(from_sh) == 2 and scripted(from_sh) == scripted(from_ps)


def scripted(calls: list[list[str]]) -> list[list[str]]:
    """`calls` with the script handed to `sh -c` in its slot."""
    return [
        [
            "<identity script>" if index and call[index - 1] == "-c" else argument
            for index, argument in enumerate(call)
        ]
        for call in calls
    ]


def test_the_twin_and_check_derive_one_identity_from_one_checkout():
    if os.environ.get(OPT_IN) != "1":
        pytest.skip(f"set {OPT_IN}=1 to run both identity scripts in the pinned base")
    if tool_on_path("docker") is None:
        pytest.skip("no docker CLI in this environment")
    base = base_image(read("Dockerfile"))
    assert base is not None
    if subprocess.run(["docker", "image", "inspect", base], capture_output=True).returncode:
        pytest.skip("the Dockerfile's pinned base is not on this engine; pull it by its digest")
    found = SH_IDENTITY.search(read("check"))
    assert found, "check's identity script is not where this reading looks"
    answers = set()
    for script in (found.group(1), identity_script(twin())):
        done = subprocess.run(
            [
                "docker", "run", "--rm", "--network", "none", *engine.run_as(),
                "--volume", f"{engine.bindable(repository_root())}:/inputs:ro",
                "--workdir", "/inputs", base, "sh", "-c", script, "identity",
                *twin_inputs().split(),
            ],
            capture_output=True,
            text=True,
        )  # fmt: skip
        assert done.returncode == 0, done.stderr
        answers.add(done.stdout.split()[0])
    assert len(answers) == 1, f"the two wrappers derive different identities: {answers}"
