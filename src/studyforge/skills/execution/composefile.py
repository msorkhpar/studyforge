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

⚠️ **The one exception is the published host port, and it is a finding rather
than an exception.** `ports[].per_project` is `true` while that entry declares
no environment variable and no compose value — unlike `image` and `runs_as`,
which both declare one — so the rendered file carries the contract's declared
host port literally and two corpora on one host collide. ⛔ **`SK-09/4`, a
finding against the component's contract; the remedy is a key there.**

## ⛔ THE RULINGS ARE CHECKED BEFORE ANYTHING IS EMITTED

⚠️ A rendered file that broke one would look exactly like a rendered file that
did not, so `rulings.findings` runs first and a non-empty answer is a refusal.
⭐ §8.3 is checked **twice** — in the declaration and over the rendered bytes —
because the two can disagree only if this module has a defect, which is exactly
when it matters.

## ⚠️ ONE SERVICE, AND THE SECOND COMPONENT'S BLOCK IS CHECKED RATHER THAN RENDERED

⭐ **The narration component's contract is read and its rulings are asserted**;
§8.1 names that service as publishing on all interfaces today and says it is to
be fixed rather than copied. ⛔ **It is not rendered into this file**, and that
is measured rather than chosen: its `service` block carries none of the
per-project keys the editor's does — no host port, no volume name, no compose
value for its uid — so rendering it would mean inventing all three here.
⚠️ **`SK-09/2`, a finding against that contract.** ⭐ It is brought up from its
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
) -> dict[str, object]:
    """One compose service, every value of it read out of `block`."""
    broken = rulings.findings(block, name=name)
    if broken:
        raise ComposeRefused(
            f"the {scrub(name)} block breaks a ruling this renderer will not emit "
            f"against: {'; '.join(broken)}"
        )
    built: dict[str, object] = {"image": image}
    built[str(require(block, "runs_as", "compose_key"))] = require(
        block, "runs_as", "compose_value"
    )
    filesystem = optional(block, "filesystem", "compose_key")
    if isinstance(filesystem, str) and filesystem:
        built[filesystem] = require(block, "filesystem", "compose_value")
    built["ports"] = [_published(entry) for entry in blocks(block, "ports")]
    environment = _environment(block)
    if environment:
        built["environment"] = environment
    command = optional(block, "command")
    if command:
        built["command"] = list(command)
    workspace = _tmpfs(block)
    if workspace:
        built["tmpfs"] = workspace
    built["volumes"] = [_mounted(entry, sources) for entry in kept(block, volumes)]
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
) -> str:
    """The whole compose file, as the bytes a corpus keeps.

    ⭐ `checked` is every other component block whose rulings are asserted and
    whose service is **not** rendered — see the module contract.
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
    document: dict[str, object] = {
        "name": project,
        "services": {
            "editor": service(
                editor, name="editor", image=image, sources=sources, volumes=volumes
            )
        },
    }
    named = sorted({str(entry["volume"]) for entry in mounts if entry.get("volume")})
    if named:
        document["volumes"] = {one: {} for one in named}
    text = emit(document) + _footer(editor, volumes, sources)
    if rulings.names_a_socket(text):
        raise ComposeRefused(
            "the rendered file names the Docker socket; §8.3 mounts none into a serving "
            "process, not behind a flag and not only locally"
        )
    return text


def volumes_for(
    seeds: Mapping[str, object] | None, runtimes: Sequence[str]
) -> tuple[str, ...]:
    """The named cache volumes a declared set earns, from the contract's own map.

    ⭐ **The join is the contract's own**: its prime block maps a runtime to the
    volume that runtime's cache is seeded into, so *"omit it when that runtime
    is not declared"* is answered from data rather than from the English
    sentence the mount's own `purpose` puts it in. ⚠️ **The mount entries carry
    no such key**, which is `SK-09/3` — a finding, and the reason this is handed
    the other block's map instead of reading its own.
    """
    declared = frozenset(runtimes)
    if not isinstance(seeds, Mapping):
        return ()
    return tuple(
        sorted(str(volume) for runtime, volume in seeds.items() if runtime in declared)
    )


def kept(
    block: Mapping[str, object], volumes: Sequence[str] = ()
) -> tuple[Mapping[str, object], ...]:
    """The mounts a rendered file carries: the required ones and the earned ones."""
    return tuple(
        entry
        for entry in blocks(block, "mounts")
        if entry.get("required") is True or str(entry.get("volume", "")) in volumes
    )


def must_exist_first(
    editor: Mapping[str, object], volumes: Sequence[str] = (), sources: str = ""
) -> tuple[str, ...]:
    """Every bind source that must exist before the container starts (ruling 4).

    ⚠️ **The HOST side of each bind, never the container side.** Ruling 4 is
    about a directory docker would create on the host, so a reader told to
    create a path inside the image has been told nothing they can act on.
    """
    return tuple(
        (sources if entry.get("per_project") is True else str(entry.get("host_path", "")))
        for entry in kept(editor, volumes)
        if entry.get("must_exist_before_start") is True and entry.get("kind") == "bind"
    )


def _published(entry: Mapping[str, object]) -> str:
    """One published port, bound to the host address the contract names."""
    host, inside = entry.get("host"), entry.get("container")
    if not _whole(host) or not _whole(inside):
        raise ContractRefused(
            f"a ports entry must carry whole-number host and container ports, got "
            f"{describe(host)} and {describe(inside)}"
        )
    protocol = entry.get("protocol", "tcp")
    suffix = "" if protocol == "tcp" else f"/{protocol}"
    return f"{entry.get('host_bind')}:{host}:{inside}{suffix}"


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
                "file writes there, and this renderer will not invent it (R19)"
            )
        if value is not None:
            built[name] = value
    return built


def _tmpfs(block: Mapping[str, object]) -> list[str]:
    """The workspace root, when the contract declares it a tmpfs."""
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
    """The health check, with every declared interval in compose's own spelling."""
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


def _footer(editor: Mapping[str, object], volumes: Sequence[str], sources: str) -> str:
    """Ruling 4, said in the file: which bind sources must exist before the start."""
    first = must_exist_first(editor, volumes, sources)
    if not first:
        return ""
    lines = [
        "",
        "# ⛔ §8.1 ruling 4 — every bind source below exists on the host BEFORE this",
        "# file is brought up. Docker creates a missing one root-owned, and the",
        "# container can then never write it:",
        *(f"#   - {one}" for one in first),
    ]
    return "\n".join(lines) + "\n"


def _whole(value: object) -> bool:
    """Whether `value` is a whole number and not a bool wearing one's clothes."""
    return isinstance(value, int) and not isinstance(value, bool)
