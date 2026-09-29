r"""The images a learner's course runs, their neutral names, and the files each is built from.

**What it does.** Names the six images a standalone course is made of — three
SHARED bases any course on the same declared set pulls once (`studyforge-serve`,
`studyforge-runner`, `studyforge-editor`) and three thin per-course images on
top of them (`<course>-site`, `<course>-runner`, `<course>-editor`) — and writes
the build files studyforge owns: the serving base, the course's site with its
two narration targets, the course's runner, and the build context's ignore file.

**How you use it.**

    names = names_for(slug=..., course=..., serve=..., builds=asked.builds)
    names.site                    # "<course>-site:<version>-${COURSE_NARRATION:-without-narration}"
    qualified(names.site)         # the same under "${STUDYFORGE_NAMESPACE:-studyforge-local}/"
    serve_dockerfile(commit=..., version=...), site_dockerfile(slug), runner_dockerfile(slug)

**Depends on.** `skills.execution.siteimage` for the pinned Python base the
study server already runs on, and `siteservice` for where the server and its
run service sit inside their containers.

## ⭐ The namespace is the publisher's, and a placeholder until then

⛔ **No registry account is written anywhere.** Every name is qualified by
`${STUDYFORGE_NAMESPACE:-studyforge-local}`, so a learner's local build tags
images nobody can pull, and a publisher who pushes sets one variable.

## ⭐ Two narrations of one site, as two targets of one build

`without-narration` is the course with no clip in it and no page naming one, so no
page asks for a clip and the console stays clear; `with-narration` is the course
with every restored clip, and refuses to build unless each one matches the
checksum the course committed. ⭐ A learner picks one with `COURSE_NARRATION`,
and both run the same server; a voiced page asks its first clip itself and hides
the player until it loads.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from studyforge.corpus.placement import AUDIO_DIRNAME, GENERATED_ROOT, STUDY_DIRNAME
from studyforge.exercise.bundle.layout import BUNDLES_DIRNAME
from studyforge.progress import store_dir
from studyforge.skills.execution.siteimage import BASE
from studyforge.skills.execution.siteservice import CORPUS, SCRIPT_INSIDE

#: The variable a publisher sets to the registry namespace the images go to.
NAMESPACE_VARIABLE = "STUDYFORGE_NAMESPACE"

#: ⛔ A placeholder, never an account: what a local build tags its images under.
NAMESPACE_DEFAULT = "studyforge-local"

#: The variable a learner sets to choose the site's narration.
NARRATION_VARIABLE = "COURSE_NARRATION"

#: The site's two build targets, the first the default.
NARRATIONS = ("without-narration", "with-narration")

#: Where the course's material sits inside the site image, and where each run happens.
WORK = "/work"

#: The one uid every service runs as: nothing from the host is bound, so no host uid is asked.
RUNS_AS = "1000:1000"

#: ⭐ The server's progress store, which no checkout tracks: made in the image, so
#: the named volume mounted there is seeded owned by `RUNS_AS` rather than root.
PROGRESS = store_dir(".").as_posix()

#: The course's clips' checksums, which the voiced target proves every clip against.
CLIPS = ".studyforge/narration-release/clips.sha256"

#: ⭐ The course's run service, baked into its runner.
RUNSERVICE = ".studyforge/execution/runservice.pl"

#: The mark every build file studyforge writes here carries.
MARK = "# Written by studyforge's execution skill (standalone). Regenerate it; never edit it."


@dataclass(frozen=True, slots=True)
class Names:
    """Every image's name, unqualified: `repository:tag`."""

    serve: str
    runner_base: str
    editor_base: str
    site: str
    runner: str
    editor: str


def qualified(name: str) -> str:
    """`name` under the publisher's namespace, as a compose interpolation."""
    return f"${{{NAMESPACE_VARIABLE}:-{NAMESPACE_DEFAULT}}}/{name}"


def names_for(
    *, slug: str, course: str, serve: str, builds: Mapping[str, Mapping[str, object]]
) -> Names:
    """Name every image: `course` versions the course's three, `serve` the serving base.

    ⭐ A shared base keeps the toolchain's own tag after the colon, so the same
    inputs name the same image for every course that pulls it.
    """
    narration = f"${{{NARRATION_VARIABLE}:-{NARRATIONS[0]}}}"
    return Names(
        serve=f"studyforge-serve:{serve}",
        runner_base=f"studyforge-runner:{_tag_of(builds['runner'])}",
        editor_base=f"studyforge-editor:{_tag_of(builds['editor'])}",
        site=f"{slug}-site:{course}-{narration}",
        runner=f"{slug}-runner:{course}",
        editor=f"{slug}-editor:{course}",
    )


def serve_dockerfile(*, commit: str, version: str) -> str:
    """Return the shared serving base: the pinned Python and the vendored runtime, nothing else."""
    return "\n".join(
        [
            MARK,
            "# The shared study server: the part of the studyforge library that serves a",
            "# course, found by its imports, with no ingestion, no skill and no synthesis.",
            f"FROM {BASE}",
            "COPY library/ /opt/studyforge/library/",
            "ENV PYTHONPATH=/opt/studyforge/library PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1",
            f'LABEL org.studyforge.serve.version="{version}" \\',
            f'      org.studyforge.serve.commit="{commit}"',
            'ENTRYPOINT ["python3", "-m", "studyforge.cli"]',
            "",
        ]
    )


#: ⭐ Where a corpus's clips sit, under either placement: a `tree` corpus's inside its
#: generated root, a `sibling` corpus's in `<source directory>/study/audio/`. ⛔ Asked of
#: the placement's own names, so the silent target leaves out both and the voiced one
#: copies both.
CLIP_EXCLUDES = (
    f"--exclude='./{GENERATED_ROOT}/*/{AUDIO_DIRNAME}' "
    f"--exclude='*/{STUDY_DIRNAME}/{AUDIO_DIRNAME}'"
)
CLIP_FINDER = (
    f"find . \\( -path './{GENERATED_ROOT}/*' -o -path '*/{STUDY_DIRNAME}/*' \\) "
    f"-type d -name {AUDIO_DIRNAME} -prune"
)

#: ⭐ What a site with no clips does to its pages: the attribute that names a clip is
#: removed from every page, so no page asks for a clip that no image holds. ⛔ The
#: same attribute `render.page.code` already strips from a page it embeds; run in the
#: one layer that extracts the tree, as root, so nothing is written twice.
#: `sed -i` keeps each file's owner, and the `chown` after it is what names it.
STRIP_CLIPS = (
    f"find {CORPUS} -type f -name '*.html' -exec sed -i -E 's/ data-audio=\"[^\"]*\"//g' {{}} +"
)


def site_dockerfile(slug: str) -> str:
    """Return the course's site: its material on the serving base, with and without its clips.

    ⭐ **Two stages from the same base, neither built on the other.** The site
    with no clips also has no reference to one, so its pages ask for nothing and the
    console stays clear. ⛔ **Each stage is one layer of the course**: the voiced one
    writes the tree, its clips and their owner in a single `RUN`, so no clip is ever
    stored twice.
    """
    extract = [
        "    set -eu; mkdir -p " + CORPUS + "; \\",
        f"    tar -C /context --exclude=./.git {CLIP_EXCLUDES} -cf - . \\",
        f"      | tar -C {CORPUS} -xf -; \\",
        f"    mkdir -p {CORPUS}/{PROGRESS}; \\",
    ]
    return "\n".join(
        [
            MARK,
            "# The course's study site: every file of the course on the shared server.",
            "# Two targets: without-narration, whose pages name no clip, and with-narration,",
            "# which adds every clip and refuses to build unless each matches the checksum",
            "# the course committed.",
            "ARG SERVE_BASE",
            "",
            f"FROM ${{SERVE_BASE}} AS {NARRATIONS[0]}",
            "USER root",
            "RUN --mount=type=bind,source=.,target=/context \\",
            *extract,
            f"    {STRIP_CLIPS}; \\",
            f"    chown -R {RUNS_AS} {CORPUS}",
            f"USER {RUNS_AS}",
            f"WORKDIR {CORPUS}",
            f'LABEL org.studyforge.course="{slug}" org.studyforge.narration="without"',
            "",
            f"FROM ${{SERVE_BASE}} AS {NARRATIONS[1]}",
            "USER root",
            "RUN --mount=type=bind,source=.,target=/context \\",
            *extract,
            "    cd /context; \\",
            f"    {CLIP_FINDER} | while IFS= read -r dir; do \\",
            f'      mkdir -p "{CORPUS}/$dir"; cp -R "$dir/." "{CORPUS}/$dir/"; \\',
            "    done; \\",
            f"    chown -R {RUNS_AS} {CORPUS}; \\",
            f"    cd {CORPUS}; sha256sum -c --quiet {CLIPS} \\",
            "      || { echo 'narration clips missing or wrong: restore them first' >&2; \\",
            "           exit 1; }",
            f"USER {RUNS_AS}",
            f"WORKDIR {CORPUS}",
            f'LABEL org.studyforge.course="{slug}" org.studyforge.narration="with"',
            "",
        ]
    )


def runner_dockerfile(slug: str) -> str:
    """Return the course's runner: its primed layer, and the run service the site talks to."""
    return "\n".join(
        [
            MARK,
            "# The course's runner: the toolchain's course layer, with the run service the",
            "# site reaches on the compose file's internal network.",
            "ARG RUNNER_PRIMED",
            "FROM ${RUNNER_PRIMED}",
            f"COPY {RUNSERVICE} {SCRIPT_INSIDE}",
            f"WORKDIR {WORK}",
            f'CMD ["perl", "{SCRIPT_INSIDE}"]',
            f'LABEL org.studyforge.course="{slug}"',
            "",
        ]
    )


#: ⭐ What the site's build context leaves out: the build files, the learner's own
#: state, and what a build or a run writes. ⛔ Also the authored exercises and the course's
#: scripts: kept on `main`, but nothing an image reads (the server serves `practice/` and the
#: archive; the runner is handed the learner's files), so they never swell an image.
#: Clips stay IN, for the voiced target.
DOCKERIGNORE = "\n".join(
    [
        "# Written by studyforge's execution skill (standalone). Regenerate it; never edit it.",
        ".git",
        ".env",
        "compose.yaml",
        "compose.pull.yaml",
        "course.env",
        "README.md",
        BUNDLES_DIRNAME,
        "scripts",
        ".studyforge/images",
        ".studyforge/narration-release/download",
        ".studyforge/site.json",
        ".studyforge/site.json.writing",
        ".studyforge/progress",
        ".studyforge/execution/code/*",
        "!.studyforge/execution/code/.gitignore",
        ".studyforge/execution/allowed/*",
        "!.studyforge/execution/allowed/.gitignore",
        "**/target",
        "**/__pycache__",
        "",
    ]
)


def _tag_of(build: Mapping[str, object]) -> str:
    """Return the part of a toolchain tag after its repository."""
    return str(build["tag"]).split(":", 1)[1]
