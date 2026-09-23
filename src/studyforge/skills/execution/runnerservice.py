r"""The runner Submit execs into, as a compose service — read from the contract's `runner` block.

**What it does.** Turns the component's `runner` block into the second service
of the corpus's compose file, so ONE `docker compose up` brings up the editor
AND the long-lived container a graded run `docker exec`s into (`W445`).

**How you use it.** `plan(document, source=…, root=…, runs_as=…)` returns a
`Runner`: the service mapping `composefile.render` places beside the editor,
the container's name, and the selection whose `tag_from` `record` runs.

**Depends on.** `contract` for every value, `rulings` for §8.1 and §8.3,
`toolchain` for the argv with the declared set in its slot. ⛔ No I/O and
nothing source-specific (R1).

## ⛔ THE NAME IS THE CONTRACT'S, AND IT IS THE ONE `execute` LOOKS FOR

⭐ **`runner.run.name_template` with the corpus's `source` in its slot** — the
same sentence `execute.commands.container_for` spells, which is how a Submit
finds the container and `execute.mode` stops falling back to the host. ⚠️ Two
spellings of one name is the defect where they differ by a character and every
run silently goes to the host; the skill's tests hold the two equal.

## ⛔ THE SERVING PROCESS IS NOT HERE, AND NEITHER IS THE SOCKET

⭐ **The reader's `docker compose` starts this container, never `serve`** (spec
§8.3, round 112's `TC-00` answer 6): the runner only asks whether it is up and
execs into it from the host. ⛔ Nothing rendered here mounts the Docker socket,
and `composefile.render` checks the whole file's bytes for one besides.

## ⚠️ TWO VALUES THE RUNNER BLOCK DOES NOT CARRY FOR COMPOSE — BOTH FINDINGS

- ⛔ **`runner.image` declares a `run_value` (`<tag>`) and no `compose_value`**,
  so the interpolation is composed here from the block's own `env_var`: the
  compose syntax `${VAR:?why}` and nothing else. `W445/1`.
- ⛔ **`runner.runs_as` declares a shell `run_value` (`$(id -u):$(id -g)`) and
  no compose key or value**, which compose cannot evaluate. ⭐ The editor
  block's `runs_as` IS that answer — *"the uid:gid that owns the mounted
  sources"* — so it is read from there rather than typed. `W445/2`.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from studyforge.archive.scrub import scrub
from studyforge.skills.execution import rulings, toolchain
from studyforge.skills.execution.contract import ContractRefused, blocks, optional, require

#: The slot `runner.run.name_template` leaves for the corpus's `source`.
SOURCE_SLOT = "<source>"

#: The slot a runner mount's `host_path` leaves for the corpus's source root.
ROOT_SLOT = "<source root>"

#: The compose service's name. ⭐ A key in the file only; the CONTAINER's name is
#: `container_name`, which is what `execute` looks the runner up by.
SERVICE = "runner"


class RunnerRefused(ValueError):
    """A runner service this renderer will not emit, and which ruling it breaks."""


@dataclass(frozen=True, slots=True)
class Runner:
    """The runner's compose service, its container name, and how its tag is computed."""

    #: The container's name, the contract's template with `source` in its slot.
    name: str
    #: The compose service mapping, every value read out of the contract.
    service: dict[str, object]
    #: The runner block's selection: the argv that builds it and prints its tag.
    selection: toolchain.Selection
    #: `runner.image.repository`, which a printed tag must begin with.
    repository: str
    #: `runner.prime.declared_by`, its directory slot left open.
    prime_flag: str


def plan(
    document: Mapping[str, object],
    *,
    source: str,
    root: str,
    runtimes: tuple[str, ...],
    runs_as: Mapping[str, object],
) -> Runner:
    """Return the runner service for corpus `source`, whose root compose reaches at `root`."""
    block = require(document, SERVICE)
    if not isinstance(block, Mapping):
        raise ContractRefused("the contract's runner must be an object")
    broken = rulings.findings(block, name=SERVICE)
    if broken:
        raise RunnerRefused(
            f"the runner block breaks a ruling this renderer will not emit against: "
            f"{'; '.join(broken)}"
        )
    selection = toolchain.select(runtimes, document, block=SERVICE)
    name = container_name(block, source)
    built: dict[str, object] = {
        "image": f"${{{selection.image_env}:?{_why_unset(selection.image_env)}}}",
        "container_name": name,
        str(require(runs_as, "compose_key")): require(runs_as, "compose_value"),
    }
    if optional(block, "init", "enabled") is True:
        built["init"] = True
    built["network_mode"] = require(block, "network", "mode")
    if blocks(block, "ports"):
        raise RunnerRefused(
            "the runner block declares a published port; nothing in it listens, and a port "
            "is a surface with no service behind it"
        )
    built["volumes"] = [_mounted(entry, root) for entry in blocks(block, "mounts")]
    built["restart"] = require(block, "restart")
    flag = require(block, "prime", "declared_by")
    if not isinstance(flag, str):
        raise ContractRefused("runner.prime.declared_by must be a string")
    return Runner(
        name=name,
        service=built,
        selection=selection,
        repository=str(require(block, "image", "repository")),
        prime_flag=flag,
    )


def container_name(block: Mapping[str, object], source: str) -> str:
    """Return the contract's container name with `source` in its one slot."""
    template = require(block, "run", "name_template")
    if not isinstance(template, str) or template.count(SOURCE_SLOT) != 1:
        raise ContractRefused(f"runner.run.name_template has no single {SOURCE_SLOT} slot")
    return template.replace(SOURCE_SLOT, source)


def _mounted(entry: Mapping[str, object], root: str) -> str:
    """One runner bind: the corpus's source root, where the contract says it goes."""
    if entry.get("kind") != "bind" or entry.get("per_project") is not True:
        raise RunnerRefused(
            f"the runner block declares a mount this renderer has no host side for: "
            f"{scrub(str(entry.get('container_path', '')))}"
        )
    if entry.get("host_path") != ROOT_SLOT:
        raise ContractRefused(f"a runner bind's host_path must be the {ROOT_SLOT} slot")
    inside = require(entry, "container_path")
    return f"{root}:{inside}{':ro' if entry.get('read_only') is True else ''}"


def _why_unset(variable: str) -> str:
    """Return the sentence compose prints when the runner's tag was never recorded."""
    return f"record the primed runner's tag with the execution skill; it writes {variable}"
