r"""The release manifest a learner tree carries, and the toolchain paths a thin tree keeps.

**What it does.** Builds `.studyforge/release.json`: the course, the commits, the toolchain's
tags, every image's name, the verdict on each tracked path and `keeps`, the list of every
path the tree holds. ⭐ A thin export adds `bases`, the locked reference of each published
base; a self-contained export has no such key. `thin_inputs` names the toolchain paths a
thin tree copies: only what the course's own layers read.

**How you use it.**

    document = manifest(slug, commit, library_commit, version, asked, platform, names,
                        verdicts, kept, written, bases)
    thin_inputs(asked)        # the toolchain paths the runner and editor layers read
    unprimed_tags(asked)      # the tags a bases lock must name for the runner and editor

**Depends on.** `closure` for the edges the serving runtime does not follow, `images` for
the names, and `bases` for the locked references. It writes nothing.
"""

from __future__ import annotations

from studyforge.skills.execution.standalone import bases as locked
from studyforge.skills.execution.standalone import closure, images

#: The manifest's path in the learner tree, and its shape's version.
MANIFEST = ".studyforge/release.json"
RELEASE_API = 1


def manifest(
    slug,
    course_commit,
    library_commit,
    version,
    asked,
    platform,
    names,
    verdicts,
    kept,
    written,
    bases=None,
) -> dict:
    """`.studyforge/release.json`: every path the tree keeps, and where each came from.

    ⭐ A thin export adds `bases`, the locked reference of each published base; a
    self-contained one has no such key.
    """
    document = {
        "release_api": RELEASE_API,
        "course": slug,
        "exported_from": course_commit,
        "library": {"version": version, "commit": library_commit},
        "toolchain": {
            "commit": asked.commit,
            "tags": {k: v["tag"] for k, v in asked.builds.items()},
        },
        "platform": platform,
        "images": {key: images.qualified(value) for key, value in vars_of(names).items()},
        "deferred_edges": [f"{a} -> {b}" for a, b in closure.DEFERRED],
        "verdicts": [{"path": v.path, "verdict": v.verdict, "why": v.why} for v in verdicts],
        "keeps": sorted({*kept, *written, MANIFEST}),
    }
    if bases is not None:
        document["bases"] = {
            kind: {"image": one.image, "tag": one.tag, "digest": one.digest}
            for kind in locked.KINDS
            for one in (getattr(bases, kind),)
        }
    return document


def thin_inputs(asked) -> tuple[str, ...]:
    """Return the toolchain paths a thin tree keeps: what the course layers read."""
    return tuple(
        sorted(
            {
                str(one)
                for image in ("runner-prime", "editor-prime")
                for one in asked.builds[image]["inputs"]
            }
        )
    )


def vars_of(names: images.Names) -> dict[str, str]:
    """Every image name, by its field."""
    return {field: getattr(names, field) for field in names.__slots__}


def unprimed_tags(asked) -> dict[str, str]:
    """Return the tag, after its repository, of the toolchain's unprimed runner and editor."""
    return {kind: str(asked.builds[kind]["tag"]).split(":", 1)[1] for kind in ("runner", "editor")}
