r"""What an authored exercise IS on disk, and how it becomes `practice-M.json`.

**What it does.** Defines the **bundle** — the directory a corpus repository
commits for one authored exercise, carrying its statement, its starter, its
reference solution, its tests, its plants, its `cases` and the gate record
`AX-03` wrote — and the emission an adapter calls to turn one into an archive
practice document and the reader's own workspace.

**How you use it.**

    bundle = bundle_of(json.loads(text), where)
    emission = emit(root, bundle, source="demo", ingested="2026-01-05")
    emission.document                       # render this to practice-M.json
    write(root, emission, where)            # the reader's files, created not overwritten

⛔ **`studyforge validate`'s half is not called from here.** It is
`validate.exercises`, which reads a bundle through `Places` and `unpermitted`
and re-reads the gate record through `exercise.gates`.

**Depends on.** `address`, `archive.document`, `archive.blocks`,
`archive.markdown`, `corpus.placement` for the workspace segment,
`exercise.cases`, `exercise.gates`, `exercise.record` (through `build`),
`exercise.safety`, `exercise.errors`. Standard library only.

## What is in the package

| Module | Owns |
|---|---|
| `layout` | the two roots, the closed file set, and where each role's copy sits |
| `document` | `bundle.json`: what an exercise declares about itself |
| `emit` | the archive document a bundle becomes, and the workspace it creates |

## ⛔ THE FRAMEWORK NEVER AUTHORS, AND NEVER REACHES INTO A CORPUS (R1, R2)

⭐ **Nothing here writes a statement, a test or a solution.** Authoring happens
once, at ingestion, by the skill `AX-08` runs (`E14`'s second property); this
package is the **shape** that skill writes into and the **arithmetic** an
adapter reads it back out with. ⛔ No corpus is imported, named or branched on:
every source-specific fact arrives as the bundle's own data.

## ⛔ TWO ROOTS, BECAUSE THE READER'S FILE IS NOT THE STARTER

⭐ **The bundle holds the pristine material and the workspace holds the
reader's copy**, both derived from the identity the archive document already
carries. ⚠️ **The alternative was measured rather than dismissed:** with one
root, the gate record's digest of the starter would drift the moment anybody
did the exercise, and `studyforge validate` would report every worked corpus as
broken. ⛔ So every file a gate record digests is one no reader touches, which
is what keeps `AX-11`'s *"every shipped exercise's gate record verifies against
the files beside it"* true after the corpus has been used.

## ⛔ A BUNDLE'S FILE SET IS CLOSED, AND THAT IS `AX-03/1`'s ANSWER

⚠️ **A JUnit report carries the machine's HOSTNAME** — `pytest --junit-xml`
and surefire both write `hostname="…"`, measured by `AX-03` — and a corpus
repository is where **this** repository's personal-data gate never looks (R7).
⛔ **The remedy is mechanical in two places rather than a sentence in a
guide:** a bundle may hold `bundle.json`, `statement.md`, `gates.json` and the
files under `starter/`, `reference/`, `tests/` and `plants/`, so a committed
report is named by `validate.exercises`; and the bundle document's report path
is **workspace-relative**, so it cannot address the bundle at all. ⭐ **The
report is a run artifact, never a bundle input**, and that is now a refusal
instead of a promise.

## ⭐ THE REFERENCE SOLUTION SHIPS, WITHHELD BUT PRESENT

⛔ **The user ruled it always available** and `AX-09` offers it at any time,
never gated on a pass. ⭐ `emit` writes it into the practice document as a
`disclosure` block — the archive's own *present but withheld* state — so an
offline page can offer it with no run, no request and nothing recorded.
⚠️ Withholding it would be a pretence anyway: the bundle is already on the
reader's disk.

## ⚠️ A PLANT IS FILED BY POSITION, NEVER BY CASE ID

⛔ **`AX-03/4`**: a valid case id permits `/` and `:`, so one spelled as a path
segment could put a plant outside its own bundle. ⭐ The directory is
`plants/edge-N`, N being the edge case's position in the record's `cases`, and
the case id reaches the gate record's **role**, where `gates.require_role`
already bounds it.

**Landed at AX-04 (E14, step 10.2).** `AX-08` writes bundles into a corpus;
`AX-06`'s quiz has no workspace and is a shape of its own.
"""

from __future__ import annotations

from studyforge.exercise.bundle.document import (
    BUNDLE_API,
    BUNDLE_KEYS,
    OPTIONAL_KEYS,
    Bundle,
    bundle_document,
    bundle_of,
)
from studyforge.exercise.bundle.emit import (
    REFERENCE_SUMMARY,
    SHIPPED_ROLES,
    Emission,
    emit,
    emit_page,
    write,
)
from studyforge.exercise.bundle.layout import (
    BUNDLE_DIRNAMES,
    BUNDLE_FILENAME,
    BUNDLE_FILENAMES,
    BUNDLES_DIRNAME,
    GATES_FILENAME,
    PLANT_DIRNAME,
    PLANTS_DIRNAME,
    ROLE_DIRNAMES,
    STATEMENT,
    STATEMENT_FILENAME,
    TESTS,
    Places,
    edges_of,
    ordinals,
    plant_dirname,
    plant_positions,
    require_inside,
    require_no_gap,
    unpermitted,
)

#: ⛔ The package's whole public surface. A consumer that has to import
#: `studyforge.exercise.bundle.layout` directly is a consumer this contract
#: failed — `docs/conventions/module-structure.md` calls `__init__.py` the
#: contract, and this is what it says.
__all__ = [
    "BUNDLES_DIRNAME",
    "BUNDLE_API",
    "BUNDLE_DIRNAMES",
    "BUNDLE_FILENAME",
    "BUNDLE_FILENAMES",
    "BUNDLE_KEYS",
    "Bundle",
    "Emission",
    "GATES_FILENAME",
    "OPTIONAL_KEYS",
    "PLANTS_DIRNAME",
    "PLANT_DIRNAME",
    "Places",
    "REFERENCE_SUMMARY",
    "ROLE_DIRNAMES",
    "SHIPPED_ROLES",
    "STATEMENT",
    "STATEMENT_FILENAME",
    "TESTS",
    "bundle_document",
    "bundle_of",
    "edges_of",
    "emit",
    "emit_page",
    "ordinals",
    "plant_dirname",
    "plant_positions",
    "require_inside",
    "require_no_gap",
    "unpermitted",
    "write",
]
