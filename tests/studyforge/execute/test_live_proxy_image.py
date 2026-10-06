"""The egress proof, run: the allowed host is reached and every other destination is not.

⭐ The first exit test of the live path. Two stand-in servers (`allowed.test`, `denied.test`) sit on
an ordinary network; a client sits on an `--internal` network that holds only it and two copies of
the SHIPPED proxy (`assets/egress.py.txt`), which also join the ordinary one. Expected, and asserted
from the client's own output:

- every DIRECT connection from the client fails: the stand-in's name and address, and the internet;
- through the proxy, `allowed.test:443` returns the stand-in's body, and `denied.test:443`,
  `allowed.test:80` and `127.0.0.1:443` are each refused with `403`;
- the proxy as shipped (production guard) refuses even `allowed.test:443`, because the stand-in is
  on a private address; the first copy swaps only that guard (`live_proof/swapped.py`).

⚠️ Opt-in: `STUDYFORGE_PROOF_STAGE` names an empty directory the engine can bind (never under the
host's temporary directory). ⛔ A heavy job: run it through the heavy-job slot. Every container and
network it makes carries the label below and only those are removed.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import uuid
from pathlib import Path

import pytest

import studyforge.execute as execute
from tests.harness import engine

STAGE = os.environ.get("STUDYFORGE_PROOF_STAGE")
IMAGE = "python@sha256:cad9a2c871761c413caa6fdd6441c783451e740a48aaeba60ae62a8b53525ef6"
LABEL = "org.studyforge.proof=live-egress"
HERE = Path(__file__).parent / "live_proof"
SHIPPED = Path(execute.__file__).parent / "assets" / "egress.py.txt"

pytestmark = pytest.mark.skipif(not STAGE, reason="set STUDYFORGE_PROOF_STAGE")


def docker(*arguments: str, check: bool = True) -> str:
    done = subprocess.run(  # noqa: S603 - fixed argv, no shell
        ["docker", "--context", "desktop-linux", *arguments],
        capture_output=True,
        text=True,
        check=False,
        stdin=subprocess.DEVNULL,
    )
    if check and done.returncode:
        raise AssertionError(done.stderr)
    return done.stdout.strip()


def remove(names: list[str], networks: list[str]) -> None:
    for name in names:
        docker("rm", "-f", name, check=False)
    for network in networks:
        docker("network", "rm", network, check=False)


def ip_of(network: str) -> str:
    """A `docker inspect` template for a container's address on `network`."""
    return '{{(index .NetworkSettings.Networks "' + network + '").IPAddress}}'


def run(tag: str) -> dict[str, str]:
    """Bring the proof up under names carrying `tag`, read each proxy's client output, remove it."""
    stage = Path(STAGE) / uuid.uuid4().hex
    stage.mkdir(parents=True)
    for source in HERE.glob("*.py"):
        shutil.copy(source, stage / source.name)
    shutil.copy(SHIPPED, stage / "egress.py")
    internal, outer = f"e18-int-{tag}", f"e18-out-{tag}"
    names = [f"e18-{role}-{tag}" for role in ("allowed", "denied", "proxy-a", "proxy-b", "client")]
    safe = [
        "--label",
        LABEL,
        "--read-only",
        "--cap-drop",
        "ALL",
        "--security-opt",
        "no-new-privileges",
        "-v",
        f"{engine.bindable(stage)}:/p:ro",
    ]
    remove(names, [internal, outer])
    try:
        docker("network", "create", "--internal", "--label", LABEL, internal)
        docker("network", "create", "--label", LABEL, outer)
        for who, name in (("ALLOWED-STANDIN", names[0]), ("DENIED-STANDIN", names[1])):
            alias = "allowed.test" if who.startswith("ALLOWED") else "denied.test"
            docker(
                "run",
                "-d",
                "--name",
                name,
                "--network",
                outer,
                "--network-alias",
                alias,
                "-e",
                f"WHO={who}",
                *safe,
                IMAGE,
                "python",
                "/p/standin.py",
            )
        for name, script in ((names[2], "/p/swapped.py"), (names[3], "/p/egress.py")):
            docker(
                "run",
                "-d",
                "--name",
                name,
                "--network",
                outer,
                "-e",
                "EGRESS_ALLOW_HOST=allowed.test",
                *safe,
                IMAGE,
                "python",
                script,
            )
            docker("network", "connect", internal, name)
        address = docker("inspect", "-f", ip_of(outer), names[0])
        seen = {}
        for variant, name in (("swapped", names[2]), ("shipped", names[3])):
            proxy = docker("inspect", "-f", ip_of(internal), name)
            seen[variant] = docker(
                "run",
                "--rm",
                "--name",
                names[4],
                "--network",
                internal,
                "--label",
                LABEL,
                "--cap-drop",
                "ALL",
                *safe[2:],
                IMAGE,
                "python",
                "/p/client.py",
                proxy,
                address,
            )
        return seen
    finally:
        remove(names, [internal, outer])
        shutil.rmtree(stage, ignore_errors=True)


def line(output: str, label: str) -> str:
    found = re.search(rf"^{re.escape(label)}\s*->\s*(.*)$", output, re.M)
    assert found, output
    return found.group(1)


def test_the_allowed_host_is_reached_through_the_proxy_and_no_other_destination_is():
    tag = uuid.uuid4().hex[:8]
    seen = run(tag)
    for variant in ("swapped", "shipped"):
        out = seen[variant]
        for label in (
            "direct allowed.test:443",
            "direct stand-in ip:443",
            "direct 1.1.1.1:443 (internet)",
        ):
            assert "CONNECTED" not in line(out, label), (variant, label, out)
        assert "403" in line(out, "via proxy denied.test:443"), out
        assert "403" in line(out, "via proxy allowed.test:80"), out
        assert "403" in line(out, "via proxy 127.0.0.1:443"), out
    assert "200 Connection established" in line(seen["swapped"], "via proxy allowed.test:443")
    assert "ALLOWED-STANDIN" in line(seen["swapped"], "via proxy allowed.test:443")
    assert "DENIED-STANDIN" not in seen["swapped"]
    # ⛔ As shipped, the stand-in's private address is refused even for the allowed name.
    assert "403" in line(seen["shipped"], "via proxy allowed.test:443")
    leftover = docker("ps", "-a", "--filter", f"label={LABEL}", "--format", "{{.Names}}")
    nets = docker("network", "ls", "--filter", f"label={LABEL}", "--format", "{{.Name}}")
    assert leftover == "" and nets == ""
