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
from studyforge.skills.execution.standalone import pages, tour
from studyforge.skills.execution.standalone.compose import (
    EDITOR_PORT_VARIABLE,
    PROJECT_VARIABLE,
    SITE_PORT_VARIABLE,
)
from studyforge.skills.execution.standalone.facts import Facts
from studyforge.skills.execution.standalone.images import (
    NAMESPACE_VARIABLE,
    NARRATION_VARIABLE,
    NARRATIONS,
)

#: The branch that keeps everything the build left behind.
BUILD_BRANCH = "studyforge/build"

#: The file a learner copies to `.env` to change a setting.
SETTINGS = "course.env"

#: ⛔ What the settings file shows as an example account: never a real one.
NAMESPACE_PLACEHOLDER = "your-dockerhub-account"

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
    facts: Facts = Facts()
    shots: tuple[tuple[str, str], ...] = ()
    runtimes: tuple[str, ...] = ()
    licence: bool = False
    #: ⭐ Thin: the images start from published bases, so a build needs the account too.
    thin: bool = False


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
        "# The Docker Hub account the published images are pulled from. The person who",
        "# gave you this course tells you its name: set it here, for example",
        f"# {NAMESPACE_VARIABLE}={NAMESPACE_PLACEHOLDER}",
        *(
            [
                "# compose.pull.yaml stops with a message until it is set. The course's images",
                "# start from shared base images published under the same account, so building",
                "# them yourself needs it too: compose.yaml stops until it is set.",
            ]
            if course.thin
            else [
                "# compose.pull.yaml stops with a message until it is set. Building the images",
                "# yourself needs no account: leave it empty and they are tagged "
                f"{course.namespace}.",
            ]
        ),
        f"{NAMESPACE_VARIABLE}=",
        "",
    ]
    return "\n".join(lines)


def _link(name: str, exists: bool) -> str:
    """`name` as a relative link when the tree holds it, else as plain code."""
    return f"[`{name}`]({name})" if exists else f"`{name}`"


def _requirements(course: Course) -> list[str]:
    runtime = (
        tour.join_and([one.capitalize() for one in course.runtimes]) if course.runtimes else ""
    )
    carried = f" What the practices need ({runtime}) is inside the runner." if runtime else ""
    return [
        "## What you need",
        "",
        "Docker: Docker Desktop on Windows or macOS, or Docker Engine with the compose",
        "plugin on Linux. Nothing else: no Java, no Python, no other download." + carried,
        "A current browser. Your machine needs room for the images, which download once.",
        "",
    ]


def readme(course: Course) -> str:
    """Return the learner's README, whole."""
    site = f"http://127.0.0.1:{course.site_port}/"
    editor = f"http://127.0.0.1:{course.editor_port}/"
    parts = [
        f"# {course.title}",
        "",
        *tour.sections(
            course.facts, dict(course.shots), title=course.title, narrated=course.narrated
        ),
        *_requirements(course),
        f"## {tour.RUN_HEADING}",
        "",
        "1. Install Docker, and start it.",
        "2. Clone this repository and open a terminal in its directory.",
        f"3. Copy `{SETTINGS}` to `.env`, and set `{NAMESPACE_VARIABLE}` in it to the Docker Hub",
        "   account you were given: the images are published under that account.",
        "",
        "   ```",
        f"   cp {SETTINGS} .env",
        "   ```",
        "",
        "   On Windows, use `copy course.env .env`.",
        "4. Start the course from the published images:",
        "",
        "   ```",
        "   docker compose -f compose.pull.yaml up -d",
        "   ```",
        "",
        "   The first start downloads the images, which takes a while.",
        f"   Until `{NAMESPACE_VARIABLE}` is set, compose stops and says so.",
        f"5. Open {site} in your browser.",
        "",
        "The images are built for amd64 (Intel and AMD). On an Apple Silicon Mac they run",
        "under emulation, which is slower.",
        "",
        *(
            [
                "To build the course's own images from this checkout instead, set",
                f"`{NAMESPACE_VARIABLE}` first: the shared base images are pulled from that",
                "account. The first build takes a while, and downloads only those bases and",
                "the course's pinned dependencies:",
            ]
            if course.thin
            else [
                "To build every image from this checkout instead, which needs no account (the",
                "first build takes a while, and downloads only pinned base images and the",
                "course's pinned dependencies):",
            ]
        ),
        "",
        "```",
        "docker compose up -d --build",
        "```",
        "",
        "To see what is running: `docker compose -f compose.pull.yaml ps`. Use the same",
        "`-f compose.pull.yaml` with every compose command for the pulled course.",
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
        "## Where your work is kept",
        "",
        "Your answers, your progress and the editor's settings live in Docker volumes,",
        "so they survive a restart. `down` stops the course and keeps them; `down -v`",
        f"deletes them too. Every setting is explained in {_link(SETTINGS, True)}.",
        "",
    ]
    if course.narrated:
        parts += [
            "## Narration (optional)",
            "",
            "The site is complete without narration: a lesson with no recording shows no",
            "player. The recordings are not stored in this repository, because of their",
            "size: they are assets of this repository's release, and the pulled voiced",
            "site already has them. To hear the lessons read aloud, set",
            f"`{NARRATION_VARIABLE}={NARRATIONS[1]}` in `.env` (copy it from `course.env`), then:",
            "",
            "- **Pulled images**: `docker compose -f compose.pull.yaml up -d` pulls the voiced"
            " site. Leave the setting as it is for the site without narration.",
            "- **Building it yourself**: download the recordings from the course's release",
            "  first, then build:",
            "",
            "```",
            f"sh {RESTORE_SH}",
            "docker compose up -d --build",
            "```",
            "",
            f"  On Windows, run `pwsh {RESTORE_PS1}` instead of the first line.",
            f"  The scripts are {_link(RESTORE_SH, True)} and {_link(RESTORE_PS1, True)}.",
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
        "docker compose -f compose.pull.yaml down",
        "```",
        "",
        "(`docker compose down` stops a course started with the build file.)",
        "",
        "## The online preview",
        "",
        "The read-only preview is built automatically from `main` on every push, so it is",
        "never out of date, and no other branch holds it. To switch it on for your copy of",
        "this repository, open Settings, then Pages, and choose",
        '"GitHub Actions" as the source. The next push to `main` publishes it, and the',
        "Actions tab can run it by hand. The website link at the top of this repository",
        f"opens it. The workflow is [`{pages.WORKFLOW}`]({pages.WORKFLOW}).",
        "",
        "## Licence",
        "",
        f"The course's licence is in {_link('LICENSE', course.licence)}.",
        "",
        "## How this course was built",
        "",
        f"How it was built lives on the `{BUILD_BRANCH}` branch; you do not need it.",
        "",
    ]
    return "\n".join(parts)
