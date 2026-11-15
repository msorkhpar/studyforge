r"""The live runner and its egress proxy: the `live` profile of the compose file.

**What it does.** Renders the two services a corpus that declares live runs adds beside the
study server: the live runner (the runner's image, hardened, with no route out but the proxy)
and the egress proxy (the site's image, allowing exactly one host on port 443).

**How you use it.** `siteservice.plan` and `standalone.live` call `live_runner(...)` with the
site's internal network and `egress_proxy(...)`, and add `LIVE_NET` and `LIVE_OUT` to the
networks; `files` writes `LIVE_SCRIPT_FILE` and `EGRESS_SCRIPT_FILE` beside the compose file.

**Depends on.** `contract.require` for the editor's restart policy. ⛔ No I/O and nothing
source-specific (R1). A corpus that declares no live run never reaches this module.
"""

from __future__ import annotations

from collections.abc import Mapping

from studyforge.skills.execution.contract import require

#: The live runner and its egress proxy: services of the `live` profile, only for a corpus that
#: declares live runs. ⭐ `LIVE_NET` is internal (the live runner has no route but the proxy) and
#: only the proxy also joins `LIVE_OUT`, which has one.
LIVE = "live"
EGRESS = "egress"
LIVE_NET = "live-net"
LIVE_OUT = "live-out"
LIVE_SCRIPT_FILE = "liverun.pl"
EGRESS_SCRIPT_FILE = "egress.py"
LIVE_SCRIPT_INSIDE = "/opt/studyforge/liverun.pl"
EGRESS_SCRIPT_INSIDE = "/opt/studyforge/egress.py"

#: What a live run may use: the proxy's address inside `LIVE_NET`, and the limits of one run.
PROXY = f"http://{EGRESS}:3128"
LIVE_LIMITS = {"mem_limit": "1g", "pids_limit": 256, "cpus": 1.0}


def hardened() -> dict[str, object]:
    """Return what both live services carry: a read-only root, no capabilities, no privileges."""
    return {
        "read_only": True,
        "cap_drop": ["ALL"],
        "security_opt": ["no-new-privileges:true"],
        "ulimits": {"core": 0},
    }


def live_runner(
    runner: Mapping[str, object],
    variable: str,
    owner: str,
    block: Mapping[str, object],
    network: str,
) -> dict[str, object]:
    """Return the live runner: the runner's image, hardened, with no way out but the proxy.

    ⛔ It is NOT the graded runner: a service of its own, on `network` (the site reaches it) and
    `LIVE_NET` (the proxy), with its own script, the corpus mounted READ-ONLY, a size-capped scratch
    tmpfs, limits, and an environment holding the proxy and the key variable's NAME, never a value.
    """
    mounts = [
        f"{one}" if str(one).endswith(":ro") else f"{one}:ro"
        for one in runner.get("volumes", [])  # type: ignore[attr-defined]
    ]
    return {
        "image": runner["image"],
        owner: runner[owner],
        "profiles": [LIVE],
        "command": ["perl", LIVE_SCRIPT_INSIDE],
        "volumes": [*mounts, f"./{LIVE_SCRIPT_FILE}:{LIVE_SCRIPT_INSIDE}:ro"],
        "environment": {
            "HTTPS_PROXY": PROXY,
            "https_proxy": PROXY,
            "HOME": "/scratch",
            "STUDYFORGE_LIVE_KEY_NAME": variable,
        },
        "tmpfs": ["/scratch:size=256m,mode=1777", "/tmp:size=64m,mode=1777"],
        **hardened(),
        **LIVE_LIMITS,
        "networks": [network, LIVE_NET],
        "restart": require(block, "restart"),
    }


def egress_proxy(
    site: Mapping[str, object], host: str, owner: str, block: Mapping[str, object]
) -> dict[str, object]:
    """Return the egress proxy: the site's own image, allowing exactly one host on port 443."""
    return {
        "image": site["image"],
        owner: site[owner],
        "profiles": [LIVE],
        "command": ["python3", EGRESS_SCRIPT_INSIDE],
        "volumes": [f"./{EGRESS_SCRIPT_FILE}:{EGRESS_SCRIPT_INSIDE}:ro"],
        "environment": {"EGRESS_ALLOW_HOST": host},
        **hardened(),
        "networks": [LIVE_NET, LIVE_OUT],
        "restart": require(block, "restart"),
    }
