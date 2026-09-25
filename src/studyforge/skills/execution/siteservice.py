r"""The study server as the compose file's third service, and the runner's run service beside it.

**What it does.** Renders the `site` service — the installed library's `serve`,
published with one compose — and turns the runner `runnerservice` planned into
the one the site reaches: on an INTERNAL network only the two of them join,
running the run service (`execute.published.run_service_script`) in place of
its idle command, with no port published.

**How you use it.** `onboard.generate` calls `plan(...)` with the editor block,
the corpus's source, the editor's binds and the runner's mapping, and hands the
answer's `services` and `networks` to `composefile.render`.

**Depends on.** `contract` for the editor's restart, uid:gid and health check,
`execute.instance` and `execute.published` for the one spelling of every
variable the site reads. ⛔ No I/O and nothing source-specific (R1).

## ⛔ THE DOCKER SOCKET NEVER REACHES THE SITE, AND THE RUNNER PUBLISHES NOTHING

⭐ **The site reaches the runner over the compose network's internal side**: the
runner leaves `network_mode: none` for the `runs` network, which is `internal`
(no route out, as `none` had none) and which the editor never joins — the
editor hands a person a shell, and nothing on that network should answer one.
⛔ The runner still publishes no port; the run service listens only there, and
runs only the argv the corpus's records name (the allowlist the site writes).

⭐ **No credential on that network, and why that is enough**: the only other
member is the site, which is the one process that may ask for a run; a
credential would be a secret both containers read from one corpus, so it would
guard nothing the allowlist does not already guard. Spec §8.3 is argued there.

## ⭐ EVERY PORT IS SET IN ONE PLACE, AND THE PAGE LEARNS IT FROM THE API

⭐ **The site's port and the editor's port are `instance.env`'s**, each
interpolated with the default an instance that recorded none has. The site is
told the editor's browser-facing origin through its environment and hands it
to a page through the run index, so no built file names a port (R8).
⭐ The site listens on the same port inside its container that it publishes, so
the `Host` a browser sends is the one `serve` admits.

## ⛔ THE PUBLISHER'S VALUES ARE CHECKED BEFORE ANYTHING STARTS

⭐ `instance.env` is the publisher's file, so the `preflight` service runs
`studyforge preflight /corpus` first, from the site's image, with the corpus
read-only and no network, and every other service `depends_on` it completing.
⭐ The dependency is `required: ${STUDYFORGE_PREFLIGHT:-false}`: before a site
image is staged the profile is off, the preflight does not exist, and the editor
and the runner start as they always did — a bad value is then refused by
`studyforge serve`. ⛔ Once staged, `SITE_ENV_NAME` sets it `true`, because a
failed OPTIONAL dependency is only a warning to compose, which then starts every
service anyway; a required one stops them all, with the preflight's sentence in
its log.

## ⭐ THE SITE IS HEALTHY ONLY ONCE ITS PAGE ANSWERS

⭐ The site's healthcheck asks the published route itself — the course's page
at `/`, on the port it publishes — from inside the container, so `up --wait`
reports the site healthy only once a reader's first request is answered.
⛔ A running process is not an answering site: the server discovers the corpus
and writes the runner's allowlist before it listens.

## ⛔ LOOPBACK ONLY, WRITTEN LITERALLY

⭐ The site's port is published on the editor's own `host_bind` — the
contract's loopback address, which `rulings` refuses anything wider than.
⚠️ **A reader who widens either bind must restore the editor's authentication
first**: the editor is unauthenticated because loopback is its whole access
control, and the reader's document says so.
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from studyforge.execute import instance, published
from studyforge.skills.execution.contract import ContractRefused, blocks, optional, require

#: The compose service the study server is.
SERVICE = "site"

#: The one-shot service that checks the publisher's `instance.env` before the
#: others start (`studyforge preflight`), in the site's profile and image.
PREFLIGHT = "preflight"

#: The editor's compose service, which the site asks for its health by name.
EDITOR_SERVICE = "editor"

#: The internal network only the site and the runner join.
NETWORK = "runs"

#: Where the corpus is inside the site's container.
CORPUS = "/corpus"

#: Where the run service's script is inside the runner.
SCRIPT_INSIDE = "/opt/studyforge/runservice.pl"

#: The run service's script, beside the compose file that mounts it.
SCRIPT_FILE = "runservice.pl"

#: The site image's variable, recorded by the execution skill's site step.
IMAGE = "STUDYFORGE_SITE_IMAGE"

#: The variable that makes the preflight a gate: `true` once an image is staged.
GATED = "STUDYFORGE_PREFLIGHT"

#: The file the corpus's one compose command reads the site's image from, beside it.
SITE_ENV_NAME = "site.env"

#: `SITE_ENV_NAME` before any image is staged: no profile, so no site is brought up.
UNSTAGED = (
    "# No study server image is staged yet, so the compose command brings up the\n"
    "# editor and the runner alone; the execution skill's site step records one.\n"
)

#: The path a quoted URL or path in the editor's health check fetches.
HEALTH_PATH = re.compile(r"['\"](?:https?://[^/'\"\s]+)?(/[^'\"\s]*)['\"]")


@dataclass(frozen=True, slots=True)
class Site:
    """The services and networks the published form adds to the compose file."""

    #: `(service name, mapping)`, the site first, then the runner as the site reaches it.
    services: tuple[tuple[str, Mapping[str, object]], ...]
    #: The compose file's top-level `networks`.
    networks: Mapping[str, Mapping[str, object]]
    #: The `depends_on` every other service carries: the preflight, when it runs.
    gate: Mapping[str, Mapping[str, object]]


#: The route the site's healthcheck asks: the course's own page, which a reader opens first.
HEALTH_ROUTE = "/"


def answered(port: str) -> dict[str, object]:
    """Return the site's healthcheck: healthy only once `HEALTH_ROUTE` answers on `port`."""
    probe = (
        "import urllib.request; "
        f"urllib.request.urlopen('http://127.0.0.1:{port}{HEALTH_ROUTE}', timeout=2)"
    )
    return {
        "test": ["CMD", "python3", "-c", probe],
        "interval": "30s",
        "timeout": "5s",
        "retries": 3,
        "start_period": "60s",
        "start_interval": "1s",
    }


def plan(
    block: Mapping[str, object],
    *,
    source: str,
    sources: str,
    extra: Sequence[tuple[str, str]],
    runner: tuple[str, Mapping[str, object]],
) -> Site:
    """Return the site service and the runner it reaches, for corpus `source`.

    ⭐ The editor's binds — its per-project mount of `sources` and the `extra`
    `(corpus-relative directory, folder inside)` pairs — are what the site hands a
    page as the editor's folders, exactly as the host's probe reads them.
    """
    binds = sorted([*_per_project(block, sources), *extra])
    port = interpolated(instance.SITE_PORT, instance.DEFAULT_SITE_PORT)
    editor_port = interpolated(instance.EDITOR_PORT, _ported(block)["host"])
    bind = str(_ported(block)["host_bind"])
    site: dict[str, object] = {
        # ⭐ Empty until staged: the site is in a profile `SITE_ENV_NAME` turns on
        # with the image, so an unstaged corpus still brings the other two up.
        "image": f"${{{IMAGE}:-}}",
        "profiles": [SERVICE],
        "container_name": interpolated(instance.SITE_NAME, instance.site_container_for(source)),
        str(require(block, "runs_as", "compose_key")): require(block, "runs_as", "compose_value"),
        "command": ["serve", CORPUS, "--published", "--port", port],
        "ports": [f"{bind}:{port}:{port}"],
        "environment": {
            published.EDITOR_ORIGIN: f"http://{bind}:{editor_port}",
            published.EDITOR_BINDS: ";".join(f"{base}={inside}" for base, inside in binds),
            published.EDITOR_HEALTH: health_url(block),
            published.RUN_SERVICE: runner[0],
            "PYTHONDONTWRITEBYTECODE": "1",
        },
        "healthcheck": answered(port),
        "volumes": [f"../..:{CORPUS}"],
        "networks": ["default", NETWORK],
        "restart": require(block, "restart"),
    }
    reached = {key: value for key, value in runner[1].items() if key != "network_mode"}
    reached["command"] = ["perl", SCRIPT_INSIDE]
    reached["volumes"] = [*list(reached.get("volumes", [])), f"./{SCRIPT_FILE}:{SCRIPT_INSIDE}:ro"]
    reached["networks"] = [NETWORK]
    owner = str(require(block, "runs_as", "compose_key"))
    check: dict[str, object] = {
        "image": site["image"],
        "profiles": [SERVICE],
        owner: site[owner],
        "command": ["preflight", CORPUS],
        "volumes": [f"../..:{CORPUS}:ro"],
        "network_mode": "none",
        "restart": require(block, "restart"),
    }
    return Site(
        services=((PREFLIGHT, check), (SERVICE, site), (runner[0], reached)),
        networks={NETWORK: {"internal": True}},
        gate={
            PREFLIGHT: {
                "condition": "service_completed_successfully",
                "required": f"${{{GATED}:-false}}",
            }
        },
    )


def files(directory: str, allowed_ignore: str) -> tuple[tuple[str, str], ...]:
    """Return what the published form needs beside the compose file under `directory`."""
    return (
        (f"{directory}/{SCRIPT_FILE}", published.run_service_script()),
        (f"{published.ALLOWED_DIR}/.gitignore", allowed_ignore),
    )


def interpolated(variable: str, default: object) -> str:
    """Return compose's `${VARIABLE:-default}`."""
    return f"${{{variable}:-{default}}}"


def health_url(block: Mapping[str, object]) -> str:
    """Return the editor's own health URL, asked of the editor's service by name.

    ⭐ The path is the one the contract's health check fetches, and the port the
    editor listens on inside its container; a contract with no health check is
    asked at its root, which answers once the editor is up.
    """
    command = optional(block, "healthcheck", "command", default=[])
    paths = [
        found.group(1)
        for word in (command if isinstance(command, list) else [])
        if (found := HEALTH_PATH.search(str(word)))
    ]
    return f"http://{EDITOR_SERVICE}:{_ported(block)['container']}{(paths or ['/'])[0]}"


def _per_project(block: Mapping[str, object], sources: str) -> list[tuple[str, str]]:
    """Return the editor's per-project bind of `sources`, `(sources, folder inside)`."""
    return [
        (sources, str(require(entry, "container_path")))
        for entry in blocks(block, "mounts")
        if entry.get("per_project") is True and entry.get("kind") == "bind" and sources
    ]


def _ported(block: Mapping[str, object]) -> Mapping[str, object]:
    """Return the editor block's one per-project port entry."""
    for entry in blocks(block, "ports"):
        if entry.get("per_project") is True:
            return entry
    raise ContractRefused("the editor block declares no per-project host port")
