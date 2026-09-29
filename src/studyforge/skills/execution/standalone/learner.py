r"""What a learner reads first: the README of a standalone course, and its settings file.

**What it does.** Writes the learner's `README.md` — what the course is, what
it needs, the one command that starts it, its ports, how to study and practise,
and how to get narration — and `course.env`, every setting a learner may
change, with its default.

**How you use it.** `readme(course)` and `settings(course)`, each a text, for a
`Course` naming the title, the project, the two ports and the images' namespace.

**Depends on.** `compose` and `images` for the variables and the file names it
cites, so the README never names a variable the compose files do not read.

## ⛔ What the README never says

⭐ **It is a learner's document.** ⛔ It says nothing about ingestion, the
archive, the skills or how the pages were made, except one line pointing to the
branch that holds that. ⛔ It names no account, no host and no path of the
machine that wrote it: the namespace is a placeholder until a publisher sets it.
"""

from __future__ import annotations

from dataclasses import dataclass

from studyforge.exercise.bundle.layout import BUNDLES_DIRNAME
from studyforge.skills.execution.standalone.compose import (
    EDITOR_PORT_VARIABLE,
    PROJECT_VARIABLE,
    SITE_PORT_VARIABLE,
)
from studyforge.skills.execution.standalone.images import (
    NAMESPACE_VARIABLE,
    NARRATION_VARIABLE,
    NARRATIONS,
)

#: The branch that keeps everything the build left behind.
BUILD_BRANCH = "studyforge/build"

#: The file a learner copies to `.env` to change a setting.
SETTINGS = "course.env"

#: The narration restore scripts, as the course carries them.
RESTORE_SH = ".studyforge/narration-release/restore.sh"
RESTORE_PS1 = ".studyforge/narration-release/restore.ps1"


@dataclass(frozen=True, slots=True)
class Course:
    """The few facts a learner's documents state."""

    title: str
    project: str
    site_port: int
    editor_port: int
    namespace: str
    narrated: bool
    exercises: bool = False


def settings(course: Course) -> str:
    """`course.env`: every variable either compose file reads, at its default."""
    lines = [
        "# The course's settings, each at its default. Compose reads a file named .env",
        "# beside compose.yaml: copy this file to .env and change what you need.",
        "",
        "# The study site's port on this machine.",
        f"{SITE_PORT_VARIABLE}={course.site_port}",
        "# The editor's port on this machine. The site opens the editor for you.",
        f"{EDITOR_PORT_VARIABLE}={course.editor_port}",
        f"# {NARRATIONS[0]}, or {NARRATIONS[1]}: the site with its lessons read aloud.",
        f"{NARRATION_VARIABLE}={NARRATIONS[0]}",
        "# The compose project: another name runs a second copy beside the first.",
        f"{PROJECT_VARIABLE}={course.project}",
        "# Where the images come from: the namespace they are published under.",
        f"{NAMESPACE_VARIABLE}={course.namespace}",
        "",
    ]
    return "\n".join(lines)


def readme(course: Course) -> str:
    """Return the learner's README, whole."""
    site = f"http://127.0.0.1:{course.site_port}/"
    editor = f"http://127.0.0.1:{course.editor_port}/"
    parts = [
        f"# {course.title}",
        "",
        "This repository is the whole course, ready to study on your own machine: its",
        "lessons as a study site, its practices with a runner that grades them, and an",
        "editor to write your answers in. Everything runs in Docker, on this machine only.",
        "",
        "## What you need",
        "",
        "Docker: Docker Desktop on Windows or macOS, or Docker Engine with the compose",
        "plugin on Linux. Nothing else: no Java, no Python, no other download.",
        "",
        "## Start it",
        "",
        "From this directory, either pull the published images:",
        "",
        "```",
        "docker compose -f compose.pull.yaml up -d",
        "```",
        "",
        "or build every image from this checkout (the first build takes a while, and",
        "downloads only pinned base images and the course's pinned dependencies):",
        "",
        "```",
        "docker compose up -d --build",
        "```",
        "",
        f"Then open {site} in your browser.",
        "",
        "## The ports",
        "",
        "| What | Where |",
        "|---|---|",
        f"| The study site | {site} |",
        f"| The editor, which the site opens inside each practice | {editor} |",
        "",
        "Both listen on this machine only. To use other ports, copy `course.env` to",
        f"`.env` and change `{SITE_PORT_VARIABLE}` and `{EDITOR_PORT_VARIABLE}`.",
        "",
        "## Study and practise",
        "",
        "Open a lesson from the site's contents and read it. A lesson with practices",
        "lists them after the text: open one, and the editor shows its file beside the",
        "task. **Run** runs your code; **Submit** runs the practice's tests in the",
        "runner, which has no network, and marks the practice passed when they pass.",
        "",
        "Your answers, your progress and the editor's settings live in Docker volumes,",
        "so they survive a restart. `docker compose down` stops the course and keeps",
        "them; `docker compose down -v` deletes them too.",
        "",
    ]
    if course.narrated:
        parts += [
            "## Narration (optional)",
            "",
            "The site is complete without narration: a lesson with no recording shows no",
            "player. To hear the lessons read aloud, set",
            f"`{NARRATION_VARIABLE}={NARRATIONS[1]}` in `.env` (copy it from `course.env`), then:",
            "",
            "- **Pulled images**: `docker compose -f compose.pull.yaml up -d` pulls the voiced"
            " site.",
            "- **Building it yourself**: download the recordings from the course's release",
            "  first, then build:",
            "",
            "```",
            f"sh {RESTORE_SH}",
            "docker compose up -d --build",
            "```",
            "",
            f"  On Windows, run `pwsh {RESTORE_PS1}` instead of the first line.",
            "  The script checks every download and every recording against the checksums",
            "  in this repository before it places anything, and deletes the downloads",
            "  afterwards. Set `NARRATION_LOCAL_DIR` to a directory holding the release's",
            "  volumes to read them from disk instead of downloading them.",
            "",
        ]
    if course.exercises:
        parts += [
            "## The exercises",
            "",
            f"`{BUNDLES_DIRNAME}/` holds the course's authored exercises: each one's statement,",
            "starter, tests and reference solution. `practice/` holds your working copy of",
            "each: the files you edit and submit live there, and "
            f"`{BUNDLES_DIRNAME}/` is only read.",
            "",
        ]
    parts += [
        "## Stop it",
        "",
        "```",
        "docker compose down",
        "```",
        "",
        "## Licence",
        "",
        "The course's licence is in `LICENSE`.",
        "",
        "## How this course was built",
        "",
        f"How it was built lives on the `{BUILD_BRANCH}` branch; you do not need it.",
        "",
    ]
    return "\n".join(parts)
