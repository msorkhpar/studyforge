"""The real runner container `execute`'s acceptance runs against — started as the READER starts it.

⭐ **Opt-in, by naming the image:** `STUDYFORGE_RUNNER_IMAGE=<tag>`, the tag
`code-server-toolchain`'s `docker/minimal/build.py --runtimes python` built. ⛔
Absent, or with no Docker reachable, every container-mode case SKIPS and says
which — the pinned dev image carries no Docker, so its suite reads host mode
only, and the real-container reading is taken on a host that has one.

⭐ **The container is started from the sibling's DECLARATION** — the `runner`
block of its `consuming.json`, read at run time and rendered here — so the
runner is proved against the container a reader actually has: source root alone
at the declared workspace, the declared network mode, an init, the reader's
uid:gid, no port, no socket. ⛔ The runner itself starts nothing; this is the
test standing in for the reader.

## ⛔ Why this reads DATA and never parses the README

Parsing the sibling's `docker run` line out of its README would make a
paragraph of prose an interface: a consumer of the runner image would re-derive
its run shape by parsing English, and a rewording of the sentence would be a
silent break. The runner declares its shape the way the editor does, and this
reads the declaration. The README's line still exists for a person to copy, and the
sibling's own tests assert it is what the block renders.

⭐ **`PROMISE` is the `provides` this was built against** (R9), the way
`skills.buildserve.narration.PROMISE` records `narrate-service`'s. A sibling
that promises less is REFUSED rather than migrated: the cases skip and say so.
⛔ **Nothing but `consuming.json` is read from the sibling** — not its
Dockerfile, not its `consuming/` modules, not its README.

⛔ **Every invocation that reaches this module must hold the shared container
lock**: it is taken around the pytest run, not in here, so
one gate is one lock.

## ⛔ THE CONTRACT IS READ AT A COMMIT, NEVER OFF A WORKING TREE

⚠️ **Measured:** while the sibling's checkout was mid-merge, its
`consuming.json` read as **present** from a **staged** file that existed on no
ref — so a green reading here could be reproduced from no commit anywhere, and
nothing in the reading said so. ⭐ `tests.harness.sibling` is the one reader
now: it finds the checkout through `STUDYFORGE_WORKSPACE` and distinguishes the
**three** outcomes this module acts on:

| the reading | what this module does |
|---|---|
| **at the checked-out commit** | uses it — ⭐ the case another host reproduces |
| **working tree only** | ⛔ **refuses**, saying it is LOCAL; every container case SKIPS |
| **absent** | refuses the same way — ⭐ a clean clone's case, never a crash |

⛔ **A directory a CALLER names is a fourth thing and is not one of the three.**
No commit covers it, so `declaration_reason(root)` reads it and does not demand
one. ⚠️ That is what keeps a synthetic fixture usable while the real sibling is
held to a commit, and the policy is stated **once**, as `must_be_committed` on
`reason_for`, rather than implied in two places.
"""

from __future__ import annotations

import json
import os
import shlex
import subprocess
import uuid
from pathlib import Path

from tests.harness import engine, sibling
from tests.support import tool_on_path

IMAGE_VARIABLE = "STUDYFORGE_RUNNER_IMAGE"
SIBLING = "code-server-toolchain"
#: The component's machine-readable contract, and the block this reads from it.
CONTRACT = "consuming.json"
BLOCK = "runner"
#: The schema version this understands, and the `provides` it was built against.
CONSUMING_API = 1
PROMISE = 2


def image() -> str | None:
    """The runner image this run was asked to use, or `None`."""
    return os.environ.get(IMAGE_VARIABLE) or None


def skip_reason() -> str | None:
    """Why the container cases cannot run here, or `None` when they can."""
    if image() is None:
        return f"no runner image named: set {IMAGE_VARIABLE} to a tag built by {SIBLING}"
    if tool_on_path("docker") is None:
        return "no docker CLI in this environment (the pinned dev image carries none)"
    if _docker("image", "inspect", image()).returncode != 0:
        return f"{IMAGE_VARIABLE} names an image this daemon does not hold"
    return declaration_reason()


def contract_reading(root: Path | None = None) -> sibling.Reading:
    """The sibling's whole contract **and what it was read from**.

    ⭐ With no `root` the sibling is found through `STUDYFORGE_WORKSPACE` and
    read at its checked-out commit. With one, that directory is read as given —
    no commit covers a directory a caller named, and the reading says so.
    """
    if root is not None:
        return sibling.read_directory(Path(root), CONTRACT)
    return sibling.read_sibling(SIBLING, CONTRACT)


def reason_for(reading: sibling.Reading, *, must_be_committed: bool) -> str | None:
    """Why this reading cannot be used, or `None` when it can.

    ⛔ **The whole policy, in one place.** `must_be_committed` is the caller
    saying *"I resolved this sibling myself, so it has to be read at a commit"* —
    the working-tree refusal. A caller that named a directory passes `False`, because
    no commit covers that reading.
    """
    contract = _loaded(reading)
    if contract is None:
        return (
            f"the sibling {SIBLING}'s {CONTRACT} is not reachable from this "
            f"checkout: {reading.source}"
        )
    if must_be_committed and reading.working_tree:
        # ⛔ A staged or uncommitted contract is a green reading that
        # exists on no ref, so it reproduces on no other host. Refused.
        return (
            f"{SIBLING}'s {CONTRACT} was not read at a commit, so a reading from "
            f"it is LOCAL: {reading.source}"
        )
    if contract.get("consuming_api") != CONSUMING_API:
        return (
            f"{SIBLING}'s {CONTRACT} is schema {contract.get('consuming_api')!r}; "
            f"this reads {CONSUMING_API}"
        )
    if not isinstance(contract.get("provides"), int) or contract["provides"] < PROMISE:
        return (
            f"{SIBLING} promises {contract.get('provides')!r}; this was built against "
            f"{PROMISE} and refuses a mismatch rather than migrating it (R9)"
        )
    if not contract.get(BLOCK):
        return f"{SIBLING}'s {CONTRACT} declares no {BLOCK} block, so its run shape is not data"
    return None


def declaration_reason(root: Path | None = None) -> str | None:
    """Why the sibling's runner declaration cannot be used, or `None` when it can."""
    return reason_for(contract_reading(root), must_be_committed=root is None)


def declaration(root: Path | None = None) -> dict | None:
    """The sibling's `runner` block, or `None` when `declaration_reason` says why not."""
    reading = contract_reading(root)
    if reason_for(reading, must_be_committed=root is None) is not None:
        return None
    return _loaded(reading)[BLOCK]


def run_argv(
    runner: dict, *, name: str, source_root: Path | str, tag: str, user: str | None = None
) -> list[str]:
    """The `docker run` argv the declaration describes, with every value filled.

    ⛔ No quoting and no shell: the declaration's `runs_as.run_value` is the
    substitution a person's shell would expand, so it is never passed through —
    this fills the real uid:gid instead.
    """
    run = runner["run"]
    argv = ["docker", "run"]
    if run.get("detached"):
        argv.append(run["detach_flag"])
    argv += [run["name_flag"], name]
    if runner.get("init", {}).get("enabled"):
        argv.append(runner["init"]["run_flag"])
    argv += [runner["network"]["run_flag"], runner["network"]["mode"]]
    argv += [runner["runs_as"]["run_flag"], user or f"{os.getuid()}:{os.getgid()}"]
    for mount in runner["mounts"]:
        if mount.get("kind") != "bind":
            continue
        suffix = ":ro" if mount.get("read_only") else ""
        argv += ["-v", f"{engine.bindable(source_root)}:{mount['container_path']}{suffix}"]
    argv.append(tag)
    argv += list(runner.get("command", []))
    return argv


def workspace_path(runner: dict) -> str:
    """Where the source root is mounted inside the container, as declared."""
    return runner["workspace"]["container_path"]


def exec_argv(runner: dict, *, name: str, directory: str, command: list[str]) -> list[str]:
    """A command run inside the container from outside, from the declared template."""
    root = workspace_path(runner)
    filled = {"<name>": name, f"{root}/<directory>": f"{root}/{directory}"}
    argv = [filled.get(part, part) for part in runner["command_notes"]["exec_template"]]
    return argv[:-1] + list(command)


def start(source_root: Path) -> str:
    """Start the runner container over `source_root` as the reader would; its name."""
    runner = declaration()
    if runner is None:
        raise RuntimeError(declaration_reason())
    name = f"sf20-{uuid.uuid4().hex[:10]}"
    argv = run_argv(runner, name=name, source_root=source_root, tag=image())
    started = subprocess.run(argv, stdin=subprocess.DEVNULL, capture_output=True, text=True)
    if started.returncode != 0:
        remove(name)
        raise RuntimeError(
            f"the declared run line did not start: exit {started.returncode}: {shlex.join(argv)}"
        )
    return name


def remove(name: str) -> None:
    """Remove the container this module started. ⛔ Leave none behind."""
    _docker("rm", "-f", name)


def settings(name: str) -> str:
    """Its network mode, published ports and mounts, as `docker inspect` reports them."""
    return _docker(
        "inspect",
        "--format",
        "{{.HostConfig.NetworkMode}} {{json .HostConfig.PortBindings}} {{json .Mounts}}",
        name,
    ).stdout


def alive_in(name: str):
    """A predicate: is process `pid` alive, and not a zombie, inside container `name`?"""

    def alive(pid: int) -> bool:
        probe = _docker(
            "exec",
            name,
            "sh",
            "-c",
            'grep -q "^State:[[:space:]]*[^Z]" "/proc/$1/status"',
            "sh",
            str(pid),
        )
        return probe.returncode == 0

    return alive


def _loaded(reading: sibling.Reading) -> dict | None:
    """The reading parsed as a contract, or `None` when there is none to parse.

    ⚠️ Unreadable and unparseable collapse into the same answer deliberately:
    both mean *"this checkout has no contract this module can act on"*, and the
    `source` sentence is what distinguishes them for a person.
    """
    if reading.text is None:
        return None
    try:
        loaded = json.loads(reading.text)
    except json.JSONDecodeError:
        return None
    return loaded if isinstance(loaded, dict) else None


def _docker(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["docker", *arguments],
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        check=False,
    )
