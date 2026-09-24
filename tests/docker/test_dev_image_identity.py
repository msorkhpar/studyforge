"""The image a `check` run executes is named by its build inputs' CONTENT.

⛔ **The defect.** `compose.yaml` named ONE tag, `studyforge/dev:local`, for every
checkout, and `check`'s `run --build` rewrote it from whichever checkout ran last.
Two checkouts running `check` at once could therefore start a container from each
other's image (measured racing, twice), and the guard offices used —
`command -v studyforge` — tells an image without the installed command from one with
it and nothing else.

⭐ **The repair, in `check`'s own block:** a sha256 over every build input's content
is exported as `STUDYFORGE_DEV_IDENTITY`, `compose.yaml`'s `image:` REQUIRES it, and
every run prints the name it runs. Inputs that differ name different tags, so no
build can overwrite what another checkout is about to run.

**Static — always run.** Each predicate reads TEXT, and each is fed a doctored copy
that must make it say no.

**The plant — opt-in** (`STUDYFORGE_DOCKER_TESTS=1`, `test_dev_image.py`'s reasons).
Two scratch checkouts differ in one input. A docker client on `PATH` OPENS THE RACE
WINDOW ON PURPOSE: between the first checkout's build and its container start, the
second checkout's whole `check` runs. ⛔ Each run must still read its own input —
and with the fixed shared tag restored, the first reads the second's (a moved exit).
⚠️ The scratch checkouts build under a throwaway repository, never `studyforge/dev`,
so the plant cannot touch a tag a live office runs; the images are removed after.
"""

from __future__ import annotations

import os
import shutil
import tomllib
import uuid
from pathlib import Path

import pytest

from tests.docker.devfiles import DEV, instructions, read
from tests.docker.devgate import announced_image, announced_images, require_docker_run
from tests.docker.test_dev_image_command import crossing, dockerfile
from tests.docker.test_dev_provenance import joined
from tests.support import repository_root, run

#: The variable `check` derives and `compose.yaml` requires.
VARIABLE = "STUDYFORGE_DEV_IDENTITY"

#: The repository and tag prefix both files name. ⛔ Asserted to AGREE, because
#: `check` prints what `compose.yaml` resolves and a disagreement is a false print.
NAME = "studyforge/dev:inputs-"

#: The shared tag this row retired. ⛔ No instruction in `docker/dev/` may name it.
SHARED = "studyforge/dev:local"

#: The hand build the Dockerfile's FIRST sentence must carry.
HAND_BUILD = "docker build --build-context project=. docker/dev"


# --- the predicates, each one fed a doctored copy below ---------------------


def image_declarations(compose: str) -> list[str]:
    """Every `image:` value in `compose.yaml` text, a file with no continuations."""
    return [
        line.strip().removeprefix("image:").strip()
        for line in compose.splitlines()
        if line.strip().startswith("image:")
    ]


def named_by_identity(compose: str) -> bool:
    """Is the one image named by the REQUIRED identity, with no fallback?"""
    values = image_declarations(compose)
    return len(values) == 1 and values[0].startswith(f'"{NAME}${{{VARIABLE}:?')


def check_lines(script: str) -> list[str]:
    """`check`, one LOGICAL line per element, whitespace normalised."""
    return [" ".join(line.split()) for line in joined(script).splitlines()]


def hashed_inputs(script: str) -> set[str] | None:
    """The checkout files `check` hashes beside the build context, or None."""
    values = [line.split("=", 1)[1] for line in check_lines(script) if line.startswith("INPUTS=")]
    return set(values[0].strip('"').split()) if len(values) == 1 else None


def hashes_the_build_context(script: str) -> bool:
    """Does the identity cover every file of the build context, read-only and by
    relative name?"""
    derivations = [
        line for line in check_lines(script) if line.startswith(f"{VARIABLE}=$(docker run ")
    ]
    return len(derivations) == 1 and all(
        part in derivations[0]
        for part in (
            '--volume "$ROOT:/inputs:ro"',
            "--workdir /inputs",
            "find docker/dev -type f | LC_ALL=C sort",
            "--network none",
        )
    )


def derived_before_compose(script: str) -> bool:
    """Derived, exported, then Compose — with no caller override anywhere."""
    lines = check_lines(script)
    derived = [i for i, line in enumerate(lines) if line.startswith(f"{VARIABLE}=$(")]
    exported = [i for i, line in enumerate(lines) if line == f"export {VARIABLE}"]
    compose = [i for i, line in enumerate(lines) if "docker compose" in line]
    return (
        len(derived) == 1
        and len(exported) == 1
        and len(compose) == 1
        and derived[0] < exported[0] < compose[0]
        and f"${{{VARIABLE}:-" not in script
    )


def announcements(script: str) -> list[str]:
    """The lines that print the image to stderr before Compose runs."""
    lines = check_lines(script)
    compose = min((i for i, line in enumerate(lines) if "docker compose" in line), default=-1)
    return [
        line
        for line in lines[:compose]
        if line.startswith("echo ") and line.endswith(">&2") and f"{NAME}${VARIABLE}" in line
    ]


def first_sentence(dockerfile_text: str) -> str:
    """The Dockerfile's opening comment paragraph, as one line of prose."""
    paragraph = dockerfile_text.split("\n#\n", 1)[0]
    return " ".join(paragraph.replace("#", " ").split())


# --- static: the shape, each with its control -------------------------------


def test_compose_names_the_image_by_the_required_identity():
    assert named_by_identity(read("compose.yaml")), image_declarations(read("compose.yaml"))


def test_the_naming_check_can_say_no():
    compose = read("compose.yaml")
    [declared] = image_declarations(compose)
    assert not named_by_identity(compose.replace(declared, SHARED)), "the shared tag read as named"
    fallback = declared.replace(f"{VARIABLE}:?", f"{VARIABLE}:-")
    assert fallback != declared, "the control's subject is absent"
    assert not named_by_identity(compose.replace(declared, fallback)), "a fallback read as required"


def test_no_instruction_in_docker_dev_names_the_shared_tag():
    for name in ("Dockerfile", "compose.yaml", "check"):
        assert SHARED not in instructions(name), f"{DEV}/{name} still names {SHARED}"


def test_the_identity_is_derived_exported_and_unconditional_before_compose():
    assert derived_before_compose(instructions("check"))


def test_the_derivation_check_can_say_no():
    script = instructions("check")
    assert f"export {VARIABLE}" in script, "the control's subject is absent"
    late = script.replace(f"export {VARIABLE}\n", "") + f"\nexport {VARIABLE}\n"
    assert not derived_before_compose(late), "an export after the exec read as effective"
    assert not derived_before_compose(script + f"\n: ${{{VARIABLE}:-x}}\n"), (
        "an override read as none"
    )


def test_the_whole_build_context_is_hashed_by_relative_name():
    assert "context: ." in instructions("compose.yaml"), (
        "the build context moved; re-derive the hash"
    )
    assert hashes_the_build_context(instructions("check"))


def test_the_context_check_can_say_no():
    script = instructions("check")
    narrowed = script.replace("find docker/dev -type f", "find docker/dev -name Dockerfile")
    assert narrowed != script, "the control's subject is absent"
    assert not hashes_the_build_context(narrowed), "a partial context read as whole"


def test_the_hashed_checkout_files_are_what_the_dockerfile_takes_from_the_checkout():
    # ⛔ A CHECKED copy: a file the Dockerfile mounts from `project` and the hash
    # omits is an input two checkouts can differ in while naming one tag.
    assert hashed_inputs(instructions("check")) == crossing(dockerfile())


def test_the_inputs_check_can_say_no():
    script = instructions("check")
    widened = [
        *dockerfile(),
        "--mount=type=bind,from=project,source=LICENSE,target=/workspace/LICENSE",
    ]
    assert hashed_inputs(script) != crossing(widened), "a new crossing file read as hashed"
    narrowed = script.replace('INPUTS="pyproject.toml README.md"', 'INPUTS="pyproject.toml"')
    assert narrowed != script, "the control's subject is absent"
    assert hashed_inputs(narrowed) != crossing(dockerfile()), "a dropped input read as hashed"


def test_every_run_prints_the_image_it_runs_and_the_name_agrees_with_compose():
    [line] = announcements(instructions("check"))
    assert "$ROOT" not in line, "the print carries the checkout path (R7)"
    assert named_by_identity(read("compose.yaml")), "the printed name is not the resolved one"


def test_the_print_check_can_say_no():
    script = instructions("check")
    [line] = announcements(script)
    assert announcements(script.replace(line, ":")) == [], "a removed print read as present"
    assert announcements(script.replace(" >&2", "")) == [], "a stdout print read as stderr"


def test_the_dockerfile_s_first_sentence_says_how_to_build_it_by_hand():
    assert HAND_BUILD in first_sentence(read("Dockerfile")), first_sentence(read("Dockerfile"))


def test_the_first_sentence_check_can_say_no():
    text = read("Dockerfile")
    moved = text.split("\n#\n", 1)[1]
    assert HAND_BUILD not in first_sentence(moved), "a later paragraph read as the first"


# --- the plant: the race window opened on purpose ---------------------------

#: A docker client that runs the OTHER checkout's whole `check` between this
#: checkout's build and its container start — the window Compose leaves inside
#: `run --build`. ⛔ It carries no path: every location arrives by environment.
RACING_CLIENT = """#!/usr/bin/env python3
import os, subprocess, sys
real, args = os.environ["W225_REAL_DOCKER"], sys.argv[1:]
if args[:1] == ["compose"] and "run" in args and "--build" in args:
    quiet = {"stdout": sys.stderr, "stdin": subprocess.DEVNULL, "check": True}
    subprocess.run([real, *args[: args.index("run")], "build", "dev"], **quiet)
    other = {k: v for k, v in os.environ.items() if k != "STUDYFORGE_DEV_IDENTITY"}
    other["PATH"] = os.environ["W225_PATH"]
    subprocess.run([os.environ["W225_OTHER_CHECK"], "true"], env=other, **quiet)
    args = [arg for arg in args if arg != "--build"]
os.execv(real, [real, *args])
"""

#: Which input differs, how, and the command that reads it back from the image.
PROBES = {
    "Dockerfile": ["printenv", "STUDYFORGE_W225_PROBE"],
    "pyproject.toml": [
        "python3",
        "-c",
        "import importlib.metadata as m; print(m.version('studyforge'))",
    ],
}


def differ(root: Path, differing: str, mark: str) -> str:
    """Make `root`'s copy of one input unique to `mark`; return what the probe reads."""
    if differing == "Dockerfile":
        path = root / DEV / "Dockerfile"
        path.write_text(path.read_text("utf-8") + f"ENV STUDYFORGE_W225_PROBE={mark}\n", "utf-8")
        return mark
    path = root / "pyproject.toml"
    text = path.read_text("utf-8")
    version = tomllib.loads(text)["project"]["version"]
    assert text.count(f'version = "{version}"') == 1, "the version line is not unique"
    path.write_text(
        text.replace(f'version = "{version}"', f'version = "{version}+w225{mark}"'), "utf-8"
    )
    return f"{version}+w225{mark}"


def checkout(root: Path, repository: str, differing: str, mark: str) -> str:
    """A scratch checkout holding every build input, under a throwaway repository."""
    shutil.copytree(repository_root() / DEV, root / DEV)
    for name in hashed_inputs(instructions("check")) or ():
        shutil.copy2(repository_root() / name, root / name)
    for name in ("check", "compose.yaml"):
        path = root / DEV / name
        text = path.read_text("utf-8")
        assert "studyforge/dev:" in instructions(name), (
            f"{name} names no image; nothing to redirect"
        )
        path.write_text(text.replace("studyforge/dev:", f"{repository}:"), "utf-8")
    return differ(root, differing, mark)


def last_line(output: str) -> str:
    return output.strip().rpartition("\n")[2]


@pytest.mark.parametrize("differing", sorted(PROBES))
def test_two_checkouts_with_different_inputs_each_run_their_own_image(tmp_path, differing):
    docker = require_docker_run(builds_fresh=True)
    repository = f"studyforge-test/w225-{uuid.uuid4().hex[:12]}"
    try:
        first, second = tmp_path / "first", tmp_path / "second"
        expected = [
            checkout(first, repository, differing, "a"),
            checkout(second, repository, differing, "b"),
        ]
        client = tmp_path / "client"
        client.mkdir()
        (client / "docker").write_text(RACING_CLIENT, "utf-8")
        (client / "docker").chmod(0o755)
        path = os.environ["PATH"]
        racing = [
            "env",
            f"PATH={client}{os.pathsep}{path}",
            f"W225_PATH={path}",
            f"W225_REAL_DOCKER={docker}",
            f"W225_OTHER_CHECK={second / DEV / 'check'}",
        ]
        raced = run([*racing, f"./{DEV}/check", *PROBES[differing]], cwd=first)
        alone = run([f"./{DEV}/check", *PROBES[differing]], cwd=second)
        scrub = str(tmp_path)
        for result in (raced, alone):
            assert result.returncode == 0, result.stderr[-2000:].replace(scrub, "<tmp>")
        # ⛔ The window really opened, or the readings below are vacuous: the raced
        # run's stderr names its OWN image first and then the other checkout's.
        own, other = announced_images(raced.stderr), announced_image(alone.stderr)
        assert len(own) == 2 and own[1] == other != own[0], (
            f"the other checkout's check did not run inside the window: {own} / {other}"
        )
        readings = [last_line(raced.stdout), last_line(alone.stdout)]
        assert readings == expected, (
            f"the {differing} each checkout ran is not its own: read {readings}, "
            f"declared {expected} — a build from the other checkout replaced the image "
            f"between this one's build and its run"
        )
    finally:
        listed = run(
            [docker, "image", "ls", "--format", "{{.Repository}}:{{.Tag}}", repository],
            cwd=tmp_path,
        )
        tags = listed.stdout.split()
        if tags:
            run([docker, "image", "rm", *tags], cwd=tmp_path)
