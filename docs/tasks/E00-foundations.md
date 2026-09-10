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
M0 unachievable, `FND-06` was added, and two Definitions were corrected. M0 has
two steps, not one.

⚠️ **Revised again the same day** (`handoffs/CTO-2026-09-09-round3.md`), after
the standing decision that **nothing is ever pushed to any remote**. `FND-05a`
becomes a pin file rather than a submodule composition; **`FND-05b` is cancelled
outright**. The epic is **five live tasks**.

⭐ **Two authors edited `FND-05a` in the same round, and neither contribution is
dropped silently.** The PO marked it blocked with a stop sign reading *do not
start this task*; the CTO then made the ruling that unblocked it. ⛔ **The stop
sign is superseded and deliberately removed** — a blocked notice on a task that
is now startable is worse than none, because it stops the wrong person. ⭐ **The
argument behind it survives and is why this note exists:** an agent reads the
epic document and not always the board, so a status the board carries must reach
the epic too. `FND-05b`'s row records the same thing for the gap the PO raised
there.

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
**Effort** ⚠️ **Large, and measured after the fact: roughly an order of magnitude
over the reading budget.** A 12-chunk parallel extraction over 217 documents plus
a bridging pass, then the same again for this repository. ⭐ Recorded because it
is the evidence that produced the `Effort` field at all.

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

⛔ **Follow-up: the three skips that appear in every container run.** They skip
because the sibling repositories are absent from the image, and ⚠️ **a skip that
every run reports is not a skip — it is an untested claim wearing a skip's
clothes.** ⭐ A skip is meant to say *"not applicable here, covered there"*; one
that is never applicable anywhere says nothing and is read as reassurance. **The
container is authoritative by three less than it claims to be.**

**Two acceptable resolutions, and "leave them skipping" is not one:** detect the
workspace and set `STUDYFORGE_WORKSPACE` so the image can see the siblings and
the three run — or ⭐ **name those three explicitly as covered elsewhere**, in the
skip message itself, so the reason is legible at the point of the skip rather
than in somebody's memory.

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

⛔ **STOP — blocked on a CTO ruling, and its acceptance below is under
re-ruling. Do not start this task.** A standing user decision, taken
2026-09-09, is that **nothing is ever pushed to any remote**; everything stays in
local repositories, permanently. An absolute local submodule URL writes a home
directory into a tracked `.gitmodules` (R7) and a relative one resolves against a
remote that will never exist — ⛔ **so the submodule composition has no legal
form**, not merely an inconvenient one. ⭐ The workflow-document half needs no URL
and is expected to survive; the CTO is ruling on what the rest becomes. See
`BOARD.md`, **B2** and **G1**.

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

⚠️ **What the PO's superseded version of this row asked, and where it was
answered.** It recorded R18's lost guarantee as an open gap — *"the parent's
recorded submodule commits are the version pin"* is the sentence R9's
cross-repository reproducibility rests on, and it assumed fetchable remotes.
⭐ **That question is closed, not dropped:** R18's amendment and `FND-05a`'s pin
file are the answer, and the honest reduction — reproducible **across time on
this machine**, ⛔ **not across machines** — is stated there rather than left to
be inferred.

---

### FND-07 — Knowledge-index availability and freshness
**Milestone** M1 · **Depends on** — · **Team** solo
**Owns** the index tripwire in `tools/quality/`, and `graphify.md`'s worktree section
**Context** ~15k — R14, `handoffs/FND-02.md`, `docs/conventions/graphify.md`, `tests/test_knowledge_index.py`

⭐ **This task exists because `FND-02` was marked done for an artifact that never
reached the repository.** Its acceptance — *"the `studyforge` graph is rebuilt at
the M0 close"* — was **true in the worktree where it ran and false everywhere
else**, because `graphify-out/` is git-ignored and ⛔ **an ignored artifact cannot
travel on a branch.** Measured 2026-09-09: **33 worktrees, 2 with a graph** — the
main checkout and `FND-02`'s own. ⚠️ **Every agent since has worked without the
index while the board said it existed**, which is the R14 premise every `Context`
budget in the plan rests on.

⛔ **This is not a criticism of `FND-02`.** It did the work, it verified it, and it
recorded what it saw. The defect is that **the acceptance was unverifiable from
the repository**, so nothing could have caught the gap — which is why the fix is a
rule and a check rather than a rebuild.

**Definition.** Three things, and the third is the cheap one nobody had measured.

1. ⭐ **The tripwire.** A check that answers, from any checkout, *is there an index
   here and can it be trusted?*
   - **Absent** → ⚠️ **report, with the rebuild command, and do not fail.** A
     fresh clone legitimately has no index, and ⛔ a red suite on clone is hostile
     and gets muted, which is how a check stops being read.
   - ⛔ **Present but older than the newest tracked file under `src/`, `tools/` or
     `docs/` → FAIL.** ⭐ **A stale index is worse than an absent one**, because
     the agent trusts it: absence is visible and staleness answers confidently
     with yesterday's tree.
2. **The wave-open checklist gains a line** — *index present and current in this
   checkout* — beside the `[structural]` sweep. The PO runs both.
3. ⭐ **The worktree convention, which makes R14 affordable and is mostly already
   there.** Measured: `graphify explain` and `graphify path` accept
   `--graph <path>` and **work from a worktree with no index of its own**;
   `graphify query` does not and reads `./graphify-out/graph.json` only.

   ⚠️ **That maps exactly onto R14's own qualification.** The two commands the
   ruling holds for *unconditionally* are the two that need no local build; the
   one that needs a local build is `query`, already the weak one. ⭐ **So the cost
   is paid once per repository, not once per worktree** — 33 rebuilds was never
   payable, and an unaffordable rule is one that gets skipped, which is what
   happened. `graphify.md` gains the invocation; ⚠️ four tests assert that
   document's content, so they move with it.

4. ⛔ **Bridge the framework's own graph, and make the tripwire care.** Measured
   on the rebuilt index: **232 doc↔code edges out of 6,081 — 3.8%**, and
   `graphify path "R7 — No Personal Data…" "assert_clean()"` returns **no path,
   even undirected.** ⚠️ **That is the question this repository most needs
   answered — *which ruling does this code implement?* — and the index cannot
   answer it.** The 3.8% is incidental, from handoffs naming functions in prose;
   it is not a bridge.

   ⭐ **We wrote this rule for somebody else and did not apply it to ourselves.**
   `SK-07` item 9 already says a graph built by running the tool alone has no
   doc↔code edges and that **bridging is the part that would be missed** —
   `FND-02` built the bridging pass, applied it to the **corpus** (806 edges, 162
   of 166 lessons), and nobody ran the equivalent here. The recipe is in
   `handoffs/FND-02.md`, deterministic, literal symbol occurrence, ⛔ never an LLM.

   ⚠️ **So the tripwire must check usefulness, not just presence** — ⛔ **present,
   current and unbridged is a worse lie than absent**, because all three green
   lights are on and the one question that matters returns silence.

**Acceptance.** The tripwire reports absence naming the rebuild command and exits
zero; ⛔ **it fails when the doc↔code edge census is below a recorded floor**, so
an index that cannot connect a ruling to its enforcement is not certified as
healthy — the framework's graph is bridged to establish that floor, and the
census command is the one `graphify.md` already documents; ⛔ it **fails** on an index older than the newest tracked source, asserted
by a test that backdates one rather than by description. `graphify.md` carries the
`--graph` invocation for a worktree, and `tests/test_knowledge_index.py` asserts
it as it does the other runbook entries. ⛔ **No test in the suite skips
unconditionally** — a skip every run reports is an untested claim wearing a
skip's clothes.

**Out of scope.** Building any graph. Committing one — `graphify-out/` stays
ignored, and ⛔ the answer to an untracked artifact is never *"track it"*: the
index is 90 MB for a corpus, derived, and rebuilt rather than merged.

---

### FND-06 — Repository personal-data check
**Milestone** M0 · **Depends on** FND-01 · **Team** solo
**Owns** `tools/quality/personal_data.py` and its mirrored test
**Context** ~20k — R7, `../conventions/review-rubric.md` §1a, §1b, §1e, `handoffs/FND-01.md`

⭐ **Re-sequenced 2026-09-09: this is now the first task to land under whatever
C5 rule the CTO makes, and it should land before M1 step 1.2.** ⛔ It is a task
that **adds a rule to the floor**, and adding a rule is exactly what has now
broken three in-flight branches in one milestone (`BOARD.md`, **C5**). So it is
the proving instance rather than another victim: ⭐ **if option 1 is ruled, this
task carries the mechanism** — the rule and a tree-wide pass that makes the rule
true arrive in the same commit — and it does so while **two** branches are in
flight rather than fifteen. ⚠️ Every week it waits, the blast radius of the next
rule grows.

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

⛔ **And it is the first task to obey the same-commit rule, on itself** (CTO,
`handoffs/CTO-2026-09-09-round4.md`):

> ⛔ **A commit that adds or tightens a check brings the whole tree into
> compliance in the same commit**, and the check is never merged in a state where
> any tracked file fails it. ⭐ **No open branch is expected to fix a rule it
> never saw** — the rule-adding commit fixes the tree, and open branches inherit
> compliance when they rebase.

⚠️ This is C5's actual lesson, and `FND-06` is where it is first tested: it adds
the fifth rule to a tree that fifteen M1 branches are open against. **If the
sweep finds anything, `FND-06` fixes it** — it does not file fifteen findings.

⭐ **It also carries one consolidation it did not create.** `is_ignored()` is
duplicated between `tests/test_repository.py` and `tests/test_knowledge_index.py`,
against `tests/support.py`'s own stated rule. `FND-02` created the duplicate
deliberately rather than edit a file outside its task, and said so. ⛔ Three
lines, into `tests/support.py`, and both call sites import it — this task is the
next one whose scope legitimately spans both.

⭐ **The false-positive allow-list is specified and deliberately not built —
because the problem it was for does not exist.** Recorded rather than dropped, so
it is not re-proposed.

⚠️ **The claim it rested on was true when it was written and false when it was
acted on.** `FND-04`'s finding 8 reported the repository-wide sweep as unclean,
its only hit being `E02-content-pipeline.md` quoting `n@router` + `.get` — E02's
own worked example of the escaping artefact that refused three clean lessons.
⭐ **Re-measured on the merged tip, and both numbers are zero:**

- `tools.quality`'s implemented check: **0 findings** over the whole tree;
- the rubric's **current** §1a patterns: **0 hits** across `docs/` and
  `CLAUDE.md`, and they do not fire on that line.

The **superseded** §1a patterns produced **24 hits**, every one a false positive
and E02's among them. ⛔ **The two-character minimum local part kills
`n@router.get` exactly** — the local part is one character — and the `.local`
trailing guard and the dropped `$HOME`/`~/` alternatives account for the rest.

⭐ **The reasoning survives and is the part worth keeping, if a real hit ever
arrives:** ⛔ the sweep does **not** stop reading `docs/` — that is where R7 was
violated once already (`CLAUDE.md`), and excluding the directory would remove the
check from the place with the worst record. ⛔ Nor would prose qualify as a §1e
sanctioned fixture, which requires a named directory with a `VIOLATION.md`. So
the shape, if it is ever needed, is **a narrow list of documented false
positives, each carrying its reason inline and asserted to stay short** — because
⭐ **a gate that must be silenced somewhere is safer with a short list that fails
when it grows: the list gets read, the exclusion does not.**

⚠️ **But the better answer is the one that was actually taken, and it is worth
naming as the precedent:** ⭐ **the pattern was corrected, not exempted.** An
allow-list would have recorded 24 instances of a defect in the pattern as 24
facts about the tree. ⛔ **Fix the class; list the instance only when the class is
right and the instance is genuinely exceptional.**

⛔ **Follow-up: the exception text is itself a rule and needs enforcing.** The
`Size exception:` opt-out states *why splitting would be worse* — ⚠️ but nothing
checks that the line says anything at all, so `Size exception: needed` passes the
same gate as a real justification. ⭐ **An opt-out nobody has to justify is a
ceiling with a documented bypass**, which is the erosion `FND-01` exists to
prevent, arriving through the door it left open. A minimum-substance check
belongs beside the other floor rules.

⛔ **Follow-up (CTO round 14): a split literal defeats the sweep, and folding
closes it without anyone having to judge intent.** ⚠️ Two of SF-03's tests
legitimately need the shape they refuse, and spell it as a concatenation of two
literals so the sweep does not read it as a leak. `tests/studyforge/
test_version.py` did the same first, and it is now the established technique.
⛔ The sweep reads source **text**, so it sees the operator between the halves
and no leak — and it cannot tell a legitimate split from an evasive one.

⭐ **It never needs to.** Evaluate the expression instead of reading the line:
walk the Python file's AST and constant-fold adjacent literal concatenation
before matching. A split then folds to the same string as an unsplit one, and
the distinction the sweep cannot make stops existing. ⚠️ **Python files only,
and the check says so** — a `.md` file has no AST and keeps the text sweep.

⛔ **Then the tests that genuinely need a shape get one sanctioned home**, not a
technique: one named module holding the shapes, each with the reason it is
there, added to `SANCTIONED_PERSONAL_DATA_DIRS` and imported by every test that
refuses one. ⭐ That is what the sanctioned list already says the design is —
"the ONE directory allowed to hold the shape" — and the split is a second,
unlisted one that arrived because it was easier.

⚠️ **State the reach honestly.** Folding stops the accident and the easy
workaround; `chr(47)`, a `join`, or a runtime-built string still pass, and no
source-text gate will ever catch those. ⛔ **The gate that matters for those is
not this one** — see the rubric's emission clause, added in the same round.

**Out of scope.** Rewriting history when a hit is found — that is the author's,
under the rubric. Scanning commit messages of merged history; this gates what is
being added. ⛔ Chasing an adversary: this repository has no adversary, it has
agents who need a shape for a test and will take whichever route is open.
