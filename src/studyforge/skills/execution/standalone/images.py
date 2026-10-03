r"""The images a learner's course runs, their neutral names, and the files each is built from.

**What it does.** Names the six images a standalone course is made of — three
SHARED bases any course on the same declared set pulls once (`studyforge-serve`,
`studyforge-runner`, `studyforge-editor`) and three thin per-course images on
top of them (`<course>-site`, `<course>-runner`, `<course>-editor`) — and writes
the build files studyforge owns: the serving base, the course's site with its
two narration targets, the course's runner, and the build context's ignore file.

**How you use it.**

    names = names_for(slug=..., course=..., serve=..., builds=asked.builds)
    names.site                    # "<course>-site:<commit>-<inputs>-<narration>"
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

import hashlib
from collections.abc import Mapping
from dataclasses import dataclass

from studyforge.corpus.placement import AUDIO_DIRNAME, GENERATED_ROOT, STUDY_DIRNAME
from studyforge.exercise.bundle.layout import BUNDLES_DIRNAME
from studyforge.progress import store_dir
from studyforge.skills.execution.siteimage import BASE
from studyforge.skills.execution.siteservice import CORPUS, SCRIPT_INSIDE
from studyforge.skills.execution.standalone import bases as locked
from studyforge.skills.execution.standalone import profile

#: The variable a publisher sets to the registry namespace the images go to.
NAMESPACE_VARIABLE = "STUDYFORGE_NAMESPACE"

#: ⛔ A placeholder, never an account: what a local build tags its images under.
NAMESPACE_DEFAULT = "studyforge-local"

#: ⛔ What a recipe says when the account is unset: a word with no space, because the
#: builder reads a `FROM` line's arguments by their spaces. It names the variable.
NAMESPACE_UNSET = f"{NAMESPACE_VARIABLE}-is-not-set"

#: The size of the site inputs' digest, in bytes: twelve hex digits, made short by its
#: own size rather than cut from a longer one.
INPUTS_BYTES = 6

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
    *,
    slug: str,
    course: str,
    serve: str,
    builds: Mapping[str, Mapping[str, object]],
    bases: locked.Bases | None = None,
) -> Names:
    """Name every image: `course` versions the course's three, `serve` the serving base.

    ⭐ A shared base keeps the toolchain's own tag after the colon, so the same
    inputs name the same image for every course that pulls it.

    ⭐ **With `bases` (a thin export) each base is the locked reference, tag and digest,
    and each course image's tag carries the digest of the base it starts from**: a
    base that changes names a new course image, as a changed input does for the site.
    """
    narration = f"${{{NARRATION_VARIABLE}:-{NARRATIONS[0]}}}"
    if bases is not None:
        inputs = site_inputs(slug, bases.serve.reference, bases.serve)
        # ⭐ A course's layer starts from the profile's image where the lock names one, and
        # from the plain base where it does not, so the layer's name follows the base it is on.
        runner, editor = profile.built_on(bases)
        return Names(
            serve=bases.serve.reference,
            runner_base=runner.reference,
            editor_base=editor.reference,
            site=f"{slug}-site:{course}-{inputs}-{narration}",
            runner=f"{slug}-runner:{course}-{locked.key(runner)}",
            editor=f"{slug}-editor:{course}-{locked.key(editor)}",
        )
    inputs = site_inputs(slug, serve)
    return Names(
        serve=f"studyforge-serve:{serve}",
        runner_base=f"studyforge-runner:{_tag_of(builds['runner'])}",
        editor_base=f"studyforge-editor:{_tag_of(builds['editor'])}",
        site=f"{slug}-site:{course}-{inputs}-{narration}",
        runner=f"{slug}-runner:{course}",
        editor=f"{slug}-editor:{course}",
    )


def site_inputs(slug: str, serve: str, base: locked.Base | None = None) -> str:
    """Return the short digest of what a course's site image is built from, beyond its files.

    ⭐ **The site's tag moves when the site's content moves.** The serving base's
    tag already carries the whole digest of the vendored library, and the site's
    own build file and ignore file are the other inputs; a library or build-file
    change therefore names a NEW site image rather than re-pushing an old name
    that anyone who already pulled it would keep. ⛔ The course's own files are
    the course commit's, already in the tag. A thin site's `serve` is the locked
    reference, whose digest is the base's own, and `base` puts its build file in.
    """
    digest = hashlib.blake2b(digest_size=INPUTS_BYTES)
    for part in (serve, site_dockerfile(slug, base), DOCKERIGNORE):
        digest.update(part.encode("utf-8") + b"\0")
    return digest.hexdigest()


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


def site_dockerfile(slug: str, base: locked.Base | None = None) -> str:
    """Return the course's site: its material on the serving base, with and without its clips.

    ⭐ **Thin**: with `base` the recipe starts `FROM` the published serving base by tag
    and digest, under the account `STUDYFORGE_NAMESPACE` names when the image is built:
    ⛔ no account is written here, and an unset one stops the build before anything
    is pulled. Without it the recipe starts from the serving base this tree builds.

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
    head = ["ARG SERVE_BASE"]
    first = second = "${SERVE_BASE}"
    if base is not None:
        head = [f"ARG {NAMESPACE_VARIABLE}"]
        first = second = f"${{{NAMESPACE_VARIABLE}:?{NAMESPACE_UNSET}}}/{base.reference}"
    return "\n".join(
        [
            MARK,
            "# The course's study site: every file of the course on the shared server.",
            "# Two targets: without-narration, whose pages name no clip, and with-narration,",
            "# which adds every clip and refuses to build unless each matches the checksum",
            "# the course committed.",
            *head,
            "",
            f"FROM {first} AS {NARRATIONS[0]}",
            "USER root",
            "RUN --mount=type=bind,source=.,target=/context \\",
            *extract,
            f"    {STRIP_CLIPS}; \\",
            f"    chown -R {RUNS_AS} {CORPUS}",
            f"USER {RUNS_AS}",
            f"WORKDIR {CORPUS}",
            f'LABEL org.studyforge.course="{slug}" org.studyforge.narration="without"',
            "",
            f"FROM {second} AS {NARRATIONS[1]}",
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
