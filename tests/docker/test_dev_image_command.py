"""`studyforge` on the path inside the pinned image, asserted rather than arranged.

⛔ **The property.** The image installs this project, not only
`requirements.txt`, and carries the build backend to install it with — so
`command -v studyforge` answers in the one environment R15 makes authoritative,
and a reading about the INSTALLED command is not host-only.

Two halves, split the way `test_dev_image.py` splits:

**Static — always run.** The Dockerfile's installs, read one COMMAND at a time
(`commands()`): this project is installed EDITABLE against `/workspace`,
offline, by a backend pinned by version and hash that is removed afterwards, and
only the declaration crosses from the checkout.

**In the image — a skip on a host, a failure in the image.** The command is on
PATH and dispatches (exit codes read), what it runs is imported from the MOUNT,
its entry point is the MOUNTED declaration, and no backend survives. ⛔ Those are
the property; the static half is only the shape that produces it.
"""

from __future__ import annotations

import importlib.metadata
import importlib.util
import os
import re
import shutil
import subprocess
import tomllib
from pathlib import Path

import pytest

from studyforge.cli import PROGRAM
from studyforge.validate.cli import UNUSABLE
from tests.docker.devfiles import commands, instructions
from tests.support import repository_root

#: Set inside the image by the Dockerfile (see `test_dev_image.py`).
MARKER = "STUDYFORGE_DEV_CONTAINER"

#: The three installs the Dockerfile declares, each by the flags that identify it.
#: ⛔ Every flag of a role must sit in ONE command; a flag on a neighbour does not count.
ROLES: dict[str, tuple[str, ...]] = {
    "tools": ("--requirement /opt/studyforge/requirements.txt",),
    "backend": ("--require-hashes", "--no-deps", "--requirement /tmp/backend.txt"),
    "project": ("--editable /workspace", "--no-index", "--no-build-isolation", "--no-deps"),
}

#: What may cross from the checkout into the build, and nothing else.
DECLARATION = {"pyproject.toml", "README.md"}


def dockerfile() -> list[str]:
    """`docker/dev/Dockerfile`, one shell command or instruction per element."""
    return [" ".join(command.split()) for command in commands("Dockerfile")]


def has(command: str, flag: str) -> bool:
    """Is `flag` in `command` as whole tokens (so `/workspace` is not `/workspace/x`)?"""
    return f" {flag} " in f" {command} "


def classify(installs: list[str]) -> dict[str | None, list[str]]:
    """Each `pip install` under the one role it matches; `None` for none or several."""
    found: dict[str | None, list[str]] = {role: [] for role in ROLES} | {None: []}
    for command in installs:
        roles = [role for role, flags in ROLES.items() if all(has(command, f) for f in flags)]
        found[roles[0] if len(roles) == 1 else None].append(command)
    return found


def install_problems(steps: list[str]) -> list[str]:
    """What is wrong with the installs in `steps`, empty when nothing is."""
    found = classify([step for step in steps if "pip install" in step])
    problems = [f"no `pip install` is the {role} install" for role in ROLES if not found[role]]
    problems += [f"{role} is installed more than once" for role in ROLES if len(found[role]) > 1]
    problems += [f"an install this image does not declare: {c}" for c in found[None]]
    return problems


def crossing(steps: list[str]) -> set[str]:
    """Every file bind-mounted from the `project` build context."""
    text = " ".join(steps)
    if re.search(r"from=(?!project,)", text):
        return {"<a build context other than `project`>"}
    return set(re.findall(r"from=project,source=([^,\s]+),target=/workspace/\1\b", text))


def pinned(steps: list[str], name: str) -> str | None:
    """The default of `ARG <name>=...`, or None."""
    for step in steps:
        match = re.fullmatch(rf"ARG {name}=(\S+)", step)
        if match:
            return match.group(1)
    return None


# --- static: the shape that produces the property ---------------------------


def test_the_project_is_installed_once_editable_against_the_mount_and_offline():
    assert install_problems(dockerfile()) == []


def test_the_install_check_can_say_no():
    steps = dockerfile()
    assert install_problems([*steps, "pip install ."]), "a second install read as healthy"
    unplugged = [s.replace("--no-index", "") for s in steps]
    assert install_problems(unplugged), "an install that may fetch read as offline"
    copied = [s.replace("--editable /workspace", "/workspace") for s in steps]
    assert install_problems(copied), "a non-editable install (a COPY) read as editable"


def test_only_the_declaration_crosses_from_the_checkout():
    assert crossing(dockerfile()) == DECLARATION
    assert "project: ../.." in instructions("compose.yaml")
    widened = [*dockerfile(), "--mount=type=bind,from=project,source=src,target=/workspace/src"]
    assert crossing(widened) != DECLARATION, "the check cannot see the source crossing"


def test_the_build_backend_is_pinned_by_version_and_hash_and_satisfies_the_declaration():
    steps = dockerfile()
    version, digest = pinned(steps, "SETUPTOOLS_VERSION"), pinned(steps, "SETUPTOOLS_SHA256")
    assert version and re.fullmatch(r"\d+(\.\d+)*", version), version
    assert digest and re.fullmatch(r"[0-9a-f]{64}", digest), digest
    printf = [s for s in steps if "${SETUPTOOLS_VERSION}" in s and "${SETUPTOOLS_SHA256}" in s]
    assert printf and "--hash=sha256:" in printf[0], printf
    system = tomllib.loads((repository_root() / "pyproject.toml").read_text("utf-8"))
    assert system["build-system"]["build-backend"] == "setuptools.build_meta"
    floors = [r.split(">=")[1] for r in system["build-system"]["requires"] if ">=" in r]
    assert len(floors) == 1, system["build-system"]["requires"]
    as_ints = [tuple(int(part) for part in v.split(".")) for v in (version, floors[0])]
    assert as_ints[0] >= as_ints[1], f"pinned {version} is below the declared >={floors[0]}"


def test_the_build_backend_is_removed_after_the_project_install():
    steps = dockerfile()
    project = classify([s for s in steps if "pip install" in s])["project"]
    assert project and "pip uninstall -y setuptools" in steps
    assert steps.index("pip uninstall -y setuptools") > steps.index(project[0])


# --- in the image: the property itself --------------------------------------


def require_the_image() -> None:
    """Skip on a host; only the pinned image can answer these."""
    if not os.environ.get(MARKER):
        pytest.skip(
            "not inside the dev image. The static checks above assert the Dockerfile "
            "installs the command; only a run inside the image can assert it arrived."
        )


def isolated(argv: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    """Run `argv` outside the checkout, with no `PYTHONPATH` to find the source by."""
    env = {key: value for key, value in os.environ.items() if key != "PYTHONPATH"}
    return subprocess.run(  # noqa: S603 - fixed argv, no shell
        argv, cwd=cwd, env=env, capture_output=True, text=True, check=False, timeout=120
    )


def test_the_installed_command_is_on_the_path_and_dispatches(tmp_path):
    require_the_image()
    command = shutil.which(PROGRAM)
    assert command, f"`{PROGRAM}` is not on PATH inside the dev image"
    helped = isolated([command, "--help"], tmp_path)
    assert helped.returncode == 0, helped.stdout + helped.stderr
    assert helped.stdout.startswith(f"usage: {PROGRAM} "), helped.stdout
    # ⭐ A MOVED code: 2 is the dispatcher's own answer to no verb, and a missing
    # interpreter, module or script would answer 127 or 1 instead.
    assert isolated([command], tmp_path).returncode == UNUSABLE


def test_the_installed_command_runs_the_mounted_checkout(tmp_path):
    require_the_image()
    command = shutil.which(PROGRAM)
    assert command, f"`{PROGRAM}` is not on PATH inside the dev image"
    interpreter = Path(command).read_text("utf-8").partition("\n")[0].removeprefix("#!")
    # ⛔ The SCRIPT's own import line, executed without calling `main`, then asked
    # where the object it would call came from.
    probe = (
        "import sys; namespace = {'__name__': 'w211_probe'}; "
        f"exec(compile(open({command!r}).read(), {command!r}, 'exec'), namespace); "
        "print(sys.modules[namespace['main'].__module__].__file__)"
    )
    result = isolated([interpreter, "-c", probe], tmp_path)
    assert result.returncode == 0, result.stdout + result.stderr
    origin = Path(result.stdout.strip())
    assert origin.is_relative_to(repository_root() / "src"), origin
    files = importlib.metadata.distribution(PROGRAM).files or []
    copies = [str(f) for f in files if str(f).startswith(f"{PROGRAM}/")]
    assert copies == [], f"site-packages holds a copy of the source: {copies}"


def test_the_installed_entry_point_is_the_mounted_declaration():
    require_the_image()
    declared = tomllib.loads((repository_root() / "pyproject.toml").read_text("utf-8"))
    installed = importlib.metadata.distribution(PROGRAM)
    scripts = {e.name: e.value for e in installed.entry_points if e.group == "console_scripts"}
    assert scripts == declared["project"]["scripts"], (
        "the image was built from another pyproject.toml; rebuild it (docker/dev/check does)"
    )
    assert installed.version == declared["project"]["version"]


def test_no_build_backend_survives_into_the_image():
    require_the_image()
    assert importlib.util.find_spec("setuptools") is None, (
        "setuptools is importable in the dev image, so an offline `pip install -e .` "
        "into the mounted checkout would succeed and write into it"
    )
