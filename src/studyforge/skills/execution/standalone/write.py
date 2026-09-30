r"""Write a course's learner tree: its material, and all that serves it without studyforge.

**What it does.** From a course checkout, writes into an empty directory the
tree its learner `main` holds: every tracked file `split` keeps, the vendored
serving runtime (`closure`), the toolchain's build context at the course's
pinned inputs (`vendor`), the build files studyforge owns (`images`), the two
compose files (`compose`), the learner's README and settings (`learner`), and
`.studyforge/release.json`, the manifest of every path the tree keeps. ⭐ The tree also
carries its own Pages automation (`pages`): the workflow that deploys the read-only
preview on every push to `main`, and the copy of the builder it runs.

**How you use it.**

    released = release(course, out, toolchain=checkout, run=run)   # run: split.Run
    released.kept, released.written, released.verdicts

**Depends on.** Every module of this package, `generate.read_corpus` for the
course's declarations, `skills.onboarding.library` for the loaded library's
version, and `git`, asked for commits. ⛔ It never writes into the course
checkout, and it refuses a target directory that is not empty.

## ⛔ Nothing here is a second copy of a decision

⭐ Which files are kept is `split`'s; which modules serve is `closure`'s; how
an image is built is the toolchain's own data (`vendor`); what a compose file
may say is `compose`'s. This module calls them in order and writes what they
return, and the manifest is the record of all of it, so the move a procedure
makes from it is reviewable file by file.
"""

from __future__ import annotations

import hashlib
import json
import platform as host
import shutil
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from studyforge.execute import instance
from studyforge.exercise.bundle.layout import BUNDLES_DIRNAME
from studyforge.generate import read_corpus
from studyforge.skills.execution.binds import code_bind, source_root, workspaces_bind
from studyforge.skills.execution.contract import (
    CONSUMING,
    EDITOR_API,
    EDITOR_COMPONENT,
    EDITOR_PROMISE,
    blocks,
    read,
    require,
)
from studyforge.skills.execution.standalone import (
    bases as locked,
)
from studyforge.skills.execution.standalone import (
    closure,
    compose,
    facts,
    images,
    learner,
    pages,
    preview,
    record,
    split,
    tour,
    vendor,
)
from studyforge.skills.execution.standalone.record import MANIFEST
from studyforge.skills.onboarding import library

#: The manifest's path in the learner tree, and its shape's version.

#: The machines a toolchain pins, by what `platform.machine()` says.
MACHINES = {
    "x86_64": "linux/amd64",
    "amd64": "linux/amd64",
    "aarch64": "linux/arm64",
    "arm64": "linux/arm64",
}

#: What a learner's `.gitignore` must hold: their own settings stay theirs.
IGNORED = ".env"


class ReleaseRefused(ValueError):
    """A course this skill will not write a learner tree for, and why."""


@dataclass(frozen=True, slots=True)
class Released:
    """What one release wrote, and the proposal it is."""

    verdicts: tuple[split.Verdict, ...]
    kept: tuple[str, ...]
    written: tuple[str, ...]
    names: images.Names
    manifest: dict
    previewed: preview.Previewed | None = None


def host_platform() -> str:
    """Return this machine's platform, as the toolchain pins name it."""
    machine = host.machine().lower()
    return MACHINES.get(machine, f"linux/{machine}")


def release(
    root: Path,
    out: Path,
    *,
    toolchain: Path,
    platform: str | None = None,
    namespace: str = images.NAMESPACE_DEFAULT,
    screenshots: Path | None = None,
    preview_to: Path | None = None,
    bases: locked.Bases | None = None,
    run: split.Run,
) -> Released:
    """Write the learner tree of the course at `root` into `out`, or refuse by name.

    `screenshots` names a directory of the README's pictures (`tour.ROLES`), copied
    into the tree; `preview_to` names a new directory that also receives the
    read-only preview of the finished tree (`preview`).

    ⭐ **Thin export**: with `bases` (from `bases.read`) the tree carries no serving library,
    no serve recipe and no runner or editor base recipe: the site starts from the published
    serving base and the runner and editor from the published toolchain bases, each by tag and
    digest, and the tree keeps only the course's own layers. Without it the tree is
    self-contained, byte for byte as it always was.
    """
    root, out, toolchain = Path(root), Path(out), Path(toolchain)
    if out.exists() and any(out.iterdir()):
        raise ReleaseRefused("the target directory is not empty; name a new or empty one")
    platform = platform or host_platform()
    corpus = read_corpus(root)
    manifest = corpus.manifest
    if not manifest.runtimes:
        raise ReleaseRefused("the course declares no runtime, so it has nothing to run standalone")
    files = split.tracked(root, run)
    verdicts = split.classify(root, files)
    if not any(one.path == split.HOSTING for one in verdicts):
        verdicts = (*verdicts, split.HOSTED)
    kept = split.kept(verdicts, files)
    prime = root / split.PRIME
    vendor.pinned(root, toolchain, manifest.runtimes, prime, platform=platform, run=run)
    asked = vendor.ask(toolchain, manifest.runtimes, prime, platform=platform, run=run)
    editor = require(
        read(
            (toolchain / CONSUMING).read_text(encoding="utf-8"),
            component=EDITOR_COMPONENT,
            api=EDITOR_API,
            promise=EDITOR_PROMISE,
        ),
        "editor",
    )
    if bases is not None:
        locked.check(
            bases,
            version=library.version(),
            toolchain=record.unprimed_tags(asked),
            declared=manifest.runtimes,
            tags_for=vendor.asker(toolchain, platform=platform, run=run),
            serve_tag=locked.computed_serve_tag(library.PACKAGE.parent),
        )
    out.mkdir(parents=True, exist_ok=True)
    owned = [one for one in kept if one in pages.OWNED or one.startswith(pages.BUILDER_DIR + "/")]
    if owned:
        raise ReleaseRefused(
            f"the course tracks {owned}, which the export writes itself; move or rename them"
        )
    for one in kept:
        _copy(root / one, out / one)
    written: list[str] = []
    library_commit = _library_commit(run)
    version = library.version()
    serve = bases.serve.tag if bases else _write_runtime(out, library_commit, version, written)
    written += [
        f"{compose.TOOLCHAIN}/{one}"
        for one in vendor.copy(
            toolchain, out / compose.TOOLCHAIN, record.thin_inputs(asked) if bases else asked.inputs
        )
    ]
    course_commit = _commit(root, run)
    names = images.names_for(
        slug=manifest.source,
        course=course_commit[:12],
        serve=serve,
        builds=asked.builds,
        bases=bases,
    )
    ports = _ports(root, editor)
    plan = compose.Plan(
        slug=manifest.source,
        names=names,
        builds=asked.builds,
        editor=editor,
        runtimes=tuple(manifest.runtimes),
        binds=_binds(manifest, editor),
        site_port=ports[0],
        editor_port=ports[1],
        bases=bases,
    )
    built, pulled = compose.render(plan)
    shots = _screenshots(screenshots, out, written)
    narrated = bool(manifest.narration) and (root / images.CLIPS).is_file()
    course = learner.Course(
        manifest.title,
        manifest.source,
        ports[0],
        ports[1],
        namespace,
        narrated,
        exercises=any(one.startswith(f"{BUNDLES_DIRNAME}/") for one in kept),
        facts=facts.read(out),
        shots=shots,
        runtimes=tuple(manifest.runtimes),
        licence="LICENSE" in kept,
        thin=bases is not None,
    )
    texts = {
        f"{compose.IMAGES}/site/Dockerfile": images.site_dockerfile(
            manifest.source, bases.serve if bases else None
        ),
        f"{compose.IMAGES}/runner/Dockerfile": images.runner_dockerfile(manifest.source),
        ".dockerignore": images.DOCKERIGNORE,
        "compose.yaml": _namespaced(built, namespace),
        "compose.pull.yaml": _namespaced(pulled, namespace),
        learner.SETTINGS: learner.settings(course),
        "README.md": learner.readme(course),
    }
    if bases is None:
        texts[f"{compose.NO_PRIME}/README"] = (
            "An empty build context: an unprimed image warms nothing.\n"
        )
    for where, text in texts.items():
        _text(out / where, text)
        written.append(where)
    for where, data in pages.builder().items():
        target = out / where
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        written.append(where)
    _text(out / pages.WORKFLOW, pages.workflow())
    written.append(pages.WORKFLOW)
    if _ignore_env(out / ".gitignore"):
        written.append(".gitignore")
    document = record.manifest(
        manifest.source,
        course_commit,
        library_commit,
        version,
        asked,
        platform,
        names,
        verdicts,
        kept,
        written,
        bases,
    )
    _text(out / MANIFEST, json.dumps(document, indent=2) + "\n")
    written.append(MANIFEST)
    previewed = preview.preview(out, Path(preview_to)) if preview_to else None
    return Released(
        tuple(verdicts), tuple(kept), tuple(sorted(set(written))), names, document, previewed
    )


#: The README's pictures: what a file may be, and how much of the repository they may take.
SHOT_SUFFIXES = (".png", ".webp")
SHOT_MAX_BYTES = 160 * 1024
SHOTS_MAX_BYTES = 700 * 1024


def _screenshots(source: Path | None, out: Path, written: list[str]) -> tuple[tuple[str, str], ...]:
    """Copy the README's pictures into the tree; return `(role, path)` for each, or refuse."""
    if source is None:
        return ()
    roles = [role for role, _ in tour.ROLES]
    found: list[tuple[str, Path]] = []
    for one in sorted(Path(source).iterdir()):
        if one.stem not in roles or one.suffix not in SHOT_SUFFIXES:
            raise ReleaseRefused(f"{one.name} is not a picture the README shows: {roles}")
        if one.stat().st_size > SHOT_MAX_BYTES:
            raise ReleaseRefused(f"{one.name} is over {SHOT_MAX_BYTES // 1024} KB")
        found.append((one.stem, one))
    if sum(one.stat().st_size for _, one in found) > SHOTS_MAX_BYTES:
        raise ReleaseRefused(f"the pictures together are over {SHOTS_MAX_BYTES // 1024} KB")
    if len({role for role, _ in found}) != len(found):
        raise ReleaseRefused("a role has two pictures; keep one")
    placed = []
    for role in roles:
        for name, one in found:
            if name == role:
                where = f"{compose.IMAGES}/readme/{one.name}"
                _copy(one, out / where)
                written.append(where)
                placed.append((role, where))
    return tuple(placed)


def _write_runtime(out: Path, commit: str, version: str, written: list[str]) -> str:
    """Vendor the serving closure and its build file; return the serving base's tag.

    ⭐ The tag carries the WHOLE digest of what the base is built from: only a
    clip's name is minted short (`narrate.speakable`), and a tag has the room.
    """
    src = library.PACKAGE.parent
    base = out / compose.IMAGES / "serve"
    digest = hashlib.sha256()
    dockerfile = images.serve_dockerfile(commit=commit, version=version)
    digest.update(dockerfile.encode("utf-8"))
    for one in closure.vendored(src):
        target = base / "library" / one
        _copy(src / one, target)
        digest.update(one.encode("utf-8") + b"\0" + target.read_bytes() + b"\0")
        written.append(f"{compose.IMAGES}/serve/library/{one}")
    stamp = f"{compose.IMAGES}/serve/library/{closure.PACKAGE}/{closure.STAMP}"
    _text(out / stamp, commit + "\n")
    _text(base / "Dockerfile", dockerfile)
    written += [stamp, f"{compose.IMAGES}/serve/Dockerfile"]
    return f"{version}-{digest.hexdigest()}"


def _binds(manifest, editor) -> tuple[tuple[str, str], ...]:
    """Return what the editor opens, sources first: the execution skill's own answer."""
    sources = source_root(manifest)
    inside = next(
        str(entry["container_path"])
        for entry in blocks(editor, "mounts")
        if entry.get("per_project") is True
    )
    extra = [one for one in (workspaces_bind(editor, sources), code_bind(editor, sources)) if one]
    return ((sources, inside), *extra)


def _ports(root: Path, editor) -> tuple[int, int]:
    """Return the site's and the editor's ports: the course's recorded ones, else the defaults."""
    try:
        recorded = instance.read(root)
    except OSError, ValueError:
        recorded = {}
    editor_default = next(
        int(one["host"]) for one in blocks(editor, "ports") if one.get("per_project")
    )
    return (
        int(recorded.get(instance.SITE_PORT, instance.DEFAULT_SITE_PORT)),
        int(recorded.get(instance.EDITOR_PORT, editor_default)),
    )


def _namespaced(text: str, namespace: str) -> str:
    """Return a compose text whose namespace default is `namespace`."""
    placeholder = f"${{{images.NAMESPACE_VARIABLE}:-{images.NAMESPACE_DEFAULT}}}"
    return text.replace(placeholder, f"${{{images.NAMESPACE_VARIABLE}:-{namespace}}}")


def _ignore_env(path: Path) -> bool:
    """Make the learner's `.gitignore` ignore `.env`; say whether it had to be written."""
    lines = path.read_text(encoding="utf-8").splitlines() if path.is_file() else []
    if IGNORED in (line.strip() for line in lines):
        return False
    body = "\n".join(
        [*lines, "", "# A learner's own settings (course.env explains them).", IGNORED, ""]
    )
    _text(path, body.lstrip("\n"))
    return True


def _copy(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def _text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def _commit(root: Path, run: split.Run) -> str:
    code, printed = run(["git", "-C", str(root), "rev-parse", "HEAD"], root)
    if code != 0:
        raise ReleaseRefused("the course is not a git checkout, so no commit versions its images")
    return printed.strip()


def _library_commit(run: split.Run) -> str:
    """Return the loaded library's commit: its stamp, or its source checkout's HEAD."""
    stamped = library.commit()
    if stamped:
        return stamped
    code, printed = run(["git", "-C", str(library.PACKAGE), "rev-parse", "HEAD"], library.PACKAGE)
    return printed.strip() if code == 0 else "unknown"


def kept_paths(released: Released) -> Sequence[str]:
    """Every path the learner tree keeps, as the manifest lists them."""
    return released.manifest["keeps"]
