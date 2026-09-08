# E00 — Foundations

**Wave 0. Blocks everything.**

This epic exists so that no other agent has to invent a package layout, hunt
for a knowledge index, build its own container, or hand-roll test data. Four
tasks, deliberately small, deliberately first. Everything here is infrastructure
the other twelve epics consume without thinking about it.

**Rulings that bite here:** R11 (size), R12 (tests mirror source), R14
(graphify), R15 (containers), R17 (docstrings as contract).

---

### FND-01 — Repository scaffolding and quality floor
**Milestone** M0 · **Depends on** — · **Team** pair
**Owns** the `studyforge` repository skeleton
**Context** ~30k — `../conventions/module-structure.md`, `CS/pyproject.toml`, `CS/tests/support.py`

**Definition.** The skeleton every other task builds inside, and the automated
floor that keeps R11 and R12 true without anybody policing them. Establishes:
the `src/` package layout of spec §3; the mirrored `tests/` tree; packaging and
dependency configuration (standard library only for source, test-only
dependencies allowed); the test runner; lint and format configuration; and a
**module size check that fails the build** on a source module over 400 lines or
a test module over 600, with a documented per-module opt-out that requires a
justification line in the docstring. Also the git ignore rules for generated
audio, discovery caches and `graphify-out/`.

Size enforcement is automated on purpose. A ceiling that lives only in a
document is a ceiling that erodes under deadline, and the debt this project is
explicitly paying down (a 2,743-line module) is what erosion looks like.

**Acceptance.** A trivial package and its mirrored test run green from a clean
checkout. The size check fails on a deliberately oversized module and passes
with a justified opt-out. Lint and format run clean. `pyproject` declares no
runtime dependencies.

**Out of scope.** CI hosting. The container is FND-03.

---

### FND-02 — Knowledge index
**Milestone** M0 · **Depends on** — · **Team** solo
**Owns** `graphify-out/` in all three repositories
**Context** ~20k — `../conventions/graphify.md`, `CSD/graphify-out/GRAPH_REPORT.md` (skim only)

**Definition.** R14's enablement. Builds and verifies a graph for `studyforge`
and for `Claude-senior-java-engineer` (CodeSignal already has one at
`CSD/graphify-out/`), confirms the query, path and explain commands answer, and
records in the repository how an agent invokes them and when the graph is
rebuilt. Establishes the rebuild point — between waves, never mid-task by the
agent doing the work, because a graph built against a half-finished tree
indexes a state nobody will see again.

The Java repository's graph is the more valuable of the two: 212 documents and
345 classes are exactly the shape where an agent otherwise burns its whole
context budget re-deriving structure.

**Acceptance.** Both graphs build. Three representative queries return useful
answers, recorded as examples in the conventions document. The rebuild command
is documented and works incrementally. `graphify-out/` is git-ignored.

---

### FND-03 — Development and test container
**Milestone** M0 · **Depends on** — · **Team** solo
**Owns** `docker/dev`
**Context** ~25k — `CSD/docker-compose.yml` (service definitions only)

**Definition.** R15's floor: the image in which the framework's own tests,
lint and size checks run, so a contributor needs Docker and nothing else and a
result never depends on whose machine produced it. Distinct from the toolchain
image of E12 — that one is the *reader's* IDE for a consuming project; this one
is the *framework's* build environment.

**Acceptance.** The full test suite runs in the container from a clean
checkout with no host Python. The same command runs on the host for anyone who
prefers it. No network access is required to run tests.

---

### FND-04 — Shared contract fixtures
**Milestone** M0 · **Depends on** — · **Team** pair
**Owns** `tests/fixtures/`
**Context** ~35k — spec §4–§6, `CS/tests/fixtures/`

**Definition.** Two synthetic corpora that every downstream task tests
against, so twelve epics are not each inventing their own idea of valid input —
which is how parallel work drifts into twelve incompatible mental models.

- **`depth1/`** — one container level, three units, one variant, **zero
  exercises**. This is the SPARQL shape, and it exists to keep the 1-level and
  no-exercise paths first-class from wave 0 rather than discovered late.
- **`depth2/`** — two container levels, two containers, several units, one
  variant, exercises present, including one unit with an authored overlay and
  one with none. This is the Java and CodeSignal shape.

Both are complete and valid: manifest, container maps, archive documents with
every block type, and the expected generated output as golden files. Also a
small set of **deliberately invalid** fixtures — bad version, address/directory
mismatch, digest mismatch, ordinal gap, personal data present — which are
SF-25's acceptance inputs.

**Acceptance.** Both corpora are complete and internally consistent. Every
block type appears at least once. The invalid fixtures each violate exactly one
rule, named in a comment. Fixtures are small enough to read.

**Out of scope.** The real Java corpus. These are synthetic on purpose:
fixtures that depend on 166 real files are fixtures nobody can debug.

---

### FND-05 — Workspace and submodule composition
**Milestone** M0 · **Depends on** — · **Team** pair
**Owns** the parent workspace repository
**Context** ~25k — spec §3.1 and R18

**Definition.** R18's realisation: the parent repository that composes the
framework, the toolchain image, the narration service and each corpus as
submodules, so one checkout is a complete working system while each component
keeps its own remote and cadence.

The parent holds almost no code. **What it holds is the combination** — which
commit of each component works with which, plus the compose files and scripts
that run them together. That recorded set of pins is the artifact, and it is
what makes a working configuration reproducible across machines and across
time.

Two workflows must be documented because both are silent first-run failures:

- **A plain clone yields empty submodule directories.** The clone must recurse,
  and the documented first-run command must say so. This is the single most
  common way somebody concludes the project is broken.
- **A change to a component is two commits** — one in the component, one in the
  parent recording the new pin. A submodule tracks a *commit*, not a branch,
  which is the feature (reproducibility) and the surprise (a forgotten parent
  commit means nobody else sees your change). Detached-HEAD checkout is the
  default; the branch-tracking configuration and the update command are part of
  this task's deliverable, not folklore.

Also establishes how a component is **advanced deliberately** — pulling a
component to a newer commit is a decision recorded in the parent, reviewed like
any other change, never an incidental side effect of someone's local state.

**Acceptance.** A recursive clone on a clean machine yields every component at
its pinned commit. A component change plus a parent pin update is reproducible
by another checkout. A plain non-recursive clone fails with a message pointing
at the documented command rather than an empty directory. The workflow document
covers clone, update, advance, and the two-commit rule.

**Out of scope.** Migrating CodeSignal into the workspace — that is v2.
