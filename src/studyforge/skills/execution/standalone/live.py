"""The live runs of a thin export: the runner and the proxy, their network, their directories.

**What it does.** For a course that declares live runs, answers what its compose files add
(the live runner and the egress proxy in the compose profile `live`, and their two networks) and
which of the course's directories its runner image carries for the live runner to start in. A
course that declares none gets nothing from any of it.

**How you use it.**

    live.networks(plan.live)               # the file's networks
    live.services(plan, site, runner)      # {"live": ..., "egress": ...}
    live.started(run)                      # those two out of a render's services
    live.directories(manifest)             # ("examples",)

**Depends on.** `siteservice` for the two services the builder's own compose file writes,
which this reuses; the plan and the manifest are read, never imported (R3).

## ⛔ The scripts are read out of the images

⚠️ The builder's file binds the two scripts from the checkout; a learner's file binds no host
path. ⭐ The live runner's script is baked into the course's runner image, and the proxy's is in
the course's site image, whose entrypoint is the study server: the proxy replaces it. ⛔ The
site is told the live service's name, never a key.
"""

from __future__ import annotations

from collections.abc import Mapping

from studyforge.execute import published
from studyforge.skills.execution.contract import require
from studyforge.skills.execution.siteservice import (
    CORPUS,
    EGRESS,
    EGRESS_SCRIPT_FILE,
    LIVE,
    LIVE_NET,
    LIVE_OUT,
    NETWORK,
    egress_proxy,
    live_runner,
)

#: Where the execution skill's scripts sit in the course, and so in the site image.
EXECUTION_DIR = ".studyforge/execution"


def networks(live: tuple[str, str] | None) -> dict[str, dict[str, object]]:
    """Return the file's networks: the internal run network, and the live pair for a live course."""
    found: dict[str, dict[str, object]] = {NETWORK: {"internal": True}}
    if live is not None:
        found |= {LIVE_NET: {"internal": True}, LIVE_OUT: {}}
    return found


def started(run: Mapping[str, dict[str, object]]) -> dict[str, dict[str, object]]:
    """Return the live runner and the proxy, started from images the file already builds."""
    return {name: run[name] for name in (LIVE, EGRESS) if name in run}


def services(plan, site: dict[str, object], runner: dict[str, object]):
    """Return the live runner and the egress proxy of a course that declares live runs."""
    host, variable = plan.live
    owner = str(require(plan.editor, "runs_as", "compose_key"))
    told = dict(site["environment"])  # type: ignore[call-overload]
    site["environment"] = {**told, published.LIVE_SERVICE: LIVE}
    runs = live_runner(runner, variable, owner, plan.editor)
    held = list(runs["volumes"])  # type: ignore[call-overload]
    runs["volumes"] = [one for one in held if not str(one).startswith("./")]
    runs["restart"] = "no"
    proxy = egress_proxy(site, host, owner, plan.editor)
    proxy["entrypoint"] = ["python3"]
    proxy["command"] = [f"{CORPUS}/{EXECUTION_DIR}/{EGRESS_SCRIPT_FILE}"]
    proxy.pop("volumes", None)
    proxy["restart"] = "no"
    return {LIVE: runs, EGRESS: proxy}


def directories(manifest) -> tuple[str, ...]:
    """Return the top-level directories the course's live examples run from, in declared order."""
    found: list[str] = []
    for example in manifest.live.examples if manifest.live else ():
        top = example.path.split("/", 1)[0]
        if "/" in example.path and top not in found:
            found.append(top)
    return tuple(found)
