# E00 — Foundations

**Wave 0. Blocks everything.**

This epic exists so that no other agent has to invent a package layout, hunt
for a knowledge index, build its own container, or hand-roll test data. Small
tasks, deliberately first. Everything here is infrastructure the other twelve
epics consume without thinking about it.

**Rulings that bite here:** R7 (personal data), R11 (size), R12 (tests mirror
source), R14 (graphify), R15 (containers), R17 (docstrings as contract).

⚠️ **Revised 2026-09-09**, after the CTO's M0 readiness audit
(`handoffs/CTO-2026-09-09-m0-readiness.md`). `FND-03` gained a dependency it
always had, `FND-05` split into `FND-05a`/`FND-05b` because as written it made
M0 unachievable, `FND-06` was added, and two Definitions were corrected. The
epic is now six tasks and M0 has two steps, not one.

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
justification line in the docstring. Also the git ignore rules for **generated
audio produced by this repository's own runs and test runs**, discovery caches
and `graphify-out/`.

⚠️ **That wording is deliberate and it was corrected once.** ⛔ **A corpus's
narration is committed by default** (`SF-17`, `SF-32`) — a clone that carries its
own clips speaks with no synthesis service, no GPU and no network, which is what
R8 is for. What is ignored here is the audio *this* repository's own runs and
tests produce, never a corpus's shipped media. The earlier wording predates that
ruling and invited the next reader to reverse it.

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

⛔ **How `graphify-out/` is ignored in `JS/` is ruled, and the obvious way is
forbidden.** `JS/` is a consumer repository, so R3 applies: the repository's root
ignore file is one of the three edits **no `permitted_edits` entry can
authorise**. ⭐ The fix is the one R3 names — write the ignore file *inside* the
generated directory: `graphify-out/.gitignore` containing a single `*`, which
ignores every path in that directory including itself. `git status` in `JS/`
stays clean and **zero pre-existing files are touched**. ⚠️ This does not apply
to `SF/`, whose own `.gitignore` already carries the directory and is free to.

⚠️ **The two halves of this task are separated in time, on purpose.** The `JS/`
graph is buildable the day the task starts and is the valuable one. A `studyforge`
graph built before `FND-01` lands indexes a tree with no `src/` — "a state nobody
will see again", which is the failure this task's own rebuild rule exists to
prevent.

**Acceptance.** Both graphs build. ⭐ **The `studyforge` graph is rebuilt at the
M0/M1 boundary, after `FND-01`'s layout exists, and that rebuild is the one the
acceptance is judged on** — a graph of a docs-only tree does not satisfy this
task. Three representative queries return useful answers, recorded as examples in
the conventions document. The rebuild command is documented and works
incrementally. `graphify-out/` is ignored in both repositories — in `SF/` by its
root ignore file, in `JS/` by `graphify-out/.gitignore` containing `*`, and
`git status` in `JS/` is clean with the graph present. `graphify.md` states that
R14 binds on a repository when it enters the project's working set, not before.

---

### FND-03 — Development and test container
**Milestone** M0 · **Depends on** **FND-01** · **Team** solo
**Owns** `docker/dev`
**Context** ~25k — `CSD/docker-compose.yml` (service definitions only)

**Definition.** R15's floor: the image in which the framework's own tests,
lint and size checks run, so a contributor needs Docker and nothing else and a
result never depends on whose machine produced it. Distinct from the toolchain
image of E12 — that one is the *reader's* IDE for a consuming project; this one
is the *framework's* build environment.

⚠️ **The dependency on `FND-01` is not a scheduling preference.** This task's
acceptance is that the suite runs — and until `FND-01` lands there is no suite,
no test runner and no lint invocation for the image to run. An image built
earlier is an image rewritten the day the toolchain is chosen.

⭐ **This is where the linter lives, and it closes `FND-01`'s one open clause.**
No `ruff`, `black`, `uv` or `poetry` is installed on the machines available, so
`FND-01`'s "lint and format run clean" had nothing to run and shipped **Blocked**,
not failed. `FND-01` configured ruff in `pyproject.toml` and declared it as the
`lint` extra; `tests/test_repository.py` runs `ruff check` and `ruff format
--check` **where ruff exists** and otherwise skips with a message naming the
extra. ⭐ **The image installs `.[test,lint]` at image-build time**, which turns
those two skipped tests into real ones. That is consistent with the acceptance
below, which requires no network to *run* tests and says nothing about building
the image. ⛔ Do not quietly drop the clause — an unenforced format is the same
class of erosion as an unenforced ceiling.

**Acceptance.** The full test suite runs in the container from a clean
checkout with no host Python. ⭐ **`FND-01`'s two skipped ruff tests run and
pass** rather than skipping. The suite and the quality floor
(`python3 -m tools.quality`) are each separately invocable, and each fails
non-zero on a deliberate violation. The same commands run on the host for anyone
who prefers it, degrading to the standard-library checks where ruff is absent. No
network access is required to run tests.

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

Both are complete and valid: manifest, container maps, and archive documents with
every block type. Also a small set of **deliberately invalid** fixtures — bad version, address/directory
mismatch, digest mismatch, ordinal gap, personal data present — which are
SF-25's acceptance inputs.

⛔ **No golden files here, and the removal was deliberate.** An earlier
Definition asked for "the expected generated output as golden files"; no
Acceptance bullet ever did, and it could not have — `SF-03`, `SF-09`, `SF-10`,
`SF-11` and `SF-12` each own a piece of shapes nobody has drawn yet, so a golden
committed at M0 is a guess that five later tasks must either match or delete.
⭐ **The gap is closed at the point the shape first exists**: `SF-31`'s
acceptance now commits `plan` output for both fixtures as the golden, which is
the cheapest close available and puts the golden next to the contract that
produces it.

⭐ **`depth1/` is the common case, not the exotic one.** Two of the four designed
sources are depth-1 — SPARQL *and* ISO-8583, whose `levels` is `["group"]`
(CTO ruling 1, 2026-09-09). Do not read §11.1's "one depth-1, one depth-2" as
"one odd, one normal".

⛔ **Any fixture carrying personal-data-shaped content satisfies all five
conditions of the review rubric's §1e** — fabricated and unreachable, traceable
to nobody, in a named directory that says so, asserted in **both** directions by
a test, and present in a registry that is itself asserted. This binds anything
later added to the fixture tree, not only the original set.

**Acceptance.** Both corpora are complete and internally consistent. Every
block type appears at least once. The invalid fixtures each violate exactly one
rule, named in a comment. Fixtures are small enough to read.

**Delivered 2026-09-09** — 7 corpora, 43 files, 22 tests, CTO verdict APPROVE.
Beyond the acceptance above the set carries the constraints CTO finding F2
measured rather than assumed: a unit whose content is a **fenced code block full
of XML** (a fence-unaware `<`-scan misreads 26 of ISO's files), and the same tags
appearing **both fenced and raw in one document**, plus a blockquote nesting a
paragraph and a list, and a thematic break. See `handoffs/FND-04.md`, which also
names the golden files it deliberately did **not** write and who owes each.

**Out of scope.** The real Java corpus. These are synthetic on purpose:
fixtures that depend on 166 real files are fixtures nobody can debug.

---

### FND-05a — Workspace, workflow and the pin file
**Milestone** M0 · **Depends on** — · **Team** pair
**Owns** the parent workspace repository
**Context** ~25k — spec §3.1 and R18, `handoffs/CTO-2026-09-09-m0-readiness.md` ruling 2

⚠️ **`FND-05` split on 2026-09-09.** As written it made M0 permanently
unachievable, and M0 gates every other task in the plan. Measured that day: ⛔
**`studyforge` itself has no git remote** — R18's "every component has its own
remote" is currently false of the one component the parent exists to pin — while
`JS/`, `CS/`/`CSD/`, `ISO/` and `SPARQL/` each have one. And ⛔ **`TC/` and `NS/`
do not exist at all**; E12 and E13 create them, at M5 and M3. No amount of remote
provisioning fixes the second blocker, so the whole task was never an M0 task.

⛔ **Neither local-path workaround survives.** An **absolute** local path in
`.gitmodules` writes a home directory into a tracked file — a direct R7
violation. A **relative** URL is R7-clean but git resolves it against the
parent's own remote, and the parent has none, so it resolves to nothing on any
other machine. This task's acceptance says "on a clean machine" and "reproducible
by another checkout" precisely because that is the point.

⛔ **Superseded again, 2026-09-09: nothing is ever pushed to any remote.** That
is a standing decision, so the "create a remote for `studyforge`" unblock is
dead, and so is composition itself — a pin that names an unpushed commit resolves
to nothing anywhere, **including here**. ⭐ **Git submodules are not used in this
project.** See R18's amendment.

⭐ **The workflow survives, the composition does not, and the pin was always the
valuable half.** A submodule is exactly two things — a URL and a commit — and
only the URL half needed pushing.

**Definition.** R18's realisation without submodules: the parent repository that
**records and verifies** which commit of each component a working configuration
used, plus the compose files and scripts that run them together.

⛔ **No `.gitmodules` and no `git submodule add`.** Instead:

- **A tracked pin file** naming each component and the commit it was verified at.
  That file *is* the artifact — it is what a submodule's gitlink was for.
- **A verification command** that fails when a recorded commit is not present in
  the corresponding local checkout, or when a component's `HEAD` has moved
  without the parent recording it. ⭐ That is the two-commit rule, enforced
  mechanically instead of documented as folklore — which is how this project
  enforces everything else.
- **The advance workflow**: pulling a component to a newer commit is a decision
  recorded in the parent and reviewed like any other change, never an incidental
  side effect of somebody's local state.

⚠️ **State the claim honestly and do not inflate it.** This reproduces a working
configuration **on this machine and across time**, which is what R9's
cross-repository versioning needs. ⛔ It does **not** reproduce one across
machines, and no document in the workspace may say it does. If pushing is ever
adopted, the recorded commits are already exactly the data submodules would want.

The parent holds almost no code. **What it holds is the combination** — which
commit of each component works with which, plus the compose files and scripts
that run them together.

⚠️ **The silent first-run failure is still real; it has just changed shape.** It
is no longer "a plain clone yields empty submodule directories" — nobody clones
this. It is now **a component sitting at a commit the parent never recorded**,
which is the same surprise (your change is not part of the configuration) with no
symptom at all. ⛔ That is why verification is a command and not a paragraph.

**Acceptance.** The pin file records every component that exists, `studyforge`
included — there is no longer a reason to exclude it, because nothing is being
fetched. Verification **exits 0** on a correctly recorded workspace; it **exits
1, naming the component**, when a recorded commit is absent from its local
checkout and again when a component's `HEAD` has moved without the parent
recording it — both asserted, not described. ⭐ **The workflow document covers
record, verify, advance and the two-commit rule**, which is the task's stated
reason for existing. ⛔ **No absolute path in any tracked file** (R7) — the pin
file names components by their workspace-relative directory, never by where this
machine happens to keep them. ⛔ **No `.gitmodules` anywhere**, asserted.

**Out of scope.** Migrating CodeSignal into the workspace — that is v2.

---

### FND-05b — ⛔ CANCELLED 2026-09-09

**Milestone** — · **Depends on** — · **Team** —

⛔ **Cancelled outright, not deferred**, by the CTO ruling in
`handoffs/CTO-2026-09-09-round3.md`. Its whole content was "add the three
components `FND-05a` could not, as submodules", and **submodules are no longer
used in this project** (R18, amended): nothing is ever pushed to any remote, so a
submodule pin names a commit that resolves to nothing anywhere.

⭐ **Its residue costs nothing and has already moved.** `studyforge`, `TC/` and
`NS/` are now recorded in `FND-05a`'s pin file like every other component — there
is no reason to exclude them once nothing is being fetched — and each is added by
the task that creates it (E12, E13). **No task is needed to do this.**

⚠️ **Both of its original blockers are gone rather than solved.** A remote for
`studyforge` is no longer wanted; `TC/` and `NS/` not existing yet is now just a
pin file with fewer rows, which is a correct state rather than an incomplete one.

---

### FND-06 — Repository personal-data check
**Milestone** M0 · **Depends on** FND-01 · **Team** solo
**Owns** `tools/quality/personal_data.py` and its mirrored test
**Context** ~20k — R7, `../conventions/review-rubric.md` §1a, §1b, §1e, `handoffs/FND-01.md`

⭐ **This is `FND-01`'s own finding 5, promoted to a task.** `FND-01` established
the quality floor and named this as the one rule it could not carry: the seam is
already there — a fifth entry in `tools/quality/__init__.py`'s `CHECKS` tuple, and
nothing else changes. ⛔ It is not `FND-01`'s scope creeping; it is a finding
being acted on, which is what the handoff mechanism is for.

**Definition.** R7 enforced by the build rather than by a reviewer's grep. A
standard-library check living beside the size, mirror, docstring and style checks,
carrying three things the rubric currently asks a human to run by hand:

- **The pattern sweep** (rubric §1a) — home paths, addresses, `$HOME`, `~/…`,
  `.local` hostnames — over the repository tree, with the documented placeholders
  (`contact@example.com`, `Example/0.1 (+https://example.invalid)`, `Jane Doe`,
  `/path/to/project`) and the attribution trailer's `noreply@anthropic.com` as
  the entire allow-list.
- **The sanctioned-directory registry** (§1e) — the named directories whose whole
  purpose is to hold content the gate must refuse. ⛔ **The registry is asserted
  by a test**, so a sixth negative fixture cannot appear without showing up in
  one, and the sweep excludes **those directories and only those**. ⛔ A sweep
  that excludes `tests/` wholesale has stopped checking the tree where fixtures
  live.
- **The session-identifier check** (§1b) — the current user name, hostname and
  git identity, ⛔ **derived at runtime and never written to disk**. That
  constraint is the whole design: a check that stores the values it looks for has
  become the leak it was built to prevent.

⛔ **This is not `SF-08`.** `SF-08` gates strings entering the **archive** — the
generated artifact, at build time. This gates strings entering the
**repository** — source, docs, fixtures, commit messages. Different inputs,
different moment, and neither substitutes for the other.

⭐ **Why it is a task and not a habit.** `CLAUDE.md` records that R7 has already
been violated once in this repository's own documents and corrected. The rubric
makes R7 the one ⛔ HARD FAIL with no "minor" verdict, because an identifier in a
commit survives the commit that removes it. This project has twice decided not to
rely on somebody remembering to look — once for the size ceiling, once for the
test mirror — and this is the third instance of the same argument.

**Acceptance.** The check exits non-zero on a purpose-built violating file and
zero on the tree as it stands. It is registered in `CHECKS`, so
`python3 -m tools.quality` and `pytest` both fail on a hit **from one
implementation** — ⛔ a second definition of what R7 means is a second thing to
drift. The sanctioned-directory registry is asserted by a test that fails when a
directory is added to the tree but not to the registry.
⛔ The check writes no derived identifier to any file, log or error message — a
refusal names the **shape**, never the value, verified by a test that asserts the
message does not contain the matched text. Standard library only. `tools/` stays
excluded from the packaging config.

**Out of scope.** Rewriting history when a hit is found — that is the author's,
under the rubric. Scanning commit messages of merged history; this gates what is
being added.
