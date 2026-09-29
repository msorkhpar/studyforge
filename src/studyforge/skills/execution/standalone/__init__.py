r"""A course that stands alone: its learner `main`, served without studyforge.

**What it does.** Writes, from a course checkout, the tree its learner `main`
holds: the course's own material and a copy of everything that serves it —
the part of the studyforge library the study server imports, the toolchain's
build context at the course's pinned inputs, and two compose files, one that
builds and runs the course and one that only pulls and runs it. ⭐ A learner
needs Docker and pinned base images, and nothing else: not studyforge, not
code-server-toolchain, not narrate-service.

**How you use it.** Through the execution skill's `SKILL.md`, whose section
*A course's main stands alone* is the procedure. In code:

    from studyforge.skills.execution.standalone import release

    released = release(course, out, toolchain=checkout, run=run)
    print(table(released.verdicts))

**Depends on.** The execution skill's contract reader, compose renderer and
bind rules; `generate` for the course's declarations; the caller's `run`
(`Run`), which asks `git` for the tracked files and the commits and the
toolchain for its builds. ⛔ **This package imports nothing that can start a
process** (§8.3): the caller hands the one way in, as the execution skill's
`record` takes its `ask`. ⛔ Never Docker: it writes files, and the procedure
builds them.

| module | what it owns |
|---|---|
| `closure` | the part of the library serving imports, and what it never carries |
| `split` | KEEP or MOVE for every tracked entry of the course |
| `vendor` | the toolchain's builds as its own data, and its context as bytes |
| `images` | the six images' names, and the build files studyforge owns |
| `compose` | `compose.yaml` and `compose.pull.yaml`, and the rules they keep |
| `facts` | the counts a README states, read from the course's own records |
| `tour` | the README's sections on what the course is, what it gives, and its two ways to be used |
| `learner` | the learner's `README.md` and `course.env` |
| `preview` | the read-only static tree for GitHub Pages, made from the finished learner tree |
| `previewkit` | the preview's words, script and stylesheet, and its edits of one page |
| `write` | the whole of it, and `.studyforge/release.json` |

## ⭐ Shared bases, and thin images per course

⭐ **Three images every course on one declared set shares**: the serving
runtime, and the toolchain's unprimed runner and editor. **Three per course**
on top of them: the site (the course's material, with or without its clips),
and the runner and editor warmed with the course's own dependencies. A learner
who pulls two courses downloads the bases once.
"""

from studyforge.skills.execution.standalone.closure import (
    DEFERRED,
    FORBIDDEN,
    ROOTS,
    forbidden,
    served,
    stale,
    vendored,
)
from studyforge.skills.execution.standalone.preview import Previewed, PreviewRefused
from studyforge.skills.execution.standalone.split import (
    KEEP,
    MOVE,
    Run,
    Verdict,
    classify,
    kept,
    table,
    tracked,
)
from studyforge.skills.execution.standalone.vendor import VendorRefused
from studyforge.skills.execution.standalone.write import (
    MANIFEST,
    Released,
    ReleaseRefused,
    release,
)

#: ⛔ The package's whole public surface.
__all__ = [
    "DEFERRED",
    "FORBIDDEN",
    "KEEP",
    "MANIFEST",
    "MOVE",
    "ROOTS",
    "PreviewRefused",
    "Previewed",
    "ReleaseRefused",
    "Released",
    "Run",
    "VendorRefused",
    "Verdict",
    "classify",
    "forbidden",
    "kept",
    "release",
    "served",
    "stale",
    "table",
    "tracked",
    "vendored",
]
