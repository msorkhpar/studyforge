"""`studyforge plan` — what a build will do to a repository, before it does it.

**What it does.** Reads one corpus's declarations and emits every path a build
will create, every existing file it will edit and why, the ignore lines the
declared placement profile requires, and the projected media footprint against
the corpus's own limits.

**How you use it.**

    studyforge plan <repo>            # python3 -m studyforge.cli.plan <repo>

    from studyforge.cli.plan import plan_for
    plan_for(root).paths              # what SK-07 renders and OPS-05 asserts

**Depends on.** `corpus.manifest`, `corpus.container`, `corpus.placement`, and
`validate` for the three names both commands must spell the same way. ⛔ It
writes nothing, it creates nothing, and it raises nothing.

## ⛔ It reads the declarations, never the source material

⭐ **A dry-run that scans first reports what is there, not what is coming — and
the two differ precisely in the case that matters, the first run.** So this
reads `corpus.json` and the container maps under the archive, which are the
corpus's *declarations about itself*, and it opens no file the material is made
of. `Plan.read_files` is the exact list of what was opened, so the acceptance
clause *"reads no file inside the source material"* is checkable rather than
promised.

⚠️ **Deliberately a narrower read than `validate.corpus.read`**, which also
parses every archive document. A plan that went red because one lesson's JSON
was malformed would be answering `validate`'s question with `plan`'s exit code.

## ⛔ Why this seam had no contract

The archive seam has `studyforge validate`; the runtime seam has each shared
component's consuming contract; **placement had nothing.** A consumer had to
write ignore rules, declare `permitted_edits` (R3) and reason about what would
land in their repository with no way to ask, while `SF-03` already computed
every bit of it. ⭐ And a person reads this before letting a tool loose in a
repository they care about — **an onboarding somebody cannot preview is one
they are right not to run.**

## ⛔ Printing corpus text is safe here *because the gate ran* (R7)

Titles, `why` sentences and an edit's inserted line are somebody else's text,
and this command prints them verbatim where `describe` would refuse to. That is
not an exception to R7 and it is not a refusal site: `manifest.parse` and
`container.parse` run `assert_clean` over the whole decoded document before any
field is read, so a corpus carrying a home path is refused before a line is
emitted. ⭐ Asserted, not assumed —
`test_a_manifest_carrying_personal_data_is_refused_before_any_line_is_printed`.

⛔ **And every path printed is relative to the corpus root**, because every path
placement returns is. An absolute path in a plan is the user's home directory
in whatever the plan gets pasted into.

## What is in the package

⚠️ **Four modules rather than one file, and the shape is `validate/`'s.** The
model that a plan *is*, the derivation that produces one, and the command that
prints it are three concerns with three sets of tests, and the house already
answered this question once for the other command that reads a corpus root.

| Module | Owns |
|---|---|
| `report` | what a plan is, and how each line renders |
| `derive` | one corpus root in, one `Plan` out |
| `cli` | the arguments, the stream and the exit code |
"""

from __future__ import annotations

from studyforge.cli.plan.cli import build_parser, main
from studyforge.cli.plan.derive import plan_for
from studyforge.cli.plan.report import (
    UNPROJECTED,
    Creation,
    MediaProjection,
    Plan,
    Refusal,
    edit_lines,
)

#: ⛔ The package's whole public surface. A consumer that has to import
#: `studyforge.cli.plan.derive` directly is a consumer this contract failed.
__all__ = [
    "UNPROJECTED",
    "Creation",
    "MediaProjection",
    "Plan",
    "Refusal",
    "build_parser",
    "edit_lines",
    "main",
    "plan_for",
]
