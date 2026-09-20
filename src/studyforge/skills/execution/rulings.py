r"""Spec §8.1's four rulings and §8.3's, asserted against a contract block.

**What it does.** Reports every ruling one component's consuming block breaks,
in ruling order, so a renderer can refuse rather than emit a file that looks
exactly like a correct one.

**How you use it.** `findings(block, name=…)` for the list; empty is clean.

**Depends on.** `contract` for the reads and `archive.scrub` for the one name
that reaches a message. ⛔ No I/O and nothing source-specific (R1).

## ⛔ WHY THESE ARE CHECKED AND NOT REMEMBERED

⚠️ Each of the four was bought by a failure, and each failure is silent in the
rendered bytes:

1. **Loopback only, never every interface.** An unencrypted editor with a shell
   offered to every machine that can reach this host. ⭐ §8.1 names the
   synthesis service as publishing on all interfaces *today* and says it is to
   be **fixed rather than copied**, which is why this runs over every block a
   renderer is handed and not only over the one it emits.
2. **Only the sources are mounted** — not the repository, not a home directory.
3. **The container runs as the owner of those sources**, or every file a build
   writes there is root-owned and the reader can never edit their own
   repository.
4. **A bind source exists on the host before the start**, or docker creates it
   root-owned and the writer can never write it.

⛔ **And §8.3: the Docker socket is never mounted into a serving process** —
not behind a flag, not "only locally". ⚠️ A socket beside an IDE with a shell
hands a reader's unreviewed code the host's daemon.
"""

from __future__ import annotations

from collections.abc import Mapping

from studyforge.archive.scrub import scrub
from studyforge.skills.execution.contract import blocks, optional

#: Every spelling of the Docker socket a block or a rendered file is searched
#: for. ⛔ §8.3, asserted over bytes as well as over declarations.
SOCKET_PATHS = ("/var/run/docker.sock", "/run/docker.sock", "docker.sock")

#: A host bind that offers a service to every machine that can reach this host.
#: ⛔ Ruling 1's failure, by value — including the empty string, which docker
#: reads as every interface rather than as nothing.
EVERY_INTERFACE = ("0.0.0.0", "::", "*", "")

#: Host paths a bind may never name, whatever a contract declares. ⛔ Ruling 2.
NEVER_BOUND = (".", "..", "/", "~", "${HOME}", "$HOME")


def findings(block: Mapping[str, object], *, name: str) -> tuple[str, ...]:
    """Every §8.1 or §8.3 ruling this block breaks, in ruling order."""
    return tuple(
        [
            *_ports(block, name),
            *_mounts(block, name),
            *_owner(block, name),
            *_socket(block, name),
        ]
    )


def names_a_socket(text: str) -> bool:
    """Whether rendered bytes name the Docker socket. ⛔ §8.3 over the output."""
    return any(path in text for path in SOCKET_PATHS)


def _ports(block: Mapping[str, object], name: str) -> list[str]:
    """Ruling 1 — loopback only, never every interface."""
    found = []
    for entry in blocks(block, "ports"):
        if entry.get("publish_on_all_interfaces") is True or entry.get(
            "host_bind"
        ) in EVERY_INTERFACE:
            found.append(
                f"{scrub(name)} publishes a port on every interface; §8.1 ruling 1 binds "
                f"it to loopback, because this is an unencrypted service with a shell"
            )
    return found


def _mounts(block: Mapping[str, object], name: str) -> list[str]:
    """Rulings 2 and 4 — only the sources, and a bind source that exists first."""
    found = []
    binds = [entry for entry in blocks(block, "mounts") if entry.get("kind") == "bind"]
    for entry in binds:
        if str(entry.get("host_path", "")).strip() in NEVER_BOUND:
            found.append(
                f"{scrub(name)} binds the repository or a home directory; §8.1 ruling 2 "
                f"mounts only the sources"
            )
        if entry.get("must_exist_before_start") is not True:
            found.append(
                f"{scrub(name)} declares a bind that need not exist before the start; "
                f"§8.1 ruling 4 says docker then creates it root-owned and the writer "
                f"can never write it"
            )
    per_project = [entry for entry in binds if entry.get("per_project") is True]
    if binds and len(per_project) != 1:
        found.append(
            f"{scrub(name)} declares {len(per_project)} per-project binds; §8.1 ruling 2 "
            f"gives a corpus exactly one, which is its sources"
        )
    return found


def _owner(block: Mapping[str, object], name: str) -> list[str]:
    """Ruling 3 — the container runs as the owner of the mounted sources."""
    if not any(entry.get("kind") == "bind" for entry in blocks(block, "mounts")):
        return []
    if optional(block, "runs_as", "compose_value") or optional(block, "runs_as", "run_value"):
        return []
    return [
        f"{scrub(name)} binds a host directory and declares no value for the uid to run "
        f"as; §8.1 ruling 3 says every file it writes there is then root-owned and the "
        f"reader can never edit their own repository"
    ]


def _socket(block: Mapping[str, object], name: str) -> list[str]:
    """§8.3 — the Docker socket is never mounted into a serving process."""
    if optional(block, "docker_socket", default=False) is not False:
        return [
            f"{scrub(name)} declares a Docker socket; §8.3 mounts none into a serving "
            f"process, not behind a flag and not only locally"
        ]
    return [
        f"{scrub(name)} declares a mount at a Docker socket path; §8.3 mounts none"
        for entry in blocks(block, "mounts")
        if names_a_socket(str(entry.get("host_path", "")))
    ]
