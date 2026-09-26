r"""Spec §8.1's four compose rules and §8.3's, asserted against a contract block.

**What it does.** Reports every rule one component's consuming block breaks,
in the order below, so a renderer can refuse rather than emit a file that looks
exactly like a correct one.

**How you use it.** `findings(block, name=…)` for the list; empty is clean.

**Depends on.** `contract` for the reads and `archive.scrub` for the one name
that reaches a message. ⛔ No I/O and nothing source-specific (R1).

## ⛔ WHY THESE ARE CHECKED AND NOT REMEMBERED

⚠️ **The spec does not number these.** §8.1 states them as the bullets
of *"what the compose side gets right"*, so a refusal cites each by what it
says — loopback, the sources alone, the owner's uid:gid, a bind source that
exists first — and never by a number a reader would look for and not find.
The numbers below order this list and nothing else.

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

⭐ **And every bind in the rendered file is written relative to the file**
(`bind_findings`). The register's direction is that the compose file runs on
any engine, Docker Desktop and Windows included: Docker Desktop shares no host
`/tmp`, Windows has no `/tmp` and no POSIX root, and an absolute path written
at build time is one machine's layout. ⛔ So a bind source that is absolute —
POSIX, a drive letter, a UNC share or a home shorthand — or spelled with a
backslash is refused; a named volume or a `tmpfs` is the store for anything
that is not the corpus's own checkout.
"""

from __future__ import annotations

import re
from collections.abc import Mapping

from studyforge.archive.scrub import scrub
from studyforge.skills.execution.contract import blocks, optional

#: Every spelling of the Docker socket a block or a rendered file is searched
#: for. ⛔ §8.3, asserted over bytes as well as over declarations.
SOCKET_PATHS = ("/var/run/docker.sock", "/run/docker.sock", "docker.sock")

#: A host bind that offers a service to every machine that can reach this host.
#: ⛔ The loopback rule's failure, by value — including the empty string, which docker
#: reads as every interface rather than as nothing.
EVERY_INTERFACE = ("0.0.0.0", "::", "*", "")

#: Host paths a bind may never name, whatever a contract declares. ⛔ The sources alone.
NEVER_BOUND = (".", "..", "/", "~", "${HOME}", "$HOME")


def findings(block: Mapping[str, object], *, name: str) -> tuple[str, ...]:
    """Every §8.1 or §8.3 rule this block breaks, in the module's order."""
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
    """Loopback only, never every interface (§8.1)."""
    found = []
    for entry in blocks(block, "ports"):
        if (
            entry.get("publish_on_all_interfaces") is True
            or entry.get("host_bind") in EVERY_INTERFACE
        ):
            found.append(
                f"{scrub(name)} publishes a port on every interface; §8.1 binds it to "
                f"loopback only, because this is an unencrypted service with a shell"
            )
    return found


def _mounts(block: Mapping[str, object], name: str) -> list[str]:
    """Only the sources, and a bind source that exists first (§8.1)."""
    found = []
    binds = [entry for entry in blocks(block, "mounts") if entry.get("kind") == "bind"]
    for entry in binds:
        if str(entry.get("host_path", "")).strip() in NEVER_BOUND:
            found.append(
                f"{scrub(name)} binds the repository or a home directory; §8.1 mounts "
                f"only the sources"
            )
        if entry.get("must_exist_before_start") is not True:
            found.append(
                f"{scrub(name)} declares a bind that need not exist before the start; "
                f"§8.1 says a bind source exists on the host before the start, or docker "
                f"creates it root-owned and the writer can never write it"
            )
    per_project = [entry for entry in binds if entry.get("per_project") is True]
    if binds and len(per_project) != 1:
        found.append(
            f"{scrub(name)} declares {len(per_project)} per-project binds; §8.1 mounts "
            f"only the sources, so a corpus gets exactly one"
        )
    return found


def _owner(block: Mapping[str, object], name: str) -> list[str]:
    """Report a bind with no owner to run as (§8.1: the repository owner's uid:gid)."""
    if not any(entry.get("kind") == "bind" for entry in blocks(block, "mounts")):
        return []
    if optional(block, "runs_as", "compose_value") or optional(block, "runs_as", "run_value"):
        return []
    return [
        f"{scrub(name)} binds a host directory and declares no value for the uid to run "
        f"as; §8.1 runs the container as the repository owner's uid:gid, or every file "
        f"it writes there is root-owned and the reader can never edit their own repository"
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


#: A Windows drive root (`C:\\`, `C:/`) at the start of a bind source.
_DRIVE = re.compile(r"^[A-Za-z]:[\\/]")


def bind_findings(services: Mapping[str, object]) -> list[str]:
    """Every rendered bind whose host side is not written relative to the compose file.

    ⭐ A source with no path separator and no leading dot is a named volume, and
    passes; `./…` and `../…` are the corpus's own directories, and pass.
    """
    found = []
    for name, service in services.items():
        entries = service.get("volumes", []) if isinstance(service, Mapping) else []
        for entry in entries if isinstance(entries, list) else []:
            source = _source(str(entry))
            if source.startswith(("/", "~", "\\", "$")) or _DRIVE.match(source) or "\\" in source:
                found.append(
                    f"the {scrub(str(name))} service binds {scrub(source)!r}, which is not "
                    "relative to the compose file; it runs on no other machine or engine"
                )
    return found


def _source(entry: str) -> str:
    """Return the host side of a short-syntax volume entry, a drive letter kept whole."""
    drive = _DRIVE.match(entry)
    head, rest = (entry[:2], entry[2:]) if drive else ("", entry)
    return head + rest.split(":", 1)[0]
