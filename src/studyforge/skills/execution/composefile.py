r"""The corpus's compose file, rendered from a component's contract and nothing else.

**What it does.** Turns one contract block into one compose service and the
whole file around it, and refuses to emit anything that breaks a ruling.

**How you use it.** `service(block, …)` for the mapping, `render(…)` for the
bytes a corpus keeps, `volumes_for(…)` and `must_exist_first(…)` for the two
answers the reader's document repeats.

**Depends on.** `contract` for every value it reads, `rulings` for §8.1 and
§8.3, `emit` for the bytes. ⛔ No I/O and nothing source-specific (R1).

## ⛔ EVERY VALUE IN THE OUTPUT IS READ, NOT WRITTEN

⛔ **Not one port, mount point, uid, command word or health check is typed in
this module.** Each is resolved out of the contract at render time, so a
component that moves one moves this output with it, and a component that drops
one is refused by name rather than filled in from memory (R19).

⭐ **Per-project values arrive as compose interpolations with defaults**, which
is how *"sufficient from the contract alone"* and *"the uid differs per host"*
are both true of one file at once.

⭐ **The published host port is one of them**: a `per_project` port is
`127.0.0.1:${STUDYFORGE_EDITOR_PORT:-<the contract's host>}:<container>`, so a
second instance of one corpus publishes its own port and an instance that
recorded none publishes the one it always did. ⛔ **Only the PORT is
interpolated**: the contract's `host_bind` is written literally, so no recorded
value can widen the bind. ⚠️ The variable's NAME is the framework's
(`execute.instance`), because `serve` reads the same record; the contract's
entry still declares none, and the default is its `host`.

## ⛔ THE RULINGS ARE CHECKED BEFORE ANYTHING IS EMITTED

⚠️ A rendered file that broke one would look exactly like a rendered file that
did not, so `rulings.findings` runs first and a non-empty answer is a refusal.
⭐ §8.3 is checked **twice** — in the declaration and over the rendered bytes —
because the two can disagree only if this module has a defect, which is exactly
when it matters.

## ⭐ THE EDITOR, THE RUNNER BESIDE IT, AND WHAT THE EDITOR BINDS

⭐ **The runner a Submit execs into is the file's second service**, rendered by
`runnerservice` from the same component's `runner` block and placed here, so
one `docker compose up` starts both. ⭐ **The editor binds the practice
workspaces too** (`binds`), from where `emit` places them, beside the sources
it already shows: a practice file the editor does not hold is a frame that
cannot open it.

## ⚠️ THE SECOND COMPONENT'S BLOCK IS CHECKED RATHER THAN RENDERED

⭐ **The narration component's contract is read and its rulings are asserted**;
§8.1 names that service as publishing on all interfaces today and says it is to
be fixed rather than copied. ⛔ **It is not rendered into this file**, and that
is measured rather than chosen: its `service` block carries none of the
per-project keys the editor's does — no host port, no volume name, no compose
value for its uid — so rendering it would mean inventing all three here.
⚠️ **A finding against that contract (R19).** ⭐ It is brought up from its
own checkout by its own compose files, which the generated document says by
pointing at the key that names them.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from studyforge.archive.scrub import scrub
from studyforge.describe import describe
from studyforge.skills.execution import rulings
from studyforge.skills.execution.contract import ContractRefused, blocks, optional, require
from studyforge.skills.execution.emit import emit

#: The contract's duration keys and compose's names for them. ⛔ A mapping, not
#: a rule: the contract spells these and compose spells those, and neither
#: spelling is this module's to choose.
DURATIONS = (
    ("interval_seconds", "interval"),
    ("timeout_seconds", "timeout"),
    ("start_period_seconds", "start_period"),
    ("start_interval_seconds", "start_interval"),
)


class ComposeRefused(ValueError):
    """A compose file this renderer will not emit, and which ruling it breaks."""


def service(
    block: Mapping[str, object],
    *,
    name: str,
    image: str,
    sources: str,
    volumes: Sequence[str] = (),
    binds: Sequence[tuple[str, str]] = (),
    container_name: str | None = None,
    port_variable: str | None = None,
) -> dict[str, object]:
    """One compose service, every value of it read out of `block`.

    ⭐ `binds` are further `(host, container)` binds of the corpus's own
    directories — the practice workspaces — each writable and each
    named in the footer's list of bind sources that exist before the start. ⭐ `container_name` is
    written as given (an interpolation); `port_variable` names the
    variable a `per_project` port's host side is interpolated from.
    """
    broken = rulings.findings(block, name=name)
    if broken:
        raise ComposeRefused(
            f"the {scrub(name)} block breaks a ruling this renderer will not emit "
            f"against: {'; '.join(broken)}"
        )
    built: dict[str, object] = {"image": image}
    if container_name is not None:
        built["container_name"] = container_name
    built[str(require(block, "runs_as", "compose_key"))] = require(
        block, "runs_as", "compose_value"
    )
    filesystem = optional(block, "filesystem", "compose_key")
    if isinstance(filesystem, str) and filesystem:
        built[filesystem] = require(block, "filesystem", "compose_value")
    built["ports"] = _ports(block, port_variable)
    environment = _environment(block)
    if environment:
        built["environment"] = environment
    command = optional(block, "command")
    if command:
        built["command"] = list(command)
    workspace = _tmpfs(block)
    if workspace:
        built["tmpfs"] = workspace
    built["volumes"] = [
        *(_mounted(entry, sources) for entry in kept(block, volumes)),
        *(f"{host}:{inside}" for host, inside in binds),
    ]
    health = _healthcheck(block)
    if health:
        built["healthcheck"] = health
    built["restart"] = require(block, "restart")
    return built


def render(
    *,
    project: str,
    editor: Mapping[str, object],
    image: str,
    sources: str,
    runtimes: Sequence[str] = (),
    seeds: Mapping[str, object] | None = None,
    checked: Sequence[tuple[str, Mapping[str, object]]] = (),
    binds: Sequence[tuple[str, str]] = (),
    runner: tuple[str, Mapping[str, object]] | None = None,
    container_name: str | None = None,
    port_variable: str | None = None,
    published: tuple[
        Sequence[tuple[str, Mapping[str, object]]], Mapping[str, object], Mapping[str, object]
    ] = ((), {}, {}),
) -> str:
    """Return the whole compose file, as the bytes a corpus keeps.

    ⭐ `checked` is every other component block whose rulings are asserted and
    whose service is **not** rendered — see the module contract. ⭐ `runner` is
    `(service name, mapping)` as `runnerservice.plan` rendered it. ⭐ `published`
    is `(services, networks, gate)` as `siteservice.plan` rendered them: each
    service is placed after, in place of one of the same name, the networks are
    declared, and every other service `depends_on` the gate.
    ⭐ `project`, `container_name` and `port_variable` are written as given, so
    the caller hands in interpolations with their defaults.
    """
    for other, block in checked:
        broken = rulings.findings(block, name=other)
        if broken:
            raise ComposeRefused(
                f"the {scrub(other)} block breaks a ruling this renderer will not "
                f"stand beside: {'; '.join(broken)}"
            )
    volumes = volumes_for(seeds, runtimes)
    mounts = kept(editor, volumes)
    services: dict[str, object] = {
        "editor": service(
            editor,
            name="editor",
            image=image,
            sources=sources,
            volumes=volumes,
            binds=binds,
            container_name=container_name,
            port_variable=port_variable,
        )
    }
    if runner is not None:
        services[runner[0]] = dict(runner[1])
    services.update((name, dict(mapping)) for name, mapping in published[0])
    gated = published[2]
    for name, mapping in services.items():
        if gated and name not in gated:
            mapping["depends_on"] = dict(gated)  # type: ignore[index]
    document: dict[str, object] = {"name": project, "services": services}
    if published[1]:
        document["networks"] = dict(published[1])
    named = sorted({str(entry["volume"]) for entry in mounts if entry.get("volume")})
    if named:
        document["volumes"] = {one: {} for one in named}
    text = emit(document) + _footer(editor, volumes, sources, [host for host, _ in binds])
    if rulings.names_a_socket(text):
        raise ComposeRefused(
            "the rendered file names the Docker socket; §8.3 mounts none into a serving "
            "process, not behind a flag and not only locally"
        )
    unportable = rulings.bind_findings(services)
    if unportable:
        raise ComposeRefused(f"a bind would not run on another engine: {'; '.join(unportable)}")
    return text


def volumes_for(seeds: Mapping[str, object] | None, runtimes: Sequence[str]) -> tuple[str, ...]:
    """Return the cache volumes a declared set earns, from the contract's own map.

    ⭐ **The join is the contract's own**: its prime block maps a runtime to the
    volume that runtime's cache is seeded into, so *"omit it when that runtime
    is not declared"* is answered from data rather than from the English
    sentence the mount's own `purpose` puts it in. ⚠️ **The mount entries carry
    no such key** — a finding against the contract, and the reason this is handed
    the other block's map instead of reading its own.
    """
    declared = frozenset(runtimes)
    if not isinstance(seeds, Mapping):
        return ()
    return tuple(sorted(str(volume) for runtime, volume in seeds.items() if runtime in declared))


def kept(
    block: Mapping[str, object], volumes: Sequence[str] = ()
) -> tuple[Mapping[str, object], ...]:
    """Return the mounts a rendered file carries: the required and the earned."""
    return tuple(
        entry
        for entry in blocks(block, "mounts")
        if entry.get("required") is True or str(entry.get("volume", "")) in volumes
    )


def must_exist_first(
    editor: Mapping[str, object],
    volumes: Sequence[str] = (),
    sources: str = "",
    *,
    also: Sequence[str] = (),
) -> tuple[str, ...]:
    """Every bind source that must exist before the container starts.

    ⚠️ **The HOST side of each bind, never the container side.** §8.1's rule is
    about a directory docker would create on the host, so a reader told to
    create a path inside the image has been told nothing they can act on.
    """
    declared = tuple(
        (sources if entry.get("per_project") is True else str(entry.get("host_path", "")))
        for entry in kept(editor, volumes)
        if entry.get("must_exist_before_start") is True and entry.get("kind") == "bind"
    )
    return declared + tuple(also)


def interpolated(variable: str, default: object) -> str:
    """Return compose's `${VARIABLE:-default}`: the recorded value, or the one it always was."""
    return f"${{{variable}:-{default}}}"


def per_project_port(block: Mapping[str, object]) -> int:
    """Return the host port the block's one `per_project` port entry declares."""
    for entry in blocks(block, "ports"):
        if entry.get("per_project") is True and _whole(entry.get("host")):
            return int(str(entry["host"]))
    raise ContractRefused("the editor block declares no per-project host port")


def _ports(block: Mapping[str, object], variable: str | None) -> list[str]:
    """Every published port; a `per_project` one's host side from `variable` when given.

    ⛔ **One variable holds one port**, so a block declaring two per-project
    ports is refused rather than publishing both on one recorded number.
    """
    entries = blocks(block, "ports")
    per_project = [entry for entry in entries if entry.get("per_project") is True]
    if variable is not None and len(per_project) > 1:
        raise ComposeRefused(
            f"the block declares {len(per_project)} per-project ports and one recorded "
            f"variable, {variable}, holds one"
        )
    return [
        _published(entry, variable if entry.get("per_project") is True else None)
        for entry in entries
    ]


def _published(entry: Mapping[str, object], variable: str | None = None) -> str:
    """One published port, bound to the host address the contract names.

    ⛔ The address is the contract's, written literally, whatever `variable`
    is: only the port number is ever interpolated.
    """
    host, inside = entry.get("host"), entry.get("container")
    if not _whole(host) or not _whole(inside):
        raise ContractRefused(
            f"a ports entry must carry whole-number host and container ports, got "
            f"{describe(host)} and {describe(inside)}"
        )
    protocol = entry.get("protocol", "tcp")
    suffix = "" if protocol == "tcp" else f"/{protocol}"
    published = host if variable is None else interpolated(variable, host)
    return f"{entry.get('host_bind')}:{published}:{inside}{suffix}"


def _environment(block: Mapping[str, object]) -> dict[str, object]:
    """Every declared variable, by the contract's own compose value or default."""
    built: dict[str, object] = {}
    for entry in blocks(block, "environment"):
        name = entry.get("name")
        if not isinstance(name, str) or not name:
            raise ContractRefused(f"an environment entry must carry a name, got {describe(name)}")
        value = entry.get("compose_value", entry.get("default"))
        if value is None and entry.get("required") is True:
            raise ContractRefused(
                "the contract requires an environment variable and declares neither a "
                "default nor a compose value for it, so nothing says what a rendered "
                "file writes there, and this renderer will not invent it"
            )
        if value is not None:
            built[name] = value
    return built


def _tmpfs(block: Mapping[str, object]) -> list[str]:
    """Return the workspace root, where the contract declares it a tmpfs."""
    if optional(block, "workspace", "kind") != "tmpfs":
        return []
    return [str(require(block, "workspace", "container_path"))]


def _mounted(entry: Mapping[str, object], sources: str) -> str:
    """One compose volume line, bind or named volume, with its read-only flag."""
    inside = require(entry, "container_path")
    outside = sources if entry.get("per_project") is True else entry.get("volume")
    if not outside:
        raise ContractRefused(
            "a mount entry declares neither a volume name nor a per-project host path, "
            "so nothing says what is mounted there"
        )
    return f"{outside}:{inside}{':ro' if entry.get('read_only') is True else ''}"


def _healthcheck(block: Mapping[str, object]) -> dict[str, object]:
    """Return the health check, each declared interval in compose's own spelling."""
    declared = optional(block, "healthcheck")
    if not isinstance(declared, Mapping):
        return {}
    built: dict[str, object] = {"test": list(require(block, "healthcheck", "command"))}
    for key, compose in DURATIONS:
        if _whole(declared.get(key)):
            built[compose] = f"{declared[key]}s"
    if _whole(declared.get("retries")):
        built["retries"] = declared["retries"]
    return built


def _footer(
    editor: Mapping[str, object], volumes: Sequence[str], sources: str, also: Sequence[str]
) -> str:
    """§8.1, said in the file: which bind sources must exist before the start."""
    first = must_exist_first(editor, volumes, sources, also=also)
    if not first:
        return ""
    lines = [
        "",
        "# ⛔ Spec §8.1: every bind source below exists on the host BEFORE this",
        "# file is brought up. Docker creates a missing one root-owned, and the",
        "# container can then never write it:",
        *(f"#   - {one}" for one in first),
    ]
    return "\n".join(lines) + "\n"


def _whole(value: object) -> bool:
    """Whether `value` is a whole number and not a bool wearing one's clothes."""
    return isinstance(value, int) and not isinstance(value, bool)
