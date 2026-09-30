r"""A standalone course's two compose files: one builds and runs it, one only pulls and runs it.

**What it does.** Renders `compose.yaml`, which builds every image from the
learner's own checkout and starts the site, the runner and the editor, and
`compose.pull.yaml`, which starts the same three services from published
images and builds nothing. ⭐ **Both run the same services the same way**: the
course's material is baked into the images, and what a learner changes —
their practices, the copy of the code the editor opens, their progress, the
editor's own state — lives in named volumes, never in a bind of a host path.

**How you use it.**

    built, pulled = render(plan)          # two texts
    problems = findings(text)             # empty, or the rulings a text breaks

`Plan` carries the names, the toolchain's builds and the editor's contract.

**Depends on.** `composefile` for the editor's service, rendered from the
toolchain's contract as the execution skill renders it; `rulings` for the bind
rules every compose file this framework writes keeps; `emit` for the YAML;
`execute.published` for what the published server reads from its environment.

## ⛔ The rules a learner's compose file keeps

- ⛔ **Every port on loopback**, written literally: the editor is an
  unauthenticated IDE with a shell, and loopback is its whole access control.
- ⛔ **No host path is bound**, relative or absolute, and no host temp
  directory: a named volume is the only store, so the file runs from any
  directory on any engine, Docker Desktop and Windows included.
- ⛔ **No Docker socket**, anywhere (spec §8.3).
- ⭐ **Every service runs as `1000:1000`**, the uid the images own their
  volumes' seeds as: no host directory is bound, so no host uid is asked.
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from studyforge.corpus.placement import PRACTICE_DIRNAME
from studyforge.execute import CODE_COPY, labels, published
from studyforge.skills.execution import rulings
from studyforge.skills.execution.composefile import interpolated, service, volumes_for
from studyforge.skills.execution.contract import optional, require
from studyforge.skills.execution.emit import emit
from studyforge.skills.execution.siteservice import CORPUS, NETWORK, answered, health_url
from studyforge.skills.execution.standalone.bases import Bases
from studyforge.skills.execution.standalone.images import (
    NAMESPACE_DEFAULT,
    NAMESPACE_VARIABLE,
    NARRATION_VARIABLE,
    NARRATIONS,
    PROGRESS,
    RUNS_AS,
    WORK,
    Names,
    qualified,
)

#: Where each build file studyforge writes lives, relative to the course root.
IMAGES = ".studyforge/images"
TOOLCHAIN = f"{IMAGES}/toolchain"
NO_PRIME = f"{TOOLCHAIN}/no-prime"
PRIME = ".studyforge/execution/prime"

#: The variables a learner sets, and the compose project's own.
PROJECT_VARIABLE = "COURSE_PROJECT"
SITE_PORT_VARIABLE = "COURSE_SITE_PORT"
EDITOR_PORT_VARIABLE = "COURSE_EDITOR_PORT"

#: ⛔ What the pull file says when no account is set: it names the variable and what it holds.
NAMESPACE_REQUIRED = (
    f"{NAMESPACE_VARIABLE} is not set. It is the Docker Hub account the course images are "
    "published under: set it in .env (copy course.env) to the account you were given"
)

#: The server's own state, which only it reads and writes.
ALLOWED = ".studyforge/execution/allowed"

#: The named contexts a build reads another service's image through.
NAMED = {
    "serve-base": "studyforge-serve-base",
    "runner-base": "studyforge-runner-base",
    "editor-base": "studyforge-editor-base",
    "runner-prime": "course-runner-prime",
}


@dataclass(frozen=True, slots=True)
class Plan:
    """Everything the two files are rendered from."""

    slug: str
    names: Names
    builds: Mapping[str, Mapping[str, object]]
    editor: Mapping[str, object]
    runtimes: tuple[str, ...]
    #: `(corpus-relative directory, where the editor opens it)`, sources first.
    binds: tuple[tuple[str, str], ...]
    site_port: int
    editor_port: int
    #: ⭐ Thin: the published bases, by tag and digest. With none, every base is built here.
    bases: Bases | None = None


def volume_of(directory: str) -> str:
    """Return the named volume a corpus-relative directory the editor opens lives in."""
    if directory == CODE_COPY:
        return "code"
    if directory == PRACTICE_DIRNAME:
        return "practice"
    return "sources"


def render(plan: Plan) -> tuple[str, str]:
    """Return `compose.yaml` and `compose.pull.yaml`, each refused if it breaks a rule."""
    run = _running(plan)
    built = _thin(plan, run) if plan.bases else _whole(plan, run)
    texts = []
    for services in (built, run):
        document = {
            "name": interpolated(PROJECT_VARIABLE, plan.slug),
            "services": services,
            "networks": {NETWORK: {"internal": True}},
            "volumes": {name: {} for name in _volumes(services)},
        }
        text = emit(document)
        # ⛔ the pull file has no default account: an unset one stops here. ⛔ Nor has a thin
        # build file, which pulls its bases from that account.
        if services is run or plan.bases:
            text = text.replace(
                f"${{{NAMESPACE_VARIABLE}:-{NAMESPACE_DEFAULT}}}",
                f"${{{NAMESPACE_VARIABLE}:?{NAMESPACE_REQUIRED}}}",
            )
        problems = findings(text, services)
        if problems:
            raise rulings_refused(problems)
        texts.append(text)
    return texts[0], texts[1]


def _whole(plan: Plan, run: Mapping[str, dict[str, object]]) -> dict[str, dict[str, object]]:
    """Return the build file's services when every base is built from this tree."""
    return {
        "serve-base": _base(plan.names.serve, {"context": f"{IMAGES}/serve"}),
        "runner-base": _base(
            plan.names.runner_base, _toolchain(plan.builds["runner"], NO_PRIME, ())
        ),
        "editor-base": _base(
            plan.names.editor_base, _toolchain(plan.builds["editor"], NO_PRIME, ("runner-base",))
        ),
        "runner-prime": {
            "build": _toolchain(plan.builds["runner-prime"], PRIME, ("runner-base",)),
            "scale": 0,
        },
        "site": {"build": _site(), **run["site"]},
        "runner": {"build": _runner(), **run["runner"]},
        "editor": {
            "build": _toolchain(plan.builds["editor-prime"], PRIME, ("editor-base",)),
            **run["editor"],
        },
    }


def _thin(plan: Plan, run: Mapping[str, dict[str, object]]) -> dict[str, dict[str, object]]:
    """Return the build file's services when the bases are published: no base is built.

    ⭐ The course's runner and editor warm their dependencies on the published base the
    lock names, by tag and digest, through the toolchain's course layer; the site's own
    recipe starts from the published serving base and takes the account as a build argument.
    """
    pinned = {
        "runner": qualified(plan.names.runner_base),
        "editor": qualified(plan.names.editor_base),
    }
    return {
        "runner-prime": {
            "build": _toolchain(plan.builds["runner-prime"], PRIME, (), pinned),
            "scale": 0,
        },
        "site": {"build": _site(thin=True), **run["site"]},
        "runner": {"build": _runner(), **run["runner"]},
        "editor": {
            "build": _toolchain(plan.builds["editor-prime"], PRIME, (), pinned),
            **run["editor"],
        },
    }


def findings(text: str, services: Mapping[str, object]) -> list[str]:
    """Every rule a rendered file breaks: a socket, a host bind, a port off loopback."""
    found = list(rulings.bind_findings(services))
    if rulings.names_a_socket(text):
        found.append("the file names the Docker socket; §8.3 mounts none")
    for name, one in services.items():
        entries = one.get("volumes", []) if isinstance(one, Mapping) else []
        for entry in entries:
            if str(entry).split(":", 1)[0].startswith((".", "/", "~", "$")):
                found.append(f"the {name} service binds a host path; only named volumes are used")
        for port in one.get("ports", []) if isinstance(one, Mapping) else []:
            if not str(port).startswith("127.0.0.1:"):
                found.append(f"the {name} service publishes {port} off loopback")
    return found


def rulings_refused(problems: Sequence[str]) -> ValueError:
    """Return the refusal a file that breaks a rule is answered with."""
    return ValueError("the rendered compose file breaks a rule: " + "; ".join(problems))


def _running(plan: Plan) -> dict[str, dict[str, object]]:
    """Return the three services as a learner runs them, identical in both files."""
    site_port = interpolated(SITE_PORT_VARIABLE, plan.site_port)
    editor_port = interpolated(EDITOR_PORT_VARIABLE, plan.editor_port)
    shared = [f"{volume_of(directory)}:{{root}}/{directory}" for directory, _ in plan.binds]
    healthy = {"site": {"condition": "service_healthy"}}
    site = {
        "image": qualified(plan.names.site),
        "user": RUNS_AS,
        "command": ["serve", CORPUS, "--published", "--port", site_port],
        "ports": [f"127.0.0.1:{site_port}:{site_port}"],
        "environment": {
            published.EDITOR_ORIGIN: f"http://127.0.0.1:{editor_port}",
            published.EDITOR_BINDS: ";".join(f"{one}={inside}" for one, inside in plan.binds),
            published.EDITOR_HEALTH: health_url(plan.editor),
            published.RUN_SERVICE: "runner",
            "PYTHONDONTWRITEBYTECODE": "1",
        },
        "healthcheck": answered(site_port),
        "volumes": [
            *(one.format(root=CORPUS) for one in shared),
            f"allowed:{CORPUS}/{ALLOWED}",
            f"progress:{CORPUS}/{PROGRESS}",
        ],
        "networks": ["default", NETWORK],
        "restart": "no",
    }
    runner = {
        "image": qualified(plan.names.runner),
        "user": RUNS_AS,
        "init": True,
        "volumes": [*(one.format(root=WORK) for one in shared), f"allowed:{WORK}/{ALLOWED}:ro"],
        "labels": {labels.BINDS: labels.binds_text([("", WORK)])},
        "networks": [NETWORK],
        "depends_on": healthy,
        "restart": "no",
    }
    sources, *extra = plan.binds
    editor = dict(
        service(
            plan.editor,
            name="editor",
            image=qualified(plan.names.editor),
            sources=volume_of(sources[0]),
            volumes=volumes_for(optional(plan.editor, "prime", "seeds"), plan.runtimes),
            binds=[(volume_of(directory), inside) for directory, inside in extra],
            port_variable=EDITOR_PORT_VARIABLE,
            labels={labels.BINDS: labels.binds_text(plan.binds)},
        )
    )
    editor[str(require(plan.editor, "runs_as", "compose_key"))] = RUNS_AS
    editor["ports"] = [_port(one, plan.editor_port) for one in editor["ports"]]
    editor["depends_on"] = healthy
    return {"site": site, "runner": runner, "editor": editor}


def _port(published_port: str, default: int) -> str:
    """Return the editor's port, with the learner's default where the contract's stood."""
    return re.sub(r"\$\{(\w+):-\d+\}", lambda m: f"${{{m.group(1)}:-{default}}}", published_port)


def _volumes(services: Mapping[str, object]) -> list[str]:
    """Every named volume the services mount, read off their own entries."""
    return sorted(
        {
            str(entry).split(":", 1)[0]
            for one in services.values()
            for entry in (one.get("volumes", []) if isinstance(one, Mapping) else [])
        }
    )


def _base(image: str, build: Mapping[str, object]) -> dict[str, object]:
    """Return a shared base: built, tagged under the namespace, and never started."""
    return {"image": qualified(image), "build": dict(build), "scale": 0}


def _toolchain(
    build: Mapping[str, object],
    prime: str,
    bases: Sequence[str],
    pinned: Mapping[str, str] | None = None,
) -> dict[str, object]:
    """Return a toolchain build, as its own data says, its bases read through named contexts.

    ⭐ With `pinned` (a thin file) a base the build starts from is the published reference
    named there, passed as the build argument: it is pulled, so no context carries it.
    """
    here = dict(build["built_here"])  # type: ignore[arg-type]
    args = {key: _literal(str(value)) for key, value in build["args"].items()}
    contexts = {"consumer-prime": prime}
    for arg, which in here.items():
        if pinned is not None:
            args[arg] = pinned[which]
            continue
        base = f"{which}-base"
        if base not in bases:  # pragma: no cover - the four builds name only these
            raise ValueError(
                f"a toolchain build starts from {which}, which this file does not build"
            )
        args[arg] = NAMED[base]
        contexts[NAMED[base]] = f"service:{base}"
    return {
        "context": TOOLCHAIN,
        "dockerfile": str(build["dockerfile"]),
        "target": str(build["target"]),
        "args": args,
        "additional_contexts": contexts,
    }


def _site(*, thin: bool = False) -> dict[str, object]:
    """Return the course's site: the course root as context, on the serving base.

    ⭐ A thin site's recipe names its base itself; the build is handed only the account.
    """
    if thin:
        return {
            "context": ".",
            "dockerfile": f"{IMAGES}/site/Dockerfile",
            "target": interpolated(NARRATION_VARIABLE, NARRATIONS[0]),
            "args": {NAMESPACE_VARIABLE: f"${{{NAMESPACE_VARIABLE}:-{NAMESPACE_DEFAULT}}}"},
        }
    return {
        "context": ".",
        "dockerfile": f"{IMAGES}/site/Dockerfile",
        "target": interpolated(NARRATION_VARIABLE, NARRATIONS[0]),
        "args": {"SERVE_BASE": NAMED["serve-base"]},
        "additional_contexts": {NAMED["serve-base"]: "service:serve-base"},
    }


def _runner() -> dict[str, object]:
    """Return the course's runner: its primed layer and the run service."""
    return {
        "context": ".",
        "dockerfile": f"{IMAGES}/runner/Dockerfile",
        "args": {"RUNNER_PRIMED": NAMED["runner-prime"]},
        "additional_contexts": {NAMED["runner-prime"]: "service:runner-prime"},
    }


def _literal(value: str) -> str:
    """Return a build argument compose passes as written: every `$` doubled, none interpolated."""
    return value.replace("$", "$$")
